import streamlit as st
from dotenv import load_dotenv
import os

from transcript import fetch_transcript, estimate_tokens
from pipeline import run_pipeline
from utils import (
    build_markdown_download,
    build_html_download,
    build_zip_download,
    estimate_read_time,
    markdown_to_html_body,
    wrap_html_article,
)

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY", "")

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="YT → Article",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CUSTOM CSS — Clean light theme
# ──────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Background ── */
.stApp {
    background: #f5f3ef !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e8e4de !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04);
}

section[data-testid="stSidebar"] .stMarkdown p {
    color: #888;
    font-size: 0.82rem;
}

/* ── Sidebar headings ── */
section[data-testid="stSidebar"] h3 {
    color: #1a1a1a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

/* ── Hero ── */
.hero-wrap {
    background: linear-gradient(135deg, #ffffff 0%, #f0ede8 100%);
    border: 1px solid #e8e4de;
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 20px rgba(0,0,0,0.05);
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: #1a1a1a;
    line-height: 1.15;
    margin-bottom: 0.4rem;
}

.hero-title span {
    background: linear-gradient(135deg, #e85d26, #d4480f);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    color: #888;
    font-size: 0.95rem;
    font-weight: 400;
    letter-spacing: 0.01em;
}

/* ── Pipeline steps ── */
.pipeline-steps {
    display: flex;
    gap: 0.5rem;
    margin-top: 1.2rem;
    flex-wrap: wrap;
}

.pipe-step {
    background: #fff;
    border: 1px solid #e0dbd4;
    border-radius: 999px;
    padding: 0.3rem 0.9rem;
    font-size: 0.78rem;
    color: #555;
    font-weight: 500;
}

.pipe-step strong {
    color: #e85d26;
}

/* ── Input area ── */
.stTextInput > div > div > input {
    background: #ffffff !important;
    border: 1.5px solid #e0dbd4 !important;
    border-radius: 10px !important;
    color: #1a1a1a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
    transition: border-color 0.2s !important;
}

.stTextInput > div > div > input:focus {
    border-color: #e85d26 !important;
    box-shadow: 0 0 0 3px rgba(232, 93, 38, 0.1) !important;
}

/* ── Generate button ── */
.stButton > button {
    background: linear-gradient(135deg, #e85d26, #d4480f) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 4px 14px rgba(232, 93, 38, 0.35) !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(232, 93, 38, 0.45) !important;
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background: #ffffff !important;
    color: #e85d26 !important;
    border: 1.5px solid #e8d5cc !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    transition: all 0.15s !important;
}

.stDownloadButton > button:hover {
    background: #fff5f0 !important;
    border-color: #e85d26 !important;
}

/* ── Stat badges ── */
.stat-badge {
    display: inline-block;
    background: #ffffff;
    border: 1px solid #e0dbd4;
    color: #555;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    padding: 0.28rem 0.75rem;
    border-radius: 999px;
    margin-right: 0.4rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.stat-badge b {
    color: #e85d26;
}

/* ── Content boxes (tabs) ── */
.content-box {
    background: #ffffff;
    border: 1px solid #e8e4de;
    border-radius: 14px;
    padding: 1.8rem 2.2rem;
    font-size: 0.94rem;
    line-height: 1.85;
    color: #333;
    max-height: 520px;
    overflow-y: auto;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

.content-box h1 {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    color: #1a1a1a;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #f0ede8;
}

.content-box h2 {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    color: #1a1a1a;
    margin: 1.5rem 0 0.5rem;
}

.content-box h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #e85d26;
    margin: 1.2rem 0 0.4rem;
}

.content-box p { color: #444; margin-bottom: 1rem; }

.content-box ul { padding-left: 0; list-style: none; }

.content-box ul li {
    border-left: 3px solid #e85d26;
    padding-left: 1rem;
    margin-bottom: 0.6rem;
    color: #444;
}

.content-box code {
    font-family: 'JetBrains Mono', monospace;
    background: #f7f4f0;
    color: #c0392b;
    padding: 0.15em 0.45em;
    border-radius: 5px;
    font-size: 0.85em;
    border: 1px solid #ede9e3;
}

.content-box strong { color: #1a1a1a; font-weight: 600; }

/* ── Chunk cards ── */
.chunk-card {
    background: #ffffff;
    border: 1px solid #e8e4de;
    border-left: 3px solid #e85d26;
    border-radius: 10px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.8rem;
    font-size: 0.88rem;
    color: #555;
    line-height: 1.75;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}

.chunk-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #e85d26;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 0.25rem !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #999 !important;
    background: #ffffff !important;
    border: 1px solid #e8e4de !important;
    border-radius: 8px !important;
    padding: 0.4rem 1rem !important;
}

.stTabs [aria-selected="true"] {
    color: #e85d26 !important;
    border-color: #e85d26 !important;
    background: #fff5f0 !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #e85d26, #f0956a) !important;
    border-radius: 999px !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #ffffff !important;
    border: 1.5px solid #e0dbd4 !important;
    border-radius: 10px !important;
    color: #1a1a1a !important;
}

/* ── Radio ── */
.stRadio > label {
    color: #444 !important;
    font-size: 0.88rem !important;
}

/* ── Alerts ── */
.stAlert {
    border-radius: 10px !important;
    font-size: 0.88rem !important;
}

/* ── Divider ── */
hr {
    border-color: #e8e4de !important;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #bbb;
}

.empty-state .icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    opacity: 0.4;
}

.empty-state .title {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    color: #ccc;
    margin-bottom: 0.4rem;
}

.empty-state .sub {
    font-size: 0.85rem;
    color: #ddd;
}

/* ── Scrollbar ── */
.content-box::-webkit-scrollbar { width: 4px; }
.content-box::-webkit-scrollbar-track { background: #f5f3ef; }
.content-box::-webkit-scrollbar-thumb { background: #ddd; border-radius: 999px; }

/* ── API key warning banner ── */
.api-warning {
    background: #fff8f0;
    border: 1px solid #fcd9b8;
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    font-size: 0.85rem;
    color: #a05a2c;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# SIDEBAR — No API key input, just options
# ──────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Model")
    st.divider()

    model = st.selectbox(
        "Gemini Model",
        options=[
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-2.5-pro",
        ],
        index=0,
        help="gemini-2.5-flash-lite → highest free quota (1,000 req/day)",
    )

    st.divider()
    st.markdown("### 🎛️ Article Options")

    style = st.radio(
        "Article Style",
        options=["Blog", "Newsletter", "Report"],
        index=0,
        help="Blog = conversational · Newsletter = scannable · Report = formal",
    )

    length = st.radio(
        "Summary Length",
        options=["Short", "Medium", "Long"],
        index=1,
        help="Short = 3-5 sentences · Medium = 2-3 paragraphs · Long = 4-5 paragraphs",
    )

    output_format = st.radio(
        "Output Format",
        options=["Markdown", "HTML"],
        index=0,
    )

    st.divider()
    st.markdown("""
**Pipeline**

1. Fetch transcript
2. **Map** — chunk → key points
3. **Reduce** — points → summary
4. **Article** — summary → article
    """)

    # Show API key status (read-only, no input)
    st.divider()
    if API_KEY:
        st.success("✅ API key loaded from .env")
    else:
        st.error("❌ No API key found in .env")
        st.caption("Add `GOOGLE_API_KEY=...` to your `.env` file and restart the app.")


# ──────────────────────────────────────────────
# MAIN AREA — Hero
# ──────────────────────────────────────────────

st.markdown("""
<div class="hero-wrap">
  <div class="hero-title">YouTube <span>→ Article</span></div>
  <div class="hero-sub">Map-Reduce pipeline · Powered by Gemini + LangChain</div>
  <div class="pipeline-steps">
    <div class="pipe-step">📡 Transcript</div>
    <div class="pipe-step">→</div>
    <div class="pipe-step"><strong>Map</strong> chunks</div>
    <div class="pipe-step">→</div>
    <div class="pipe-step"><strong>Reduce</strong> summary</div>
    <div class="pipe-step">→</div>
    <div class="pipe-step"><strong>Article</strong></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── URL Input ──
url_col, btn_col = st.columns([5, 1])

with url_col:
    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed",
    )

with btn_col:
    generate_btn = st.button("🚀 Generate", use_container_width=True)


# ──────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────

if "result" not in st.session_state:
    st.session_state.result = None
if "transcript" not in st.session_state:
    st.session_state.transcript = None


# ──────────────────────────────────────────────
# GENERATION LOGIC
# ──────────────────────────────────────────────

if generate_btn:
    if not youtube_url.strip():
        st.error("Please enter a YouTube URL.")
    elif not API_KEY:
        st.error("No API key found. Add GOOGLE_API_KEY to your .env file and restart.")
    else:
        st.session_state.result = None
        st.session_state.transcript = None

        with st.status("Fetching transcript...", expanded=True) as status:
            try:
                st.write("📡 Connecting to YouTube...")
                transcript = fetch_transcript(youtube_url)
                token_count = estimate_tokens(transcript)
                st.session_state.transcript = transcript

                mode_label = "map-reduce" if token_count >= 3000 else "direct"
                st.write(f"✅ Transcript fetched — ~{token_count:,} tokens · mode: **{mode_label}**")

                progress_bar = st.progress(0)
                progress_text = st.empty()

                def progress_callback(step, total, message="Processing..."):
                    pct = int((step / max(total, 1)) * 100)
                    progress_bar.progress(min(pct, 100))
                    progress_text.markdown(f"`{message}`")

                result = run_pipeline(
                    transcript=transcript,
                    api_key=API_KEY,
                    model=model,
                    length=length,
                    style=style,
                    output_format=output_format,
                    progress_callback=progress_callback,
                )

                st.session_state.result = result
                progress_bar.progress(100)
                progress_text.markdown("`✅ Done!`")
                status.update(label="✅ Generation complete!", state="complete")

            except ValueError as e:
                st.error(str(e))
                status.update(label="❌ Failed", state="error")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
                status.update(label="❌ Failed", state="error")


# ──────────────────────────────────────────────
# RESULTS
# ──────────────────────────────────────────────

if st.session_state.result:
    result = st.session_state.result
    transcript = st.session_state.transcript

    st.markdown("<br>", unsafe_allow_html=True)

    read_time   = estimate_read_time(result["article"])
    chunk_count = result.get("chunk_count", 1)
    mode        = result.get("mode", "direct")
    tokens      = result.get("token_count", 0)

    st.markdown(
        f'<span class="stat-badge">~<b>{tokens:,}</b> tokens</span>'
        f'<span class="stat-badge"><b>{chunk_count}</b> chunk{"s" if chunk_count > 1 else ""}</span>'
        f'<span class="stat-badge">mode: <b>{mode}</b></span>'
        f'<span class="stat-badge"><b>{read_time}</b></span>'
        f'<span class="stat-badge">style: <b>{style}</b></span>'
        f'<span class="stat-badge">length: <b>{length}</b></span>',
        unsafe_allow_html=True,
    )

    tab_transcript, tab_chunks, tab_summary, tab_article, tab_export = st.tabs([
        "📄 Transcript",
        "🔀 Chunks",
        "✨ Summary",
        "📝 Article",
        "⬇️ Export",
    ])

    with tab_transcript:
        st.markdown(f'<div class="content-box">{transcript}</div>', unsafe_allow_html=True)

    with tab_chunks:
        mini_summaries = result.get("mini_summaries", [])
        if mini_summaries:
            st.markdown(f"**{len(mini_summaries)} chunks** processed during the Map phase:")
            st.markdown("<br>", unsafe_allow_html=True)
            for i, mini in enumerate(mini_summaries):
                st.markdown(
                    f'<div class="chunk-card">'
                    f'<div class="chunk-label">Section {i+1}</div>'
                    f'{mini.replace(chr(10), "<br>")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Short video — direct summarization used, no chunking needed.")

    with tab_summary:
        st.markdown(
            f'<div class="content-box">{result["summary"].replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )

    with tab_article:
        article_text = result["article"]
        if output_format == "HTML":
            full_html = wrap_html_article(article_text)
            st.components.v1.html(full_html, height=600, scrolling=True)
        else:
            article_html = markdown_to_html_body(article_text)
            st.markdown(f'<div class="content-box">{article_html}</div>', unsafe_allow_html=True)

        with st.expander("🔍 View raw source"):
            st.code(article_text, language="html" if output_format == "HTML" else "markdown")

    with tab_export:
        st.markdown("#### Download your content")
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            md_bytes = build_markdown_download(result["summary"], result["article"])
            st.download_button(
                label="⬇️ Markdown (.md)",
                data=md_bytes,
                file_name="youtube_article.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.caption("Summary + Article")

        with col2:
            html_bytes = build_html_download(result["summary"], result["article"])
            st.download_button(
                label="⬇️ HTML (.html)",
                data=html_bytes,
                file_name="youtube_article.html",
                mime="text/html",
                use_container_width=True,
            )
            st.caption("Styled webpage")

        with col3:
            zip_bytes = build_zip_download(result["summary"], result["article"], result["article"])
            st.download_button(
                label="⬇️ ZIP bundle",
                data=zip_bytes,
                file_name="youtube_article.zip",
                mime="application/zip",
                use_container_width=True,
            )
            st.caption("All files bundled")

        st.divider()
        st.markdown("#### 🔀 Pipeline Summary")
        st.markdown(f"""
| Stage | Details |
|---|---|
| **Transcript tokens** | ~{tokens:,} |
| **Chunks processed** | {chunk_count} |
| **Pipeline mode** | {mode} |
| **Summary length** | {length} |
| **Article style** | {style} |
| **Output format** | {output_format} |
| **Read time** | {read_time} |
        """)

# ── Empty state ──
elif not generate_btn:
    st.markdown("""
<div class="empty-state">
  <div class="icon">🎬</div>
  <div class="title">Paste a YouTube URL above to get started</div>
  <div class="sub">Transcript → Map-Reduce Summary → Structured Article</div>
</div>
""", unsafe_allow_html=True)
