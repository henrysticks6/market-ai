# MARKET AI

**Every Business Deserves a Voice.**

A fresh Streamlit starter application for an AI-powered advertising, publicity and business intelligence platform.

## Included in this first build
- Blue, green, white and navy Market AI visual identity
- Dashboard and navigation for the planned ecosystem
- Business profile creation (SQLite development database)
- Advertising concept and script generation workflow
- Optional OpenAI integration for live AI text and assistant responses
- AI Video Studio integration adapter for Replicate text-to-video models
- Video job status polling and playback when provider returns a video URL
- RSS-based Market Live news feed
- Social content preparation (not direct publishing)
- Campaign records and basic activity analytics
- Publicity Network and Creator Network foundations

## Important current limitations
This is a deployable first release, not yet the complete production platform.
- Real video rendering requires a valid Replicate API token, a supported model slug, correct model input schema and available provider credits. Model input fields vary; check the chosen model's documentation.
- The current video adapter supports text-to-video. Image-to-video and multi-scene editing require the next integration stage.
- OpenAI API usage is separately billed. The app has a demo fallback when no key is configured.
- Direct social publishing requires official OAuth apps, permissions and platform review. This version prepares content but does not publish.
- SQLite is suitable for local testing only. Streamlit Community Cloud's local filesystem is not a durable multi-user database. Connect Supabase before public use.
- Public directory listings, creator payouts, attribution, moderation, subscriptions and secure account roles need production implementation.

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Configure secrets
Create `.streamlit/secrets.toml` locally (do not commit it):
```toml
OPENAI_API_KEY = "..."
REPLICATE_API_TOKEN = "..."
REPLICATE_MODEL = "owner/model-name"
```
On Streamlit Community Cloud, add the same values in App settings → Secrets.

## Deploy from GitHub
1. Create a new GitHub repository named `market-ai`.
2. Upload the contents of this folder to the repository root.
3. Open https://share.streamlit.io and sign in with GitHub.
4. Choose the repository, branch `main`, and main file `app.py`.
5. Deploy, then add API secrets in the app settings.

## Before public launch
Add Supabase Auth, database and storage; user-level authorization; rate limits; usage accounting; provider-specific video schemas; durable media storage; official social integrations; moderation; privacy policy; terms; backups; error monitoring; and security review.
