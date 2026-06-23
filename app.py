
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Hotel Revenue Intelligence", layout="wide")
# -----------------------------
# 1. Load data
# -----------------------------
df = pd.read_csv("hotel_synthetic_data3.csv")
df["date"] = pd.to_datetime(df["date"])
# -----------------------------
# 2. Page config
# -----------------------------

st.title("🏨 Hotel Revenue Intelligence Dashboard")
st.write("Occupancy, revenue, and performance insights for decision making")

# -----------------------------
# 4. Filters
# -----------------------------
st.sidebar.header("Filters")

room_filter = st.sidebar.multiselect(
    "Room Type",
    df["room_type"].unique(),
    default=df["room_type"].unique()
)

season_filter = st.sidebar.multiselect(
    "Season",
    df["season"].unique(),
    default=df["season"].unique()
)


filtered_df = df[
    (df["room_type"].isin(room_filter)) &
    (df["season"].isin(season_filter))
]

if filtered_df.empty:
    st.warning("No data available for selected filters")
    st.stop()


# -----------------------------
# 3. KPIs (top section)
# -----------------------------
revpar = filtered_df["revenue"].sum() / filtered_df["available_rooms"].sum()

avg_occupancy = filtered_df["booked_rooms"].sum() / filtered_df["available_rooms"].sum()

total_revenue = filtered_df["revenue"].sum()
avg_price = filtered_df["revenue"].sum() / filtered_df["booked_rooms"].sum()
total_bookings = filtered_df["booked_rooms"].sum()
# Main KPIs
col1, col2 = st.columns(2)

col1.metric("Total Revenue", f"{total_revenue:,.0f}")
col2.metric("Occupancy", f"{avg_occupancy:.2%}")

# Secondary KPIs
col3, col4, col5 = st.columns(3)

col3.metric("ADR", f"{avg_price:,.0f}")
col4.metric("RevPAR", f"{revpar:,.0f}")
col5.metric("Bookings", f"{total_bookings:,.0f}")
st.divider()
#-----key insights---------
booked_by_day = filtered_df.groupby("date")["booked_rooms"].sum()
avail_by_day = filtered_df.groupby("date")["available_rooms"].sum()

occupancy_trend = (booked_by_day / avail_by_day).reset_index(name="occupancy_rate")
best_occ = occupancy_trend["occupancy_rate"].max()
worst_occ = occupancy_trend["occupancy_rate"].min()

low_occ_days = filtered_df.groupby("date")["booked_rooms"].sum() / filtered_df.groupby("date")["available_rooms"].sum()
low_occ_days = (low_occ_days < 0.5).sum()

revenue_std = filtered_df.groupby("date")["revenue"].sum().std()
peak_revenue = filtered_df.groupby("date")["revenue"].sum().max()

room_perf = (
    filtered_df.groupby("room_type")["revenue"]
    .sum()
    .reset_index()
)
best_room = room_perf.loc[room_perf["revenue"].idxmax(), "room_type"]
room_perf["revenue_share"] = (
    room_perf["revenue"] / room_perf["revenue"].sum()
)

top_share = room_perf["revenue_share"].max()

season_perf = (
    filtered_df.groupby("season")["revenue"]
    .mean()
    .reset_index()
)
best_season = season_perf.loc[season_perf["revenue"].idxmax(), "season"]


st.subheader("📌 Executive Summary")

st.info(
    f"""
    • Best performing room type: {best_room} ({top_share:.1%} of revenue)

    • Peak daily revenue reached {peak_revenue:,.0f}

    • {low_occ_days} days experienced occupancy below 50%
    
    • Occupancy ranged from **{worst_occ:.0%}** to **{best_occ:.0%}**

    Recommendation: The {best_room} room category generates the strongest revenue contribution and should be a primary focus for pricing optimization and inventory planning.
    """
)
st.divider()

# -----------------------------
# 5. Occupancy trend
# -----------------------------
st.subheader("📊 Occupancy Trend Over Time")


fig1 = px.line(
    occupancy_trend,
    x="date",
    y="occupancy_rate",
    title="Daily Occupancy Rate"
)

st.plotly_chart(fig1, use_container_width=True)
st.success(
    f"""
    Occupancy fluctuated between {worst_occ:.0%} and {best_occ:.0%}.
    Demand volatility indicates periods that may require pricing adjustments.
    """
)
#st.write(fig1)
correlation = df["occupancy_rate"].corr(df["revenue"])
st.info(f"Occupancy-Revenue correlation: {correlation:.2f}")
st.divider()
# -----------------------------
# 6. Revenue trend
# -----------------------------
st.subheader("💰 Revenue Trend")

revenue_trend = (
    filtered_df
    .groupby("date")["revenue"]
    .sum()
    .reset_index()
)

fig2 = px.line(
    revenue_trend,
    x="date",
    y="revenue",
    title="Daily Revenue"
)

st.plotly_chart(fig2, use_container_width=True)

st.info(
    "Revenue peaks highlight strong demand periods and may represent pricing opportunities."
)
#st.write(fig2)
st.divider()

# -----------------------------
# 7. Performance Alerts
# -----------------------------
st.subheader("⚠ Performance Alerts")
if low_occ_days > 3:
    st.warning(
        f"{low_occ_days} days experienced occupancy below 50%."
    )

if avg_occupancy < 0.65:
    st.warning(
        "Average occupancy remains below target levels."
    )

if revenue_std > 10000:
    st.warning(
        "Revenue volatility is elevated. Demand patterns should be monitored."
    )

st.divider()
# -----------------------------
# 7. Revenue opportunities
# -----------------------------
st.subheader("🎯 Revenue Opportunities")

st.success(
    f"""
    {best_room} rooms contribute {top_share:.1%} of total revenue and represent the strongest pricing optimization opportunity.
    """
)

st.success(
    f"""
    {best_season} season delivers the highest average revenue and should be prioritized for revenue planning.
    """
)

st.divider()
# -----------------------------
# 8. Room type performance
# -----------------------------
st.subheader("🛏️ Room Type Performance")


fig3 = px.bar(
    room_perf,
    x="room_type",
    y="revenue",
    title="Revenue by Room Type"
)

st.plotly_chart(fig3, use_container_width=True)

st.info(
    f"""
    {best_room} rooms generated the highest revenue contribution ({top_share:.1%} of total revenue).
    """
)
#st.write(fig3)

# -----------------------------



st.caption(
    "Demonstration dashboard built with Python, Streamlit and Plotly using synthetic hotel performance data."
)
