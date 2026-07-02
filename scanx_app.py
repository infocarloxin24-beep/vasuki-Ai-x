import streamlit as st
import sqlite3
from datetime import datetime
from scanx_engine import ScanXAdvancedEngine

conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()
engine = ScanXAdvancedEngine()

c.execute('''CREATE TABLE IF NOT EXISTS votes (user_id INTEGER, post_id INTEGER, timestamp TEXT)''')
conn.commit()

st.title("HumotiX AI - Bot Detector")
scan_mode = st.radio("Scan Mode:", ["Auto - X API/Nitter", "Manual - Khud bharo"])
st.subheader("🛠️ Scan X Advanced Engines Settings")
enable_stylo = st.toggle("👍 Enable AI Stylometry Analysis", value=True)
enable_heartbeat = st.toggle("💗 Enable MAD Server Heartbeat Engine", value=True)
enable_cib = st.toggle("🌐 Enable Cross-Platform Persona Tracker", value=True)

username = st.text_input("Username", "user12345")
comment_text = st.text_area("Post/Comment Text Daalo", "")

if st.button("🚀 Scan Karo"):
    user_id = 1
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO votes (user_id, post_id, timestamp) VALUES (?,?,?)", (user_id, 1, current_time))
    conn.commit()

    hb_result = {"verdict": "Disabled", "bot_probability": 0}
    style_result = {"verdict": "Disabled", "ai_probability": 0}
    cib_result = {"verdict": "Disabled", "coordinated_risk_score": 0}

    if enable_heartbeat:
        timestamps = c.execute("SELECT timestamp FROM votes WHERE user_id=? ORDER BY timestamp DESC LIMIT 15", (user_id,)).fetchall()
        hb_result = engine.analyze_server_heartbeat([t[0] for t in timestamps])
    if enable_stylo and comment_text:
        style_result = engine.analyze_stylometry([comment_text])
    if enable_cib:
        cib_result = engine.cross_platform_persona_tracker(username, comment_text)

    st.markdown("---")
    st.caption(f"*1. Heartbeat Check:* {hb_result['verdict']} | Score: {hb_result['bot_probability']}%")
    st.caption(f"*2. AI Text Check:* {style_result['verdict']} | Score: {style_result['ai_probability']}%")
    st.caption(f"*3. Network Check:* {cib_result['verdict']} | Score: {cib_result['coordinated_risk_score']}%")
    st.markdown("---")
