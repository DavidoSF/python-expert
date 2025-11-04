# ...existing code...
from fastapi.testclient import TestClient
from app.main import app
import re
import pytest
from pathlib import Path
import json

client = TestClient(app)

DEFAULT_QUERY = {"city": "Paris", "countryCode": "FR", "date": "2025-10-21"}
DEFAULT_JSON = {
    "id": 9999,
    "activity_id": 1,
    "user_id": 1,
    "score": 5,
    "name": "AutoTest",
    "type": "test",
    "location": "Paris",
    "is_indoor": True,
    "date": "2025-10-21",
    "description": "Auto-generated test payload"
}

SKIP_PREFIXES = ("/user/reset", "/static", "/openapi.json", "/favicon.ico")


def _fill_path(path: str) -> str:
    def repl(match):
        name = match.group(1)
        lname = name.lower()
        if "city" in lname:
            return "Paris"
        if "date" in lname:
            return "2025-10-21"
        if "country" in lname:
            return "FR"
        if "id" in lname or "pk" in lname:
            return "1"
        return "1"
    return re.sub(r"{([^}]+)}", repl, path)

# load per-route overrides if present
_OVERRIDES_PATH = Path(__file__).parent / "route_overrides.json"
try:
    ROUTE_OVERRIDES = json.loads(_OVERRIDES_PATH.read_text(encoding="utf-8")) if _OVERRIDES_PATH.exists() else {}
except Exception:
    ROUTE_OVERRIDES = {}

# build route+method list once so pytest ids are stable and readable and show the HTTP method
_ROUTE_METHODS = []
for r in app.routes:
    if not hasattr(r, "methods"):
        continue
    path = getattr(r, "path", None)
    if not path or any(path.startswith(p) for p in SKIP_PREFIXES):
        # skip docs/static routes at collection time to reduce clutter
        continue
    methods = set(getattr(r, "methods", [])) - {"HEAD", "OPTIONS"}
    for m in sorted(methods):
        _ROUTE_METHODS.append((r, m))
# precompute readable ids to avoid issues during pytest collection
_ROUTE_METHODS_IDS = [f"{getattr(r, 'path', str(r))} [{m}]" for (r, m) in _ROUTE_METHODS]


@pytest.mark.parametrize("route,method", _ROUTE_METHODS, ids=_ROUTE_METHODS_IDS)
def test_route_responsive(route, method):
    path = getattr(route, "path", None)

    # allow per-route skip via overrides
    override = ROUTE_OVERRIDES.get(path, {})
    if override.get("skip"):
        pytest.skip(f"Skipped by route_overrides: {override.get('reason', '')}")

    methods = set(getattr(route, "methods", [])) - {"HEAD", "OPTIONS"}
    if method not in methods:
        pytest.skip(f"Method {method} not enabled for route: {path}")

    url = _fill_path(path)

    try:
        method_cfg = override.get("methods", {}).get(method, {})
        params = method_cfg.get("params", DEFAULT_QUERY)
        json_body = method_cfg.get("json", DEFAULT_JSON) if method in ("POST", "PUT", "PATCH") else None

        if method == "GET":
            resp = client.get(url, params=params)
        elif method == "POST":
            resp = client.post(url, json=json_body, params=params)
        elif method == "PUT":
            resp = client.put(url, json=json_body, params=params)
        elif method == "PATCH":
            resp = client.patch(url, json=json_body, params=params)
        elif method == "DELETE":
            resp = client.delete(url, params=params)
        else:
            pytest.skip(f"Skipping uncommon method {method} for route {path}")
    except Exception as e:
        pytest.fail(f"Request to {method} {url} raised exception: {e}")

    assert resp is not None, f"No response for {method} {url}"

    # check expected status if provided in overrides, otherwise ensure no 5xx
    expected = override.get("methods", {}).get(method, {}).get("expected_status")
    if expected:
        assert resp.status_code in expected, f"Unexpected status {resp.status_code} for {method} {url} (expected {expected})"
    else:
        assert resp.status_code < 500, f"Server error {resp.status_code} for {method} {url}"

    ctype = resp.headers.get("content-type", "")
    if "application/json" in ctype:
        try:
            _ = resp.json()
        except Exception as e:
            pytest.fail(f"Invalid JSON response for {method} {url}: {e}")