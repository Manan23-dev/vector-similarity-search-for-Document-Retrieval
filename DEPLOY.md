# Deployment Checklist

Open the **repository root** in your editor so that `main.py` is visible at the top level (not just a subfolder).

---

## Render dashboard

| Setting | Value |
|--------|--------|
| **Runtime** | `Python 3.11` (from `runtime.txt`) |
| **Build Command** | `./build.sh` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

---

## Manual steps (do these yourself)

### 1. HuggingFace token for Q&A

- Go to **https://huggingface.co/settings/tokens**
- Create a free **Read** token
- In **Render** → your service → **Environment** → add:
  - **Key:** `HF_TOKEN`
  - **Value:** (paste your token)
- Optional performance env vars:
  - `MAX_PAPERS=5000` (or higher)
  - `FREQUENT_QUERIES=["machine learning","transformer"]`
- Save and redeploy if the service was already deployed

### 2. Point frontend at your backend

- After deploying to Render, copy your app URL (e.g. `https://your-app-name.onrender.com`)
- In this repo, open **`docs/assets/js/demo.js`**
- Replace the backend URL in `CONFIG.API_BASE_URL` (search for `API_BASE_URL` or `YOUR-APP.onrender.com`)
- Set it to your actual Render URL, e.g. `https://your-app-name.onrender.com`
- Commit and push so GitHub Pages serves the updated frontend

If the URL is wrong or the backend is down, the site will show **Demo mode** (local sample data) instead of **Live mode**.

---

## Staging, cutover, rollback

### Staging validation checklist

1. Deploy a separate Render staging service from the same branch.
2. Verify:
   - `GET /health`
   - `GET /api/health`
   - `POST /api/search`
   - `POST /api/qa`
   - `GET /api/eval`
   - `GET /api/tune`
3. Confirm build logs show index initialization succeeded.
4. Confirm response latency is acceptable after warmup.

### Production cutover

1. Keep current production service running.
2. Update frontend `CONFIG.API_BASE_URL` to staging URL only after all checks pass.
3. Monitor logs/errors for 10-15 minutes.

### Rollback

1. Revert frontend `CONFIG.API_BASE_URL` to previous production backend URL.
2. Scale down or pause the new service.
3. Redeploy previous known-good commit if needed.
