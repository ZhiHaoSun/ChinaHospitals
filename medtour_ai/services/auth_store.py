"""In-memory auth store for local development.

Production should replace this with a durable user store, a real email sender,
and WebAuthn credential verification.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import hashlib
import secrets
from typing import Any
from uuid import uuid4


TRUSTED_SESSION_DAYS = 90
STANDARD_SESSION_DAYS = 30
ABSOLUTE_SESSION_DAYS = 180
LOGIN_CODE_MINUTES = 10


class InMemoryAuthStore:
    def __init__(self) -> None:
        self.users_by_id: dict[str, dict[str, Any]] = {}
        self.user_ids_by_email: dict[str, str] = {}
        self.login_challenges: dict[str, dict[str, Any]] = {}
        self.sessions_by_hash: dict[str, dict[str, Any]] = {}
        self.recovery_code_hashes: dict[str, dict[str, Any]] = {}
        self.passkey_challenges: dict[str, dict[str, Any]] = {}

    def start_email_login(self, email: str, trusted_device: bool = True) -> dict[str, Any]:
        normalized_email = _normalize_email(email)
        user, created = self._get_or_create_user(normalized_email)
        code = f"{secrets.randbelow(1_000_000):06d}"
        challenge_id = f"lc_{uuid4().hex}"
        challenge = {
            "challenge_id": challenge_id,
            "user_id": user["user_id"],
            "code_hash": _hash_secret(code),
            "expires_at": _future(minutes=LOGIN_CODE_MINUTES),
            "trusted_device": trusted_device,
            "attempts": 0,
            "created_at": _now(),
        }
        self.login_challenges[challenge_id] = challenge
        return {
            "challenge_id": challenge_id,
            "email": normalized_email,
            "delivery_channel": "email",
            "expires_in_seconds": LOGIN_CODE_MINUTES * 60,
            "created_user": created,
            "dev_code": code,
        }

    def verify_email_login(self, challenge_id: str, code: str, trusted_device: bool = True) -> dict[str, Any] | None:
        challenge = self.login_challenges.get(challenge_id)
        if not challenge or _parse(challenge["expires_at"]) < datetime.now(UTC):
            return None
        challenge["attempts"] += 1
        if challenge["attempts"] > 5 or not secrets.compare_digest(challenge["code_hash"], _hash_secret(code)):
            return None
        user = self.users_by_id[challenge["user_id"]]
        del self.login_challenges[challenge_id]
        return self.create_session(user["user_id"], trusted_device or challenge["trusted_device"], method="email_code")

    def create_session(self, user_id: str, trusted_device: bool, method: str) -> dict[str, Any]:
        raw_token = secrets.token_urlsafe(48)
        now = datetime.now(UTC)
        rolling_days = TRUSTED_SESSION_DAYS if trusted_device else STANDARD_SESSION_DAYS
        session = {
            "session_id": f"ses_{uuid4().hex}",
            "user_id": user_id,
            "token_hash": _hash_secret(raw_token),
            "trusted_device": trusted_device,
            "auth_method": method,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=rolling_days)).isoformat(),
            "absolute_expires_at": (now + timedelta(days=ABSOLUTE_SESSION_DAYS)).isoformat(),
            "last_seen_at": now.isoformat(),
        }
        self.sessions_by_hash[session["token_hash"]] = session
        user = self.users_by_id[user_id]
        return {
            "session_token": raw_token,
            "session": self.public_session(session),
            "user": self.public_user(user),
            "recovery_codes": self._ensure_recovery_codes(user_id),
        }

    def session_from_token(self, token: str | None) -> dict[str, Any] | None:
        if not token:
            return None
        token_hash = _hash_secret(token)
        session = self.sessions_by_hash.get(token_hash)
        if not session:
            return None
        now = datetime.now(UTC)
        if _parse(session["expires_at"]) < now or _parse(session["absolute_expires_at"]) < now:
            self.sessions_by_hash.pop(token_hash, None)
            return None
        session["last_seen_at"] = now.isoformat()
        if session["trusted_device"]:
            renewed_expiry = min(now + timedelta(days=TRUSTED_SESSION_DAYS), _parse(session["absolute_expires_at"]))
            session["expires_at"] = renewed_expiry.isoformat()
        return session

    def end_session(self, token: str | None) -> None:
        if token:
            self.sessions_by_hash.pop(_hash_secret(token), None)

    def public_session(self, session: dict[str, Any]) -> dict[str, Any]:
        return {
            "session_id": session["session_id"],
            "trusted_device": session["trusted_device"],
            "auth_method": session["auth_method"],
            "expires_at": session["expires_at"],
            "absolute_expires_at": session["absolute_expires_at"],
        }

    def public_user(self, user: dict[str, Any]) -> dict[str, Any]:
        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "passkey_enabled": bool(user.get("passkeys")),
            "recovery_codes_remaining": user.get("recovery_codes_remaining", 0),
        }

    def verify_recovery_code(self, email: str, code: str, trusted_device: bool = True) -> dict[str, Any] | None:
        user_id = self.user_ids_by_email.get(_normalize_email(email))
        if not user_id:
            return None
        code_hash = _hash_secret(code.strip().upper())
        record = self.recovery_code_hashes.get(code_hash)
        if not record or record["user_id"] != user_id or record.get("used_at"):
            return None
        record["used_at"] = _now()
        user = self.users_by_id[user_id]
        user["recovery_codes_remaining"] = max(0, user.get("recovery_codes_remaining", 0) - 1)
        return self.create_session(user_id, trusted_device, method="recovery_code")

    def start_passkey_registration(self, user_id: str) -> dict[str, Any]:
        challenge_id = f"pkreg_{uuid4().hex}"
        self.passkey_challenges[challenge_id] = {
            "challenge_id": challenge_id,
            "user_id": user_id,
            "type": "registration",
            "expires_at": _future(minutes=10),
        }
        return {
            "challenge_id": challenge_id,
            "rp_id": "localhost",
            "user_id": user_id,
            "challenge": secrets.token_urlsafe(32),
            "note": "Local demo challenge. Replace with verified WebAuthn options in production.",
        }

    def complete_passkey_registration(self, challenge_id: str, label: str = "Trusted device") -> dict[str, Any] | None:
        challenge = self.passkey_challenges.pop(challenge_id, None)
        if not challenge or challenge["type"] != "registration" or _parse(challenge["expires_at"]) < datetime.now(UTC):
            return None
        user = self.users_by_id[challenge["user_id"]]
        credential = {
            "credential_id": f"pk_{uuid4().hex}",
            "label": label,
            "created_at": _now(),
        }
        user.setdefault("passkeys", []).append(credential)
        return credential

    def _get_or_create_user(self, email: str) -> tuple[dict[str, Any], bool]:
        user_id = self.user_ids_by_email.get(email)
        if user_id:
            return self.users_by_id[user_id], False
        user_id = f"usr_{uuid4().hex}"
        user = {
            "user_id": user_id,
            "email": email,
            "passkeys": [],
            "created_at": _now(),
            "recovery_codes_remaining": 0,
        }
        self.users_by_id[user_id] = user
        self.user_ids_by_email[email] = user_id
        return user, True

    def _ensure_recovery_codes(self, user_id: str) -> list[str]:
        user = self.users_by_id[user_id]
        if user.get("recovery_codes_remaining", 0) > 0:
            return []
        codes = [f"MT-{secrets.token_hex(3).upper()}-{secrets.token_hex(3).upper()}" for _ in range(8)]
        for code in codes:
            self.recovery_code_hashes[_hash_secret(code)] = {"user_id": user_id, "created_at": _now(), "used_at": None}
        user["recovery_codes_remaining"] = len(codes)
        return codes


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _future(*, minutes: int) -> str:
    return (datetime.now(UTC) + timedelta(minutes=minutes)).isoformat()


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value)
