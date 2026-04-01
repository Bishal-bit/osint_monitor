# ==============================
# 🚀 STREAMLIT DASHBOARD (ALL VISUALS)
# ==============================

import streamlit as st
import pandas as pd
import plotly.express as px

# -------- CONFIG --------
st.set_page_config(page_title="Geopolitical Intelligence Dashboard", layout="wide")

st.title("🌍 AI-Powered Intelligence Dashboard")

# -------- LOAD DATA --------
df = pd.read_csv("final_data.csv")
events = pd.read_csv("events_ranked.csv")

# -------- CLEAN DATE (FIXED) --------
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])

# -------- SIDEBAR --------
st.sidebar.header("Controls")
top_n = st.sidebar.slider("Top Events", 5, 20, 10)

# ==============================
# 🔥 TOP EVENTS
# ==============================
st.subheader("🔥 Top Events")

top_events = events.head(top_n)

fig1 = px.bar(
    top_events,
    x="count",
    y="event_name",
    orientation="h",
    title="Top Events by Coverage"
)

st.plotly_chart(fig1, use_container_width=True)

# ==============================
# 📈 NEWS TREND
# ==============================
st.subheader("📈 News Trend Over Time")

trend = df.groupby(df["date"].dt.date).size().sort_index()

fig2 = px.line(
    x=trend.index,
    y=trend.values,
    labels={"x": "Date", "y": "Articles"},
    title="News Volume Trend"
)

st.plotly_chart(fig2, use_container_width=True)

# ==============================
# 📊 EVENT DISTRIBUTION
# ==============================
st.subheader("📊 Event Distribution")

fig3 = px.histogram(
    df,
    x="cluster",
    nbins=30,
    title="Distribution of Articles Across Events"
)

st.plotly_chart(fig3, use_container_width=True)

# ==============================
# 📰 SOURCE DISTRIBUTION
# ==============================
st.subheader("📰 Top News Sources")

source_counts = df["source"].value_counts().head(10).reset_index()
source_counts.columns = ["source", "count"]

fig4 = px.bar(
    source_counts,
    x="source",
    y="count",
    title="Top Sources"
)

st.plotly_chart(fig4, use_container_width=True)

# ==============================
# 🥧 EVENT SHARE
# ==============================
st.subheader("🥧 Top Event Share")

top5 = events.head(5)

fig5 = px.pie(
    top5,
    names="event_name",
    values="count",
    title="Top 5 Event Share"
)

st.plotly_chart(fig5, use_container_width=True)

# ==============================
# ⚠️ CLICKBAIT
# ==============================
st.subheader("⚠️ Clickbait Detection")

if "is_clickbait" in df.columns:
    clickbait_df = df[df["is_clickbait"] == True].head(10)
    st.dataframe(clickbait_df[["headline", "clickbait_prob"]])
else:
    st.write("Clickbait data not available")

# ==============================
# 🧍 ACTORS
# ==============================
st.subheader("🧍 Actor Extraction")

if "actors" in df.columns:
    for _, row in df.head(5).iterrows():
        st.markdown(f"**Headline:** {row['headline']}")
        st.write("Actors:", row["actors"])
        st.markdown("---")
else:
    st.write("Actor data not available")
