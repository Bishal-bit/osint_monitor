import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from itertools import combinations

# ==============================
# 1. TACTICAL UI CONFIG
# ==============================
st.set_page_config(page_title="ONINT Conflict Monitoring System", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"]  { 
        font-family: 'JetBrains Mono', monospace; 
        background-color: #050505; 
    }

    .risk-banner {
        background-color: #ff4b4b;
        color: white;
        padding: 12px;
        text-align: center;
        font-weight: bold;
        border-radius: 4px;
        margin-bottom: 20px;
        border: 2px solid #ffffff;
        animation: blinker 2s linear infinite;
    }
    @keyframes blinker { 50% { opacity: 0.6; } }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #111 0%, #000 100%);
        border: 1px solid #333; 
        border-radius: 4px; 
        padding: 15px;
    }

    [data-testid="stMetricLabel"] p {
        color: #FFFFFF !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1rem;
    }
    [data-testid="stMetricValue"] div {
        color: #FFFFFF !important;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.15);
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 2. DATA INGESTION ENGINE
# ==============================
@st.cache_data
def load_unified_data():
    try:
        # Load Primary Intel (JSON)
        with open('data_processed_events.json', 'r') as f:
            intel_df = pd.DataFrame(json.load(f))
        
        # Load News & Ranking (CSV)
        news_df = pd.read_csv("final_data.csv")
        rank_df = pd.read_csv("events_ranked.csv")

        # Standardize Dates
        intel_df['event_datetime_utc'] = pd.to_datetime(intel_df['event_datetime_utc'], unit='ms', errors='coerce')
        news_df["date"] = pd.to_datetime(news_df["date"], errors="coerce")
        
        # Helper: Tags to string
        if 'tags' in intel_df.columns:
            intel_df['tags_str'] = intel_df['tags'].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
            
        return intel_df, news_df, rank_df
    except Exception as e:
        st.error(f"⚠️ Systems Linkage Failure: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_intel, df_news, df_rank = load_unified_data()

# ==============================
# 3. SIDEBAR & FILTERS
# ==============================
with st.sidebar:
    st.title("🔍 DRILL-DOWN")
    st.markdown("---")
    
    if not df_intel.empty:
        locs = df_intel['location_text'].unique() if 'location_text' in df_intel.columns else []
        srcs = df_intel['source_name'].unique() if 'source_name' in df_intel.columns else []
        
        loc_select = st.multiselect("SECTOR LOCK", locs, default=locs)
        source_select = st.multiselect("SOURCE FILTER", srcs, default=srcs)
        
        f_df = df_intel[(df_intel['location_text'].isin(loc_select)) & (df_intel['source_name'].isin(source_select))]
    
    st.markdown("---")
    top_n = st.slider("VISIBLE TREND DEPTH", 5, 20, 10)
    st.caption("OMNI-RECON v3.0 | Hybrid Intel Stream")

# ==============================
# 4. STRATEGIC COMMAND HEADERS
# ==============================
if not df_intel.empty:
    avg_sev = f_df['severity_score'].mean() if not f_df.empty else 0
    
    if avg_sev > 7.0:
        st.markdown(f'<div class="risk-banner">⚠️ CRITICAL THREAT LEVEL: KINETIC ESCALATION DETECTED (AVG: {avg_sev:.1f})</div>', unsafe_allow_html=True)

    st.title("🛰️ OMNI-RECON | STRATEGIC COMMAND")
    
    # Unified Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("THREAT LEVEL", f"{avg_sev:.1f}")
    m2.metric("INTEL SIGNALS", len(f_df))
    m3.metric("NEWS VOLUME", len(df_news))
    m4.metric("VERIFIED %", f"{(len(f_df[f_df['information_status']=='verified'])/len(f_df)*100):.1f}%" if len(f_df)>0 else "0%")
    m5.metric("TOP SOURCE", df_news["source"].mode()[0] if not df_news.empty else "N/A")

    # ==============================
    # 5. ROW 1: SPATIAL & TOP EVENTS
    # ==============================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📍 GEOSPATIAL OVERLAY")
        COORDS = {
            "Tehran": [35.68, 51.38], "Shiraz": [29.59, 52.58], "Jerusalem": [31.76, 35.21], 
            "Tel Aviv": [32.08, 34.78], "Isfahan": [32.65, 51.66], "Haifa": [32.79, 34.98],
            "Beirut": [33.89, 35.50], "Gaza": [31.50, 34.46], "Iran": [32.42, 53.68]
        }
        f_df['lat'] = f_df['location_text'].map(lambda x: COORDS.get(x, [None])[0])
        f_df['lon'] = f_df['location_text'].map(lambda x: COORDS.get(x, [None, None])[1])
        st.map(f_df.dropna(subset=['lat', 'lon'])[['lat', 'lon']])

    with col2:
        st.subheader("🔥 TOP RANKED EVENTS")
        fig_rank = px.bar(df_rank.head(top_n), x="count", y="event_name", orientation="h", 
                          template="plotly_dark", color_discrete_sequence=['#ff4b4b'])
        st.plotly_chart(fig_rank, width="stretch", key="top_ranked_events_bar")

    # ==============================
    # 6. ROW 2: TEMPORAL TRENDS
    # ==============================
    st.markdown("---")
    t1, t2 = st.columns(2)

    with t1:
        st.subheader("📈 NEWS VOLUME TREND")
        trend = df_news.groupby(df_news["date"].dt.date).size().sort_index()
        fig_trend = px.line(x=trend.index, y=trend.values, template="plotly_dark", color_discrete_sequence=['#00f2ff'])
        st.plotly_chart(fig_trend, width="stretch", key="news_volume_trend_line")

    with t2:
        st.subheader("🛡️ SEVERITY VS CONFIDENCE")
        resampled = f_df.resample('D', on='event_datetime_utc')[['severity_score', 'confidence_score']].mean().reset_index()
        fig_comp = px.area(resampled, x='event_datetime_utc', y=['severity_score', 'confidence_score'], 
                        template="plotly_dark")
        st.plotly_chart(fig_comp, width="stretch", key="sev_vs_conf_area")

    # ==============================
    # 7. ROW 3: ACTORS & CLICKBAIT
    # ==============================
    st.markdown("---")
    a1, a2 = st.columns([2, 1])

    with a1:
        st.subheader("🤝 ACTOR EXTRACTION & ENGAGEMENT")
        if "actors" in df_news.columns:
            for _, row in df_news.head(3).iterrows():
                st.info(f"**{row['headline']}**\n\nIdentified: {row['actors']}")
        else:
            acts = f_df['actor_1'].dropna().tolist() + f_df['actor_2'].dropna().tolist()
            act_df = pd.Series(acts).value_counts().reset_index(name='mentions')
            fig_a = px.bar(act_df.head(10), x='index', y='mentions', template="plotly_dark")
            st.plotly_chart(fig_a, width="stretch", key="actor_engagement_bar")

    with a2:
        st.subheader("⚠️ CLICKBAIT AUDIT")
        if "is_clickbait" in df_news.columns:
            cb_df = df_news[df_news["is_clickbait"] == True].head(5)
            st.dataframe(cb_df[["headline", "clickbait_prob"]], hide_index=True)
        else:
            st.warning("Clickbait detection module offline.")

    # ==============================
    # 🌍 COUNTRY INFLUENCE GRAPH
    # ==============================
    st.markdown("---")
    st.subheader("🕸️ COUNTRY INFLUENCE NETWORK")

    country_list = [
        "United States", "US", "USA", "India", "China", "Russia", "Iran", "Israel", 
        "Pakistan", "Ukraine", "France", "Germany", "UK", "United Kingdom", 
        "Saudi Arabia", "UAE", "Iraq", "Turkey", "Qatar", "Kuwait", "Lebanon", "Afghanistan"
    ]

    def extract_countries(actor_val):
        if not isinstance(actor_val, str): return []
        found = []
        for country in country_list:
            if country.lower() in actor_val.lower():
                found.append(country)
        return list(set(found))

    if "actors" in df_news.columns:
        df_news["countries"] = df_news["actors"].apply(extract_countries)
        G = nx.Graph()
        for countries in df_news["countries"]:
            if len(countries) >= 2:
                for c1, c2 in combinations(countries, 2):
                    if G.has_edge(c1, c2):
                        G[c1][c2]["weight"] += 1
                    else:
                        G.add_edge(c1, c2, weight=1)

        if len(G.nodes) > 0:
            centrality = nx.degree_centrality(G)
            top_nodes = [c for c, _ in sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:12]]
            subG = G.subgraph(top_nodes)

            fig, ax = plt.subplots(figsize=(10, 7))
            fig.patch.set_facecolor('#050505')
            ax.set_facecolor('#050505')

            pos = nx.spring_layout(subG, seed=42, k=0.5)
            weights = [d["weight"] for (_, _, d) in subG.edges(data=True)]
            norm = plt.Normalize(min(weights) if weights else 0, max(weights) if weights else 1)
            cmap = cm.magma 
            edge_colors = cmap(norm(weights))

            nx.draw(
                subG, pos, ax=ax, with_labels=True,
                node_size=1800, node_color="#111",
                font_size=8, font_color="white", font_weight="bold",
                edge_color=edge_colors, width=2
            )

            sm = cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = fig.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
            plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
            cbar.set_label("Interaction Density", color="white", size=8)
            st.pyplot(fig)
        else:
            st.info("Insufficient co-occurrence data for country network.")

    # ==============================
    # 📊 EXTENDED ANALYTICS
    # ==============================
    st.markdown("---")
    st.header("📊 MULTI-DIMENSIONAL INTEL ANALYSIS")

    col_dist1, col_dist2 = st.columns(2)

    with col_dist1:
        st.subheader("🔥 TOP 10 EVENTS (STATIC)")
        fig_static, ax_static = plt.subplots()
        fig_static.patch.set_facecolor('#050505')
        ax_static.set_facecolor('#111')
        ax_static.barh(df_rank.head(10)["event_name"], df_rank.head(10)["count"], color='#ff4b4b')
        ax_static.tick_params(colors='white')
        ax_static.invert_yaxis()
        st.pyplot(fig_static)

    with col_dist2:
        st.subheader("🧩 CLUSTER DENSITY")
        fig_hist, ax_hist = plt.subplots()
        fig_hist.patch.set_facecolor('#050505')
        ax_hist.set_facecolor('#111')
        ax_hist.hist(df_news["cluster"], bins=20, color='#00f2ff', edgecolor='black')
        ax_hist.tick_params(colors='white')
        st.pyplot(fig_hist)

    col_vol1, col_vol2 = st.columns(2)

    with col_vol1:
        st.subheader("📈 CHRONOLOGICAL VOLUME")
        df_news['date_only'] = df_news['date'].dt.date
        events_per_day = df_news.groupby("date_only").size()
        fig_vol, ax_vol = plt.subplots()
        fig_vol.patch.set_facecolor('#050505')
        ax_vol.set_facecolor('#111')
        events_per_day.plot(ax=ax_vol, color='#00f2ff', linewidth=2)
        ax_vol.tick_params(colors='white')
        st.pyplot(fig_vol)

    with col_vol2:
        st.subheader("📰 TOP NEWS SOURCES")
        source_counts = df_news["source"].value_counts().head(10)
        fig_src, ax_src = plt.subplots()
        fig_src.patch.set_facecolor('#050505')
        ax_src.set_facecolor('#111')
        source_counts.plot(kind="bar", ax=ax_src, color='#ff4b4b')
        ax_src.tick_params(axis='x', rotation=45, colors='white')
        ax_src.tick_params(axis='y', colors='white')
        st.pyplot(fig_src)

    col_share1, col_share2 = st.columns([1, 2])

    with col_share1:
        st.subheader("🥧 TOP 5 EVENT SHARE")
        fig_pie, ax_pie = plt.subplots()
        fig_pie.patch.set_facecolor('#050505')
        ax_pie.pie(df_rank.head(5)["count"], labels=df_rank.head(5)["event_name"], autopct='%1.1f%%', 
                textprops={'color':"w"}, colors=['#ff4b4b', '#00f2ff', '#333', '#555', '#777'])
        st.pyplot(fig_pie)

    with col_share2:
        st.subheader("🛰️ INTERACTIVE RECONNAISSANCE")
        fig_inter = px.bar(
            df_rank.head(10), x="count", y="event_name", orientation='h',
            template="plotly_dark", color_discrete_sequence=['#ff4b4b']
        )
        st.plotly_chart(fig_inter, width="stretch", key="interactive_recon_bar_final")

    # ==============================
    # 8. DATA LOGS
    # ==============================
    st.markdown("---")
    st.subheader("📋 RAW RECONNAISSANCE LOGS")
    st.dataframe(f_df[['event_datetime_utc', 'source_name', 'claim_text', 'severity_score', 'information_status']], width="stretch")
else:
    st.warning("Awaiting Ingestion Stream... Ensure JSON and CSV files are in the root directory.")
