# Retention & Policy Performance Dashboard (Streamlit)
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from login import login

st.set_page_config(page_title="Insurance Retention & Performance", layout="wide")

# === Login ===
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if not st.session_state.logged_in:
    login()
    st.stop()

col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# === Title ===
st.title("📊 Insurance Retention & Policy Performance Dashboard")

# Load Data
df = pd.read_csv("finalapi.csv")

# Tabs Setup
tabs = st.tabs(["KPI Overview", "Retention Insights", "Loss & Growth Insights", "Correlation", "Scatter & Segments"])

# --- Tab 1: KPI Overview ---
with tabs[0]:
    st.header("📌 Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg Retention Ratio", f"{df['RETENTION_RATIO'].mean():.2f}")
    with col2:
        st.metric("Avg Loss Ratio", f"{df['LOSS_RATIO'].mean():.2f}")
    with col3:
        st.metric("Avg Growth Rate (3Yr)", f"{df['GROWTH_RATE_3YR'].mean():.2f}")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Total Active Producers", f"{df['ACTIVE_PRODUCERS'].sum()}")
    with col5:
        st.metric("Total Policies In Force", f"{df['POLY_INFORCE_QTY'].sum():,.0f}")
    with col6:
        st.metric("Total NB Premium", f"${df['NB_WRTN_PREM_AMT'].sum():,.0f}")

# --- Tab 2: Retention Distribution ---
with tabs[1]:
    st.header("🔁 Retention Distribution")
    fig_ret_hist = px.histogram(df, x='RETENTION_RATIO', nbins=50, title="Distribution of Retention Ratios")
    st.plotly_chart(fig_ret_hist, use_container_width=True)

    st.subheader("Retention Ratio by Agency Appointment Year")
    fig_line = px.line(df.groupby('AGENCY_APPOINTMENT_YEAR')['RETENTION_RATIO'].mean().reset_index(),
                       x='AGENCY_APPOINTMENT_YEAR', y='RETENTION_RATIO', markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

# --- Tab 3: Loss & Growth Insights ---
with tabs[2]:
    st.header("📉 Loss & Growth Relationship")
    fig_loss = px.histogram(df, x='LOSS_RATIO', nbins=40, title="Loss Ratio Distribution")
    st.plotly_chart(fig_loss, use_container_width=True)

    fig_growth = px.histogram(df, x='GROWTH_RATE_3YR', nbins=40, title="3-Year Growth Rate Distribution")
    st.plotly_chart(fig_growth, use_container_width=True)

    st.subheader("Scatter: Loss Ratio vs Retention Ratio")
    fig_scatter = px.scatter(df, x='LOSS_RATIO', y='RETENTION_RATIO',
                             size='ACTIVE_PRODUCERS', color='GROWTH_RATE_3YR',
                             labels={'LOSS_RATIO': 'Loss Ratio', 'RETENTION_RATIO': 'Retention Ratio'})
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- Tab 4: Correlation ---
with tabs[3]:
    st.header("🧮 Correlation Heatmap")
    numeric_cols = df.select_dtypes(include='number').columns
    corr = df[numeric_cols].corr()
    fig_corr, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', ax=ax)
    st.pyplot(fig_corr)

# --- Tab 5: Categorization & Comparison ---
with tabs[4]:
    st.header("🧩 Categorized Retention Segments")

    def categorize_retention(r):
        if r >= 0.8: return 'High'
        elif r >= 0.5: return 'Medium'
        else: return 'Low'

    df['Retention_Level'] = df['RETENTION_RATIO'].apply(categorize_retention)
    group_df = df.groupby('Retention_Level')[['LOSS_RATIO', 'GROWTH_RATE_3YR', 'ACTIVE_PRODUCERS']].mean().reset_index()

    st.dataframe(group_df)

    fig_bar = px.bar(group_df, x='Retention_Level', y=['LOSS_RATIO', 'GROWTH_RATE_3YR'], barmode='group')
    st.plotly_chart(fig_bar, use_container_width=True)
