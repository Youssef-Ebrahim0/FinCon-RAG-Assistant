import streamlit as st
import sys
from pathlib import Path
import time

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.generation.chain import FinConRAGPipeline
from src.ingestion.run_ingestion import run_ingestion_pipeline

# ------------------------------------------------------
# 1. Page Configuration & Custom CSS
# ------------------------------------------------------
st.set_page_config(
    page_title="FinCon Intelligence | Enterprise RAG",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS for a cleaner, enterprise SaaS look
st.markdown("""
    <style>
    /* Hide Streamlit default branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Subtle container styling */
    .st-emotion-cache-1znd72v {
        padding: 2rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
    }
    
    /* Professional header typography */
    h1 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #1E3A8A;
        font-weight: 600;
    }
    
    /* Style entity badges */
    .entity-badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        margin: 0.2em;
        font-size: 0.85em;
        font-weight: 600;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.375rem;
        background-color: #E0E7FF;
        color: #3730A3;
        border: 1px solid #C7D2FE;
    }
    </style>
""", unsafe_allow_html=True)


# ------------------------------------------------------
# 2. State Management & Initialization
# ------------------------------------------------------
@st.cache_resource
def get_pipeline():
    return FinConRAGPipeline()

pipeline = get_pipeline()

if "query_input" not in st.session_state:
    st.session_state.query_input = ""

def apply_template(template):
    st.session_state.query_input = template

# ------------------------------------------------------
# 3. Sidebar: Enterprise Controls & Telemetry
# ------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=60) # Placeholder for enterprise logo
    st.title("System Controls")
    
    with st.expander("⚙️ Pipeline Configuration", expanded=True):
        top_k = st.slider("Retrieval Breadth (Top-K)", min_value=1, max_value=8, value=3, 
                          help="Number of chunks returned by the Cross-Encoder after Hybrid Search.")
        
    with st.expander("🗄️ Knowledge Base Management", expanded=False):
        st.markdown("Update vector and sparse indexes with new regulatory documents.")
        if st.button("🔄 Run Document Ingestion", use_container_width=True):
            with st.spinner("Rebuilding Hierarchical Indexes (ChromaDB + BM25)..."):
                try:
                    start_time = time.time()
                    run_ingestion_pipeline()
                    elapsed = time.time() - start_time
                    st.success(f"Index updated successfully in {elapsed:.1f}s")
                except Exception as e:
                    st.error(f"Ingestion Error: {e}")

    st.markdown("---")
    st.markdown("### 📋 2026 Policy Templates")
    templates = [
        "What is the mandatory timeline for Form 8-K disclosure under SEC Item 1.05 for material cybersecurity incidents?",
        "What are the differences between Scope 1, Scope 2, and Scope 3 emissions under IFRS S2 in 2026?",
        "What are the eligibility criteria and turnover thresholds for EU CSRD Wave 2 compliance in 2026?",
        "What is the Basel III Endgame capital output floor percentage for risk-weighted assets?",
        "What confidence level is required for Expected Shortfall under the FRTB market risk framework?"
    ]
    
    for tmpl in templates:
        st.button(tmpl, on_click=apply_template, args=(tmpl,), use_container_width=True, type="secondary")

# ------------------------------------------------------
# 4. Main Application Interface
# ------------------------------------------------------
st.title("Financial Regulatory Intelligence Assistant")
st.markdown("**Hybrid RAG Architecture** • `IFRS` • `ASC GAAP` • `Basel III` • `CSRD`")

# Input Section
with st.container(border=True):
    user_query = st.text_area("Enter Financial or Regulatory Query:", 
                              value=st.session_state.query_input, 
                              height=100, 
                              placeholder="e.g., How does ASC 606 impact revenue recognition for multi-year SaaS contracts?")
    
    col1, col2, col3 = st.columns([1, 1, 6])
    with col1:
        submit_btn = st.button("🔍 Analyze Query", type="primary", use_container_width=True)
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.query_input = ""
            st.rerun()

# Execution Section
if submit_btn:
    if not user_query.strip():
        st.warning("⚠️ Please provide a query to initiate analysis.")
    else:
        with st.spinner("Executing Hierarchical Retrieval & Cross-Encoder Synthesis..."):
            start_time = time.time()
            result = pipeline.run(query=user_query, top_k_rerank=top_k)
            execution_time = time.time() - start_time
            
            # --- TOP LEVEL METRICS ---
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Execution Time", f"{execution_time:.2f}s")
            m2.metric("Sources Retrieved", len(result.get("sources", [])))
            m3.metric("Entities Identified", len(result.get("entities", [])))
            m4.metric("Reranker Top-K", top_k)
            
            # --- TABBED INTERFACE ---
            tab_report, tab_sources, tab_telemetry = st.tabs([
                "📑 Intelligence Synthesis", 
                "📚 Source Attribution", 
                "⚙️ RAG Telemetry & Logs"
            ])
            
            # TAB 1: Main Answer & Entities
            with tab_report:
                if result.get("expanded_query") and result.get("expanded_query") != user_query:
                    st.caption(f"🔄 **Query Expanded (Pre-Retrieval):** {result['expanded_query']}")
                
                with st.container(border=True):
                    st.markdown("### Executive Summary")
                    st.markdown(result["answer"])
                
                entities = result.get("entities", [])
                if entities:
                    st.markdown("#### 🏷️ Financial Entities Recognized")
                    html_badges = "".join([f"<span class='entity-badge'>{e['text']} ({e['label']})</span>" for e in entities])
                    st.markdown(html_badges, unsafe_allow_html=True)

            # TAB 2: Source Citations
            with tab_sources:
                st.markdown("### Grounding Sources")
                sources = result.get("sources", [])
                if sources:
                    for i, src in enumerate(sources):
                        st.info(f"**[{i+1}]** {src}", icon="📄")
                else:
                    st.warning("No specific regulatory sources could be matched to this query.")

            # TAB 3: Pipeline Transparency (Child & Parent Chunks)
            with tab_telemetry:
                st.markdown("### Hierarchical Retrieval Deep Dive")
                
                col_child, col_parent = st.columns(2)
                
                with col_child:
                    st.markdown("#### 🎯 Retrieved Child Chunks (Ranked)")
                    for idx, chunk in enumerate(result.get("retrieved_child_chunks", []), start=1):
                        with st.expander(f"Rank {idx}: Score {chunk.get('rerank_score', 0.0):.4f}"):
                            st.caption(f"**RRF Score:** {chunk.get('rrf_score', 0.0):.4f} | **ID:** `{chunk['id']}`")
                            st.code(chunk["text"], language="markdown")
                            st.caption(f"**Maps to Parent ID:** `{chunk.get('parent_id')}`")
                
                with col_parent:
                    st.markdown("#### 📖 Expanded Parent Context (LLM Input)")
                    with st.expander("View Full Context Payload", expanded=True):
                        st.code(result.get("context_used", "No context generated."), language="markdown")
else:
    # Empty State
    st.info("👋 Welcome to the FinCon Regulatory Assistant. Enter a query above or select a template from the sidebar to begin.")
