# Deployment Checklist

Open the **repository root** in your editor so that `main.py` is visible at the top level (not just a subfolder).

---

## Render dashboard

| Setting | Value |
|--------|--------|
| **Build Command** | `pip install -r requirements.txt && python initialize_dataset.py --max-papers 5000` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

---

## Manual steps (do these yourself)

### 1. HuggingFace token for Q&A

- Go to **https://huggingface.co/settings/tokens**
- Create a free **Read** token
- In **Render** → your service → **Environment** → add:
  - **Key:** `HF_TOKEN`
  - **Value:** (paste your token)
- Save and redeploy if the service was already deployed

### 2. Point frontend at your backend

- After deploying to Render, copy your app URL (e.g. `https://your-app-name.onrender.com`)
- In this repo, open **`docs/assets/js/demo.js`**
- Replace the backend URL in `CONFIG.API_BASE_URL` (search for `API_BASE_URL` or `YOUR-APP.onrender.com`)
- Set it to your actual Render URL, e.g. `https://your-app-name.onrender.com`
- Commit and push so GitHub Pages serves the updated frontend

If the URL is wrong or the backend is down, the site will show **Demo mode** (local sample data) instead of **Live mode**.
