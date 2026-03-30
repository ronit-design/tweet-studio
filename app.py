# app.py — Tweet Studio
# Streamlit frontend for Finance Twitter content generation

import streamlit as st
from datetime import date, timedelta

from utils.data import US_CATEGORIES, INTL_CATEGORIES, COUNTRIES, COUNTRY_COLORS
from utils.api import (
    fetch_company_news,
    fetch_latest_earnings_call,
    generate_data_first_tweets,
    generate_explainer_tweets,
    generate_stock_tweets,
)
from utils.helpers import parse_tweet_blocks, get_upcoming_releases, format_date_label
from utils.chart import parse_pasted_data, detect_date_col, render_bloomberg_chart  # noqa: E501

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tweet Studio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  .masthead {
    border-bottom: 2px solid #1a1814;
    padding-bottom: 12px;
    margin-bottom: 24px;
  }
  .masthead h1 {
    font-family: 'DM Serif Display', serif;
    font-size: 36px;
    color: #1a1814;
    margin: 0;
    line-height: 1;
  }
  .masthead h1 em { color: #c23b22; font-style: italic; }
  .masthead-date {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #8a8480;
    margin-top: 4px;
  }

  .tweet-card {
    background: #ede8df;
    border: 1px solid #d4cfc5;
    border-radius: 6px;
    padding: 16px 18px;
    margin-bottom: 12px;
  }
  .tweet-angle {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8a8480;
    background: #e5e0d6;
    padding: 2px 8px;
    border-radius: 3px;
    display: inline-block;
    margin-bottom: 10px;
  }
  .tweet-text {
    font-size: 14px;
    line-height: 1.7;
    color: #1a1814;
    white-space: pre-wrap;
  }
  .char-count {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #8a8480;
    text-align: right;
    margin-top: 8px;
  }
  .char-count.over { color: #c23b22; font-weight: 500; }

  .section-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #8a8480;
    margin-bottom: 4px;
  }

  .cal-item {
    padding: 8px 12px;
    border-left: 3px solid #d4cfc5;
    margin-bottom: 6px;
    background: #ede8df;
    border-radius: 0 4px 4px 0;
    cursor: pointer;
  }
  .cal-item:hover { background: #e5e0d6; }
  .cal-item-name { font-size: 13px; font-weight: 500; color: #1a1814; }
  .cal-item-meta { font-family: 'DM Mono', monospace; font-size: 10px; color: #8a8480; }

  .stTextArea textarea {
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
  }

  div[data-testid="stSidebar"] {
    background-color: #ede8df;
  }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "company_news": [],
        "company_transcript": None,
        "company_ticker": "",
        "macro_results": [],
        "stock_results": [],
        "stock_gen_v": 0,
        "selected_release": "",
        "cal_country_filter": {"US", "CN", "JP", "KR", "IN", "EU", "UK"},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Sidebar: Release Calendar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📅 Release Calendar")
    st.caption("Upcoming economic data — next 6 weeks")

    # Country filters
    all_countries = [("US", "🇺🇸")] + [(c["id"], c["flag"]) for c in COUNTRIES]
    active = st.session_state.cal_country_filter

    cols = st.columns(4)
    for i, (cid, flag) in enumerate(all_countries):
        with cols[i % 4]:
            checked = cid in active
            if st.checkbox(flag, value=checked, key=f"cal_filter_{cid}"):
                active.add(cid)
            else:
                active.discard(cid)
    st.session_state.cal_country_filter = active

    st.divider()

    releases = get_upcoming_releases(days_ahead=42)
    filtered = [r for r in releases if r["country"] in active]

    if not filtered:
        st.caption("No releases match current filters.")
    else:
        # Group by date
        from itertools import groupby
        for d, items in groupby(filtered, key=lambda x: x["date"]):
            label = format_date_label(d)
            st.markdown(f"**{label}**")
            for item in items:
                color = COUNTRY_COLORS.get(item["country"], "#666")
                name = item["name"]
                note = item["note"]
                # Clickable — sets selected release
                if st.button(
                    f"{item['flag']} {name}",
                    key=f"cal_{name}_{d}",
                    help=note,
                    use_container_width=True,
                ):
                    st.session_state.selected_release = name
                    # Switch to correct geo if international
                    if item["country"] != "US":
                        st.session_state.geo_mode = "intl"
                        st.session_state.active_countries = {item["country"]}
                    else:
                        st.session_state.geo_mode = "us"
                    st.rerun()

# ── Main content ──────────────────────────────────────────────────────────────

# Masthead
st.markdown(f"""
<div class="masthead">
  <h1>Tweet <em>Studio</em></h1>
  <div class="masthead-date">{date.today().strftime('%A, %B %-d, %Y')} · Finance · Macro · Equities</div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab_macro, tab_stock, tab_chart = st.tabs(["① Macro Data", "② Stock Intelligence", "③ Bloomberg Chart"])


# ══════════════════════════════════════════════════════════════════
# MACRO TAB
# ══════════════════════════════════════════════════════════════════
with tab_macro:

    # Geography toggle
    geo = st.radio(
        "Geography",
        ["🇺🇸 United States", "🌐 International"],
        horizontal=True,
        key="geo_radio",
        label_visibility="collapsed",
    )
    geo_mode = "us" if "United States" in geo else "intl"

    # Country selector (international only)
    active_countries = set()
    if geo_mode == "intl":
        st.markdown('<div class="section-label">Select countries</div>', unsafe_allow_html=True)
        country_cols = st.columns(len(COUNTRIES))
        for i, c in enumerate(COUNTRIES):
            with country_cols[i]:
                default = c["id"] in st.session_state.get("active_countries", {"CN","JP","KR","IN","EU","UK"})
                if st.checkbox(f"{c['flag']} {c['name']}", value=default, key=f"country_{c['id']}"):
                    active_countries.add(c["id"])
        st.session_state.active_countries = active_countries
        if not active_countries:
            active_countries = {"CN"}  # fallback

    st.divider()

    # Mode toggle
    mode = st.radio(
        "Mode",
        ["📊 Data-First", "📖 Explainer"],
        horizontal=True,
        key="macro_mode",
    )

    # ── DATA-FIRST MODE ──────────────────────────────────────────
    if "Data-First" in mode:

        # Category grid
        if geo_mode == "us":
            cats = US_CATEGORIES
        else:
            cats = [INTL_CATEGORIES[cid] for cid in active_countries if cid in INTL_CATEGORIES]

        st.markdown('<div class="section-label">Select category</div>', unsafe_allow_html=True)

        # Show categories in a grid
        n_cols = 4
        cat_cols = st.columns(n_cols)
        selected_cat = None

        if "selected_cat_id" not in st.session_state:
            st.session_state.selected_cat_id = None

        for i, cat in enumerate(cats):
            with cat_cols[i % n_cols]:
                is_sel = st.session_state.selected_cat_id == cat["id"]
                label = f"{cat['icon']} **{cat['name']}**\n{cat['ex']}"
                if st.button(
                    f"{cat['icon']} {cat['name']}",
                    key=f"cat_{cat['id']}",
                    use_container_width=True,
                    type="primary" if is_sel else "secondary",
                    help=cat["ex"],
                ):
                    st.session_state.selected_cat_id = cat["id"]
                    if cat.get("releases"):
                        st.session_state.selected_release = cat["releases"][0]
                    st.rerun()

        # Get selected category data
        all_cats = US_CATEGORIES + list(INTL_CATEGORIES.values())
        selected_cat = next((c for c in all_cats if c["id"] == st.session_state.selected_cat_id), None)

        # Release quick-picks
        release_name = st.session_state.get("selected_release", "")
        if selected_cat:
            st.markdown('<div class="section-label" style="margin-top:12px;">Quick-select release</div>', unsafe_allow_html=True)
            chip_cols = st.columns(3)
            for i, rel in enumerate(selected_cat["releases"]):
                with chip_cols[i % 3]:
                    if st.button(rel, key=f"rel_{rel}", use_container_width=True):
                        st.session_state.selected_release = rel
                        st.rerun()

        st.divider()

        # Inputs
        col1, col2 = st.columns(2)
        with col1:
            release_name = st.text_input(
                "Release name",
                value=st.session_state.get("selected_release", ""),
                placeholder="e.g. Kansas City Fed Services, UMich Consumer Sentiment final...",
                key="df_release",
            )
        with col2:
            numbers = st.text_input(
                "Actual data vs estimate vs prior (leave blank to auto-search)",
                placeholder="e.g. +15 vs +4 est. & +6 prior",
                key="df_numbers",
            )

        # Subcomponent hints
        if selected_cat:
            st.markdown('<div class="section-label">Subcomponents (click to add)</div>', unsafe_allow_html=True)
            subcomp_input = st.session_state.get("df_subcomps", "")
            subcomp_cols = st.columns(8)
            for i, sc in enumerate(selected_cat["subcomps"]):
                with subcomp_cols[i % 8]:
                    if st.button(sc, key=f"sc_{sc}", use_container_width=True, help="Add to subcomponents"):
                        current = st.session_state.get("df_subcomps", "")
                        if sc not in current:
                            st.session_state.df_subcomps = (current + ", " + sc).strip(", ")
                        st.rerun()

        subcomps = st.text_input(
            "Subcomponents",
            value=st.session_state.get("df_subcomps", ""),
            placeholder="e.g. employment up, capex plans up, input prices spiked...",
            key="df_subcomps_input",
        )
        context = st.text_input(
            "One-line context (optional)",
            placeholder="e.g. first back-to-back decline since 2022...",
            key="df_context",
        )

        col_fmt, col_tone = st.columns(2)
        with col_fmt:
            fmt = st.radio("Format", ["Single Tweet", "Short Thread"], horizontal=True, key="df_fmt")
        with col_tone:
            tone = st.radio("Tone", ["Neutral / Factual", "+ Dry wit"], horizontal=True, key="df_tone")
            st.caption("Dry wit: very sparingly, only on extreme or big-picture readings")

        # Determine geo context string
        if geo_mode == "us":
            geo_context = "United States"
        else:
            country_names = [c["name"] for c in COUNTRIES if c["id"] in active_countries]
            geo_context = ", ".join(country_names) if country_names else "International"

        if st.button("⚡ Generate Data-First Tweet", type="primary", use_container_width=True, key="df_gen"):
            if not release_name.strip():
                st.error("Enter a release name first.")
            else:
                with st.spinner("Searching for latest figures..." if not numbers.strip() else "Drafting tweet..."):
                    try:
                        result = generate_data_first_tweets(
                            release=release_name,
                            numbers=numbers,
                            subcomps=subcomps,
                            context=context,
                            format_type="thread" if "Thread" in fmt else "single",
                            tone="dry" if "Dry" in tone else "neutral",
                            geo_context=geo_context,
                        )
                        st.session_state.macro_results = parse_tweet_blocks(result)
                        st.session_state.macro_mode_used = "data"
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

    # ── EXPLAINER MODE ───────────────────────────────────────────
    else:
        topic = st.text_input(
            "Data point or release to explain",
            placeholder="e.g. Core PCE, UMich Consumer Sentiment, China Caixin PMI...",
            key="ex_topic",
        )
        ex_data = st.text_input(
            "Actual data (optional)",
            placeholder="e.g. CPI +3.1% YoY",
            key="ex_data",
        )

        col_fmt, col_em = st.columns(2)
        with col_fmt:
            ex_fmt = st.radio("Format", ["Single Tweet", "Thread", "3-Part Series"], horizontal=True, key="ex_fmt")
        with col_em:
            emphasis = st.multiselect(
                "Emphasis",
                ["How it's measured", "Why it matters", "Historical context", "Global comparison"],
                default=["How it's measured", "Why it matters"],
                key="ex_emphasis",
            )

        emphasis_map = {
            "How it's measured": "methodology",
            "Why it matters": "relevance",
            "Historical context": "history",
            "Global comparison": "global",
        }
        fmt_map = {"Single Tweet": "single", "Thread": "thread", "3-Part Series": "series"}

        if st.button("📖 Generate Explainer Tweet", type="primary", use_container_width=True, key="ex_gen"):
            if not topic.strip():
                st.error("Enter a topic first.")
            else:
                with st.spinner("Fetching methodology and context..."):
                    try:
                        result = generate_explainer_tweets(
                            topic=topic,
                            data=ex_data,
                            format_type=fmt_map.get(ex_fmt, "single"),
                            emphasis=[emphasis_map[e] for e in emphasis if e in emphasis_map],
                        )
                        st.session_state.macro_results = parse_tweet_blocks(result)
                        st.session_state.macro_mode_used = "explainer"
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

    # ── Results ──────────────────────────────────────────────────
    if st.session_state.macro_results:
        mode_badge = "Data-First" if st.session_state.get("macro_mode_used") == "data" else "Explainer"
        st.markdown(f"---\n**{mode_badge}** · {len(st.session_state.macro_results)} variations")

        for i, block in enumerate(st.session_state.macro_results):
            content = block["content"]
            angle = block["angle"]
            char_count = len(content)
            is_over = char_count > 280

            with st.container():
                st.markdown(f'<span class="tweet-angle">{angle}</span>', unsafe_allow_html=True)
                edited = st.text_area(
                    f"Tweet {i+1}",
                    value=content,
                    height=120,
                    key=f"macro_tweet_{i}",
                    label_visibility="collapsed",
                )
                count_class = "over" if len(edited) > 280 else ""
                st.markdown(
                    f'<div class="char-count {count_class}">{len(edited)}/280</div>',
                    unsafe_allow_html=True
                )
                col_copy, col_trim, _ = st.columns([1, 1, 4])
                with col_copy:
                    st.button("📋 Copy", key=f"macro_copy_{i}", on_click=lambda t=edited: st.write(t))
                with col_trim:
                    if len(edited) > 280:
                        if st.button("✂️ Trim", key=f"macro_trim_{i}"):
                            st.session_state.macro_results[i]["content"] = edited[:277] + "..."
                            st.rerun()
                st.markdown("---")


# ══════════════════════════════════════════════════════════════════
# STOCK INTELLIGENCE TAB
# ══════════════════════════════════════════════════════════════════
with tab_stock:
    st.markdown("### Stock Intelligence")
    st.caption("roic.ai · Earnings Calls · Company News")

    col_ticker, col_btn = st.columns([3, 1])
    with col_ticker:
        ticker_input = st.text_input(
            "Ticker symbol",
            placeholder="e.g. AAPL, MSFT, V, FICO, SPGI...",
            key="stock_ticker_input",
        ).upper()
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        pull_data = st.button("Pull Data →", type="primary", use_container_width=True, key="pull_data_btn")

    if pull_data and ticker_input:
        with st.spinner(f"Fetching data for ${ticker_input} from roic.ai..."):
            news = fetch_company_news(ticker_input)
            transcript = fetch_latest_earnings_call(ticker_input)

            if not news and not transcript:
                st.error(f"No data found for ${ticker_input}. Check the ticker symbol.")
            else:
                st.session_state.company_ticker = ticker_input
                st.session_state.company_news = news
                st.session_state.company_transcript = transcript
                st.session_state.stock_results = []
                st.success(f"✓ ${ticker_input} loaded")

    # Show data preview if loaded
    if st.session_state.company_ticker:
        ticker = st.session_state.company_ticker
        transcript = st.session_state.company_transcript
        news = st.session_state.company_news

        # Context summary
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Ticker", f"${ticker}")
        with col_b:
            if transcript:
                st.metric("Latest Call", f"Q{transcript.get('quarter','?')} {transcript.get('year','')}")
            else:
                st.metric("Latest Call", "N/A")
        with col_c:
            st.metric("News Articles", len(news))

        # News strip
        if news:
            with st.expander("📰 Recent News", expanded=True):
                for n in news[:4]:
                    pub = n.get("published_date", "")[:10] if n.get("published_date") else ""
                    st.markdown(f"**{pub}** · {n.get('title', '')} · *{n.get('site', '')}*")

        # Transcript preview
        if transcript and transcript.get("content"):
            with st.expander("🎙️ Earnings Call Preview", expanded=False):
                st.caption(f"Q{transcript.get('quarter')} {transcript.get('year')} · {transcript.get('date', '')}")
                st.markdown(f"*{transcript['content'][:600]}...*")

        st.divider()

        # Generation controls
        focus = st.text_input(
            "Specific focus (optional)",
            placeholder="e.g. working capital, ROIC trajectory, margin compression, guidance language...",
            key="stock_focus",
        )

        col_fmt, col_angles = st.columns(2)
        with col_fmt:
            stock_fmt = st.radio(
                "Format",
                ["Single Tweet", "Thread", "Hot Take"],
                horizontal=True,
                key="stock_fmt_radio",
            )
        with col_angles:
            stock_angles = st.multiselect(
                "Angles",
                ["Explain filing", "Key metric", "vs prior quarter", "What market's missing"],
                default=["Explain filing", "Key metric", "vs prior quarter", "What market's missing"],
                key="stock_angles_sel",
            )

        angle_map = {
            "Explain filing": "explain",
            "Key metric": "metric",
            "vs prior quarter": "compare",
            "What market's missing": "miss",
        }
        fmt_map = {"Single Tweet": "single", "Thread": "thread", "Hot Take": "hot"}

        if st.button("⚡ Generate Tweets from Real Data", type="primary", use_container_width=True, key="stock_gen_btn"):
            if not stock_angles:
                st.error("Select at least one angle.")
            else:
                with st.spinner(f"Analyzing ${ticker} earnings call + news..."):
                    try:
                        result = generate_stock_tweets(
                            ticker=ticker,
                            transcript=transcript,
                            news=news,
                            focus=focus,
                            format_type=fmt_map.get(stock_fmt, "single"),
                            angles=[angle_map[a] for a in stock_angles if a in angle_map],
                        )
                        st.session_state.stock_gen_v += 1
                        st.session_state.stock_results = parse_tweet_blocks(result)
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

        # Stock results
        if st.session_state.stock_results:
            st.markdown(f"---\n**Generated** · {len(st.session_state.stock_results)} variations")
            for i, block in enumerate(st.session_state.stock_results):
                content = block["content"]
                angle = block["angle"]

                st.markdown(f'<span class="tweet-angle">{angle}</span>', unsafe_allow_html=True)
                gen = st.session_state.stock_gen_v
                edited = st.text_area(
                    f"Stock tweet {i+1}",
                    value=content,
                    height=120,
                    key=f"stock_tweet_{gen}_{i}",
                    label_visibility="collapsed",
                )
                count_class = "over" if len(edited) > 280 else ""
                st.markdown(
                    f'<div class="char-count {count_class}">{len(edited)}/280</div>',
                    unsafe_allow_html=True
                )
                col_copy, col_trim, _ = st.columns([1, 1, 4])
                with col_copy:
                    st.button("📋 Copy", key=f"stock_copy_{gen}_{i}")
                with col_trim:
                    if len(edited) > 280:
                        if st.button("✂️ Trim", key=f"stock_trim_{gen}_{i}"):
                            st.session_state.stock_results[i]["content"] = edited[:277] + "..."
                            st.rerun()
                st.markdown("---")

    else:
        st.info("Enter a ticker above and click **Pull Data →** to load earnings call + news.")


# ══════════════════════════════════════════════════════════════════
# BLOOMBERG CHART TAB
# ══════════════════════════════════════════════════════════════════
with tab_chart:
    st.markdown("### Bloomberg Chart Generator")
    st.caption("Paste data from Excel or CSV — outputs a Bloomberg GP-style chart")

    raw_data = st.text_area(
        "Paste data here",
        height=160,
        placeholder="Copy from Excel or paste CSV — first row must be column headers",
        key="chart_raw_data",
    )

    if raw_data.strip():
        try:
            df_chart = parse_pasted_data(raw_data)
            st.dataframe(df_chart.head(5), use_container_width=True)

            date_col_guess = detect_date_col(df_chart)
            all_cols = df_chart.columns.tolist()

            col_x, col_y = st.columns(2)
            with col_x:
                x_col = st.selectbox(
                    "X axis (date or category column)",
                    all_cols,
                    index=all_cols.index(date_col_guess) if date_col_guess else 0,
                    key="chart_x_col",
                )
            with col_y:
                y_default = [c for c in all_cols if c != x_col][:3]
                y_cols = st.multiselect(
                    "Y axis (data series — up to 5)",
                    [c for c in all_cols if c != x_col],
                    default=y_default,
                    key="chart_y_cols",
                )

            col_title, col_ts = st.columns([3, 1])
            with col_title:
                chart_title = st.text_input(
                    "Chart title / ticker",
                    placeholder="e.g. AAPL US Equity",
                    key="chart_title",
                )
            with col_ts:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                is_ts = st.checkbox("Time series", value=bool(date_col_guess), key="chart_is_ts")

            col_xl, col_yl = st.columns(2)
            with col_xl:
                x_label = st.text_input("X axis label (optional)", key="chart_x_label",
                                        placeholder="e.g. Date")
            with col_yl:
                y_label = st.text_input("Y axis label (optional)", key="chart_y_label",
                                        placeholder="e.g. Index Value")

            if st.button("Generate Chart", type="primary", use_container_width=True, key="chart_gen_btn"):
                if not y_cols:
                    st.error("Select at least one Y axis column.")
                else:
                    with st.spinner("Rendering..."):
                        try:
                            png = render_bloomberg_chart(
                                df=df_chart,
                                x_col=x_col,
                                y_cols=y_cols,
                                title=chart_title,
                                x_label=x_label,
                                y_label=y_label,
                                is_time_series=is_ts,
                            )
                            st.session_state.chart_png = png
                        except Exception as e:
                            st.error(f"Chart error: {e}")

        except Exception as e:
            st.error(f"Could not parse data: {e}")

    if st.session_state.get("chart_png"):
        st.image(st.session_state.chart_png, use_container_width=True)
        st.download_button(
            "⬇ Download PNG",
            data=st.session_state.chart_png,
            file_name="bloomberg_chart.png",
            mime="image/png",
            key="chart_download",
        )
