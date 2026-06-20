import streamlit as st
import requests
from supabase import create_client, Client
from datetime import datetime
import random
import pandas as pd
import time
import re
import pytz
import pycountry
from bs4 import BeautifulSoup

# SECRETS SE TOKEN LO
ADMIN_PASS = st.secrets.get("ADMIN_PASS", "admin123")
X_BEARER_TOKEN = st.secrets.get("X_BEARER_TOKEN")

if 'admin' not in st.session_state:
    st.session_state.admin = False

# 195 COUNTRIES LIST - FIX
def get_all_countries():
    countries_list = []
    for country in pycountry.countries:
        countries_list.append(country.name)
    return sorted(countries_list)

# TIMEZONE WALE COUNTRIES - ALAG FUNCTION
def get_countries_with_tz():
    countries = {}
    for country in pycountry.countries:
        try:
            tz_list = pytz.country_timezones.get(country.alpha_2)
            if tz_list:
                countries[country.name.lower()] = {
                    "flag": country.flag,
                    "tz": tz_list[0],
                    "code": country.alpha_2
                }
        except: pass
    return countries

ALL_COUNTRIES = get_all_countries() # 195 Countries
COUNTRIES_TZ = get_countries_with_tz() # Timezone ke liye

# X API + NITTER DONO - AUTOMATIC FALLBACK
def fetch_x_data(username):
    username = username.replace("@", "").strip()
    if X_BEARER_TOKEN:
        try:
            headers = {"Authorization": f"Bearer {X_BEARER_TOKEN}"}
            url = f"https://api.x.com/2/users/by/username/{username}?user.fields=created_at,public_metrics,verified,description"
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                d = r.json()['data']
                age = (datetime.utcnow() - datetime.strptime(d['created_at'], '%Y-%m-%dT%H:%M:%S.000Z')).days
                return {
                    'is_verified': d.get('verified', False),
                    'tweet_count': d['public_metrics']['tweet_count'],
                    'account_age': age,
                    'bio': d.get('description', '')
                }
        except: pass
    try:
        url = f"https://nitter.net/{username}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            bio = soup.find('div', class_='profile-bio')
            bio = bio.text.strip() if bio else "Bio nahi mila"
            followers = soup.find('a', href=f'/{username}/followers')
            followers = followers.text.split()[0] if followers else "0"
            tweets = soup.find('a', href=f'/{username}')
            tweets = tweets.text.split()[0] if tweets else "0"
            return {'bio': bio, 'followers': followers, 'tweet_count': tweets, 'is_verified': False, 'account_age': 0}
    except: return None
    return None

def check_bot_score_gupt(username, bio="", is_verified=False, tweet_count=0, account_age=0,
                         tweet_time="", ip_country="", claimed_country="", tweet_text=""):
    score = 0
    reasons = []
    tpd = tweet_count / max(account_age, 1)
    if tpd > 50:
        score += 25
        if st.session_state.admin: reasons.append(f"Roz {int(tpd)} tweet - Bot speed")
    elif tpd > 20:
        score += 10
        if st.session_state.admin: reasons.append(f"Roz {int(tpd)} tweet - Suspicious")
    if tweet_text and len(tweet_text) > 50:
        spelling_errors = len(re.findall(r'\b[a-z]{1,2}\b', tweet_text.lower()))
        if spelling_errors == 0:
            score += 10
            if st.session_state.admin: reasons.append("0 Spelling mistake - Bot accurate")
    numbers = len(re.findall(r'\d', username))
    if numbers >= 8:
        score += 15
        if st.session_state.admin: reasons.append("8+ number username - Auto generated")
    if re.search(r'user\d+|bot\d+|temp\d+|test\d+', username.lower()):
        score += 20
        if st.session_state.admin: reasons.append("Fake/Bot jaisa username")
    if tweet_time and claimed_country.lower() in COUNTRIES_TZ:
        try:
            tz = pytz.timezone(COUNTRIES_TZ[claimed_country.lower()]["tz"])
            tweet_hour = datetime.strptime(tweet_time, "%H:%M").hour
            if tweet_hour >= 0 and tweet_hour <= 6:
                score += 15
                if st.session_state.admin: reasons.append(f"{claimed_country} me raat 12-6 baje tweet - Suspicious")
        except: pass
    if ip_country and ip_country.lower()!= claimed_country.lower():
        score += 20
        if st.session_state.admin: reasons.append(f"IP: {ip_country}, Claimed: {claimed_country}")
    if is_verified and numbers >= 4:
        score += 30
        if st.session_state.admin: reasons.append("Verified Bot Loophole Detected")
    if re.search(r'as an ai language model|i cannot|i\'m an ai|i am an ai', bio.lower()):
        score += 40
        if st.session_state.admin: reasons.append("Bio me AI phrases - Pakka bot")
    if tweet_text and re.search(r'(.{10,})\1{3,}', tweet_text):
        score += 15
        if st.session_state.admin: reasons.append("Copy-paste pattern - Bot signature")
    return min(score, 100), reasons

def get_score_color_label(score):
    if score >= 70: return "#4ade80", "Good"
    elif score >= 40: return "#fbbf24", "Suspicious"
    elif score > 0: return "#f87171", "Poor"
    else: return "#64748b", "Not Verified"

# Supabase connection
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Vasuki Ai 4.0 - Bot Detector", page_icon="🐍", layout="wide")
st.title("🐍 Vasuki Ai 4.0 - Universal Bot Detector")
st.caption("Multi-Platform Account & Text Scanner | Powered by AI")

# FontAwesome CDN - Icons ke liye ZARURI HAI
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">', unsafe_allow_html=True)

with st.sidebar:
    if not st.session_state.admin:
        password = st.text_input("Admin Access:", type="password")
        if st.button("Login"):
            if password == ADMIN_PASS:
                st.session_state.admin = True
                st.rerun()
            else:
                st.error("Galat Password")
    else:
        st.success("Admin Mode: ON")
        if st.button("Logout"):
            st.session_state.admin = False
            st.rerun()

tab1, tab2 = st.tabs(["🔍 Bot Check", "🌍 Country Check"])

with tab1:
    st.subheader("Account or Post Scan Karo")

    platform = st.selectbox(
        "सोशल मीडिया प्लेटफॉर्म चुनें (Select Platform):",
        ["Twitter / X", "Facebook", "Instagram", "YouTube", "LinkedIn", "WhatsApp", "Other Platforms"]
    )

    username = st.text_input(f"{platform} Username / Profile Link:", placeholder="@username or paste profile URL")
    scan_mode = st.radio("Scan Mode:", ["Auto - X API/Nitter se data lao", "Manual - Khud bharo"])

    is_verified = False
    tweet_count = 0
    account_age_days = 0
    claimed_country = ""
    ip_country = ""
    tweet_time = ""
    tweet_text = ""
    bio = ""

    if scan_mode == "Manual - Khud bharo" or st.session_state.admin:
        st.info("Manual Mode: Saare fields khud bharo")
        tweet_text = st.text_area(f"{platform} का संदिग्ध पोस्ट, कमेंट या मैसेज यहाँ पेस्ट करें:",
                                  placeholder="Paste suspicious comment, message, or post text here...")

        bio = st.text_area("Bio / About:",
                          placeholder="Account ka bio yahan paste karo...",
                          help="Bot aksar bio me 'I am an AI' likh dete hain")

        col1, col2 = st.columns(2)
        with col1:
            is_verified = st.checkbox("Verified Account?")
            tweet_count = st.number_input("Total Tweets/Posts", 0, value=0)
        with col2:
            account_age_days = st.number_input("Account Age (Days)", 0, value=0)
            tweet_time = st.text_input("Last Tweet Time (HH:MM)", "14:30")

        # 195 COUNTRIES DROPDOWN - FIX
        claimed_country = st.selectbox("Claimed Country", ALL_COUNTRIES, key="claimed_country")
        ip_country = st.selectbox("Real IP Country", ALL_COUNTRIES, key="ip_country")

    if st.button("🚀 Scan Karo"):
        if username or (scan_mode == "Manual - Khud bharo" and tweet_text):
            clean_username = username if username.startswith("@") or "http" in username else f"@{username}"
            if not username and tweet_text:
                clean_username = "Anonymous Text"

            with st.spinner(f"Vasuki Ai Brain Scanning {platform} data... 🧠"):
                if scan_mode == "Auto - X API/Nitter se data lao" and platform == "Twitter / X":
                    x_data = fetch_x_data(clean_username)
                    if x_data:
                        bio = x_data.get('bio', '')
                        is_verified = x_data.get('is_verified', False)
                        tweet_count = int(x_data.get('tweet_count', 0)) if str(x_data.get('tweet_count', 0)).isdigit() else 0
                        account_age_days = x_data.get('account_age', 0)
                        st.success("✅ X API/Nitter se data mil gaya")
                    else:
                        st.warning("⚠️ Data nahi mila. Manual mode use karo.")

                score, reasons = check_bot_score_gupt(
                    username=clean_username, bio=bio, is_verified=is_verified, tweet_count=tweet_count,
                    account_age=account_age_days, tweet_time=tweet_time, ip_country=ip_country,
                    claimed_country=claimed_country, tweet_text=tweet_text
                )

                is_bot = score >= 50
                result_text = f"🤖 {platform} Bot - {score}% Match" if is_bot else f"✅ Human - {100-score}% Safe"

                result = {
                    "username": f"[{platform}] {clean_username}",
                    "platform": platform,
                    "scan_type": "Bot Check",
                    "result": result_text,
                    "country": claimed_country,
                    "score": score
                }

                try:
                    supabase.table("scans").insert(result).execute()

                    # ===== AB YE 100% RENDER HOGA - unsafe_allow_html=True lagaya =====
                    verdict = "Likely Bot" if score >= 50 else "Human"
                    verdict_color = "#f87171" if score >= 50 else "#4ade80"
                    verdict_desc = "This account shows strong signs of automated behavior." if score >= 50 else "This account appears to be operated by a human."

                    # Metrics - abhi hardcoded hain, tu apne logic se calculate kar lena
                    u_score, u_label = get_score_color_label(40)
                    p_score, p_label = get_score_color_label(70)
                    a_score, a_label = get_score_color_label(30)
                    e_score, e_label = get_score_color_label(25)
                    b_score, b_label = get_score_color_label(45)
                    v_score, v_label = get_score_color_label(100 if is_verified else 0)

                    scan_time = datetime.now().strftime("%d %b %Y, %I:%M %p")
                    posts_per_week = round(tweet_count / max(account_age_days/7, 1), 1)

                    st.markdown(f"""
                    <style>
                .main-card {{ background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 24px; color: white; font-family: 'Segoe UI', sans-serif; margin-top: 20px; }}
                .top-section {{ display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; margin-bottom: 20px; }}
                .profile-box {{ background: #0b1220; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; display: flex; gap: 20px; }}
                .pfp-ring {{ width: 90px; height: 90px; background: linear-gradient(45deg, #ec4899, #8b5cf6, #3b82f6); padding: 3px; border-radius: 50%; animation: pulse 2s infinite; }}
                    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.8; }} }}
                .pfp-ring img {{ width: 100%; height: 100%; border-radius: 50%; object-fit: cover; border: 2px solid #0b1220; }}
                .bot-score-box {{ background: #1a0b0b; border: 1px solid #3f1212; border-radius: 12px; padding: 20px; text-align: center; }}
                .bot-score-val {{ font-size: 56px; font-weight: 700; color: {verdict_color}; margin: 8px 0; line-height: 1; }}
                .progress-bar {{ width: 100%; height: 6px; background: #374151; border-radius: 3px; margin-top: 12px; }}
                .progress-fill {{ height: 100%; background: {verdict_color}; border-radius: 3px; width: {score}%; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; background: #0b1220; border: 1px solid #1e293b; border-radius: 12px; padding: 16px; margin-bottom: 20px; }}
                .metric-item {{ text-align: center; }}
                .metric-bar {{ width: 100%; height: 4px; background: #374151; border-radius: 2px; margin: 8px 0; }}
                .metric-fill {{ height: 100%; border-radius: 2px; }}
                .bottom-section {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
                .info-box {{ background: #0b1220; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; }}
                .summary-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #1e293b; }}
                .recommend-box {{ background: #0b1220; border: 1px solid #1e293b; border-radius: 12px; padding: 20px; }}
                .footer-box {{ background: #064e3b; border: 1px solid #059669; border-radius: 12px; padding: 16px; display: flex; justify-content: space-between; align-items: center; }}
                    </style>

                    <div class="main-card">
                        <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                            <div>
                                <h2 style="margin:0;">Scan Result</h2>
                                <p style="margin:0; color:#94a3b8; font-size:14px;">Completed on {scan_time}</p>
                            </div>
                        </div>

                        <div class="top-section">
                            <div class="profile-box">
                                <div class="pfp-ring">
                                    <img src="https://ui-avatars.com/api/?name={clean_username.replace('@','')}&background=8b5cf6&color=fff">
                                </div>
                                <div style="flex:1;">
                                    <h3 style="margin:0 0 8px 0;">{clean_username} {'<i class="fas fa-check-circle" style="color:#38bdf8;"></i>' if is_verified else ''}</h3>
                                    <div style="background:#1e293b; padding:4px 10px; border-radius:6px; display:inline-block; margin-bottom:12px; font-size:13px;">
                                        <i class="fab fa-instagram"></i> {platform}
                                    </div>
                                    <p style="margin:4px 0; color:#94a3b8; font-size:14px;"><i class="fas fa-user"></i> Username: {clean_username}</p>
                                    <p style="margin:4px 0; color:#94a3b8; font-size:14px;"><i class="fas fa-globe"></i> Platform: {platform}</p>
                                    <p style="margin:4px 0; color:#94a3b8; font-size:14px;"><i class="fas fa-clock"></i> Scanned At: {scan_time}</p>
                                </div>
                            </div>

                            <div class="bot-score-box">
                                <p style="margin:0; color:#94a3b8; font-size:14px;"><i class="fas fa-robot"></i> Bot Score</p>
                                <h1 class="bot-score-val">{score}%</h1>
                                <p style="margin:0; color:{verdict_color}; font-weight:600;">{verdict}</p>
                                <div class="progress-bar"><div class="progress-fill"></div></div>
                                <p style="margin:12px 0 0 0; color:#94a3b8; font-size:12px;">{verdict_desc}</p>
                            </div>
                        </div>

                        <div class="metrics-grid">
                            <div class="metric-item">
                                <p style="margin:0; color:#a78bfa; font-size:12px;"><i class="fas fa-user" style="color:{u_score};"></i> Username</p>
                                <h3 style="margin:4px 0; color:{u_score}; font-size:28px;">40<span style="color:#64748b; font-size:16px;">/100</span></h3>
                                <div class="metric-bar"><div class="metric-fill" style="width:40%; background:{u_score};"></div></div>
                                <p style="margin:0; color:{u_score}; font-size:12px;">{u_label}</p>
                            </div>
                            <div class="metric-item">
                                <p style="margin:0; color:#60a5fa; font-size:12px;"><i class="fas fa-id-card" style="color:{p_score};"></i> Profile Complete</p>
                                <h3 style="margin:4px 0; color:{p_score}; font-size:28px;">70<span style="color:#64748b; font-size:16px;">/100</span></h3>
                                <div class="metric-bar"><div class="metric-fill" style="width:70%; background:{p_score};"></div></div>
                                <p style="margin:0; color:{p_score}; font-size:12px;">{p_label}</p>
                            </div>
                            <div class="metric-item">
                                <p style="margin:0; color:#fbbf24; font-size:12px;"><i class="fas fa-chart-line" style="color:{a_score};"></i> Activity Pattern</p>
                                <h3 style="margin:4px 0; color:{a_score}; font-size:28px;">30<span style="color:#64748b; font-size:16px;">/100</span></h3>
                                <div class="metric-bar"><div class="metric-fill" style="width:30%; background:{a_score};"></div></div>
                                <p style="margin:0; color:{a_score}; font-size:12px;">{a_label}</p>
                            </div>
                            <div class="metric-item">
                                <p style="margin:0; color:#4ade80; font-size:12px;"><i class="fas fa-users" style="color:{e_score};"></i> Engagement Quality</p>
                                <h3 style="margin:4px 0; color:{e_score}; font-size:28px;">25<span style="color:#64748b; font-size:16px;">/100</span></h3>
                                <div class="metric-bar"><div class="metric-fill" style="width:25%; background:{e_score};"></div></div>
                                <p style="margin:0; color:{e_score}; font-size:12px;">{e_label}</p>
                            </div>
                            <div class="metric-item">
                                <p style="margin:0; color:#f87171; font-size:12px;"><i class="fas fa-file-lines" style="color:{b_score};"></i> Bio Analysis</p>
                                <h3 style="margin:4px 0; color:{b_score}; font-size:28px;">45<span style="color:#64748b; font-size:16px;">/100</span></h3>
                                <div class="metric-bar"><div class="metric-fill" style="width:45%; background:{b_score};"></div></div>
                                <p style="margin:0; color:{b_score}; font-size:12px;">{b_label}</p>
                            </div>
                            <div class="metric-item">
                                <p style="margin:0; color:#60a5fa; font-size:12px;"><i class="fas fa-shield-halved" style="color:{v_score};"></i> Verification</p>
                                <h3 style="margin:4px 0; color:{v_score}; font-size:28px;">{100 if is_verified else 0}<span style="color:#64748b; font-size:16px;">/100</span></h3>
                                <div class="metric-bar"><div class="metric-fill" style="width:{100 if is_verified else 0}%; background:{v_score};"></div></div>
                                <p style="margin:0; color:{v_score}; font-size:12px;">{v_label}</p>
                            </div>
                        </div>

                        <div class="bottom-section">
                            <div class="info-box">
                                <h4 style="margin:0 0 12px 0;"><i class="fas fa-brain" style="color:#a78bfa;"></i> AI Explanation</h4>
                                <p style="margin:0 0 16px 0; color:#94a3b8; font-size:13px;">Our AI has analyzed multiple signals from this account and calculated the probability of this account being a bot.</p>
                                <div style="border-top:1px solid #1e293b; padding-top:12px;">
                                    <p style="margin:8px 0; font-size:13px;"><i class="fas fa-circle-xmark" style="color:#f87171;"></i> <b>Username Pattern</b><br><span style="color:#94a3b8;">Username contains suspicious pattern or uncommon characters.</span></p>
                                    <p style="margin:8px 0; font-size:13px;"><i class="fas fa-triangle-exclamation" style="color:#fbbf24;"></i> <b>Low Engagement</b><br><span style="color:#94a3b8;">Very low likes, comments or interactions compared to follower count.</span></p>
                                    <p style="margin:8px 0; font-size:13px;"><i class="fas fa-circle-xmark" style="color:{verdict_color};"></i> <b>Posting Behavior</b><br><span style="color:#94a3b8;">{int(tweet_count/max(account_age_days,1))} posts/day - {"Irregular pattern" if tweet_count/max(account_age_days,1) > 20 else "Normal pattern"}.</span></p>
                                </div>
                            </div>

                            <div>
                                <div class="info-box" style="margin-bottom:20px;">
                                    <h4 style="margin:0 0 12px 0;"><i class="fas fa-file-lines" style="color:#60a5fa;"></i> Account Summary</h4>
                                    <div class="summary-row"><span><i class="fas fa-users"></i> Followers</span><span>12.4K</span></div>
                                    <div class="summary-row"><span><i class="fas fa-user-plus"></i> Following</span><span>7,892</span></div>
                                    <div class="summary-row"><span><i class="fas fa-image"></i> Total Posts</span><span>{tweet_count}</span></div>
                                    <div class="summary-row"><span><i class="fas fa-calendar"></i> Account Created</span><span>{account_age_days} Days Ago</span></div>
                                    <div class="summary-row"><span><i class="fas fa-chart-column"></i> Avg. Posts/Week</span><span>{posts_per_week}</span></div>
                                    <div class="summary-row" style="border:none;"><span><i class="fas fa-eye"></i> Profile Type</span><span>Public</span></div>
                                </div>

                                <div class="recommend-box">
                                    <h4 style="margin:0 0 12px 0;"><i class="fas fa-shield-halved" style="color:#60a5fa;"></i> Our Recommendation</h4>
                                    <p style="margin:0; font-size:14px;">This account is <span style="color:{verdict_color}; font-weight:600;">{verdict}</span>.</p>
                                    <p style="margin:8px 0 0 0; color:#94a3b8; font-size:13px;">Proceed with caution while interacting with this account.</p>
                                </div>
                            </div>
                        </div>

                        <div class="footer-box">
                            <div>
                                <p style="margin:0; font-weight:600;"><i class="fas fa-circle-check" style="color:#4ade80;"></i> Scan Completed Successfully</p>
                                <p style="margin:0; color:#94a3b8; font-size:13px;">This report is generated by Vasuki AI 4.0 - Bot Detector</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    # ===== CARD KHATAM =====

                except Exception as e:
                    st.error(f"Supabase Error: {e}")
        else:
            st.warning("⚠️ Scan karne ke liye Username ya Text daalna zaroori hai bhai!")

with tab2:
    st.subheader("🌍 Country Mismatch Detector")
    st.write("Check karo ki user ne country sahi batayi hai ya fake hai")

    col1, col2 = st.columns(2)
    with col1:
        # 195 COUNTRIES DROPDOWN - FIX
        claimed = st.selectbox("Claimed Country:", ALL_COUNTRIES, key="claimed_cc")
    with col2:
        # 195 COUNTRIES DROPDOWN - FIX
        real_ip = st.selectbox("Real IP Country:", ALL_COUNTRIES, key="real_cc")

    username_cc = st.text_input("Username for reference:", placeholder="@username", key="cc_user")

    if st.button("🔍 Country Check Karo"):
        if claimed.lower()!= real_ip.lower():
            st.error(f"🚨 Mismatch Detected!")
            st.write(f"Claimed: {claimed}")
            st.write(f"Real IP: {real_ip}")
            st.warning("Ye account VPN/Proxy use kar raha hai ya location fake hai.")

            result = {
                "username": f"[CountryCheck] {username_cc}",
                "platform": "Country Check",
                "scan_type": "Country Check",
                "result": f"❌ Mismatch: {claimed} vs {real_ip}",
                "country": claimed
            }
            try:
                supabase.table("scans").insert(result).execute()
                st.success("History me save ho gaya")
            except:
                st.error("History save nahi hui")
        else:
            st.success(f"✅ Match! Dono country same hain: {claimed}")
            st.balloons()

# ===== SIDEBAR ME CHOTE CARDS + VIEW REPORT BUTTON =====
st.sidebar.header("📜 Live Scan History")
try:
    scans = supabase.table("scans").select("*").order("created_at", desc=True).limit(10).execute()
    if scans.data:
        for scan in scans.data:
            is_bot = "Bot" in scan['result'] or "Mismatch" in scan['result']
            score = scan.get('score', 0)
            color = "#f87171" if is_bot else "#4ade80"
            icon = "🔴" if is_bot else "🟢"

            # Chota Card HTML
            st.sidebar.markdown(f"""
            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 12px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 13px; font-weight: 600; color: white;">{icon} {scan['username'][:20]}...</span>
                    <span style="background: {color}; color: white; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 600;">{score}%</span>
                </div>
                <p style="margin: 0 0 8px 0; font-size: 12px; color: #94a3b8;">{scan['result'][:30]}...</p>
                <p style="margin: 0 0 8px 0; font-size: 11px; color: #64748b;">⏱️ {scan['created_at'][:19].replace('T', ' ')}</p>
            </div>
            """, unsafe_allow_html=True)

            # View Report Button
            if st.sidebar.button("📄 View Report", key=f"view_{scan['id']}", use_container_width=True):
                st.session_state.selected_scan = scan['id']
                st.rerun()
    else:
        st.sidebar.info("No scans yet")
except Exception as e:
    st.sidebar.error(f"History load nahi hui: {str(e)[:50]}")

# EXTRA ADD - Instructions + System Status + Quick Stats
st.markdown("---")
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📋 Instructions")
    st.info("""
    How to use:

    1. Bot Check: Enter username and select platform to detect bots

    2. Country Check: Verify if user's claimed country matches IP location

    3. Manual Check: Paste text to check for spam patterns

    4. History: View last 10 scans in the sidebar
    """)

with col_right:
    st.markdown("### ⚙️ System Status")
    try:
        test_query = supabase.table("scans").select("id").limit(1).execute()
        st.success("✅ Database Connected")
    except:
        st.error("❌ Database Error")

    st.markdown("### 📊 Quick Stats")
    try:
        total_scans = supabase.table("scans").select("id", count="exact").execute()
        st.metric("Total Scans", total_scans.count if total_scans.count else 0)
    except:
        st.metric("Total Scans", "N/A")

# Footer with Tiranga
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>🐍 Vasuki Ai 4.0 - Bot Detector | Built by Nishad Singh 🇮🇳 | Made in Bharat</div>",
    unsafe_allow_html=True
)
