import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from threading import Lock
from datetime import datetime, timezone

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "users.json"

_LOCK = Lock()
_STORE: Dict[int, Dict[str, Any]] = {}
_NEXT_ID = 1
_INITIAL_LOADED = False


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_initial() -> None:
    """Load users from JSON once into the in-memory store."""
    global _STORE, _NEXT_ID, _INITIAL_LOADED
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        users = json.load(f)
    store: Dict[int, Dict[str, Any]] = {}
    max_id = 0
    for u in users:
        uid = int(u.get("id"))
        store[uid] = u.copy()
        if uid > max_id:
            max_id = uid
    with _LOCK:
        _STORE = store
        _NEXT_ID = max_id + 1
        _INITIAL_LOADED = True


def reset_store() -> None:
    """Reset the in-memory store back to the initial JSON contents."""
    _load_initial()


def _ensure_loaded() -> None:
    if not _INITIAL_LOADED:
        _load_initial()


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user by ID from the store."""
    _ensure_loaded()
    with _LOCK:
        return _STORE.get(user_id)


def list_users() -> List[Dict[str, Any]]:
    _ensure_loaded()
    with _LOCK:
        return [u.copy() for u in _STORE.values()]


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    _ensure_loaded()
    with _LOCK:
        return _STORE.get(int(user_id)).copy() if int(user_id) in _STORE else None


def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new user in the in-memory store. Does NOT modify the original JSON file."""
    _ensure_loaded()
    global _NEXT_ID
    with _LOCK:
        uid = int(_NEXT_ID)
        _NEXT_ID += 1
        now = _now_iso()
        new_user = user_data.copy()
        new_user["id"] = uid
        if "created_at" not in new_user:
            new_user["created_at"] = now
        new_user["updated_at"] = now
        _STORE[uid] = new_user
        return new_user.copy()


def update_user(user_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update fields for an existing user. Returns updated user or None if not found."""
    _ensure_loaded()
    uid = int(user_id)
    with _LOCK:
        existing = _STORE.get(uid)
        if not existing:
            return None
        updates = {k: v for k, v in updates.items() if k != "id"}
        existing.update(updates)
        existing["updated_at"] = _now_iso()
        return existing.copy()


def delete_user(user_id: int) -> bool:
    """Delete a user from the in-memory store. Returns True if deleted."""
    _ensure_loaded()
    uid = int(user_id)
    with _LOCK:
        if uid in _STORE:
            del _STORE[uid]
            return True
        return False
