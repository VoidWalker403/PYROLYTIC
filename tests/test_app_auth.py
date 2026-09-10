from pathlib import Path
from types import SimpleNamespace
import sys

import pytest
from streamlit.testing.v1 import AppTest
from streamlit.proto.TextInput_pb2 import TextInput

import auth

APP = str(Path(__file__).resolve().parents[1] / "app.py")


@pytest.fixture
def app():
    auth._failures.clear()
    app = AppTest.from_file(APP, default_timeout=15)
    app.secrets["auth"] = {"users": {"alice": auth.hash_password("correct password")}}
    app.run()
    return app


def sign_in(app, password="correct password", username="alice"):
    app.text_input(key="_auth_username").input(username)
    app.text_input(key="_auth_password").input(password)
    app.button[0].click().run()
    assert not app.exception
    return app


def assert_locked(app):
    assert not app.exception
    assert len(app.chat_input) == 0
    assert len(app.metric) == 0
    assert len(app.toggle) == 0


@pytest.mark.parametrize("config", [None, {}, {"users": {}}, {"users": {"alice": "plaintext"}}])
def test_unconfigured_app_blocks_access(config):
    # Cold imports can exceed AppTest's 3-second default on Windows.
    app = AppTest.from_file(APP, default_timeout=15)
    if config is not None:
        app.secrets["auth"] = config
    app.run()
    assert_locked(app)
    assert "Sign-in is not configured" in app.error[0].value


def test_login_gate_wrong_password_and_unknown_user(app):
    assert_locked(app)
    assert app.text_input(key="_auth_password").proto.type == TextInput.PASSWORD
    sign_in(app, "wrong")
    assert_locked(app)
    error = app.error[0].value
    assert not app.session_state.filtered_state.get("_auth_password")
    sign_in(app, username="unknown")
    assert_locked(app)
    assert app.error[0].value == error


def test_login_rerun_demo_and_logout(app):
    sign_in(app)
    assert len(app.chat_input) == 1
    assert len(app.metric) == 4
    assert not app.session_state.filtered_state.get("_auth_password")
    app.run()
    assert len(app.chat_input) == 1
    app.button(key="demo_0").click().run()
    assert len(app.chat_message) == 2
    next(button for button in app.button if button.label == "Log out").click().run()
    assert_locked(app)
    assert "messages" not in app.session_state.filtered_state
    assert "_auth_identity" not in app.session_state.filtered_state
    sign_in(app)
    assert len(app.chat_message) == 0


def test_expired_session_clears_chat(app):
    sign_in(app)
    app.session_state["messages"] = [{"role": "user", "content": "private"}]
    app.session_state["_auth_identity"]["expires_at"] = 0
    app.run()
    assert_locked(app)
    assert "messages" not in app.session_state.filtered_state


def test_independent_browser_session_is_not_authenticated(app):
    sign_in(app)
    other = AppTest.from_file(APP)
    other.secrets["auth"] = app.secrets["auth"]
    other.run()
    assert_locked(other)
    assert len(other.text_input) == 2


def test_password_change_revokes_existing_session(app):
    sign_in(app)
    app.session_state["messages"] = [{"role": "user", "content": "private"}]
    app.secrets["auth"] = {"users": {"alice": auth.hash_password("replacement")}}
    app.run()
    assert_locked(app)
    assert "messages" not in app.session_state.filtered_state
    sign_in(app, "replacement")
    assert len(app.chat_input) == 1


def test_lockout_is_shared_across_browser_sessions(app):
    for _ in range(auth.MAX_FAILURES):
        sign_in(app, "wrong")
    other = AppTest.from_file(APP, default_timeout=15)
    other.secrets["auth"] = app.secrets["auth"]
    other.run()
    sign_in(other)
    assert_locked(other)
    assert len(other.error) == 1


def test_live_pipeline_only_runs_after_login(app, monkeypatch):
    calls = []
    monkeypatch.setitem(sys.modules, "retrieve", SimpleNamespace(
        retrieve=lambda question, k: calls.append((question, k)) or []))
    monkeypatch.setitem(sys.modules, "explain", SimpleNamespace(
        explain=lambda *args, **kwargs: "Live test answer"))
    app.run()
    assert calls == []
    sign_in(app)
    app.toggle[0].set_value(False).run()
    app.chat_input[0].set_value("Test live question").run()
    assert not app.exception
    assert calls == [("Test live question", 3)]
    assert app.session_state["messages"][-1]["content"] == "Live test answer"


def test_live_sources_survive_reruns_and_clear_on_logout(app, monkeypatch):
    chunk = {'source_doi': '10.1000/example', 'source_title': 'Test paper',
             'text': 'Test reported yield 70%', 'chunk_type': 'fulltext'}
    monkeypatch.setitem(sys.modules, 'retrieve', SimpleNamespace(retrieve=lambda *args, **kwargs: [chunk]))
    monkeypatch.setitem(sys.modules, 'explain', SimpleNamespace(
        explain=lambda *args, **kwargs: 'Reported 70% [SOURCE: 10.1000/example]'))
    sign_in(app)
    app.toggle[0].set_value(False).run()
    app.chat_input[0].set_value('Give a cited answer').run()
    assert not app.exception
    saved = app.session_state['messages'][-1]['sources']
    assert saved[0]['excerpts'] == ['Test reported yield 70%']
    assert any('Cited in answer' in panel.label for panel in app.expander)
    app.run()
    assert not app.exception
    assert app.session_state['messages'][-1]['sources'] == saved
    assert any('https://doi.org/10.1000/example' in item.value for item in app.markdown)
    next(button for button in app.button if button.label == 'Log out').click().run()
    assert_locked(app)
    assert 'messages' not in app.session_state.filtered_state
