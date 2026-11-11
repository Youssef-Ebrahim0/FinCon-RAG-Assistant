import sys
from pathlib import Path

import streamlit as st

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.generation.chain import FinConRAGPipeline
from src.ingestion.run_ingestion import run_ingestion_pipeline


# -----------------------------------------------------------------------------
# Page configuration and visual identity
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Financial Regulatory Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --navy: #0b1f33;
        --navy-2: #123451;
        --ink: #172433;
        --muted: #637285;
        --line: #dfe6ee;
        --surface: #ffffff;
        --surface-soft: #f4f7fa;
        --gold: #c59b4a;
        --gold-soft: #f8f1e3;
        --green: #2f8066;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: var(--ink);
    }

    [data-testid="stAppViewContainer"] {
        background: #f7f9fb;
    }

    [data-testid="stHeader"] {
        background: rgba(247, 249, 251, 0.82);
    }

    [data-testid="stSidebar"] {
        background: var(--navy);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    [data-testid="stSidebar"] * {
        color: #eef4f8;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-testid="stNumberInputContainer"],
    [data-testid="stSidebar"] [data-testid="stSlider"] {
        background: rgba(255,255,255,0.09);
        border-radius: 10px;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.16);
    }

    .brand-lockup {
        padding: 0.15rem 0 1.3rem;
    }

    .brand-mark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 38px;
        margin-bottom: 0.7rem;
        border: 1px solid var(--gold);
        border-radius: 11px;
        color: var(--gold);
        font-family: 'Manrope', sans-serif;
        font-size: 1.25rem;
        font-weight: 800;
    }

    .brand-name {
        color: white;
        font-family: 'Manrope', sans-serif;
        font-size: 1.08rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    .brand-subtitle {
        margin-top: 0.25rem;
        color: #9eb1c4;
        font-size: 0.76rem;
        line-height: 1.4;
    }

    .eyebrow {
        margin-bottom: 0.65rem;
        color: var(--gold);
        font-size: 0.73rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
    }

    .hero-title {
        margin: 0;
        color: var(--navy);
        font-family: 'Manrope', sans-serif;
        font-size: clamp(2rem, 4vw, 3.3rem);
        font-weight: 800;
        letter-spacing: -0.055em;
        line-height: 1.03;
    }

    .hero-copy {
        max-width: 720px;
        margin-top: 0.9rem;
        color: var(--muted);
        font-size: 1.02rem;
        line-height: 1.65;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.42rem 0.72rem;
        border: 1px solid #cfe4db;
        border-radius: 999px;
        background: #eef8f3;
        color: var(--green);
        font-size: 0.76rem;
        font-weight: 700;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #43aa80;
        box-shadow: 0 0 0 3px rgba(67,170,128,0.15);
    }

    .section-label {
        margin: 1.7rem 0 0.55rem;
        color: var(--navy);
        font-family: 'Manrope', sans-serif;
        font-size: 1.04rem;
        font-weight: 800;
    }

    .query-shell {
        padding: 1.15rem 1.25rem 0.45rem;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: var(--surface);
        box-shadow: 0 12px 32px rgba(19, 43, 65, 0.06);
    }

    .answer-card {
        padding: 1.35rem 1.5rem;
        border: 1px solid #dbe5ed;
        border-left: 4px solid var(--gold);
        border-radius: 14px;
        background: var(--surface);
        box-shadow: 0 10px 30px rgba(19, 43, 65, 0.05);
    }

    .answer-card h3 {
        margin-top: 0;
        color: var(--navy);
        font-family: 'Manrope', sans-serif;
    }

    .metric-card {
        min-height: 92px;
        padding: 1rem 1.1rem;
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--surface);
    }

    .metric-value {
        color: var(--navy);
        font-family: 'Manrope', sans-serif;
        font-size: 1.45rem;
        font-weight: 800;
    }

    .metric-label {
        margin-top: 0.2rem;
        color: var(--muted);
        font-size: 0.78rem;
    }

    .source-card {
        min-height: 74px;
        padding: 0.9rem 1rem;
        border: 1px solid var(--line);
        border-radius: 11px;
        background: var(--surface);
        color: var(--ink);
        font-size: 0.85rem;
        line-height: 1.4;
    }

    .source-kicker {
        margin-bottom: 0.3rem;
        color: var(--gold);
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    div.stButton > button[kind="primary"] {
        min-height: 46px;
        border: 0;
        border-radius: 10px;
        background: var(--navy);
        font-weight: 700;
        box-shadow: 0 7px 16px rgba(11,31,51,0.16);
    }

    div.stButton > button[kind="primary"]:hover {
        border: 0;
        background: var(--navy-2);
    }

    .footer-note {
        padding-top: 2rem;
        color: #8593a2;
        font-size: 0.75rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-lockup">
            <div class="brand-mark">ZH</div>
            <div class="brand-name">ZIAD-HAMED</div>
            <div class="brand-subtitle">Financial Controlling &amp;<br>Regulatory Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Workspace")
    top_k = st.slider(
        "Retrieved evidence depth",
        min_value=1,
        max_value=8,
        value=3,
        help="Number of reranked child chunks used to ground the answer.",
    )

    if st.button("Run document ingestion", use_container_width=True):
        with st.spinner("Rebuilding the regulatory knowledge index…"):
            try:
                run_ingestion_pipeline()
                st.success("Knowledge index updated.")
            except Exception as exc:
                st.error(f"Ingestion failed: {exc}")

    st.markdown("---")
    st.markdown("### Curated prompts")
    sample_queries = [
        "What is the mandatory timeline for Form 8-K disclosure under SEC Item 1.05 for material cybersecurity incidents?",
        "What are the differences between Scope 1, Scope 2, and Scope 3 emissions under IFRS S2 in 2026?",
        "What are the eligibility criteria and turnover thresholds for EU CSRD Wave 2 compliance in 2026?",
        "What is the Basel III Endgame capital output floor percentage for risk-weighted assets?",
        "What confidence level is required for Expected Shortfall under the FRTB market risk framework?",
    ]
    selected_sample = st.selectbox(
        "Start with a standard query",
        ["Select a prompt…"] + sample_queries,
        label_visibility="collapsed",
    )

    st.markdown(
        "<div style='color:#9eb1c4;font-size:.74rem;line-height:1.5;margin-top:1rem;'>"
        "Designed for evidence-led financial, accounting and regulatory analysis."
        "</div>",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Pipeline
# -----------------------------------------------------------------------------
@st.cache_resource
def get_pipeline():
    return FinConRAGPipeline()


pipeline = get_pipeline()

# -----------------------------------------------------------------------------
# Main workspace
# -----------------------------------------------------------------------------
st.markdown('<div class="eyebrow">Ziad-Hamed Intelligence Workspace</div>', unsafe_allow_html=True)
hero_col, status_col = st.columns([5, 1.35], vertical_alignment="bottom")
with hero_col:
    st.markdown('<h1 class="hero-title">Turn complex regulation<br>into confident decisions.</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-copy">A grounded research assistant for financial controlling, accounting standards and regulatory interpretation — built to show the evidence behind every synthesis.</p>',
        unsafe_allow_html=True,
    )
with status_col:
    st.markdown('<div class="status-pill"><span class="status-dot"></span>System ready</div>', unsafe_allow_html=True)

st.markdown('<div class="section-label">Ask the intelligence layer</div>', unsafe_allow_html=True)
st.markdown('<div class="query-shell">', unsafe_allow_html=True)
query_default = "" if selected_sample == "Select a prompt…" else selected_sample
user_query = st.text_area(
    "Financial or regulatory question",
    value=query_default,
    height=92,
    placeholder="e.g. What disclosure timeline applies to a material cybersecurity incident under SEC Item 1.05?",
    label_visibility="collapsed",
)
search_col, hint_col = st.columns([1.1, 4], vertical_alignment="center")
with search_col:
    run_search = st.button("Search & analyze", type="primary", use_container_width=True)
with hint_col:
    st.caption("Hybrid retrieval  ·  Cross-encoder reranking  ·  Citation-aware synthesis")
st.markdown('</div>', unsafe_allow_html=True)

if run_search:
    if not user_query.strip():
        st.warning("Enter a question or choose a curated prompt to begin.")
    else:
        with st.spinner("Retrieving evidence and preparing a grounded synthesis…"):
            try:
                result = pipeline.run(query=user_query.strip(), top_k_rerank=top_k)
            except Exception as exc:
                st.error(f"Unable to complete the analysis: {exc}")
                st.stop()

        sources = result.get("sources", []) or []
        chunks = result.get("retrieved_child_chunks", []) or []
        entities = result.get("entities", []) or []

        st.markdown('<div class="section-label">Executive synthesis</div>', unsafe_allow_html=True)
        st.markdown('<div class="answer-card">', unsafe_allow_html=True)
        st.markdown(result.get("answer", "No answer was returned."))
        st.markdown('</div>', unsafe_allow_html=True)

        metric_cols = st.columns(4)
        metrics = [
            (str(len(sources)), "Source documents"),
            (str(len(chunks)), "Evidence chunks"),
            (str(len(entities)), "Recognized entities"),
            (str(top_k), "Rerank depth"),
        ]
        for col, (value, label) in zip(metric_cols, metrics):
            with col:
                st.markdown(
                    f'<div class="metric-card"><div class="metric-value">{value}</div><div class="metric-label">{label}</div></div>',
                    unsafe_allow_html=True,
                )

        if entities:
            st.markdown('<div class="section-label">Key entities detected</div>', unsafe_allow_html=True)
            entity_text = "  ".join(f"`{entity.get('text', '')}` · {entity.get('label', 'ENTITY')}" for entity in entities)
            st.markdown(entity_text)

        expanded_query = result.get("expanded_query")
        if expanded_query and expanded_query != user_query.strip():
            with st.expander("View query expansion"):
                st.caption("The retrieval layer enriched the original query with related terminology.")
                st.code(expanded_query, language="text")

        st.markdown('<div class="section-label">Evidence base</div>', unsafe_allow_html=True)
        if sources:
            source_cols = st.columns(min(len(sources), 3))
            for index, source in enumerate(sources):
                with source_cols[index % len(source_cols)]:
                    st.markdown(
                        f'<div class="source-card"><div class="source-kicker">Source {index + 1:02d}</div>{source}</div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No source attributions were returned for this analysis.")

        with st.expander("Technical transparency · retrieved chunks and reranker scores"):
            if not chunks:
                st.caption("No retrieved child chunks were returned.")
            for index, chunk in enumerate(chunks, start=1):
                st.markdown(f"**Rank {index} · `{chunk.get('id', 'unknown')}`**")
                score_col, rrf_col, parent_col = st.columns(3)
                score_col.metric("Cross-encoder score", f"{chunk.get('rerank_score', 0.0):.4f}")
                rrf_col.metric("RRF score", f"{chunk.get('rrf_score', 0.0):.4f}")
                parent_col.caption(f"Parent ID: `{chunk.get('parent_id', '—')}`")
                st.text_area(
                    f"Retrieved evidence {index}",
                    chunk.get("text", ""),
                    height=120,
                    key=f"child_{index}",
                    label_visibility="collapsed",
                )
                st.caption(f"Metadata: {chunk.get('metadata', {})}")
                if index != len(chunks):
                    st.divider()

        with st.expander("Full parent context sent to the language model"):
            st.code(result.get("context_used", ""), language="markdown")

st.markdown(
    '<div class="footer-note">Ziad-Hamed Financial Regulatory Intelligence · Evidence before interpretation</div>',
    unsafe_allow_html=True,
)
