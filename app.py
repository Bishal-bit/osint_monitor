import streamlit as st
import pandas as pd
import plotly.express as px

# -------- CONFIG --------
st.set_page_config(page_title="Geopolitical Intelligence Dashboard", layout="wide")

st.title("🌍 AI-Powered Intelligence Dashboard")

# -------- LOAD DATA --------
df = pd.read_csv("final_data.csv")
events = pd.read_csv("events_ranked.csv")

# -------- SIDEBAR --------
st.sidebar.header("Controls")

top_n = st.sidebar.slider("Top Events", 5, 20, 10)

# -------- TOP EVENTS --------
st.subheader("🔥 Top Events")

top_events = events.head(top_n)

fig = px.bar(
    top_events,
    x="count",
    y="event_name",
    orientation="h",
    title="Top Events by Coverage"
)

st.plotly_chart(fig, use_container_width=True)

# -------- TIME TREND --------
st.subheader("📈 News Trend Over Time")

df["date"] = pd.to_datetime(df["date"])
trend = df.groupby(df["date"].dt.date).size()

fig2 = px.line(
    x=trend.index,
    y=trend.values,
    labels={"x": "Date", "y": "Articles"},
    title="News Volume Trend"
)

st.plotly_chart(fig2, use_container_width=True)

# -------- CLICKBAIT --------
st.subheader("⚠️ Clickbait Detection")

clickbait_df = df[df["is_clickbait"] == True].head(10)

st.dataframe(clickbait_df[["headline", "clickbait_prob"]])

# -------- ACTORS --------
st.subheader("Actor Extraction")

sample = df.head(10)

for _, row in sample.iterrows():
    st.markdown(f"**Headline:** {row['headline']}")
    st.write("Actors:", row["actors"])
    st.markdown("---")
