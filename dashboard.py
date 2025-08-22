import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="SME Sales Insights", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("data/superstore_sample.csv", parse_dates=["Order Date","Ship Date"])

df = load_data()

st.title("SME Sales Insights Dashboard")
st.caption("Demonstrates data cleaning, EDA, SQL-style analysis, and reporting.")

# Data quality checks
issues = []
if (df["Sales"] < 0).any(): issues.append("Negative Sales detected.")
if (df["Discount"] < 0).any() or (df["Discount"] > 1).any(): issues.append("Discount outside [0,1].")
if (df["Order Date"] > df["Ship Date"]).any(): issues.append("Ship Date earlier than Order Date.")
st.subheader("Data Quality Checks")
if issues: [st.error(i) for i in issues]
else: st.success("No issues detected in basic checks.")

# KPIs
total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
margin_pct = (total_profit/total_sales*100) if total_sales else 0
aov = df.groupby("Order ID")["Sales"].sum().mean()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Total Sales", f"£{total_sales:,.0f}")
c2.metric("Total Profit", f"£{total_profit:,.0f}")
c3.metric("Margin %", f"{margin_pct:,.1f}%")
c4.metric("Avg Order Value", f"£{aov:,.0f}")

# Filters
with st.expander("Filters"):
    region = st.multiselect("Region", sorted(df["Region"].unique().tolist()))
    category = st.multiselect("Category", sorted(df["Category"].unique().tolist()))
    dmin, dmax = df["Order Date"].min(), df["Order Date"].max()
    date_range = st.slider("Order Date Range", min_value=dmin.to_pydatetime(), max_value=dmax.to_pydatetime(), value=(dmin.to_pydatetime(), dmax.to_pydatetime()))

df_f = df.copy()
if region: df_f = df_f[df_f["Region"].isin(region)]
if category: df_f = df_f[df_f["Category"].isin(category)]
df_f = df_f[(df_f["Order Date"] >= pd.Timestamp(date_range[0])) & (df_f["Order Date"] <= pd.Timestamp(date_range[1]))]

# Monthly trend
st.subheader("Monthly Revenue vs Profit")
monthly = (df_f.set_index("Order Date").groupby(pd.Grouper(freq="MS")).agg(Revenue=("Sales","sum"), Profit=("Profit","sum")).reset_index())
fig1, ax1 = plt.subplots()
ax1.plot(monthly["Order Date"], monthly["Revenue"], label="Revenue")
ax1.plot(monthly["Order Date"], monthly["Profit"], label="Profit")
ax1.set_xlabel("Month"); ax1.set_ylabel("£"); ax1.legend()
st.pyplot(fig1)

# Profit by Category
st.subheader("Profit by Category")
cat = df_f.groupby("Category", as_index=False).agg(Revenue=("Sales","sum"), Profit=("Profit","sum"))
fig2, ax2 = plt.subplots()
ax2.bar(cat["Category"], cat["Profit"])
ax2.set_xlabel("Category"); ax2.set_ylabel("Profit (£)")
st.pyplot(fig2)

# Discount vs Profit
st.subheader("Discount vs Profit")
fig3, ax3 = plt.subplots()
ax3.scatter(df_f["Discount"], df_f["Profit"], alpha=0.3)
ax3.set_xlabel("Discount"); ax3.set_ylabel("Profit (£)")
st.pyplot(fig3)

# Simple forecast (3-month average)
st.subheader("Simple Forecast")
if len(monthly) >= 3:
    next_rev = monthly["Revenue"].tail(3).mean()
    st.write(f"Projected next-month revenue (naive): **£{next_rev:,.0f}**")
else:
    st.write("Not enough months for a forecast.")
