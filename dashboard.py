import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. Simple Security ---
# In a real app, use streamlit-authenticator for more robust security.
# For a quick local-to-ngrok setup, we can use a simple password check.
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == "admin123": # Change this!
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.sidebar.text_input("Admin Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.sidebar.text_input("Admin Password", type="password", on_change=password_entered, key="password")
        st.sidebar.error("😕 Password incorrect")
        return False
    else:
        return True

if check_password():
    st.set_page_config(page_title="AMPLIFY Admin", layout="wide")
    st.title("📊 AMPLIFY Analytics Dashboard")

    # --- 2. Load Data ---
    csv_file = 'amplify_chat_history.csv'
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # --- 3. Key Metrics ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Queries", len(df))
        col2.metric("Avg Latency", f"{df['latency_sec'].mean():.2f}s")
        col3.metric("Latest Session", df['timestamp'].max().strftime('%Y-%m-%d'))

        # --- 4. Visualizations ---
        st.subheader("Performance Over Time")
        fig_latency = px.line(df, x='timestamp', y='latency_sec', title="Inference Latency (Seconds)")
        st.plotly_chart(fig_latency, use_container_width=True)

        st.subheader("Recent Chat Logs")
        st.dataframe(df.sort_values(by='timestamp', ascending=False), use_container_width=True)
    else:
        st.warning("No data found yet. Start chatting with AMPLIFY to generate logs!")