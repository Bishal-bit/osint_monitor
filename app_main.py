# ==============================
# 🧠 UNIFIED INTELLIGENCE SYSTEM (SINGLE FILE)
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
st.set_page_config(page_title="Unified Intelligence System", layout="wide")

st.title("🧠 Unified Intelligence System")

# ==============================
# 📂 LOAD DATA
# ==============================

@st.cache_data
def load_recon():
    with open('data_processed_events.json', 'r') as f:
        data = json.load(f)
        df = pd.DataFrame(data)

    if 'event_datetime_utc' in df.columns:
        df['event_datetime_utc'] = pd.to_datetime(df['event_datetime_utc'], unit='ms', errors='coerce')

    df['severity_score'] = pd.to_numeric(df.get('severity_score', 0), errors='coerce').fillna(0)
    df['confidence_score'] = pd.to_numeric(df.get('confidence_score', 0), errors='coerce').fillna(0)

    return df


@st.cache_data
def load_ai():
    df = pd.read_csv("final_data.csv")
    events = pd.read_csv("events_ranked.csv")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    return df, events


df_recon = load_recon()
df_ai, events = load_ai()

# ==============================
# 🎛️ MODE SWITCH (SINGLE FILE)
# ==============================

mode = st.sidebar.radio(
    "Select Module",
    ["🛰️ OMNI-RECON", "🤖 AI Analytics"]
)

# ============================================================
# 🛰️ OMNI-RECON (OLD DASHBOARD)
# ============================================================

if mode == "🛰️ OMNI-RECON":

    st.subheader("🛰️ Tactical Intelligence Dashboard")

    if not df_recon.empty:

        # Filters
        locs = df_recon['location_text'].unique()
        srcs = df_recon['source_name'].unique()

        loc_select = st.sidebar.multiselect("Location", locs, default=locs)
        source_select = st.sidebar.multiselect("Source", srcs, default=srcs)

        f_df = df_recon[
            (df_recon['location_text'].isin(loc_select)) &
            (df_recon['source_name'].isin(source_select))
        ]

        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Threat Level", round(f_df['severity_score'].mean(), 2))
        c2.metric("Confidence", round(f_df['confidence_score'].mean(), 2))
        c3.metric("Signals", len(f_df))

        # Trends
        col1, col2 = st.columns(2)

        with col1:
            sev_trend = f_df.resample('D', on='event_datetime_utc')['severity_score'].mean().reset_index()
            fig = px.area(sev_trend, x='event_datetime_utc', y='severity_score')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            conf_trend = f_df.resample('D', on='event_datetime_utc')['confidence_score'].mean().reset_index()
            fig = px.line(conf_trend, x='event_datetime_utc', y='confidence_score')
            st.plotly_chart(fig, use_container_width=True)

        # Map
        st.subheader("📍 Locations")
        if "location_text" in f_df.columns:
            st.map(f_df.rename(columns={"location_text": "lat"}))

        # Actor frequency
        st.subheader("🤝 Actor Engagement")
        acts = f_df['actor_1'].dropna().tolist() + f_df['actor_2'].dropna().tolist()
        act_df = pd.Series(acts).value_counts().reset_index(name='mentions')
        act_df.columns = ['actor', 'mentions']

        fig = px.bar(act_df, x='actor', y='mentions')
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No recon data available")

# ============================================================
# 🤖 AI ANALYTICS
# ============================================================

elif mode == "🤖 AI Analytics":

    st.subheader("🤖 AI Intelligence Analytics")

    # Top Events
    st.markdown("### 🔥 Top Events")
    fig = px.bar(events.head(10), x="count", y="event_name", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

    # Trend
    st.markdown("### 📈 News Trend")
    trend = df_ai.groupby(df_ai["date"].dt.date).size().sort_index()

    fig = px.line(x=trend.index, y=trend.values)
    st.plotly_chart(fig, use_container_width=True)

    # Sources
    st.markdown("### 📰 Sources")
    source_counts = df_ai["source"].value_counts().head(10)

    fig = px.bar(x=source_counts.index, y=source_counts.values)
    st.plotly_chart(fig, use_container_width=True)

    # Clickbait
    st.markdown("### ⚠️ Clickbait")
    if "is_clickbait" in df_ai.columns:
        st.dataframe(df_ai[df_ai["is_clickbait"] == True][["headline", "clickbait_prob"]].head(10))

    # Actors
    st.markdown("### 🧍 Actors")
    for _, row in df_ai.head(5).iterrows():
        st.write(row["headline"])
        st.write(row.get("actors", []))

    # Country Graph
    st.markdown("### 🌍 Country Influence Graph")

    if "actors" in df_ai.columns:

        def extract_countries(actor_list):
            countries = []
            country_list = ["US", "India", "Iran", "Israel", "China", "Russia"]
            for actor in actor_list:
                for c in country_list:
                    if c.lower() in actor.lower():
                        countries.append(c)
            return list(set(countries))

        df_ai["countries"] = df_ai["actors"].apply(extract_countries)

        G = nx.Graph()

        for countries in df_ai["countries"]:
            if len(countries) < 2:
                continue
            for c1, c2 in combinations(countries, 2):
                if G.has_edge(c1, c2):
                    G[c1][c2]["weight"] += 1
                else:
                    G.add_edge(c1, c2, weight=1)

        weights = [d["weight"] for (_, _, d) in G.edges(data=True)]

        if weights:
            norm = plt.Normalize(min(weights), max(weights))
            cmap = cm.viridis
            edge_colors = cmap(norm(weights))

            fig, ax = plt.subplots(figsize=(8, 6))
            pos = nx.spring_layout(G, seed=42)

            nx.draw(G, pos, ax=ax, edge_color=edge_colors, with_labels=True)

            sm = cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            fig.colorbar(sm, ax=ax)

            st.pyplot(fig)
