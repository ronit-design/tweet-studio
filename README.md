# Tweet Studio 📊

Finance Twitter content generator powered by Claude AI. Generates data-first macro tweets and stock intelligence tweets from real earnings call transcripts and company news.

## Features

- **Macro Data tab** — Data-First mode (Liz Ann Sonders style) and Explainer mode
- **US + International** — US, China, Japan, South Korea, India, EU, UK
- **Release Calendar** — Upcoming economic releases in sidebar, clickable to auto-fill
- **Stock Intelligence** — Real earnings call transcripts + news via roic.ai API
- **Live web search** — Auto-fetches latest macro figures when you don't have them

---

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/tweet-studio.git
cd tweet-studio
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up API keys

Copy the example secrets file:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and add your keys:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
ROIC_API_KEY = "your_roic_api_key"
```

> ⚠️ `secrets.toml` is in `.gitignore` — never commit it to GitHub.

### 4. Run locally

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Deploy to Streamlit Cloud

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tweet-studio.git
git push -u origin main
```

### 2. Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select your GitHub repo
4. Set **Main file path** to `app.py`
5. Click **Deploy**

### 3. Add secrets in Streamlit Cloud

1. In your deployed app, go to **⋮ → Settings → Secrets**
2. Paste this and fill in your keys:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
ROIC_API_KEY = "your_roic_api_key"
```

3. Save — app will reboot with the secrets loaded

---

## Project Structure

```
tweet-studio/
├── app.py                        # Main Streamlit app
├── requirements.txt              # Python dependencies
├── .env.example                  # Local env template
├── .gitignore
├── .streamlit/
│   ├── config.toml               # Streamlit theme config
│   └── secrets.toml.example      # Secrets template (don't commit secrets.toml)
└── utils/
    ├── __init__.py
    ├── api.py                    # Anthropic + roic.ai API calls
    ├── data.py                   # Categories, countries, calendar data
    └── helpers.py                # Tweet parsing, calendar generation
```

---

## API Keys Needed

| Key | Where to get it | Cost |
|-----|----------------|------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Pay-per-token |
| `ROIC_API_KEY` | Your roic.ai account | Per your plan |

---

## Usage Notes

- **Stock tab**: roic.ai calls run server-side (no CORS issues like the HTML version)
- **Macro tab**: Leave the numbers field blank to auto-search for latest figures via web search
- **Calendar**: Click any release in the sidebar to auto-fill the release name field
- Tweets are editable inline — tweak before copying
