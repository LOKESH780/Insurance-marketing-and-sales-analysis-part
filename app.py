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

# === Title ===
st.markdown("""
    <h1 style='text-align: center; color: #ffffff; margin-bottom: 10px;'>📊 Retention Analysis Dashboard</h1>
    <hr style='border: 1px solid #666;' />
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([6, 1, 1])
with col3:
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
tabs = st.tabs(["KPI Overview", "Retention Distribution", "Loss & Growth", "Correlation Analysis", "Retention Segments"])

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
    st.header("📈 Retention Ratio Distribution")
    fig = px.histogram(filtered_df, x="RETENTION_RATIO", nbins=50, title="Distribution of Retention Ratios",
                       text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Retention Ratio by Appointment Year")
    line_df = filtered_df.groupby("AGENCY_APPOINTMENT_YEAR")[["RETENTION_RATIO"]].mean().reset_index()
    fig_line = px.line(line_df, x="AGENCY_APPOINTMENT_YEAR", y="RETENTION_RATIO", markers=True,
                       labels={"AGENCY_APPOINTMENT_YEAR": "Agency Appointment Year", "RETENTION_RATIO": "Retention Ratio"},
                       text="RETENTION_RATIO")
    fig_line.update_traces(textposition="top center")
    st.plotly_chart(fig_line, use_container_width=True)

# --- Tab 3: Loss & Growth ---
with tabs[2]:
    st.header("📉 Loss Ratio and Growth Rate")

    st.subheader("Loss Ratio Distribution")
    fig_loss = px.histogram(filtered_df, x="LOSS_RATIO", nbins=40, title="Distribution of Loss Ratios", text_auto=True)
    st.plotly_chart(fig_loss, use_container_width=True)

    st.subheader("Growth Rate (3Y) Distribution")
    fig_growth = px.histogram(filtered_df, x="GROWTH_RATE_3YR", nbins=40, title="Distribution of 3-Year Growth Rate", text_auto=True)
    st.plotly_chart(fig_growth, use_container_width=True)

    st.subheader("Scatter: Loss Ratio vs Retention Ratio")
    fig_scatter = px.scatter(filtered_df, x="LOSS_RATIO", y="RETENTION_RATIO", color="GROWTH_RATE_3YR",
                             size="ACTIVE_PRODUCERS", hover_data=['AGENCY_APPOINTMENT_YEAR'],
                             title="Loss Ratio vs Retention Ratio",
                             labels={"LOSS_RATIO": "Loss Ratio", "RETENTION_RATIO": "Retention Ratio"})
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- Tab 4: Correlation ---
with tabs[3]:
    st.header("🔍 Correlation Matrix of Key Features")
    selected_cols = [
        'AGENCY_APPOINTMENT_YEAR', 'WRTN_PREM_AMT', 'NB_WRTN_PREM_AMT',
        'POLY_INFORCE_QTY', 'PREV_POLY_INFORCE_QTY', 'LOSS_RATIO',
        'GROWTH_RATE_3YR', 'ACTIVE_PRODUCERS', 'RETENTION_RATIO']
    corr_df = filtered_df[selected_cols].dropna()
    corr_matrix = corr_df.corr()
    fig_corr, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
    ax.set_title("Correlation Heatmap of Selected Variables")
    ax.set_xlabel("Features")
    ax.set_ylabel("Features")
    st.pyplot(fig_corr)

# --- Tab 5: Retention Segments ---
with tabs[4]:
    st.header("📊 Retention Level Segmentation")

    def categorize_retention(r):
        if r >= 0.8:
            return 'High'
        elif r >= 0.5:
            return 'Medium'
        else:
            return 'Low'

    filtered_df['Retention_Level'] = filtered_df['RETENTION_RATIO'].apply(categorize_retention)
    segment_df = filtered_df.groupby('Retention_Level')[['LOSS_RATIO', 'GROWTH_RATE_3YR', 'ACTIVE_PRODUCERS']].mean().reset_index()
    st.dataframe(segment_df)

    st.subheader("Segmented Averages for Key Metrics")
    fig_bar = px.bar(segment_df, x='Retention_Level', y=['LOSS_RATIO', 'GROWTH_RATE_3YR'],
                     barmode='group', title="Average Loss & Growth by Retention Level", text_auto=True)
    st.plotly_chart(fig_bar, use_container_width=True)
