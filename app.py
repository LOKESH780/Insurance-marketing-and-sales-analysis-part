# app.py - Streamlit Dashboard for Retention Analysis
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
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
#df = pd.read_csv("finalapi.csv")
df = joblib.load("finalapi.pkl")

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
                       title="Average Retention Ratio per Year")
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Bar Chart: Avg Retention Ratio by Product Line")
    if 'PROD_LINE' in filtered_df.columns:
        bar_df = filtered_df.groupby("PROD_LINE")["RETENTION_RATIO"].mean().reset_index()
        fig_bar_ret = px.bar(bar_df, x="PROD_LINE", y="RETENTION_RATIO", text_auto=True,
                             title="Average Retention Ratio by Product Line")
        st.plotly_chart(fig_bar_ret, use_container_width=True)

    st.subheader("Histogram: Retention Ratio Distribution")
    fig_hist = px.histogram(df, x="RETENTION_RATIO", nbins=30, title="Distribution of Retention Ratios")
    st.plotly_chart(fig_hist, use_container_width=True)

# --- Tab 3: Loss & Growth Trends ---
with tabs[2]:
    st.header("📉 Loss Ratio & Growth Insights")

    st.subheader("Improved Scatter: Retention vs Loss Ratio by Product Line")
    fig_scatter = px.scatter(
        filtered_df,
        x="LOSS_RATIO", 
        y="RETENTION_RATIO",
        color="PROD_LINE",
        hover_data=["GROWTH_RATE_3YR", "ACTIVE_PRODUCERS"],
        title="Retention vs Loss Ratio by Product Line"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Line Chart: Avg Growth Rate Over Time")
    growth_df = filtered_df.groupby("AGENCY_APPOINTMENT_YEAR")["GROWTH_RATE_3YR"].mean().reset_index()
    fig_growth = px.line(growth_df, x="AGENCY_APPOINTMENT_YEAR", y="GROWTH_RATE_3YR",
                         title="Avg 3-Year Growth Rate Over Time", markers=True)
    st.plotly_chart(fig_growth, use_container_width=True)

    st.subheader("Bar Chart: Loss Ratio by Product Line")
    loss_df = filtered_df.groupby("PROD_LINE")["LOSS_RATIO"].mean().reset_index()
    fig_loss_bar = px.bar(loss_df, x="PROD_LINE", y="LOSS_RATIO", title="Average Loss Ratio by Product Line", text_auto=True)
    st.plotly_chart(fig_loss_bar, use_container_width=True)

# --- Tab 4: Correlation Analysis ---
with tabs[3]:
    st.header("🔍 Correlation Among Key Variables")
    selected_cols = [
        'AGENCY_APPOINTMENT_YEAR', 'WRTN_PREM_AMT', 'NB_WRTN_PREM_AMT',
        'POLY_INFORCE_QTY', 'PREV_POLY_INFORCE_QTY', 'LOSS_RATIO',
        'GROWTH_RATE_3YR', 'ACTIVE_PRODUCERS', 'RETENTION_RATIO']
    corr_df = filtered_df[selected_cols].dropna()
    corr_matrix = corr_df.corr()
    fig_corr, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
    ax.set_title("Correlation Heatmap of Features")
    st.pyplot(fig_corr)

    st.subheader("Scatter Plot: Premium vs Policies In Force")
    fig_corr2 = px.scatter(filtered_df, x="POLY_INFORCE_QTY", y="WRTN_PREM_AMT", color="RETENTION_RATIO",
                           title="Premium vs Policies In Force")
    st.plotly_chart(fig_corr2, use_container_width=True)

# --- Tab 5: Retention Segments ---
with tabs[4]:
    st.header("📁 Retention Segmentation")

    def categorize_retention(r):
        if r >= 0.8:
            return 'High'
        elif r >= 0.5:
            return 'Medium'
        else:
            return 'Low'

    # Apply the function to create a new column
    filtered_df['Retention_Level'] = filtered_df['RETENTION_RATIO'].apply(categorize_retention)

    # Group by Retention Level and compute mean of selected metrics
    segment_df = filtered_df.groupby('Retention_Level')[
    ['LOSS_RATIO', 'GROWTH_RATE_3YR', 'ACTIVE_PRODUCERS']
    ].mean().reset_index()

    # Display the table only if it's not empty
    st.subheader("📊 Retention Level Summary Table")
    if not segment_df.empty:
        st.dataframe(segment_df)
    else:
        st.warning("No data available for the selected filters.")

    st.subheader("Bar Chart: Avg Metrics by Retention Level")
    fig_bar = px.bar(segment_df, x='Retention_Level', y=['LOSS_RATIO', 'GROWTH_RATE_3YR'],
                     barmode='group', title="Metrics by Retention Category", text_auto=True)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Pie Chart: Retention Level Distribution")
    level_counts = filtered_df['Retention_Level'].value_counts().reset_index()
    level_counts.columns = ['Retention_Level', 'count']
    fig_pie_retention = px.pie(level_counts, names='Retention_Level', values='count', title="Retention Level Distribution")
    st.plotly_chart(fig_pie_retention, use_container_width=True)

# --- Tab 6: Premium Breakdown ---
with tabs[5]:
    st.header("💰 Premium Contribution Analysis")
    if 'PROD_LINE' in filtered_df.columns:
        prem_df = filtered_df.groupby("PROD_LINE")["WRTN_PREM_AMT"].sum().reset_index()
        fig_pie = px.pie(prem_df, names="PROD_LINE", values="WRTN_PREM_AMT",
                         title="Written Premium by Product Line", hole=0.4)
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Bar Chart: NB Premium Amount by Product")
    if 'PROD_ABBR' in filtered_df.columns:
        nb_df = filtered_df.groupby("PROD_ABBR")["NB_WRTN_PREM_AMT"].sum().reset_index()
        nb_df = nb_df.sort_values(by="NB_WRTN_PREM_AMT", ascending=False)
        fig_nb_bar = px.bar(nb_df, x="PROD_ABBR", y="NB_WRTN_PREM_AMT", title="NB Premium Amount by Product", text_auto=True)
        st.plotly_chart(fig_nb_bar, use_container_width=True)

# --- Tab 7: Agency Contribution ---
with tabs[6]:
    st.header("🏢 Agency Contribution to Premium")
    if 'AGENCY_ID' in filtered_df.columns:
        agency_prem = filtered_df.groupby("AGENCY_ID")["WRTN_PREM_AMT"].sum().reset_index()
        fig_agency = px.bar(agency_prem, x="AGENCY_ID", y="WRTN_PREM_AMT",
                            title="Premium Contribution by Agency", text_auto=True)
        st.plotly_chart(fig_agency, use_container_width=True)

# --- Tab 8: Growth vs Premium ---
with tabs[7]:
    st.header("📊 Growth vs Premium Relationship (Improved)")
    fig_rel = px.scatter(
        filtered_df,
        x="GROWTH_RATE_3YR",
        y="WRTN_PREM_AMT",
        color="PROD_ABBR",
        size="POLY_INFORCE_QTY",
        hover_data=["AGENCY_ID", "RETENTION_RATIO"],
        title="Growth Rate vs Written Premium by Product"
    )
    st.plotly_chart(fig_rel, use_container_width=True)
