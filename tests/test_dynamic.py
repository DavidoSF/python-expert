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

SKIP_PREFIXES = ("/static", "/openapi.json", "/favicon.ico")

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

# build route list once so pytest ids are stable and readable
_ROUTES = [r for r in app.routes if hasattr(r, "methods")]

@pytest.mark.parametrize("route", _ROUTES, ids=lambda r: getattr(r, "path", str(r)))
def test_route_responsive(route):
    path = getattr(route, "path", None)
    if not path or any(path.startswith(p) for p in SKIP_PREFIXES):
        pytest.skip(f"Skipping docs/static route: {path}")

    # allow per-route skip via overrides
    override = ROUTE_OVERRIDES.get(path, {})
    if override.get("skip"):
        pytest.skip(f"Skipped by route_overrides: {override.get('reason', '')}")

    methods = set(getattr(route, "methods", [])) - {"HEAD", "OPTIONS"}
    if not methods:
        pytest.skip(f"No usable methods for route: {path}")

    url = _fill_path(path)

    responses = []
    for m in methods:
        try:
            method_cfg = override.get("methods", {}).get(m, {})
            params = method_cfg.get("params", DEFAULT_QUERY)
            json_body = method_cfg.get("json", DEFAULT_JSON) if m in ("POST", "PUT", "PATCH") else None

            if m == "GET":
                resp = client.get(url, params=params)
            elif m == "POST":
                resp = client.post(url, json=json_body, params=params)
            elif m == "PUT":
                resp = client.put(url, json=json_body, params=params)
            elif m == "PATCH":
                resp = client.patch(url, json=json_body, params=params)
            elif m == "DELETE":
                resp = client.delete(url, params=params)
            else:
                # skip uncommon methods
                continue
        except Exception as e:
            responses.append((m, None, e))
            continue

        responses.append((m, resp, None))

    assert responses, f"No requests attempted for route {path} methods {methods}"

    for method, resp, exc in responses:
        if exc:
            pytest.fail(f"Request to {method} {url} raised exception: {exc}")
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