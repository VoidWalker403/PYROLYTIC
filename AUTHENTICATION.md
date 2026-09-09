# Authentication

PyroLytic requires an administrator-configured account before displaying either
demo or live content. No default password, signup service, or database is added.

## Setup

1. From the project directory, run `python auth.py`. Enter and confirm a password
   at the hidden prompts. The command prints a salted PBKDF2-SHA256 hash with
   600,000 iterations; it does not save the password.
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and replace
   the placeholder with the generated hash. Add one entry per account under
   `[auth.users]`. Usernames are case-sensitive. Quote usernames containing dots
   or other TOML special characters.
3. Run `streamlit run app.py` and sign in. Missing or invalid account configuration
   blocks access. Local secrets are ignored by Git; never commit real secrets.
   On a hosted Streamlit instance, configure the same TOML in its secrets settings.

## Sessions and account management

- Login survives Streamlit reruns within the browser session and expires after
  eight hours, checked on the next app execution. A new browser session requires
  login again.
- Logout clears all session state, including chat history. Changing an account's
  hash or removing the account invalidates its session on the next app execution
  after Streamlit reloads the secrets. Restart the app after editing secrets.
- Generate another hash with `python auth.py` to reset a password. Account creation,
  deletion, and password resets are administrator operations; there is no email
  recovery or role system.
- Five failed attempts within 60 seconds block that account until the oldest
  attempt leaves the window. This limit is shared across browser sessions in one
  server process, resets on restart, and is not shared between server replicas.
  Unknown usernames share a separate failure bucket. Deploy behind HTTPS; a
  multi-replica/public deployment should use centralized throttling or an identity
  provider. This feature does not protect files served outside the Streamlit app.

## Tests

Run `python -m pytest tests/test_auth.py tests/test_app_auth.py`. Tests use temporary
in-memory account configuration and Streamlit's AppTest; no Ollama, vector index,
network service, or real secrets are required.

The UI uses Streamlit's documented
[form callbacks](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)
and [AppTest secrets](https://docs.streamlit.io/develop/concepts/app-testing/beyond-the-basics).
