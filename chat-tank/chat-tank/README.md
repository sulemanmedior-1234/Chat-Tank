# 🛡️ Chat Tank

A streaming chatbot that runs open LLMs on the Groq API, deployable free on Streamlit Community Cloud.

**Features:** live model picker (pulled from Groq's API, so it never goes stale) · streaming replies · editable system prompt · temperature / max-token controls · chat memory · clear-chat button · friendly error handling for bad keys and rate limits.

## 1. Get a Groq API key
1. Sign up at https://console.groq.com
2. Go to **API Keys → Create API Key** and copy it (starts with `gsk_`).

## 2. Run locally (optional)
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then paste your key
streamlit run app.py
```

## 3. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Chat Tank"
git branch -M main
git remote add origin https://github.com/<your-username>/chat-tank.git
git push -u origin main
```
`.gitignore` keeps your real `secrets.toml` out of the repo.

## 4. Deploy on Streamlit Community Cloud
1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **Create app → Deploy a public app from GitHub**.
3. Pick your repo, branch `main`, main file `app.py`.
4. Open **Advanced settings → Secrets** and paste:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   ```
5. Click **Deploy**. In a minute or two you'll get a public URL like `https://<your-app>.streamlit.app`.

If you skip the secret, the app asks each visitor for their own key in the sidebar instead.

## Project layout
```
chat-tank/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
└── .streamlit/
    └── secrets.toml.example
```
