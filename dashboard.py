import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="AMPLIFY | Admin Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Professional UI Styling (Dark Mode Compatible) ---
st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background-color: transparent;
    }
    
    /* Card Container Styling */
    div[data-testid="metric-container"] {
        background-color: rgba(120, 120, 120, 0.05);
        border: 1px solid rgba(120, 120, 120, 0.1);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    
    /* Metric Typography */
    div[data-testid="stMetricLabel"] {
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05rem;
        font-size: 0.85rem !important;
        color: var(--text-color);
        opacity: 0.8;
    }

    /* Custom Sidebar Branding */
    .sidebar-brand {
        font-size: 1.5rem;
        font-weight: 900;
        letter-spacing: 4px;
        margin-bottom: 2rem;
        text-align: center;
    }

    /* Chart Containers */
    .chart-container {
        background-color: rgba(120, 120, 120, 0.02);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(120, 120, 120, 0.05);
    }

    /* Hide Streamlit Branding for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. Authentication Logic ---
def check_password():
    """Returns True if the user had the correct password."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        cols = st.columns([1, 2, 1])
        with cols[1]:
            st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
            st.title("⚡ AMPLIFY ADMIN")
            st.markdown("Please enter the administrative credentials to view local AI analytics.")
            
            pwd = st.text_input("Administrator Password", type="password")
            if st.button("Unlock Dashboard", use_container_width=True):
                if pwd == "admin123":  # Change this to your desired password
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("❌ Access Denied: Invalid Password")
        return False
    return True

# --- 4. Main Dashboard Execution ---
if check_password():
    # --- Sidebar Controls ---
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">AMPLIFY</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        st.subheader("🛠️ Operations")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
            
        st.markdown("---")
        st.subheader("📊 Data Export")
        CSV_FILE = 'amplify_chat_history.csv'
        
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'rb') as f:
                st.download_button(
                    label="📥 Download CSV Report",
                    data=f,
                    file_name=f"amplify_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)
        if st.button("🔓 Logout", use_container_width=True):
            st.session_state["password_correct"] = False
            st.rerun()

    # --- Data Loading & Processing ---
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # --- Top Section: Branding & Real-time Clock ---
        st.title("📈 System Analytics")
        st.markdown(f"**Last Sync:** {datetime.now().strftime('%B %d, %Y | %H:%M:%S')}")
        
        st.markdown("<br>", unsafe_allow_html=True)

        # --- Dashboard Metrics Row ---
        m1, m2, m3, m4 = st.columns(4)
        
        total_queries = len(df)
        avg_latency = df['latency_sec'].mean()
        peak_latency = df['latency_sec'].max()
        uptime_days = df['timestamp'].dt.date.nunique()
        
        m1.metric("Total Requests", f"{total_queries:,}")
        m2.metric("Avg Latency", f"{avg_latency:.2f}s")
        m3.metric("Peak Delay", f"{peak_latency:.2f}s")
        m4.metric("Active Model", "Nandi-Mini")

        st.markdown("<br>", unsafe_allow_html=True)

        # --- Visualizations Row ---
        c1, c2 = st.columns([2, 1])

        with c1:
            st.subheader("Performance Trend")
            # Uses transparent background to support Dark Mode automatically
            fig = px.area(df, x='timestamp', y='latency_sec', 
                          line_shape='spline',
                          title="Inference Time Over Time")
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis_title=None,
                yaxis_title="Latency (sec)",
                font=dict(color="grey")
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("Hardware Load")
            # Show distribution of latency
            fig_dist = px.histogram(df, x="latency_sec", 
                                   nbins=15, 
                                   title="Response Speed Distribution")
            fig_dist.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis_title="Seconds",
                yaxis_title="Count"
            )
            st.plotly_chart(fig_dist, use_container_width=True)

        # --- Activity Log Table ---
        st.markdown("---")
        st.subheader("📑 Interaction History")
        
        # Professional formatted dataframe
        st.dataframe(
            df.sort_values(by='timestamp', ascending=False),
            use_container_width=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Event Time"),
                "prompt": st.column_config.TextColumn("User Input", width="medium"),
                "response": st.column_config.TextColumn("Model Output", width="large"),
                "latency_sec": st.column_config.ProgressColumn(
                    "Latency", help="Generation time in seconds",
                    format="%.2f", min_value=0, max_value=max(df['latency_sec'])
                ),
                "device": st.column_config.TextColumn("Compute")
            }
        )

    else:
        # State: No Data Found
        st.info("👋 **Welcome to the AMPLIFY Ecosystem!**")
        st.markdown("""
            It looks like `amplify_chat_history.csv` hasn't been created yet. 
            Once you start a conversation in the **AMPLIFY Chat App**, the analytics will automatically populate here.
        """)