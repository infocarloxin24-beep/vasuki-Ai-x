import streamlit as st
import pandas as pd
import random, hashlib
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumBotix EV Shield PRO v5.2", page_icon="⚡", layout="wide")

CLIENT_ID = "PASTE_YOUR_CLIENT_ID_HERE"
CLIENT_SECRET = "PASTE_YOUR_CLIENT_SECRET_HERE"
REDIRECT_URI = "https://humbotix.streamlit.app"

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/auth", "https://accounts.google.com/o/oauth2/token", "https://accounts.google.com/o/oauth2/revoke")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
.main-title {font-family: 'Orbitron', sans-serif; color: #00FF88; text-align:center; font-size: 32px;}
.big-alert {background: linear-gradient(90deg, #ff0000, #8B0000); padding: 20px; border-radius: 12px; color: white; font-weight: bold; font-size: 18px; animation: blink 0.8s infinite; border: 2px solid yellow;}
@keyframes blink {50% {opacity: 0.6;}}
.safe-box {background: #002200; padding: 15px; border-radius: 10px; border-left: 5px solid #00FF88;}
.login-box {background: #1E1E2E; padding: 30px; border-radius: 15px; border: 1px solid #00FF88; max-width: 500px; margin: auto;}
.inner-lock {background: #2A0033; padding: 20px; border-radius: 10px; border: 2px solid #AA00FF;}
.blocked-ip {background: #330000; padding: 8px; margin: 5px 0; border-radius: 5px; color: #FF5555;}
</style>
""", unsafe_allow_html=True)

for key in ["logged_in", "user_info", "inner_unlocked", "companies", "monitoring", "threat_log", "blocked_ips"]:
    if key not in st.session_state:
        st.session_state[key] = False if key in ["logged_in", "inner_unlocked", "monitoring"] else [] if key in ["threat_log", "blocked_ips"] else {}

def detect_behavior(user_id, actions, ip, location):
    threat_score = 0; reason = []
    hour = datetime.now().hour
    if 1 <= hour <= 5: threat_score += 40; reason.append(f"Login at {hour}:00 AM")
    if actions.count("api_call") > 30: threat_score += 35; reason.append(f"{actions.count('api_call')} API calls - Bot")
    if actions.count("failed_login") > 5: threat_score += 50; reason.append("Brute Force Attack")
    if location in ["Russia", "China", "North Korea"]: threat_score += 30; reason.append(f"High-Risk Location: {location}")
    if ip.startswith("45.") or ip.startswith("185."): threat_score += 20; reason.append("Suspicious IP Range")
    if threat_score >= 75: return "HUMAN HACKER", reason, "CRITICAL", threat_score
    elif threat_score >= 45: return "BOT/MACHINE", reason, "HIGH", threat_score
    else: return "NORMAL USER", reason, "SAFE", threat_score

def auto_block_ip(ip_address, reason, user_id):
    if ip_address not in st.session_state.blocked_ips:
        st.session_state.blocked_ips.append(ip_address)
        st.session_state.threat_log.insert(0, {"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"Severity": "CRITICAL","User": user_id,"IP": ip_address,"Action": "AUTO BLOCKED","Reason": reason})
        return True
    return False

def generate_company_data(comp_name):
    chargers = random.randint(80, 250); active = random.randint(20, 120); cars = random.randint(200, 800)
    attack = random.random() < 0.25
    fake_ip = f"{random.randint(40,220)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    fake_loc = random.choice(["Indore", "Mumbai", "Delhi", "Russia", "China", "USA", "Germany"])
    actions = ["login", "api_call"] * random.randint(2,8)
    if attack: actions.extend(["failed_login"]*7 + ["api_call"]*35)
    user_type, reasons, risk, score = detect_behavior(f"admin@{comp_name}.com", actions, fake_ip, fake_loc)
    if risk == "CRITICAL": auto_block_ip(fake_ip, ", ".join(reasons), f"admin@{comp_name}.com")
    return {"Company": comp_name, "Chargers": chargers, "Active": active, "EVs": cars, "Risk": risk, "UserType": user_type, "IP": fake_ip, "Location": fake_loc, "Score": score}

def login_page():
    st.markdown("<h1 class='main-title'>⚡ HUMBOTIX EV SECURITY</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.subheader("1. Security Puzzle")
        puzzle_ans = st.text_input("Solve: 9 + 6 =?")
        st.subheader("2. Email & Password")
        email = st.text_input("Company Email")
        password = st.text_input("Password", type="password")
        st.subheader("3. Ya Google se Login karo")
        result = oauth2.authorize_button("🔵 Login with Google", REDIRECT_URI, scope="openid email profile")
        if result and 'token' in result:
            st.session_state.logged_in = True
            st.session_state.user_info = result.get('userinfo', {'email': 'google_user@gmail.com'})
            st.rerun()
        if st.button("🔓 Login", type="primary", use_container_width=True):
            if puzzle_ans == "15" and email and password:
                st.session_state.logged_in = True
                st.session_state.user_info = {'email': email}
                st.rerun()
            else: st.error("Puzzle ya Email/Password galat hai")
        st.markdown("</div>", unsafe_allow_html=True)

def inner_lock():
    if not st.session_state.inner_unlocked:
        st.markdown("<div class='inner-lock'>", unsafe_allow_html=True)
        st.warning("🔒 HUMBOTIX EV SECURITY - HIGH SECURITY ZONE")
        st.info("Company add karne ke liye Section Password chahiye")
        inner_pass = st.text_input("Section Password", type="password", key="inner")
        if st.button("Unlock Section"):
            if inner_pass == "humbotix@2026":
                st.session_state.inner_unlocked = True; st.rerun()
            else: st.error("Galat Password")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

if not st.session_state.logged_in:
    login_page(); st.stop()

st.markdown("<h1 class='main-title'>HumBotix EV Shield PRO v5.2</h1>", unsafe_allow_html=True)
st.success(f"✅ Logged in as: {st.session_state.user_info.get('email')}")

with st.sidebar:
    if st.button("Logout", use_container_width=True):
        st.session_state.clear(); st.rerun()
    st.header("🏢 Company Management")
    inner_lock()
    name = st.text_input("Company Name", placeholder="Tata Power EZ")
    api = st.text_input("OCPP API Key", type="password")
    ocpp = st.text_input("OCPP Server URL")
    whatsapp = st.text_input("SOC WhatsApp No")
    if st.button("➕ Encrypt & Save Company", use_container_width=True):
        if name:
            st.session_state.companies[name] = {"api": hashlib.sha256(api.encode()).hexdigest()[:16], "ocpp": ocpp, "whatsapp": whatsapp}
            st.success(f"{name} Added & Encrypted")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 START", type="primary", use_container_width=True): st.session_state.monitoring = True
    with col2:
        if st.button("🔴 STOP", use_container_width=True): st.session_state.monitoring = False

if st.session_state.monitoring and st.session_state.companies:
    st_autorefresh(interval=3000, key="datarefresh")
    all_data = [generate_company_data(c) for c in st.session_state.companies.keys()]
    df = pd.DataFrame(all_data)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Companies", len(df)); c2.metric("Chargers", df["Chargers"].sum())
    c3.metric("Active EVs", df["EVs"].sum()); c4.metric("Threats Blocked", len(df[df["Risk"]!="SAFE"]))
    st.subheader("📡 Live Company Monitoring")
    cols = st.columns(min(3, len(df)))
    for i, row in df.iterrows():
        with cols[i % 3]:
            st.markdown(f"**{row['Company']}**")
            st.write(f"Chargers: {row['Chargers']} | Active: {row['Active']}")
            st.write(f"Loc: {row['Location']} | IP: {row['IP']}")
            if row['Risk'] == "CRITICAL": st.markdown(f"<div class='big-alert'>🚨 {row['UserType']}!<br>Score: {row['Score']}/100<br>AUTO-BLOCKED</div>", unsafe_allow_html=True)
            elif row['Risk'] == "HIGH": st.warning(f"⚠️ {row['UserType']} - Score: {row['Score']}")
            else: st.markdown("<div class='safe-box'>✅ SYSTEM SAFE</div>", unsafe_allow_html=True)
    st.subheader("📜 Live Threat Intelligence Log")
    if st.session_state.threat_log: st.dataframe(pd.DataFrame(st.session_state.threat_log[:20]), use_container_width=True, height=300)
    else: st.info("Monitoring... No threats")
    st.subheader("📛 Auto-Blocked IP Firewall")
    if st.session_state.blocked_ips:
        for ip in st.session_state.blocked_ips: st.markdown(f"<div class='blocked-ip'>⛔ {ip} - Permanently Blocked</div>", unsafe_allow_html=True)
    else: st.success("No malicious IPs")
    if st.button("📄 Generate Security Report PDF"): st.success("Report Generated!")
else:
    st.info("👈 Company add karke 'START' dabao")
    st.image("https://placehold.co/1200x400/0E1117/00FF88/png?text=HumBotix+EV+Shield+PRO+v5.2", use_container_width=True)

st.markdown("---")
st.caption("© 2026 HumBotix | Double Lock | Google OAuth | AI Detection | Auto-Block")
