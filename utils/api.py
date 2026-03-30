# utils/api.py
# All external API calls: NVIDIA and roic.ai

import requests
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL   = "nvidia/llama-3.1-nemotron-ultra-253b-v1"


def get_nvidia_key():
    return st.secrets.get("NVIDIA_API_KEY") or os.getenv("NVIDIA_API_KEY", "")

def get_roic_key():
    return st.secrets.get("ROIC_API_KEY") or os.getenv("ROIC_API_KEY", "")


def _call_nvidia(system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
    """Single NVIDIA API call. Returns text or raises."""
    api_key = get_nvidia_key()
    r = requests.post(
        NVIDIA_API_URL,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"},
        json={
            "model": NVIDIA_MODEL,
            "max_tokens": max_tokens,
            "temperature": 0.6,
            "top_p": 0.95,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
        },
        timeout=120,
    )
    r.raise_for_status()
    msg = r.json()["choices"][0]["message"]
    return str(msg.get("content") or msg.get("reasoning_content") or msg.get("text") or "").strip()


# ── roic.ai calls (server-side, no CORS issue) ────────────────────────────────

def fetch_company_news(ticker: str, limit: int = 5) -> list:
    """Fetch latest company news from roic.ai"""
    roic_key = get_roic_key()
    url = f"https://api.roic.ai/v2/company/news/{ticker}"
    try:
        resp = requests.get(url, params={"limit": limit, "apikey": roic_key}, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.warning(f"News fetch failed: {e}")
        return []


def fetch_latest_earnings_call(ticker: str) -> dict | None:
    """Fetch latest earnings call transcript from roic.ai"""
    roic_key = get_roic_key()
    url = f"https://api.roic.ai/v2/company/earnings-calls/latest/{ticker}"
    try:
        resp = requests.get(url, params={"apikey": roic_key}, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.warning(f"Earnings call fetch failed: {e}")
        return None


def fetch_earnings_call_list(ticker: str) -> list:
    """Fetch list of available earnings calls"""
    roic_key = get_roic_key()
    url = f"https://api.roic.ai/v2/company/earnings-calls/list/{ticker}"
    try:
        resp = requests.get(url, params={"apikey": roic_key, "limit": 8}, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


# ── Generation calls ──────────────────────────────────────────────────────────

def generate_data_first_tweets(
    release: str,
    numbers: str,
    subcomps: str,
    context: str,
    format_type: str,
    tone: str,
    geo_context: str,
) -> str:
    """Generate data-first tweets (Liz Ann style)"""

    format_instr = (
        "Write 2 distinct short threads of 3–4 tweets. First tweet leads with the data, "
        "subsequent tweets cover subcomponents and context. Use [1/n] format."
        if format_type == "thread"
        else "Write 3 distinct single tweets (max 280 chars each), each with slightly different emphasis."
    )

    tone_instr = (
        "Dry wit permitted very sparingly — one dry rhetorical line max, only on extreme readings "
        "or big-picture fiscal scale. Otherwise stay purely factual."
        if tone == "dry"
        else "Stay purely factual and neutral. No wit, no opinion."
    )

    system_prompt = f"""You are a finance Twitter writer covering macro data for a sophisticated market audience.

GEOGRAPHY FOCUS: {geo_context}

STRUCTURE (strictly follow):
1. Open: [Release name] [reading] vs [estimate] est. & [prior] prior
2. Highlight 1–2 subcomponents — not the obvious headline. Find employment, capex, prices sub-index.
3. One neutral context sentence max. Factual observation only — no predictions.

{tone_instr}

STYLE: No AI tells. Use "…" for breaks. Source tag if relevant. No hashtags. Contractions and fragments fine.

{format_instr}

After each tweet/thread: ANGLE: [2–3 word label]
Return ONLY tweets and ANGLE labels. No preamble."""

    if not numbers.strip():
        user_prompt = (
            f"Release: {release}\nGeography: {geo_context}\n"
            f"{f'Subcomponents: {subcomps}' if subcomps else ''}\n"
            f"{f'Context: {context}' if context else ''}\n\n"
            "Use your knowledge of recent economic data to find the most recent actual reading, "
            "estimate, and prior reading. Write tweets based on real figures."
        )
    else:
        user_prompt = (
            f"Release: {release}\nNumbers: {numbers}\n"
            f"{f'Subcomponents: {subcomps}' if subcomps else ''}\n"
            f"{f'Context: {context}' if context else ''}\n\nWrite tweets using exactly these figures."
        )

    return _call_nvidia(system_prompt, user_prompt)


def generate_explainer_tweets(
    topic: str,
    data: str,
    format_type: str,
    emphasis: list[str],
) -> str:
    """Generate explainer/educational tweets"""

    format_map = {
        "single": "Write 3 distinct single explainer tweets (max 280 chars each), each covering a different facet.",
        "thread": "Write 2 educational threads of 4–5 tweets. Hook first. [1/n] format.",
        "series": "Write 3 standalone tweets postable on separate days: (1) methodology, (2) why markets care, (3) historical/global context.",
    }

    emphasis_map = {
        "methodology": "Explain HOW this data is collected — which agency, what survey, sample size, revision schedule.",
        "relevance":   "Explain WHY this matters — Fed signals, market implications, business impact.",
        "history":     "Historical context — compare to prior cycles, recessions, peaks.",
        "global":      "Compare to equivalent data from other major economies.",
    }

    emphasis_text = " ".join(emphasis_map[e] for e in emphasis if e in emphasis_map)

    system_prompt = f"""You are a finance Twitter educator writing macro data explainers. Peer-to-peer tone — not professor-to-student. Precise agency names, real methodology details. Never predict. No AI tells. No hashtags.

EMPHASIS: {emphasis_text}

{format_map.get(format_type, format_map['single'])}

After each tweet/thread: ANGLE: [2–3 word label]
Return ONLY tweets and ANGLE labels. No preamble."""

    user_prompt = (
        f"Topic: {topic}"
        f"{chr(10) + 'Data: ' + data if data else ''}"
        "\n\nUse your knowledge to provide official methodology, agency details, release schedule, and historical context."
    )

    return _call_nvidia(system_prompt, user_prompt)


def generate_stock_tweets(
    ticker: str,
    transcript: dict | None,
    news: list,
    focus: str,
    format_type: str,
    angles: list[str],
) -> str:
    """Generate stock intelligence tweets from real earnings call + news data"""

    format_map = {
        "single": "Write 3 distinct single tweets (max 280 chars each), each from a different angle.",
        "thread": "Write 2 threads of 4–6 tweets. Strong hook first, data in middle, clear so-what at end. [1/n] format.",
        "hot":    "Write 3 hot takes — punchy, data-anchored, max 220 chars. Clear claim designed to drive replies.",
    }

    angle_labels = {
        "explain": "Explain what happened in the filing/call in plain terms",
        "metric":  "Highlight the single most interesting metric (ROIC, FCF, working capital, margins, DSO)",
        "compare": "Compare this quarter to prior quarter — what changed and why it matters",
        "miss":    "What the market or consensus is underweighting or missing entirely",
    }

    angle_text = " | ".join(angle_labels[a] for a in angles if a in angle_labels)
    transcript_snippet = (transcript.get("content", "")[:6000] if transcript else "Not available")
    news_snippet = "\n\n".join(
        f"[{n.get('published_date', '')[:10]}] {n.get('title', '')} ({n.get('site', '')}): "
        f"{n.get('article_text', '')[:300]}"
        for n in news[:3]
    ) or "Not available"

    quarter = transcript.get("quarter", "?") if transcript else "?"
    year    = transcript.get("year", "") if transcript else ""

    system_prompt = f"""You are a finance Twitter ghostwriter for a sophisticated investor who reads earnings call transcripts and filings.

VOICE: Data-driven, specific to the point of obsession. Exact figures. Exact quarter references. Sounds like someone who read the transcript at 11pm and noticed something others missed.

RULES:
- Never opinionated about macro or Fed. Never says "buy" or "sell".
- No AI tells: no "delve", "fascinating", "it's worth noting", "robust", "nuanced", "landscape", "game-changer"
- Blunt. No throat-clearing. Light imperfection fine.
- Ground everything in the ACTUAL data provided — never invent numbers.
- No hashtags except $TICKER.

ANGLES: {angle_text}

{format_map.get(format_type, format_map['single'])}

After each tweet/thread: ANGLE: [2–3 word label]
Return ONLY tweets and ANGLE labels. No preamble."""

    user_prompt = (
        f"${ticker} — Q{quarter} {year}\n"
        f"{f'Focus: {focus}' if focus else ''}\n\n"
        f"=== EARNINGS CALL TRANSCRIPT ===\n{transcript_snippet}\n\n"
        f"=== RECENT NEWS ===\n{news_snippet}\n\n"
        "Write tweets grounded ONLY in the data above. Quote specific figures, specific transcript language, specific metrics."
    )

    return _call_nvidia(system_prompt, user_prompt)
