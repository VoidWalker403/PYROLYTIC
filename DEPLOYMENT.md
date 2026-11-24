# Deploying PyroLytic

This guide publishes the current PyroLytic dashboard as a public, read-only
demo using Streamlit Community Cloud. It is designed for demonstrating the
included literature dataset and static example answers, not for a shared
research database or public AI inference service.

## Before you deploy

1. Push the `public-release` branch to GitHub and confirm the repository is
   public. Community Cloud can deploy private repositories too, but requires
   additional GitHub permissions.
2. Create a deployment-only account. From the project directory, run
   `python auth.py` and store the generated hash somewhere safe. Do not commit
   the password or the generated hash.
3. Decide how viewers will sign in. The current app has no registration,
   password-reset, or role-management service. For a public demonstration,
   share a limited demo credential only with the people you want to access it.

## Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with the
   GitHub account that administers `VoidWalker403/PYROLYTIC`.
2. Select **Create app**, then choose the repository and configure:
   - **Branch:** `public-release`
   - **Main file path:** `app.py`
   - **Python version:** `3.12`
   - **App URL:** choose a memorable available subdomain, such as
     `pyrolytic-demo`.
3. Open **Advanced settings** and paste the following TOML, replacing the
   placeholder with the hash from step 2:

   ```toml
   [auth.users]
   demo = "REPLACE_WITH_GENERATED_PASSWORD_HASH"
   ```

4. Select **Deploy** and wait for the build to finish. The first build can take
   several minutes because scientific and retrieval packages are installed.
5. Open the published URL in a private/incognito browser window, sign in, and
   verify that the literature browser, research library, analytics, data-quality
   screen, and static Demo Mode answers load.

## What is public

The deployed app starts with Demo Mode enabled. Its answers are static workflow
examples; no local Ollama server or private local text is exposed. The public
repository contains the included CSV, Crossref metadata snapshot, source code,
and project documentation. Check every committed file before changing the
repository visibility.

## Hosted limitations

- Community Cloud local files are ephemeral. Imports, review notes, provenance
  changes, and rebuilt indexes can disappear when the instance restarts. Do not
  use the hosted filesystem as the source of record.
- Live mode currently expects Ollama at `localhost`, which a hosted app cannot
  reach. Keep Demo Mode on unless the app is redesigned for a secured hosted
  inference API and its key is stored in Streamlit Secrets.
- This app's sign-in is a simple administrator-managed password gate. For broad
  public access, replace it with an identity provider and move persistent data
  to a managed database before collecting user contributions.
- Review the deployment logs after upgrades. A dependency update triggers a
  fresh installation and can affect startup time or compatibility.

## Updating or removing the app

Push subsequent changes to `public-release`; Community Cloud automatically
redeploys them. Update secrets only in the Community Cloud app settings, never
in Git. If you need to stop public access, use the app's settings to delete the
deployment or make the repository private, then rotate the demo credential.

## References

- [Streamlit Community Cloud deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Streamlit Community Cloud secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
