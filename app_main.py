# ==============================
# 🧠 UNIFIED INTELLIGENCE SYSTEM
# ==============================

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import matplotlib.pyplot as plt
import networkx as nx
from itertools import combinations
import matplotlib.cm as cm

# -------- CONFIG --------
st.set_page_config(page_title="SAIG | OMNI + AI", layout="wide")

# -------- MODE SELECT --------
mode = st.sidebar.radio("SYSTEM MODE", ["🛰️ OMNI-RECON", "🤖 AI ANALYTICS"])

# ============================================================
# 🛰️ OMNI-RECON (YOUR ORIGINAL CODE - SAME)
# ============================================================

if mode == "🛰️ OMNI-RECON":

    # KEEP YOUR ORIGINAL CODE EXACTLY
    st.markdown("""
    <style>
    html, body, [class*="css"]  { background-color: #050505; }
    </style>
    """, unsafe_allow_html=True)

    def load_data():
        try:
            with open('data_processed_events.json', 'r') as f:
                data = json.load(f)
                df = pd.DataFrame(data)

            df['event_datetime_utc'] = pd.to_datetime(df['event_datetime_utc'], unit='ms', errors='coerce')
            df['severity_score'] = pd.to_numeric(df.get('severity_score', 0), errors='coerce').fillna(0)
            df['confidence_score'] = pd.to_numeric(df.get('confidence_score', 0), errors='coerce').fillna(0)

            return df.sort_values('event_datetime_utc', ascending=False)

        except Exception as e:
            st.error(f"Data Error: {e}")
            return pd.DataFrame()

    df = load_data()

    if not df.empty:

        locs = df['location_text'].unique()
        srcs = df['source_name'].unique()

        loc_select = st.sidebar.multiselect("Location", locs, default=locs)
        source_select = st.sidebar.multiselect("Source", srcs, default=srcs)

        f_df = df[(df['location_text'].isin(loc_select)) &
                  (df['source_name'].isin(source_select)]

        st.title("🛰️ OMNI-RECON")

        c1, c2, c3 = st.columns(3)
        c1.metric("Threat", round(f_df['severity_score'].mean(), 2))
        c2.metric("Confidence", round(f_df['confidence_score'].mean(), 2))
        c3.metric("Signals", len(f_df))

        # Trend
        sev_trend = f_df.resample('D', on='event_datetime_utc')['severity_score'].mean().reset_index()
        st.plotly_chart(px.area(sev_trend, x='event_datetime_utc', y='severity_score'), use_container_width=True)

    else:
        st.warning("No OMNI data")

# ============================================================
# 🤖 AI ANALYTICS (YOUR NEW SYSTEM)
# ============================================================

elif mode == "🤖 AI ANALYTICS":

    st.title("🤖 AI Intelligence Analytics")

    # -------- LOAD --------
    df = pd.read_csv("final_data.csv")
    events = pd.read_csv("events_ranked.csv")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # -------- TOP EVENTS --------
    st.subheader("🔥 Top Events")
    st.plotly_chart(
        px.bar(events.head(10), x="count", y="event_name", orientation="h"),
        use_container_width=True
    )

    # -------- TREND --------
    st.subheader("📈 News Trend")
    trend = df.groupby(df["date"].dt.date).size().sort_index()
    st.plotly_chart(px.line(x=trend.index, y=trend.values), use_container_width=True)

    # -------- SOURCES --------
    st.subheader("📰 Sources")
    source_counts = df["source"].value_counts().head(10)
    st.plotly_chart(px.bar(x=source_counts.index, y=source_counts.values), use_container_width=True)

    # -------- CLICKBAIT --------
    st.subheader("⚠️ Clickbait")
    if "is_clickbait" in df.columns:
        st.dataframe(df[df["is_clickbait"]].head(10)[["headline", "clickbait_prob"]])

    # -------- ACTORS --------
    st.subheader("🧍 Actors")
    for _, row in df.head(5).iterrows():
        st.write(row["headline"])
        st.write(row.get("actors", []))

    # -------- COUNTRY GRAPH --------
    st.subheader("🌍 Country Graph")

    if "actors" in df.columns:

        def extract_countries(actor_list):
            country_list = ["US", "India", "Iran", "Israel", "China", "Russia"]
            return list(set([c for actor in actor_list for c in country_list if c.lower() in actor.lower()]))

        df["countries"] = df["actors"].apply(extract_countries)

        G = nx.Graph()

        for countries in df["countries"]:
            if len(countries) < 2:
                continue
            for c1, c2 in combinations(countries, 2):
                G.add_edge(c1, c2, weight=G.get_edge_data(c1, c2, default={"weight": 0})["weight"] + 1)

        weights = [d["weight"] for (_, _, d) in G.edges(data=True)]

        if weights:
            norm = plt.Normalize(min(weights), max(weights))
            cmap = cm.viridis
            colors = cmap(norm(weights))

            fig, ax = plt.subplots()
            nx.draw(G, ax=ax, edge_color=colors, with_labels=True)

            sm = cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            fig.colorbar(sm, ax=ax)

            st.pyplot(fig)
