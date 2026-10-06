import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="NovaMart CEO Decision Cockpit", layout="wide")

st.title("NovaMart Executive AI Decision Cockpit")
st.markdown("Dynamic Decision-Support Simulator for Capital Allocation & Margin Throttling")

# Load Dataset
@st.cache_data
def load_data():
    df = pd.read_excel("Dataset 3.xlsx")
    df['Profit_Margin'] = df['Profit'] / df['Revenue']
    df['Net_Profit'] = df['Profit'] - df['Marketing_Spend']
    return df

df = load_data()

# Sidebar Controls
st.sidebar.header("CEO Policy Levers")
discount_cap = st.sidebar.slider("Maximum Permissible Discount Rate (%)", 5, 40, 12) / 100.0
personal_care_mkt_cut = st.sidebar.slider("Personal Care Mkt Budget Cut (%)", 0, 100, 75) / 100.0
sla_target_days = st.sidebar.slider("Delivery SLA Threshold (Days)", 3, 10, 5)

# Metrics Calculation
col1, col2, col3, col4 = st.columns(4)

baseline_revenue = df['Revenue'].sum()
baseline_profit = df['Profit'].sum()
baseline_net_profit = df['Net_Profit'].sum()

# Simulated Impact
sim_df = df.copy()
# Reallocated marketing savings from Personal Care
pc_savings = sim_df[sim_df['Category'] == 'Personal Care']['Marketing_Spend'].sum() * personal_care_mkt_cut
# Recovered profit from eliminating high discount erosion
erosion_mask = sim_df['Discount'] > discount_cap
recovered_margin = (sim_df.loc[erosion_mask, 'Revenue'] * (discount_cap * 0.4)).sum()

simulated_net_profit = baseline_net_profit + pc_savings + (recovered_margin * 0.5)

col1.metric("Total Revenue", f"‹{baseline_revenue:,.0f}")
col2.metric("Gross Profit", f"‹{baseline_profit:,.0f}")
col3.metric("Baseline Net Profit", f"‹{baseline_net_profit:,.0f}")
col4.metric("Simulated Net Profit", f"‹{simulated_net_profit:,.0f}", f"+‹{simulated_net_profit - baseline_net_profit:,.0f}")

st.markdown("---")

# Visual Diagnostic
st.subheader("Category Unit Economics: Gross Profit vs Marketing Spend")
cat_summary = df.groupby('Category').agg(
    Revenue=('Revenue', 'sum'),
    Gross_Profit=('Profit', 'sum'),
    Marketing_Spend=('Marketing_Spend', 'sum'),
    Net_Profit=('Net_Profit', 'sum')
).reset_index()

st.dataframe(cat_summary.style.format({
    'Revenue': '‹{:,.2f}',
    'Gross_Profit': '‹{:,.2f}',
    'Marketing_Spend': '‹{:,.2f}',
    'Net_Profit': '‹{:,.2f}'
}))

st.info("Logistics Warning: Orders exceeding 7 delivery days show an 11.84% return rate vs 5.04% for orders delivered within 4-5 days.")
