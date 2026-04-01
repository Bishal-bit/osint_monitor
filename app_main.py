import streamlit as st

st.set_page_config(page_title="Unified Intelligence System", layout="wide")

st.title("🧠 Unified Intelligence System")

st.markdown("### Choose Module")

col1, col2 = st.columns(2)

with col1:
    if st.button("🛰️ OMNI-RECON\nTactical Intelligence", use_container_width=True):
        st.switch_page("pages/1_OMNI_RECON.py")

with col2:
    if st.button("🤖 AI Analytics\nNLP + ML Insights", use_container_width=True):
        st.switch_page("pages/2_AI_ANALYTICS.py")
