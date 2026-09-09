import time

import pytest

import auth


@pytest.fixture(autouse=True)
def reset_attempts():
    auth._failures.clear()
    yield
    auth._failures.clear()


@pytest.fixture(scope="module")
def encoded():
    return auth.hash_password("correct password")


def test_password_hash_is_salted_and_verifies(encoded):
    assert encoded != auth.hash_password("correct password")
    assert auth.verify_password("correct password", encoded)
    assert not auth.verify_password("wrong password", encoded)
    assert not auth.verify_password("", encoded)


def test_unicode_password():
    password = "a long password with \u03c0 and \u2603"
    assert auth.verify_password(password, auth.hash_password(password))


@pytest.mark.parametrize("encoded", [None, "plaintext", "pbkdf2_sha256$1$00$00",
                                     "pbkdf2_sha256$600000$zz$00"])
def test_invalid_hash_fails_closed(encoded):
    assert not auth.verify_password("password", encoded)
    with pytest.raises(ValueError):
        auth.validate_users({"admin": encoded})


@pytest.mark.parametrize("users", [{}, None, [], {" admin ": "invalid"}])
def test_invalid_configuration(users):
    with pytest.raises(ValueError):
        auth.validate_users(users)


@pytest.mark.parametrize("password", ["", None, "x" * 1025])
def test_invalid_password_not_allowed(password):
    with pytest.raises(ValueError):
        auth.hash_password(password)


def test_accounts_and_throttle(encoded, monkeypatch):
    clock = [100.0]
    monkeypatch.setattr(auth.time, "monotonic", lambda: clock[0])
    users = {"alice": encoded, "bob": encoded}
    assert not auth.authenticate("unknown", "correct password", users)
    for _ in range(auth.MAX_FAILURES):
        assert not auth.authenticate("alice", "wrong", users)
    assert not auth.authenticate("alice", "correct password", users)
    assert auth.authenticate("bob", "correct password", users)
    clock[0] += auth.LOCKOUT_SECONDS
    assert auth.authenticate("alice", "correct password", users)
    assert "alice" not in auth._failures


def test_session_expiration_and_revocation(encoded):
    state = {"_auth_identity": {
        "username": "alice",
        "credential_version": auth._credential_version(encoded),
        "expires_at": time.time() + 60,
    }}
    assert auth.session_is_valid(state, {"alice": encoded})
    assert not auth.session_is_valid(state, {})
    assert not auth.session_is_valid(state, {"alice": auth.hash_password("changed")})
    state["_auth_identity"]["expires_at"] = 0
    assert not auth.session_is_valid(state, {"alice": encoded})
    assert not auth.session_is_valid({}, {"alice": encoded})


def test_logout_removes_identity_and_user_content():
    state = {"_auth_identity": {"username": "alice"}, "messages": ["private"],
             "_auth_password": "secret"}
    auth.clear_session(state)
    assert state == {}
