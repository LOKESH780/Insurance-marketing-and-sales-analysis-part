# app.py - Streamlit Dashboard for Retention Analysis
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from login import login

st.set_page_config(page_title="Retention Analysis Dashboard", layout="wide")

# === Login ===
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if not st.session_state.logged_in:
    login()
    st.stop()

# === Title and Logout ===
col1, col2 = st.columns([9, 1])
with col1:
    st.markdown("""
        <h1 style='text-align: left; color: #ffffff;'>📊 Retention Analysis Dashboard</h1>
        <hr style='border: 1px solid #666;' />
    """, unsafe_allow_html=True)
with col2:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Load Data
df = pd.read_csv("finalapi.csv")

# === Sidebar Filters ===
st.sidebar.header("📌 Filter Data")
year_options = sorted(df['AGENCY_APPOINTMENT_YEAR'].dropna().unique())
selected_year = st.sidebar.selectbox("Select Appointment Year (optional)", options=['All'] + list(year_options))

prod_line_options = sorted(df['PROD_LINE'].dropna().unique()) if 'PROD_LINE' in df.columns else []
selected_prod_line = st.sidebar.selectbox("Select Product Line (optional)", options=['All'] + prod_line_options) if prod_line_options else 'All'

# === Apply Filters ===
filtered_df = df.copy()
if selected_year != 'All':
    filtered_df = filtered_df[filtered_df['AGENCY_APPOINTMENT_YEAR'] == selected_year]
if selected_prod_line != 'All':
    filtered_df = filtered_df[filtered_df['PROD_LINE'] == selected_prod_line]

# Tabs
tabs = st.tabs([
    "KPI Overview",
    "Retention Distribution",
    "Loss & Growth Trends",
    "Correlation Analysis",
    "Retention Segments",
    "Premium Breakdown",
    "Agency Contribution",
    "Growth vs Premium"
])

# --- Tab 1: KPI Overview ---
with tabs[0]:
    st.header("📌 KPI Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Retention Ratio", f"{filtered_df['RETENTION_RATIO'].mean():.2f}")
    with col2:
        st.metric("Average Loss Ratio", f"{filtered_df['LOSS_RATIO'].mean():.2f}")
    with col3:
        st.metric("Avg Growth Rate (3Y)", f"{filtered_df['GROWTH_RATE_3YR'].mean():.2f}")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Policies In Force", f"{filtered_df['POLY_INFORCE_QTY'].sum():,.0f}")
    with col5:
        st.metric("Active Producers", f"{filtered_df['ACTIVE_PRODUCERS'].sum()}")
    with col6:
        st.metric("NB Premium Amt", f"${filtered_df['NB_WRTN_PREM_AMT'].sum():,.0f}")

# --- Tab 2: Retention Distribution ---
with tabs[1]:
    st.header("📈 Retention Ratio Trends")
    line_df = filtered_df.groupby("AGENCY_APPOINTMENT_YEAR")["RETENTION_RATIO"].mean().reset_index()
    fig_line = px.line(line_df, x="AGENCY_APPOINTMENT_YEAR", y="RETENTION_RATIO", markers=True,
                       text="RETENTION_RATIO", title="Average Retention Ratio per Year")
    fig_line.update_traces(textposition="top center")
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Bar Chart: Avg Retention Ratio by Product Line")
    if 'PROD_LINE' in filtered_df.columns:
        bar_df = filtered_df.groupby("PROD_LINE")["RETENTION_RATIO"].mean().reset_index()
        fig_bar_ret = px.bar(bar_df, x="PROD_LINE", y="RETENTION_RATIO", text_auto=True,
                             title="Average Retention Ratio by Product Line")
        st.plotly_chart(fig_bar_ret, use_container_width=True)

    st.subheader("Histogram: Retention Ratio Distribution")
    fig_hist = px.histogram(filtered_df, x="RETENTION_RATIO", nbins=30, title="Distribution of Retention Ratios")
    st.plotly_chart(fig_hist, use_container_width=True)

# --- Tab 3: Loss & Growth Trends ---
with tabs[2]:
    st.header("📉 Loss Ratio & Growth Insights")
    st.subheader("Grouped Bar Chart: Loss Ratio vs Retention")
    filtered_df['LOSS_BIN'] = pd.cut(filtered_df['LOSS_RATIO'], bins=5)
    loss_group = filtered_df.groupby("LOSS_BIN")["RETENTION_RATIO"].mean().reset_index()
    loss_group["LOSS_BIN"] = loss_group["LOSS_BIN"].astype(str)  # 🔧 Fix serialization issue
    fig_bar_loss = px.bar(loss_group, x="LOSS_BIN", y="RETENTION_RATIO", text_auto=True,
                          title="Avg Retention Ratio for Loss Ratio Bins")
    st.plotly_chart(fig_bar_loss, use_container_width=True)

    st.subheader("Line Chart: Avg Growth Rate Over Time")
    growth_df = filtered_df.groupby("AGENCY_APPOINTMENT_YEAR")["GROWTH_RATE_3YR"].mean().reset_index()
    fig_growth = px.line(growth_df, x="AGENCY_APPOINTMENT_YEAR", y="GROWTH_RATE_3YR",
                         title="Avg 3-Year Growth Rate Over Time", markers=True)
    st.plotly_chart(fig_growth, use_container_width=True)

    st.subheader("Bar Chart: Loss Ratio by Product Line")
    loss_df = filtered_df.groupby("PROD_LINE")["LOSS_RATIO"].mean().reset_index()
    fig_loss_bar = px.bar(loss_df, x="PROD_LINE", y="LOSS_RATIO", title="Average Loss Ratio by Product Line", text_auto=True)
    st.plotly_chart(fig_loss_bar, use_container_width=True)

# --- Tab 8: Growth vs Premium ---
with tabs[7]:
    st.header("📊 Growth vs Premium Relationship")
    filtered_df['GROWTH_BIN'] = pd.cut(filtered_df['GROWTH_RATE_3YR'], bins=5)
    growth_prem = filtered_df.groupby("GROWTH_BIN")["WRTN_PREM_AMT"].mean().reset_index()
    growth_prem["GROWTH_BIN"] = growth_prem["GROWTH_BIN"].astype(str)  # 🔧 Fix serialization issue
    fig_grouped = px.bar(growth_prem, x="GROWTH_BIN", y="WRTN_PREM_AMT",
                         title="Avg Premium by Growth Rate Bin", text_auto=True)
    st.plotly_chart(fig_grouped, use_container_width=True)
