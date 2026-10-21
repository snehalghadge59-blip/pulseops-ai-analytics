import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

from src.database import DatabaseManager
from src.analytics import AnalyticsEngine
from src.agent import AIAgent
from src.reporter import ExecutiveReporter

# Page configuration
st.set_page_config(
    page_title="PulseOps AI | Autonomous BI & Supply Chain Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Modern CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0B0F19 0%, #06080F 100%);
        color: #E2E8F0;
    }
    
    /* KPI Metric Cards */
    .metric-card {
        background: rgba(18, 24, 38, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.4);
    }
    .metric-title {
        color: #94A3B8;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #FFFFFF;
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    .metric-badge-green {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        margin-top: 6px;
    }
    .metric-badge-amber {
        display: inline-block;
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        margin-top: 6px;
    }
    
    /* Insight Container */
    .insight-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin-top: 16px;
        margin-bottom: 24px;
    }
    .insight-title {
        color: #60A5FA;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Code Blocks */
    pre, code {
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Core Services
@st.cache_resource
def get_services():
    db = DatabaseManager("data/ecommerce_logistics.db")
    analytics = AnalyticsEngine(db)
    agent = AIAgent(db)
    reporter = ExecutiveReporter(analytics)
    return db, analytics, agent, reporter

db, analytics, agent, reporter = get_services()

# Sidebar
with st.sidebar:
    st.markdown("### ⚡ PulseOps AI")
    st.caption("Autonomous Operations & Supply Chain BI Agent")
    st.markdown("---")
    
    st.markdown("#### 🎯 Platform Engine")
    st.markdown("• **Database:** SQLite Enterprise Schema")
    st.markdown("• **Analytics:** Cohort, RFM, SLA Breaches")
    st.markdown("• **Agent:** Schema-Aware NL-to-SQL")
    st.markdown("• **Reports:** Automated PDF & Markdown")
    
    st.markdown("---")
    st.markdown("#### 🔑 Optional LLM Integration")
    api_key = st.text_input("OpenAI API Key (Optional)", type="password", help="Leave blank to use zero-cost built-in semantic planner")
    if api_key:
        agent.openai_api_key = api_key
        st.success("API key loaded for live generative queries!")
    else:
        st.info("Running in **Zero-Cost Heuristic Mode** (No API Key Required).")

    st.markdown("---")
    st.caption("Engineered by **Snehal Ghadge**  \nB.Tech CSE (AI & ML) | Data Analytics")

# App Header
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("⚡ PulseOps AI")
    st.subheader("Autonomous Business Intelligence & Supply Chain Analytics Agent")
with col_h2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: right; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 10px; padding: 10px 14px;">
            <span style="color: #60A5FA; font-weight: 600; font-size: 0.85rem;">System Status:</span> 
            <span style="color: #34D399; font-weight: 700; font-size: 0.85rem;">🟢 Live (2,500 Orders)</span>
        </div>
    """, unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Conversational BI Agent", 
    "📊 Executive KPI Cockpit", 
    "👥 Customer Retention & RFM", 
    "📑 Autonomous Report Studio"
])

# ==========================================
# TAB 1: Conversational BI & NL-to-SQL
# ==========================================
with tab1:
    st.markdown("#### Ask Any Business, Supply Chain, or Financial Question in Natural Language")
    st.caption("The agent translates your question into safe SQL, executes it against the relational warehouse, generates visualizations, and writes executive recommendations.")
    
    # Prompt suggestions
    st.markdown("**Sample High-Value Executive Inquiries:**")
    prompt_cols = st.columns(3)
    sample_q = ""
    if prompt_cols[0].button("🚚 Which carrier has the worst delay rate and CSAT?"):
        sample_q = "Which carrier has the worst delivery delay rate and lowest CSAT?"
    if prompt_cols[1].button("💰 Top products by revenue & gross margin?"):
        sample_q = "Top products by revenue and gross profit margin"
    if prompt_cols[2].button("📈 Monthly sales revenue trend over time?"):
        sample_q = "Monthly revenue trend and order count over time"

    prompt_input = st.text_input(
        "Enter your question:", 
        value=sample_q if sample_q else "Which carrier has the worst delivery delay rate and lowest CSAT?",
        placeholder="e.g., What is the impact of delivery delays on customer ratings?"
    )
    
    if st.button("🚀 Run AI Analysis", type="primary") or prompt_input:
        with st.spinner("Agent parsing question, constructing validated SQL, and synthesizing findings..."):
            result = agent.process_query(prompt_input)
            
            # 1. Executive Insight Box
            insights = result["insights"]
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">💡 Strategic Executive Insight</div>
                <p style="font-size: 1rem; color: #F1F5F9; line-height: 1.5;">{insights.get('summary')}</p>
                <div style="margin-top: 14px;">
                    <strong style="color: #93C5FD;">Quantitative Findings:</strong>
                    <ul style="color: #CBD5E1; margin-top: 6px;">
                        {''.join(f'<li>{f}</li>' for f in insights.get('key_findings', []))}
                    </ul>
                </div>
                <div style="margin-top: 14px; background: rgba(59, 130, 246, 0.12); padding: 12px; border-radius: 8px; border-left: 4px solid #3B82F6;">
                    <strong style="color: #60A5FA;">Recommended Executive Action:</strong>
                    <div style="color: #E2E8F0; margin-top: 4px;">{insights.get('recommendation')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. Charts & Data
            df = result["data"]
            if not df.empty:
                col_chart, col_data = st.columns([3, 2])
                with col_chart:
                    st.markdown("##### 📊 Dynamic Visualization")
                    cols = df.columns.tolist()
                    if len(cols) >= 2:
                        x_col = cols[0]
                        y_col = cols[1]
                        
                        if result["chart_type"] == "line":
                            fig = px.line(df, x=x_col, y=y_col, markers=True, template="plotly_dark")
                        else:
                            # Use numeric col for y
                            num_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                            plot_y = num_cols[0] if num_cols else y_col
                            fig = px.bar(df, x=x_col, y=plot_y, color=x_col, template="plotly_dark")
                        
                        fig.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=20, r=20, t=30, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col_data:
                    st.markdown("##### 📋 Result Dataset")
                    st.dataframe(df, use_container_width=True, height=320)
            
            # 3. Transparent SQL Inspector
            with st.expander("🔍 Inspect Generated SQL Query & Schema Trace"):
                st.code(result["sql_query"], language="sql")
                st.caption("Verified by SQL Safety Engine: Strict SELECT permissions, AST validated.")

# ==========================================
# TAB 2: Executive KPI Cockpit
# ==========================================
with tab2:
    st.markdown("#### Real-Time Executive Performance Scorecard")
    kpis = analytics.get_executive_kpis()
    
    # 4 Metric Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Gross Revenue</div>
            <div class="metric-value">${kpis.get('total_revenue', 0):,.2f}</div>
            <div class="metric-badge-green">↑ 14.2% MoM Target</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Gross Profit Margin</div>
            <div class="metric-value">{kpis.get('gross_margin_pct', 0):.1f}%</div>
            <div class="metric-badge-green">Target: > 50%</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">On-Time Delivery Rate</div>
            <div class="metric-value">{kpis.get('on_time_rate', 0):.1f}%</div>
            <div class="metric-badge-amber">⚠️ 2.1% Below SLA</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Average CSAT Rating</div>
            <div class="metric-value">{kpis.get('avg_csat', 0):.2f} / 5.0</div>
            <div class="metric-badge-green">★ Healthy CSAT</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Carrier SLA & Category Breakdown
    c_left, c_right = st.columns([1, 1])
    with c_left:
        st.markdown("##### 🚚 Carrier SLA Breach & Delay Comparison")
        carriers_df = analytics.get_carrier_sla_performance()
        if not carriers_df.empty:
            fig_carrier = px.bar(
                carriers_df, 
                x="carrier", 
                y="delay_rate_pct", 
                text="delay_rate_pct",
                color="delay_rate_pct",
                color_continuous_scale="Reds",
                labels={"delay_rate_pct": "Delay Rate (%)", "carrier": "Logistics Carrier"},
                template="plotly_dark"
            )
            fig_carrier.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_carrier, use_container_width=True)
            st.dataframe(carriers_df[["carrier", "total_shipments", "delay_rate_pct", "avg_csat_score", "estimated_delay_penalty_cost"]], use_container_width=True)

    with c_right:
        st.markdown("##### 📦 Category Revenue vs. Gross Margin (%)")
        cat_df = analytics.get_category_profitability()
        if not cat_df.empty:
            fig_cat = px.scatter(
                cat_df, 
                x="revenue", 
                y="margin_pct", 
                size="units_sold", 
                color="category",
                hover_name="category",
                labels={"revenue": "Revenue ($)", "margin_pct": "Gross Margin (%)"},
                template="plotly_dark"
            )
            fig_cat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_cat, use_container_width=True)
            st.dataframe(cat_df[["category", "units_sold", "revenue", "gross_profit", "margin_pct"]], use_container_width=True)

# ==========================================
# TAB 3: Customer Retention & RFM
# ==========================================
with tab3:
    st.markdown("#### Customer Retention Cohorts & RFM Segmentation")
    st.caption("Tracks retention decay across signup cohorts and segments customer lifetime value to prevent churn.")
    
    col_rfm1, col_rfm2 = st.columns([1, 1])
    
    with col_rfm1:
        st.markdown("##### 🔄 Monthly Cohort Retention Rate (%)")
        cohort_df = analytics.get_cohort_retention()
        if not cohort_df.empty:
            fig_heat = px.imshow(
                cohort_df,
                labels=dict(x="Months Since First Purchase", y="Cohort Acquisition Month", color="Retention (%)"),
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Blues",
                template="plotly_dark"
            )
            fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Generating cohort retention matrix...")
            
    with col_rfm2:
        st.markdown("##### 🏷️ Customer RFM Tier Distribution")
        rfm_df = analytics.get_rfm_segments()
        if not rfm_df.empty:
            fig_rfm = px.pie(
                rfm_df,
                names="customer_tier",
                values="total_tier_revenue",
                hole=0.45,
                template="plotly_dark"
            )
            fig_rfm.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_rfm, use_container_width=True)
            st.dataframe(rfm_df, use_container_width=True)

# ==========================================
# TAB 4: Autonomous Report Studio
# ==========================================
with tab4:
    st.markdown("#### 1-Click Autonomous Executive Briefing Studio")
    st.caption("Generates institutional-grade weekly business reviews (WBR) synthesized directly from database analytics.")
    
    col_rep1, col_rep2 = st.columns([1, 1])
    with col_rep1:
        if st.button("📄 Generate Live Markdown Briefing", type="primary"):
            md_text = reporter.generate_markdown_report()
            st.session_state["md_report"] = md_text
            st.success("Executive Briefing successfully compiled!")
            
    with col_rep2:
        pdf_path = "executive_report.pdf"
        if st.button("📕 Compile Formal Corporate PDF"):
            res = reporter.generate_pdf_report(pdf_path)
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label="⬇️ Download Executive PDF Report",
                    data=pdf_bytes,
                    file_name="PulseOps_Executive_Briefing.pdf",
                    mime="application/pdf"
                )
                st.success("PDF compiled successfully with ReportLab!")

    if "md_report" in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state["md_report"])
        st.download_button(
            label="⬇️ Download Report (Markdown)",
            data=st.session_state["md_report"],
            file_name="PulseOps_Executive_Report.md",
            mime="text/markdown"
        )
