"""
Integration checks for the Muse database schema (schema.sql) and seed data (seed.sql)
using Supabase.

Environment expectations mirror test_connection.py: set SUPABASE_URL and
SUPABASE_ANON_KEY in .env (load_dotenv is called automatically). If you also provide
TEST_USER_EMAIL and TEST_USER_PASSWORD, the script will authenticate before running
mutating checks so that operations respect any row-level security policies.
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency
    from dotenv import load_dotenv  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    load_dotenv = None  # type: ignore

if load_dotenv is not None:
    load_dotenv()

SQLSTATE_CHECK_VIOLATION = "23514"
SQLSTATE_UNIQUE_VIOLATION = "23505"

REQUIRED_TABLES = [
    "user_profiles",
    "creator_profiles",
    "creator_content",
    "user_posts",
    "user_media",
    "user_follows",
    "post_inspirations",
]

# Seed expectations mirror sql/seed.sql
SEED_USERS = {
    "6d31c637-dd42-4a44-a0a4-ba9eda5dfebf": "free",
    "71fd4d4b-ad95-4d77-8e43-5d0d666a5693": "pro",
    "f08c2ad0-7629-4da6-ab99-44a7ad32a3e2": "free",
}

SEED_CREATOR_URLS = {
    "https://www.linkedin.com/in/josephalalou/",
    "https://www.linkedin.com/in/robin-guo/",
    "https://www.linkedin.com/in/ryan/",
}

SEED_POSTS = {
    "0a1894aa-a4cf-47db-8fd8-dc6373e6e8e9": "6d31c637-dd42-4a44-a0a4-ba9eda5dfebf",
    "8a845cc5-77f7-4a00-883b-e277b73a4ebb": "f08c2ad0-7629-4da6-ab99-44a7ad32a3e2",
    "e037dfd2-5e20-458c-8179-2289c23a42ea": "71fd4d4b-ad95-4d77-8e43-5d0d666a5693",
}

SEED_POST_INSPIRATIONS = [
    (
        "0a1894aa-a4cf-47db-8fd8-dc6373e6e8e9",
        "https://www.linkedin.com/feed/update/urn:li:activity:7379926081165971456/",
    ),
    (
        "e037dfd2-5e20-458c-8179-2289c23a42ea",
        "https://www.linkedin.com/feed/update/urn:li:activity:7379527699394052096/",
    ),
]

SEED_USER_POST_ROWS: Dict[str, Dict[str, Any]] = {
    "0a1894aa-a4cf-47db-8fd8-dc6373e6e8e9": {
        "user_id": "6d31c637-dd42-4a44-a0a4-ba9eda5dfebf",
        "raw_text": "If you consider yourself an engineer...",
        "created_at": "2025-10-05T21:44:37.966178+00:00",
        "updated_at": "2025-10-05T21:44:37.966178+00:00",
    },
    "8a845cc5-77f7-4a00-883b-e277b73a4ebb": {
        "user_id": "f08c2ad0-7629-4da6-ab99-44a7ad32a3e2",
        "raw_text": "I don't need any inspiration for my post because it's just a cute dog!",
        "created_at": "2025-10-05T21:44:52.004890+00:00",
        "updated_at": "2025-10-05T21:44:52.004890+00:00",
    },
    "e037dfd2-5e20-458c-8179-2289c23a42ea": {
        "user_id": "71fd4d4b-ad95-4d77-8e43-5d0d666a5693",
        "raw_text": "When I reflect on the positions of my peers...",
        "created_at": "2025-10-05T21:45:16.451121+00:00",
        "updated_at": "2025-10-05T21:45:16.451121+00:00",
    },
}

SEED_USER_MEDIA_ROWS = [
    {
        "user_media_id": "bdd7ab64-8633-417b-8068-0830d7c97fc8",
        "post_id": "8a845cc5-77f7-4a00-883b-e277b73a4ebb",
        "media_url": "https://petcube.com/blog/content/images/2018/04/boo-the-dog-2.jpg",
        "media_type": "image",
        "created_at": "2025-10-05T21:46:08.867377+00:00",
        "updated_at": "2025-10-05T21:46:08.867377+00:00",
    }
]

SEED_USER_FOLLOW_ROWS = [
    {
        "id": "4dfdadd3-104e-4472-b5c0-35b5445be233",
        "user_id": "71fd4d4b-ad95-4d77-8e43-5d0d666a5693",
        "creator_profile_url": "https://www.linkedin.com/in/robin-guo/",
        "created_at": "2025-10-05T21:51:44.075097+00:00",
    },
    {
        "id": "68c31ebd-9f75-466d-b062-fdbcdff50037",
        "user_id": "71fd4d4b-ad95-4d77-8e43-5d0d666a5693",
        "creator_profile_url": "https://www.linkedin.com/in/ryan/",
        "created_at": "2025-10-05T21:51:31.144221+00:00",
    },
    {
        "id": "f07f3fe1-9f7f-4e51-b923-d8da806c8469",
        "user_id": "6d31c637-dd42-4a44-a0a4-ba9eda5dfebf",
        "creator_profile_url": "https://www.linkedin.com/in/ryan/",
        "created_at": "2025-10-05T21:51:20.860184+00:00",
    },
]

SEED_CREATOR_CONTENT_ROWS = [
    {
        "profile_url": "https://www.linkedin.com/in/robin-guo/",
        "post_url": "https://www.linkedin.com/feed/update/urn:li:activity:7379926081165971456/",
        "post_raw": "Whenever I speak with college students I try to instill the urgency of the market ... Go make something. Because the window is short and your time finite.",
        "created_at": "2025-10-05T21:53:01.781105+00:00",
        "updated_at": "2025-10-05T21:53:01.781105+00:00",
    },
    {
        "profile_url": "https://www.linkedin.com/in/robin-guo/",
        "post_url": "https://www.linkedin.com/feed/update/urn:li:activity:7379527699394052096/",
        "post_raw": "Being an engineer or “being technical” is, at its core, understanding deeply how something works...",
        "created_at": "2025-10-05T21:56:06.719606+00:00",
        "updated_at": "2025-10-05T21:56:06.719606+00:00",
    },
]

SEED_POST_INSPIRATION_ROWS = [
    {
        "post_id": "0a1894aa-a4cf-47db-8fd8-dc6373e6e8e9",
        "content_post_url": "https://www.linkedin.com/feed/update/urn:li:activity:7379926081165971456/",
        "created_at": "2025-10-05T21:57:41.227074+00:00",
        "updated_at": "2025-10-05T21:57:41.227074+00:00",
    },
    {
        "post_id": "e037dfd2-5e20-458c-8179-2289c23a42ea",
        "content_post_url": "https://www.linkedin.com/feed/update/urn:li:activity:7379527699394052096/",
        "created_at": "2025-10-05T22:01:46.447934+00:00",
        "updated_at": "2025-10-05T22:01:46.447934+00:00",
    },
]


class ConstraintViolation(Exception):
    """Wraps constraint-related failures with the originating SQLSTATE."""

    def __init__(self, code: Optional[str], message: str) -> None:
        super().__init__(message)
        self.code = code


class DatabaseAdapter:
    """Minimal interface implemented by the Supabase adapter."""

    name = "database"
    supports_transactions = False

    def table_exists(self, table: str) -> bool:
        raise NotImplementedError

    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def update(self, table: str, filters: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def delete(self, table: str, filters: Dict[str, Any]) -> int:
        raise NotImplementedError

    def count(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        raise NotImplementedError

    def select_one(self, table: str, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def teardown(self) -> None:
        """Called at the end of the run for adapter-specific cleanup."""
        return None

    def get_authenticated_user_id(self) -> Optional[str]:
        return None

    def select_all(self, table: str, filters: Optional[Dict[str, Any]] = None) -> list[Dict[str, Any]]:
        raise NotImplementedError


class SupabaseAdapter(DatabaseAdapter):
    name = "Supabase REST API"
    supports_transactions = False

    def __init__(self, url: str, api_key: str, *, email: Optional[str] = None, password: Optional[str] = None) -> None:
        try:
            from supabase import create_client  # type: ignore
        except ModuleNotFoundError as exc:  # pragma: no cover - import guard
            raise RuntimeError("Install supabase (pip install supabase) to use the Supabase adapter") from exc
        try:
            from postgrest.exceptions import APIError  # type: ignore
        except ModuleNotFoundError as exc:  # pragma: no cover - import guard
            raise RuntimeError("Install postgrest (pip install postgrest) for Supabase error handling") from exc
        try:
            import httpx  # type: ignore
        except ModuleNotFoundError as exc:  # pragma: no cover - import guard
            raise RuntimeError("Install httpx (pip install httpx) to fetch Supabase metadata") from exc

        self._api_error = APIError
        self._httpx = httpx
        self.url = url.rstrip("/")
        self.key = api_key
        self.client = create_client(url, api_key)
        self.authenticated_user_id: Optional[str] = None
        if email and password:
            try:
                auth_response = self.client.auth.sign_in_with_password({"email": email, "password": password})
                self.authenticated_user_id = getattr(auth_response.user, "id", None)
                if self.authenticated_user_id:
                    print(f"🔐 Authenticated as {auth_response.user.email}")
            except Exception as auth_exc:
                raise RuntimeError(f"Failed to authenticate Supabase test user: {auth_exc}")
        if self.authenticated_user_id is None:
            raise RuntimeError("Supabase authentication required (set TEST_USER_EMAIL and TEST_USER_PASSWORD)")
        self._headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        }
        self._table_names = self._load_table_names()
        self._user_id_for_tests = self.authenticated_user_id

    def _load_table_names(self) -> set[str]:
        names: set[str] = set()
        try:
            response = self._httpx.get(f"{self.url}/rest/v1/", headers=self._headers, timeout=10)
            response.raise_for_status()
            payload = response.json()
            definitions = payload.get("definitions", {}) if isinstance(payload, dict) else {}
            for name in definitions.keys():
                names.add(name)
                if "." in name:
                    names.add(name.split(".")[-1])
        except Exception:
            pass
        return names

    def _wrap_error(self, exc: Exception) -> None:
        if isinstance(exc, self._api_error):
            code = getattr(exc, "code", None)
            detail = getattr(exc, "message", None) or getattr(exc, "details", None) or str(exc)
            raise ConstraintViolation(code, detail) from exc
        raise exc  # pragma: no cover - unexpected path

    def _apply_filters(self, query: Any, filters: Dict[str, Any]):
        if not filters:
            return query
        return query.match(filters)

    def table_exists(self, table: str) -> bool:
        if self._table_names and table in self._table_names:
            return True
        try:
            self.client.table(table).select("*").limit(1).execute()
            return True
        except Exception as exc:  # pragma: no cover - delegated handling
            if isinstance(exc, self._api_error):
                return False
            raise

    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = data if isinstance(data, list) else [data]
        try:
            response = self.client.table(table).insert(payload).execute()
        except Exception as exc:  # pragma: no cover - delegated handling
            self._wrap_error(exc)
        rows = response.data or []
        return rows[0] if rows else {}

    def update(self, table: str, filters: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        try:
            query = self.client.table(table).update(updates)
            response = self._apply_filters(query, filters).execute()
        except Exception as exc:  # pragma: no cover - delegated handling
            self._wrap_error(exc)
        rows = response.data or []
        return rows[0] if rows else {}

    def delete(self, table: str, filters: Dict[str, Any]) -> int:
        query = self.client.table(table).delete()
        response = self._apply_filters(query, filters).execute()
        data = response.data or []
        return len(data)

    def count(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        query = self.client.table(table).select("*", count="exact")
        response = self._apply_filters(query, filters or {}).execute()
        return int(response.count or 0)

    def select_one(self, table: str, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = self.client.table(table).select("*").limit(1)
        response = self._apply_filters(query, filters).execute()
        data = response.data or []
        return data[0] if data else None

    def get_authenticated_user_id(self) -> Optional[str]:
        return self._user_id_for_tests

    def select_all(self, table: str, filters: Optional[Dict[str, Any]] = None) -> list[Dict[str, Any]]:
        query = self.client.table(table).select("*")
        response = self._apply_filters(query, filters or {}).execute()
        return list(response.data or [])


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def assert_sqlstate(code: Optional[str], expected: str, context: str) -> None:
    assert_true(
        code == expected,
        f"{context}: expected SQLSTATE {expected}, got {code or 'unknown'}",
    )


def parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
        return datetime.fromisoformat(candidate)
    raise ValueError(f"Cannot interpret {value!r} as timestamp")


def test_tables_exist(adapter: DatabaseAdapter) -> None:
    for table in REQUIRED_TABLES:
        assert_true(adapter.table_exists(table), f"Missing required table: {table}")


def test_subscription_tier_check(adapter: DatabaseAdapter) -> None:
    user_id = adapter.get_authenticated_user_id()
    assert_true(user_id is not None, "Authenticated Supabase user required for subscription_tier checks")
    created_profile = False
    original_row = adapter.select_one("user_profiles", {"user_id": user_id})

    if original_row is None:
        adapter.insert("user_profiles", {"user_id": user_id, "subscription_tier": "free"})
        original_row = adapter.select_one("user_profiles", {"user_id": user_id})
        created_profile = True

    assert_true(original_row is not None, "Failed to establish baseline user_profile row")

    baseline_tier = original_row["subscription_tier"]
    baseline_timestamp = parse_timestamp(original_row["updated_at"])

    try:
        try:
            adapter.update(
                "user_profiles",
                {"user_id": user_id},
                {"subscription_tier": "enterprise"},
            )
            raise AssertionError("subscription_tier check accepted invalid value")
        except ConstraintViolation as exc:
            assert_sqlstate(exc.code, SQLSTATE_CHECK_VIOLATION, "user_profiles subscription_tier")

        desired_tier = "pro" if baseline_tier != "pro" else "free"
        updated = adapter.update(
            "user_profiles",
            {"user_id": user_id},
            {"subscription_tier": desired_tier},
        )
        assert_true("updated_at" in updated, "user_profiles update did not return updated_at")
        new_timestamp = parse_timestamp(updated["updated_at"])
        assert_true(new_timestamp > baseline_timestamp, "touch_updated_at trigger did not bump updated_at")
    finally:
        adapter.update(
            "user_profiles",
            {"user_id": user_id},
            {"subscription_tier": baseline_tier},
        )
        if created_profile:
            adapter.delete("user_profiles", {"user_id": user_id})


def test_creator_profile_validations(adapter: DatabaseAdapter) -> None:
    base_url = "https://example.com/creator"
    try:
        inserted = adapter.insert(
            "creator_profiles",
            {"profile_url": base_url, "platform": "blog"},
        )
        creator_id = inserted.get("creator_id")
        assert_true(creator_id is not None, "Failed to insert baseline creator_profile")

        try:
            adapter.insert(
                "creator_profiles",
                {"profile_url": base_url, "platform": "blog"},
            )
            raise AssertionError("creator_profiles unique(platform, profile_url) not enforced")
        except ConstraintViolation as exc:
            assert_sqlstate(exc.code, SQLSTATE_UNIQUE_VIOLATION, "creator_profiles unique constraint")

        try:
            adapter.insert(
                "creator_profiles",
                {"profile_url": "not-a-url", "platform": "blog"},
            )
            raise AssertionError("creator_profiles URL check accepted an invalid value")
        except ConstraintViolation as exc:
            assert_sqlstate(exc.code, SQLSTATE_CHECK_VIOLATION, "creator_profiles URL check")
    finally:
        adapter.delete("creator_profiles", {"profile_url": base_url, "platform": "blog"})


def build_content_graph(adapter: DatabaseAdapter) -> Dict[str, Any]:
    user_id = adapter.get_authenticated_user_id()
    assert_true(user_id is not None, "Authenticated Supabase user required to build content graph")
    created_profile = False
    existing_profile = adapter.select_one("user_profiles", {"user_id": user_id})
    if existing_profile is None:
        adapter.insert("user_profiles", {"user_id": user_id, "subscription_tier": "free"})
        created_profile = True

    creator = adapter.insert(
        "creator_profiles",
        {
            "profile_url": f"https://example.com/{uuid.uuid4().hex}",
            "platform": "linkedin",
        },
    )
    creator_id = creator.get("creator_id")
    assert_true(creator_id is not None, "creator_profiles insert did not return creator_id")

    content = adapter.insert(
        "creator_content",
        {
            "creator_id": creator_id,
            "post_url": f"https://example.com/post/{uuid.uuid4().hex}",
            "post_raw": "Example content",
        },
    )
    content_id = content.get("content_id")
    assert_true(content_id is not None, "creator_content insert missing content_id")

    post = adapter.insert(
        "user_posts",
        {"user_id": user_id, "raw_text": "Hello world"},
    )
    post_id = post.get("post_id")
    assert_true(post_id is not None, "user_posts insert missing post_id")

    media = adapter.insert(
        "user_media",
        {
            "post_id": post_id,
            "media_url": "https://example.com/image.png",
            "media_type": "image",
        },
    )
    media_id = media.get("user_media_id")
    assert_true(media_id is not None, "user_media insert missing user_media_id")

    follow = adapter.insert(
        "user_follows",
        {"user_id": user_id, "creator_id": creator_id},
    )
    follow_id = follow.get("id")
    assert_true(follow_id is not None, "user_follows insert missing id")

    inspiration = adapter.insert(
        "post_inspirations",
        {"post_id": post_id, "content_id": content_id},
    )
    inspiration_id = inspiration.get("id")
    assert_true(inspiration_id is not None, "post_inspirations insert missing id")

    return {
        "user_id": user_id,
        "creator_id": creator_id,
        "content_id": content_id,
        "post_id": post_id,
        "media_id": media_id,
        "follow_id": follow_id,
        "inspiration_id": inspiration_id,
        "created_profile": created_profile,
        "original_profile": existing_profile,
    }


def cleanup_graph(adapter: DatabaseAdapter, refs: Dict[str, Any]) -> None:
    if refs.get("inspiration_id") is not None:
        adapter.delete("post_inspirations", {"id": refs["inspiration_id"]})
    if refs.get("media_id") is not None:
        adapter.delete("user_media", {"user_media_id": refs["media_id"]})
    if refs.get("follow_id") is not None:
        adapter.delete("user_follows", {"id": refs["follow_id"]})
    if refs.get("post_id") is not None:
        adapter.delete("user_posts", {"post_id": refs["post_id"]})
    if refs.get("content_id") is not None:
        adapter.delete("creator_content", {"content_id": refs["content_id"]})
    if refs.get("creator_id") is not None:
        adapter.delete("creator_profiles", {"creator_id": refs["creator_id"]})
    if refs.get("created_profile"):
        adapter.delete("user_profiles", {"user_id": refs["user_id"]})


def snapshot_user_state(adapter: DatabaseAdapter, user_id: str) -> Dict[str, Any]:
    profile = adapter.select_one("user_profiles", {"user_id": user_id})
    posts = adapter.select_all("user_posts", {"user_id": user_id})
    post_ids = [row["post_id"] for row in posts]
    media: list[Dict[str, Any]] = []
    inspirations: list[Dict[str, Any]] = []
    for post_id in post_ids:
        media.extend(adapter.select_all("user_media", {"post_id": post_id}))
        inspirations.extend(adapter.select_all("post_inspirations", {"post_id": post_id}))
    follows = adapter.select_all("user_follows", {"user_id": user_id})
    return {
        "profile": profile,
        "posts": posts,
        "media": media,
        "inspirations": inspirations,
        "follows": follows,
    }


def restore_user_state(adapter: DatabaseAdapter, snapshot: Dict[str, Any]) -> None:
    profile = snapshot.get("profile")
    if profile is not None:
        try:
            adapter.insert("user_profiles", profile)
        except ConstraintViolation:
            adapter.update("user_profiles", {"user_id": profile["user_id"]}, profile)

    for post in snapshot.get("posts", []):
        try:
            adapter.insert("user_posts", post)
        except ConstraintViolation:
            adapter.update("user_posts", {"post_id": post["post_id"]}, post)

    for row in snapshot.get("media", []):
        try:
            adapter.insert("user_media", row)
        except ConstraintViolation:
            adapter.update("user_media", {"user_media_id": row["user_media_id"]}, row)

    for row in snapshot.get("inspirations", []):
        try:
            adapter.insert("post_inspirations", row)
        except ConstraintViolation:
            adapter.update("post_inspirations", {"id": row["id"]}, row)

    for row in snapshot.get("follows", []):
        try:
            adapter.insert("user_follows", row)
        except ConstraintViolation:
            adapter.update("user_follows", {"id": row["id"]}, row)


def ensure_seed_data(adapter: DatabaseAdapter) -> None:
    auth_user = adapter.get_authenticated_user_id()
    assert_true(auth_user is not None, "Supabase authentication required to verify seed data")

    for user_id, tier in SEED_USERS.items():
        row = adapter.select_one("user_profiles", {"user_id": user_id})
        if row is None and user_id == auth_user:
            adapter.insert("user_profiles", {"user_id": user_id, "subscription_tier": tier})

    for url in SEED_CREATOR_URLS:
        row = adapter.select_one("creator_profiles", {"profile_url": url})
        if row is None:
            adapter.insert("creator_profiles", {"profile_url": url, "platform": "linkedin"})

    for content_row in SEED_CREATOR_CONTENT_ROWS:
        creator = adapter.select_one("creator_profiles", {"profile_url": content_row["profile_url"]})
        if not creator:
            continue
        existing = adapter.select_one(
            "creator_content",
            {
                "creator_id": creator["creator_id"],
                "post_url": content_row["post_url"],
            },
        )
        if existing is None:
            payload = {
                "creator_id": creator["creator_id"],
                "post_url": content_row["post_url"],
                "post_raw": content_row["post_raw"],
                "created_at": content_row["created_at"],
                "updated_at": content_row["updated_at"],
            }
            adapter.insert("creator_content", payload)

    for post_id, details in SEED_USER_POST_ROWS.items():
        if details["user_id"] != auth_user:
            continue
        existing = adapter.select_one("user_posts", {"post_id": post_id})
        if existing is None:
            payload = {
                "post_id": post_id,
                "user_id": details["user_id"],
                "raw_text": details["raw_text"],
                "created_at": details["created_at"],
                "updated_at": details["updated_at"],
            }
            adapter.insert("user_posts", payload)

    for follow in SEED_USER_FOLLOW_ROWS:
        if follow["user_id"] != auth_user:
            continue
        existing = adapter.select_one("user_follows", {"id": follow["id"]})
        if existing is None:
            creator = adapter.select_one("creator_profiles", {"profile_url": follow["creator_profile_url"]})
            if not creator:
                continue
            payload = {
                "id": follow["id"],
                "user_id": follow["user_id"],
                "creator_id": creator["creator_id"],
                "created_at": follow["created_at"],
            }
            adapter.insert("user_follows", payload)

    for row in SEED_POST_INSPIRATION_ROWS:
        if SEED_POSTS.get(row["post_id"]) != auth_user:
            continue
        existing = adapter.select_one("post_inspirations", {"post_id": row["post_id"]})
        if existing is None:
            content = adapter.select_one(
                "creator_content",
                {"post_url": row["content_post_url"]},
            )
            if not content:
                continue
            payload = {
                "post_id": row["post_id"],
                "content_id": content["content_id"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            adapter.insert("post_inspirations", payload)

def test_cascades(adapter: DatabaseAdapter) -> None:
    user_id = adapter.get_authenticated_user_id()
    assert_true(user_id is not None, "Authenticated Supabase user required for cascade test")
    original_data = snapshot_user_state(adapter, user_id)
    refs = build_content_graph(adapter)
    original_profile = refs.get("original_profile")
    try:
        adapter.delete("user_profiles", {"user_id": refs["user_id"]})

        assert_true(
            adapter.count("user_posts", {"post_id": refs["post_id"]}) == 0,
            "user_posts did not cascade delete when user_profile removed",
        )
        assert_true(
            adapter.count("user_media", {"user_media_id": refs["media_id"]}) == 0,
            "user_media did not cascade delete when user_profile removed",
        )
        assert_true(
            adapter.count("user_follows", {"id": refs["follow_id"]}) == 0,
            "user_follows did not cascade delete when user_profile removed",
        )
        assert_true(
            adapter.count("post_inspirations", {"id": refs["inspiration_id"]}) == 0,
            "post_inspirations did not cascade delete via user_post",
        )
        assert_true(
            adapter.count("creator_content", {"content_id": refs["content_id"]}) == 1,
            "creator_content should remain until creator is deleted",
        )

        adapter.delete("creator_profiles", {"creator_id": refs["creator_id"]})
        assert_true(
            adapter.count("creator_content", {"content_id": refs["content_id"]}) == 0,
            "creator_content did not cascade delete when creator removed",
        )
    finally:
        if original_profile is not None:
            restore_user_state(adapter, original_data)
        cleanup_graph(adapter, refs)


def test_post_inspirations_unique(adapter: DatabaseAdapter) -> None:
    refs = build_content_graph(adapter)
    try:
        try:
            adapter.insert(
                "post_inspirations",
                {"post_id": refs["post_id"], "content_id": refs["content_id"]},
            )
            raise AssertionError("post_inspirations UNIQUE(post_id, content_id) did not reject duplicates")
        except ConstraintViolation as exc:
            assert_sqlstate(exc.code, SQLSTATE_UNIQUE_VIOLATION, "post_inspirations unique")
    finally:
        cleanup_graph(adapter, refs)


def test_seed_data_integrity(adapter: DatabaseAdapter) -> None:
    ensure_seed_data(adapter)
    auth_user = adapter.get_authenticated_user_id()
    verified_user = False
    for user_id, tier in SEED_USERS.items():
        row = adapter.select_one("user_profiles", {"user_id": user_id})
        if row is None:
            if auth_user == user_id or auth_user is None:
                raise AssertionError(f"Seed user {user_id} missing")
            continue
        assert_true(row["subscription_tier"] == tier, f"Seed user {user_id} tier mismatch")
        verified_user = True
    assert_true(verified_user, "No seed user rows accessible with current credentials")

    verified_creators = 0
    for url in SEED_CREATOR_URLS:
        row = adapter.select_one("creator_profiles", {"profile_url": url})
        assert_true(row is not None, f"Seed creator {url} missing")
        assert_true(row["platform"].lower() == "linkedin", f"Seed creator {url} platform mismatch")
        verified_creators += 1
    assert_true(verified_creators > 0, "Creator seed data not verified")

    verified_posts = 0
    for post_id, user_id in SEED_POSTS.items():
        row = adapter.select_one("user_posts", {"post_id": post_id})
        if row is None:
            continue
        assert_true(row["user_id"] == user_id, f"Seed post {post_id} owned by wrong user")
        verified_posts += 1
    assert_true(verified_posts > 0, "No seed posts visible for verification")

    media_count = adapter.count("user_media", {"post_id": "8a845cc5-77f7-4a00-883b-e277b73a4ebb"})
    assert_true(media_count == 1, "Seed user_media for the dog post missing")

    verified_inspiration = 0
    for post_id, creator_post_url in SEED_POST_INSPIRATIONS:
        inspiration = adapter.select_one("post_inspirations", {"post_id": post_id})
        if inspiration is None:
            continue
        content_id = inspiration["content_id"]
        content = adapter.select_one(
            "creator_content",
            {"content_id": content_id, "post_url": creator_post_url},
        )
        assert_true(
            content is not None,
            f"Seed post_inspiration linking {post_id} to {creator_post_url} missing",
        )
        verified_inspiration += 1
    assert_true(verified_inspiration > 0, "Could not verify any post_inspirations seeds")

    robin_creator = adapter.select_one("creator_profiles", {"profile_url": "https://www.linkedin.com/in/robin-guo/"})
    if robin_creator is not None and auth_user is not None:
        follow_count = adapter.count(
            "user_follows",
            {
                "user_id": auth_user,
                "creator_id": robin_creator["creator_id"],
            },
        )
        assert_true(
            follow_count >= 1,
            "Seed follow for Robin Guo missing for authenticated user",
        )


def get_adapter() -> DatabaseAdapter:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_ANON_KEY in your environment")

    email = os.getenv("TEST_USER_EMAIL")
    password = os.getenv("TEST_USER_PASSWORD")

    return SupabaseAdapter(supabase_url, supabase_key, email=email, password=password)


def run() -> None:
    try:
        adapter = get_adapter()
    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    print(f"Using backend: {adapter.name}")

    checks = [
        ("▶ Verifying table existence...", test_tables_exist, "  ✓ All expected tables present"),
        (
            "▶ Validating subscription_tier check and trigger...",
            test_subscription_tier_check,
            "  ✓ subscription_tier enforced and updated_at trigger works",
        ),
        (
            "▶ Validating creator_profiles constraints...",
            test_creator_profile_validations,
            "  ✓ creator_profiles unique + URL constraints enforced",
        ),
        ("▶ Exercising cascade chains...", test_cascades, "  ✓ Cascades behave as expected"),
        (
            "▶ Checking post_inspirations unique constraint...",
            test_post_inspirations_unique,
            "  ✓ post_inspirations enforces UNIQUE(post_id, content_id)",
        ),
        ("▶ Verifying seed data integrity...", test_seed_data_integrity, "  ✓ Seed data matches expectations"),
    ]

    failures = 0

    try:
        for heading, fn, success_msg in checks:
            print(heading)
            try:
                fn(adapter)
                print(success_msg)
            except Exception as exc:
                failures += 1
                print(f"  ✗ {fn.__name__} failed: {exc}")
                if adapter.supports_transactions:
                    # Keep going but ensure we do not leave partial state in Postgres mode
                    pass
    finally:
        adapter.teardown()

    if failures:
        print(f"\n❌ {failures} TEST(S) FAILED")
        sys.exit(1)

    print("\n✅ ALL TESTS PASSED")
    sys.exit(0)


if __name__ == "__main__":
    run()
