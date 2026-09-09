"""Local account authentication for the Streamlit app.

Run ``python auth.py`` to generate a password hash without echoing the password.
"""
import hashlib
import hmac
import secrets
import threading
import time
from collections.abc import Mapping

ITERATIONS = 600_000
SESSION_SECONDS = 8 * 60 * 60
MAX_FAILURES = 5
LOCKOUT_SECONDS = 60
MAX_PASSWORD_LENGTH = 1024
_failures = {}
_lock = threading.Lock()


def hash_password(password):
    if not isinstance(password, str) or not 1 <= len(password) <= MAX_PASSWORD_LENGTH:
        raise ValueError("Password must contain 1 to 1024 characters.")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}"


def _parse_hash(encoded):
    algorithm, iterations, salt, digest = encoded.split("$")
    if algorithm != "pbkdf2_sha256" or int(iterations) != ITERATIONS:
        raise ValueError("Unsupported password hash.")
    salt, digest = bytes.fromhex(salt), bytes.fromhex(digest)
    if len(salt) != 16 or len(digest) != 32:
        raise ValueError("Invalid password hash.")
    return salt, digest


def verify_password(password, encoded):
    if not isinstance(password, str) or not 1 <= len(password) <= MAX_PASSWORD_LENGTH:
        return False
    try:
        salt, expected = _parse_hash(encoded)
    except (ValueError, TypeError, AttributeError):
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return hmac.compare_digest(actual, expected)


# Unknown accounts still perform the same password derivation as known accounts.
_DUMMY_HASH = f"pbkdf2_sha256${ITERATIONS}${'00' * 16}${'00' * 32}"


def validate_users(users):
    if not isinstance(users, Mapping) or not users:
        raise ValueError("No accounts configured.")
    for username, encoded in users.items():
        if (not isinstance(username, str) or not 1 <= len(username) <= 128
                or username != username.strip()):
            raise ValueError("Invalid username.")
        try:
            _parse_hash(encoded)
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValueError("Invalid password hash.") from exc
    return dict(users)


def authenticate(username, password, users):
    """Limit failures per configured account across sessions in this process."""
    key = username if username in users else None
    with _lock:
        now = time.monotonic()
        failures = [stamp for stamp in _failures.get(key, [])
                    if now - stamp < LOCKOUT_SECONDS]
        _failures[key] = failures
        if len(failures) >= MAX_FAILURES:
            return False
        valid = verify_password(password, users.get(username, _DUMMY_HASH))
        if valid and username in users:
            _failures.pop(key, None)
            return True
        failures.append(now)
        return False


def clear_session(state):
    # Clear user content as well as identity when logging out or changing accounts.
    for key in list(state):
        del state[key]


def _credential_version(encoded):
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def session_is_valid(state, users):
    identity = state.get("_auth_identity")
    if not isinstance(identity, dict):
        return False
    username = identity.get("username")
    return (username in users
            and identity.get("credential_version") == _credential_version(users[username])
            and time.time() < identity.get("expires_at", 0))


def require_login():
    """Stop execution before any dashboard content unless authenticated."""
    import streamlit as st

    try:
        users = validate_users(st.secrets["auth"]["users"])
    except (KeyError, FileNotFoundError, ValueError, TypeError):
        clear_session(st.session_state)
        st.error("Sign-in is not configured. Ask the administrator to follow AUTHENTICATION.md.")
        st.stop()

    if session_is_valid(st.session_state, users):
        st.sidebar.caption(f"Signed in as {st.session_state['_auth_identity']['username']}")
        st.sidebar.button("Log out", on_click=clear_session, args=(st.session_state,))
        return

    if "_auth_identity" in st.session_state:
        clear_session(st.session_state)

    def submit_login():
        username = st.session_state.pop("_auth_username", "").strip()
        password = st.session_state.pop("_auth_password", "")
        if authenticate(username, password, users):
            clear_session(st.session_state)
            st.session_state["_auth_identity"] = {
                "username": username,
                "credential_version": _credential_version(users[username]),
                "expires_at": time.time() + SESSION_SECONDS,
            }
        else:
            st.session_state["_auth_error"] = True

    st.header("Sign in to PyroLytic")
    with st.form("login", clear_on_submit=True):
        st.text_input("Username", key="_auth_username", max_chars=128)
        st.text_input("Password", type="password", key="_auth_password",
                      max_chars=MAX_PASSWORD_LENGTH)
        st.form_submit_button("Sign in", on_click=submit_login)
    if st.session_state.get("_auth_error"):
        st.error("Sign-in failed. Check your credentials, or wait 60 seconds after repeated attempts.")
    st.stop()


if __name__ == "__main__":
    from getpass import getpass

    password = getpass("New password: ")
    if not password or password != getpass("Confirm password: "):
        raise SystemExit("Passwords must be nonempty and match.")
    print(hash_password(password))
