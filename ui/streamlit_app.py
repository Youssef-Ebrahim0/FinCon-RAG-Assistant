import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.generation.chain import FinConRAGPipeline
from src.ingestion.run_ingestion import run_ingestion_pipeline

# ------------------------------------------------------
# 1. Page Configuration & Executive Styling
# ------------------------------------------------------
st.set_page_config(
    page_title="FinCon Executive Intelligence",
    page_icon="📊",
    layout="centered", # Centered layout is often easier for reading high-level text
    initial_sidebar_state="collapsed" # Hide sidebar by default for a cleaner interface
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Clean, minimalist typography */
    h1, h2, h3 {
        font-family: 'Inter', 'Helvetica Neue', sans-serif;
        color: #0F172A;
    }
    
    /* Subtle answer box styling */
    .executive-summary {
        background-color: #F8FAFC;
        border-left: 4px solid #0284C7;
        padding: 1.5rem;
        border-radius: 0.25rem;
        font-size: 1.05rem;
        line-height: 1.6;
        color: #334155;
    }

    /* Entity Tags */
    .entity-tag {
        display: inline-block;
        background: #F1F5F9;
        color: #475569;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 8px;
        margin-bottom: 8px;
        border: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------
# 2. State & Pipeline Initialization
# ------------------------------------------------------
@st.cache_resource
def get_pipeline():
    return FinConRAGPipeline()

pipeline = get_pipeline()

if "query_input" not in st.session_state:
    st.session_state.query_input = ""

def set_query(q):
    st.session_state.query_input = q

# ------------------------------------------------------
# 3. Sidebar: Admin & Advanced Options (Hidden by default)
# ------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ System Administration")
    
    with st.expander("Database Management"):
        st.markdown("Sync latest IFRS/GAAP documents to the knowledge base.")
        if st.button("Sync Documents", use_container_width=True):
            with st.spinner("Updating knowledge base..."):
                run_ingestion_pipeline()
                st.success("Knowledge base updated.")
                
    with st.expander("Retrieval Tuning"):
        top_k = st.slider("Source Depth", min_value=1, max_value=8, value=3)

# ------------------------------------------------------
# 4. Main Executive Interface
# ------------------------------------------------------
st.title("Financial Compliance Intelligence")
st.markdown("Ask questions across corporate policies, IFRS, and GAAP standards.")

# Quick-action query pills
st.markdown("**Common Inquiries:**")
col1, col2, col3 = st.columns(3)
col1.button("IFRS S2 Emissions 2026", on_click=set_query, args=("What are the differences between Scope 1, Scope 2, and Scope 3 emissions under IFRS S2 in 2026?",), use_container_width=True)
col2.button("CSRD Wave 2 Thresholds", on_click=set_query, args=("What are the eligibility criteria and turnover thresholds for EU CSRD Wave 2 compliance in 2026?",), use_container_width=True)
col3.button("SEC 8-K Cyber Timeline", on_click=set_query, args=("What is the mandatory timeline for Form 8-K disclosure under SEC Item 1.05 for material cybersecurity incidents?",), use_container_width=True)

st.write("") # Spacer

# Search Bar
user_query = st.text_input("Analysis Request:", value=st.session_state.query_input, placeholder="Enter a regulatory or financial controlling query...")

if st.button("Generate Briefing", type="primary"):
    if not user_query:
        st.warning("Please enter a query.")
    else:
        with st.spinner("Analyzing regulatory frameworks..."):
            # Execute Pipeline
            result = pipeline.run(query=user_query, top_k_rerank=top_k if 'top_k' in locals() else 3)
            
            # --- HIGH LEVEL OUTPUT ---
            
            # 1. Executive Summary
            st.markdown("### 📑 Executive Briefing")
            st.markdown(f"<div class='executive-summary'>{result['answer']}</div>", unsafe_allow_html=True)
            
            st.write("")
            
            # 2. Key Concepts (Entities)
            entities = result.get("entities", [])
            if entities:
                st.markdown("#### Key Financial Terminology")
                tags_html = "".join([f"<span class='entity-tag'>{e['text']}</span>" for e in entities])
                st.markdown(tags_html, unsafe_allow_html=True)
                
            st.write("")

            # 3. Referenced Standards (Sources)
            st.markdown("#### 📚 Referenced Standards")
            sources = result.get("sources", [])
            if sources:
                for src in sources:
                    st.markdown(f"- {src}")
            else:
                st.markdown("- *No specific regulatory documents cited.*")

            # 4. Audit Trail (Collapsed by default for non-technical users)
            st.write("")
            with st.expander("🔍 View Technical Audit Trail (Context & Ranking)"):
                st.caption("This section contains the exact document chunks and retrieval scores used by the AI.")
                
                if result.get("expanded_query") and result.get("expanded_query") != user_query:
                    st.markdown(f"**Expanded Query:** `{result['expanded_query']}`")
                    
                st.markdown("**Retrieved Regulatory Context:**")
                st.code(result.get("context_used", ""), language="markdown")
