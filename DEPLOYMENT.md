# Deploying AnalytixPro for Recruiter Demos

This guide shows quick ways to run and share the Streamlit app live. No API keys are required.

## 1) Run Locally (fastest sanity check)
1. Install Python 3.10+.
2. From the project root, create a virtual env (optional) and install deps:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Launch Streamlit (pick any open port):
   ```bash
   streamlit run app.py --server.port 8501
   ```
4. Open http://localhost:8501.

## 2) Streamlit Community Cloud (no servers to manage)
1. Push this folder to a public GitHub repo.
2. Go to https://share.streamlit.io → "New app" → pick the repo/branch.
3. Set the app entry point to `app.py`.
4. (Optional) In Advanced settings, set `Server port` to `8501` if needed; otherwise leave default.
5. Deploy. Share the provided URL with recruiters.

Notes:
- Secrets: none required (AI features are removed).
- If you add dependencies, update `requirements.txt` and redeploy.

## 3) Hugging Face Spaces (free tier, quick spin-up)
1. Create a new Space → type "Streamlit".
2. Upload the project files or point the Space to your GitHub repo.
3. Ensure `requirements.txt` is present (it is).
4. Set `app.py` as the entry file (default for Streamlit template).
5. Wait for the build; share the Space URL.

## 4) Render (always-on HTTPS)
1. Create a free Web Service on https://render.com.
2. Connect your repo and use these settings:
   - Environment: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - Environment variable: `PORT` (Render provides it automatically)
3. Deploy and use the Render URL.

## 5) Ngrok tunnel (temporary demo from your machine)
1. Run locally (see section 1).
2. In another terminal, run: `ngrok http 8501`
3. Share the HTTPS forwarding URL from ngrok.
4. Keep both terminals open during the demo.

## Troubleshooting
- Port in use: change `--server.port` to another open port (e.g., 8502).
- Packages missing: rerun `pip install -r requirements.txt`.
- Large files: prefer CSV over Excel; keep uploads under Streamlit’s default 200MB limit unless you adjust `server.maxUploadSize`.

## Repository Checklist for Recruiters
- Include these files at repo root: `app.py`, `requirements.txt`, `README.md`, `DEPLOYMENT.md`, `assets/`, `modules/`, `demo_data.csv`, `demo_dirty_data.csv`.
- Add a short note in the README with the live demo URL once deployed.
