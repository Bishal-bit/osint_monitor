import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime
import random

# 1. TACTICAL UI CONFIG
st.set_page_config(page_title="SAIG | OMNI-RECON", layout="wide", initial_sidebar_state="expanded")

# "White & Slate" Tactical CSS
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

def load_data():
    try:
        with open('data_processed_events.json', 'r') as f:
            data = json.load(f)
            df = pd.DataFrame(data)
        
        if 'event_datetime_utc' in df.columns:
            df['event_datetime_utc'] = pd.to_datetime(df['event_datetime_utc'], unit='ms', errors='coerce')
        
        for col in ['severity_score', 'confidence_score']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            else:
                df[col] = 0.0
            
        df['tags_str'] = df['tags'].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
        return df.sort_values('event_datetime_utc', ascending=False)
    except Exception as e:
        st.error(f"Data Sync Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 2. SIDEBAR
    with st.sidebar:
        st.title("🔍 DRILL-DOWN")
        st.markdown("---")
        locs = df['location_text'].unique() if 'location_text' in df.columns else []
        srcs = df['source_name'].unique() if 'source_name' in df.columns else []
        
        loc_select = st.multiselect("SECTOR LOCK", locs, default=locs)
        source_select = st.multiselect("SOURCE FILTER", srcs, default=srcs)
        
        f_df = df[(df['location_text'].isin(loc_select)) & (df['source_name'].isin(source_select))]
        st.markdown("---")
        st.caption("OMNI-RECON v2.8 | Encrypted Stream")

    # 3. METRICS
    avg_sev = f_df['severity_score'].mean() if not f_df.empty else 0
    avg_conf = f_df['confidence_score'].mean() if not f_df.empty else 0

    if avg_sev > 7.0:
        st.markdown(f'<div class="risk-banner">⚠️ CRITICAL THREAT LEVEL: KINETIC ESCALATION DETECTED (AVG: {avg_sev:.1f})</div>', unsafe_allow_html=True)

    st.title("🛰️ OMNI-RECON | STRATEGIC COMMAND")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("THREAT LEVEL", f"{avg_sev:.1f}")
    c2.metric("CONFIDENCE", f"{avg_conf:.2f}")
    c3.metric("SIGNALS", len(f_df))
    c4.metric("SOURCES", f_df['source_name'].nunique() if 'source_name' in f_df.columns else 0)
    c5.metric("VERIFIED %", f"{(len(f_df[f_df['information_status']=='verified'])/len(f_df)*100):.1f}%" if len(f_df)>0 else "0%")

    # 4. ROW 1: SIDE-BY-SIDE TRENDS (Severity & Confidence)
    row1_l, row1_r = st.columns(2)

    with row1_l:
        st.subheader("📈 INTENSITY TREND (Severity)")
        sev_trend = f_df.resample('D', on='event_datetime_utc')['severity_score'].mean().reset_index()
        fig_sev = px.area(sev_trend, x='event_datetime_utc', y='severity_score', 
                        template="plotly_dark", color_discrete_sequence=['#ff4b4b'])
        st.plotly_chart(fig_sev, use_container_width=True)

    with row1_r:
        st.subheader("🛡️ CONFIDENCE TREND")
        conf_trend = f_df.resample('D', on='event_datetime_utc')['confidence_score'].mean().reset_index()
        fig_conf = px.line(conf_trend, x='event_datetime_utc', y='confidence_score', 
                           template="plotly_dark", color_discrete_sequence=['#00f2ff'])
        st.plotly_chart(fig_conf, use_container_width=True)

    # 5. ROW 2: MAP & ACTORS
    row2_l, row2_r = st.columns(2)

    with row2_l:
        st.subheader("📍 GEOSPATIAL OVERLAY")
        COORDS = {
            "Tehran": [35.68, 51.38], "Shiraz": [29.59, 52.58], "Jerusalem": [31.76, 35.21], 
            "Tel Aviv": [32.08, 34.78], "Isfahan": [32.65, 51.66], "Haifa": [32.79, 34.98],
            "Beirut": [33.89, 35.50], "Gaza": [31.50, 34.46], "West Asia": [32.0, 45.0], "Iran": [32.42, 53.68]
        }
        f_df['lat'] = f_df['location_text'].map(lambda x: COORDS.get(x, [None])[0])
        f_df['lon'] = f_df['location_text'].map(lambda x: COORDS.get(x, [None, None])[1])
        st.map(f_df.dropna(subset=['lat', 'lon'])[['lat', 'lon']])

    with row2_r:
        st.subheader("🤝 ACTOR ENGAGEMENT")
        acts = f_df['actor_1'].dropna().tolist() + f_df['actor_2'].dropna().tolist()
        act_df = pd.Series(acts).value_counts().reset_index(name='mentions')
        act_df.columns = ['actor', 'mentions']
        fig_a = px.bar(act_df, x='actor', y='mentions', color='actor', template="plotly_dark")
        fig_a.update_layout(showlegend=False)
        st.plotly_chart(fig_a, use_container_width=True)

    # 6. ROW 3: DOMAINS & LOGS
    row3_l, row3_r = st.columns([1, 2])

    with row3_l:
        st.subheader("📊 DOMAIN DISTRIBUTION")
        dom_df = f_df['domain'].value_counts().reset_index()
        fig_p = px.pie(dom_df, values='count', names='domain', hole=0.5, template="plotly_dark")
        st.plotly_chart(fig_p, use_container_width=True)

    with row3_r:
        st.subheader("📋 RECONNAISSANCE LOGS")
        st.dataframe(f_df[['event_datetime_utc', 'source_name', 'claim_text', 'severity_score', 'confidence_score', 'information_status']], use_container_width=True)

else:
    st.warning("Awaiting Ingestion Stream...")
