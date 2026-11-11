import streamlit as st
import sys
from pathlib import Path
import markdown  # ضروري لتحويل الـ Markdown إلى HTML داخل الـ div المخصص

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.generation.chain import FinConRAGPipeline
from src.ingestion.run_ingestion import run_ingestion_pipeline

# ------------------------------------------------------
# 1. Page Configuration & Executive Styling
# ------------------------------------------------------
st.set_page_config(
    page_title="FinCon Executive Intelligence",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a professional, minimalist executive dashboard
st.markdown("""
    <style>
    /* إخفاء عناصر واجهة Streamlit الافتراضية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* تحسين خطوط العناوين */
    h1, h2, h3 {
        font-family: 'Inter', 'Helvetica Neue', sans-serif;
        color: #0F172A;
    }
    
    /* تصميم الـ Executive Summary المخصص */
    .executive-summary {
        background-color: #F8FAFC;
        border-left: 4px solid #0284C7;
        padding: 1.5rem;
        border-radius: 0.25rem;
        font-size: 1.05rem;
        line-height: 1.6;
        color: #1E293B;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    /* تنسيق الكلمات الدلالية (Entities) */
    .entity-tag {
        display: inline-block;
        background: #F1F5F9;
        color: #334155;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
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
# 3. Sidebar: System Administration (Hidden by default)
# ------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ System Administration")
    
    with st.expander("🗄️ Database Management"):
        st.caption("Sync latest IFRS/GAAP documents to the knowledge base.")
        if st.button("🔄 Sync Documents", use_container_width=True):
            with st.spinner("Rebuilding Hybrid Indexes..."):
                try:
                    run_ingestion_pipeline()
                    st.success("Knowledge base updated successfully.")
                except Exception as e:
                    st.error(f"Ingestion failed: {e}")
                
    with st.expander("🎛️ Retrieval Tuning"):
        top_k = st.slider("Cross-Encoder Top-K", min_value=1, max_value=8, value=3, 
                          help="Number of chunks to retrieve and analyze.")

# ------------------------------------------------------
# 4. Main Executive Interface
# ------------------------------------------------------
st.title("💼 Financial Compliance Intelligence")
st.markdown("Ask questions across corporate policies, IFRS, and GAAP standards.")

# Quick-action query pills
st.markdown("**📌 Common Regulatory Inquiries:**")
col1, col2, col3 = st.columns(3)
col1.button("IFRS S2 Emissions 2026", on_click=set_query, args=("What are the differences between Scope 1, Scope 2, and Scope 3 emissions under IFRS S2 in 2026?",), use_container_width=True)
col2.button("CSRD Wave 2 Thresholds", on_click=set_query, args=("What are the eligibility criteria and turnover thresholds for EU CSRD Wave 2 compliance in 2026?",), use_container_width=True)
col3.button("SEC 8-K Cyber Timeline", on_click=set_query, args=("What is the mandatory timeline for Form 8-K disclosure under SEC Item 1.05 for material cybersecurity incidents?",), use_container_width=True)

st.write("") # Spacer

# Search Bar Area
user_query = st.text_input("Analysis Request:", value=st.session_state.query_input, placeholder="e.g., What is the Basel III Endgame capital output floor?")

if st.button("🔍 Generate Briefing", type="primary"):
    if not user_query.strip():
        st.warning("⚠️ Please enter a query.")
    else:
        with st.spinner("Analyzing regulatory frameworks and synthesizing response..."):
            # Execute the RAG Pipeline
            result = pipeline.run(query=user_query, top_k_rerank=top_k if 'top_k' in locals() else 3)
            
            st.divider()
            
            # --- 1. Executive Summary ---
            st.markdown("### 📑 Executive Briefing")
            
            # تحويل الماركداون لـ HTML عشان التنسيقات (مثل الخط العريض) تشتغل جوة الـ div المخصص
            html_answer = markdown.markdown(result['answer'], extensions=['extra'])
            st.markdown(f"<div class='executive-summary'>{html_answer}</div>", unsafe_allow_html=True)
            
            st.write("")
            
            # --- 2. Key Concepts (Entities) ---
            entities = result.get("entities", [])
            if entities:
                st.markdown("#### 🏷️ Key Financial Terminology")
                tags_html = "".join([f"<span class='entity-tag'>{e['text']}</span>" for e in entities])
                st.markdown(tags_html, unsafe_allow_html=True)
                
            st.write("")

            # --- 3. Referenced Standards (Sources) ---
            st.markdown("#### 📚 Referenced Standards")
            sources = result.get("sources", [])
            if sources:
                for src in sources:
                    st.info(f"**Source Document:** {src}", icon="📄")
            else:
                st.warning("No specific regulatory documents cited for this query.")

            # --- 4. Technical Audit Trail ---
            st.write("")
            with st.expander("🔍 View Technical Audit Trail (Context & Ranking)"):
                st.caption("Detailed retrieval metadata for compliance auditing.")
                
                if result.get("expanded_query") and result.get("expanded_query") != user_query:
                    st.markdown(f"**Expanded Query:** `{result['expanded_query']}`")
                
                st.markdown("**Retrieved Regulatory Context:**")
                st.code(result.get("context_used", "No context retrieved."), language="markdown")
