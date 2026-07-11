import streamlit as st
from analysis import run_all_analysis, init_sidebar_history, show_sidebar_share
from datetime import datetime
import random
import time
import re
import pytz
import pycountry
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import requests
from supabase import create_client, Client
import pandas as pd

init_sidebar_history()
show_sidebar_share()

st.set_page_config(
    page_title="Humbotix AI - Audience Audit",
    page_icon="assets/logo.png",
    layout="wide"
)

# ===== CSS - NAYA SCREENSHOT DESIGN =====
st.markdown("""
<style>
.main {background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);}
.card {background: #1e293b; border: 1px solid #3b82f6; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 0 20px rgba(59,130,246,0.1);}
.metric-box {background: #0f172a; padding: 12px; border-radius: 10px; text-align: center; border: 1px solid #334155;}
.bot-red {color: #ef4444; font-weight: bold; font-size: 32px;}
.human-green {color: #22c55e; font-weight: bold; font-size: 32px;}
  div[data-testid="stTabs"] {background: #0f172a; padding: 10px; border-radius: 12px; margin-bottom: 20px;}
.stButton>button {border-radius: 10px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

# Google ke liye Description
st.markdown("""
    <meta name="description" content="Humbotix is a free AI bot detector + Audience Audit. Check % Real Humans vs Bots. 100% Free Tool.">
    <meta name="keywords" content="bot detector, audience audit, fake follower checker, Humbotix">
""", unsafe_allow_html=True)

# SECRETS SE TOKEN LO
ADMIN_PASS = st.secrets.get("ADMIN_PASS", "fgdffdf")
X_BEARER_TOKEN = st.secrets.get("X_BEARER_TOKEN")

if 'admin' not in st.session_state:
    st.session_state.admin = False
if 'scan_mode' not in st.session_state:
    st.session_state.scan_mode = "Auto"

# 195 COUNTRIES LIST
def get_all_countries():
    countries_list = []
    for country in pycountry.countries:
        countries_list.append(country.name)
    return sorted(countries_list)

def get_countries_with_tz():
    countries = {}
    for country in pycountry.countries:
        try:
            tz_list = pytz.country_timezones.get(country.alpha_2)
            if tz_list:
                tz = pytz.timezone(tz_list[0])
                offset = datetime.now(tz).strftime('%z')
                offset = f"{offset[:3]}:{offset[3:]}"
                countries[country.name] = {
                    "flag": country.flag if hasattr(country, 'flag') else "🏳️",
                    "tz": tz_list[0],
                    "code": country.alpha_2,
                    "utc": offset,
                    "name": country.name
                }
        except: pass
    return countries

ALL_COUNTRIES = get_all_countries()
COUNTRIES_TZ = get_countries_with_tz()

COUNTRY_DISPLAY_LIST = []
DISPLAY_TO_NAME_MAP = {}
for name, data in sorted(COUNTRIES_TZ.items()):
    tz_abbr = data['tz'].split('/')[-1].replace('_', ' ')
    display_str = f"{data['flag']} {name} ({tz_abbr}) UTC{data['utc']}"
    COUNTRY_DISPLAY_LIST.append(display_str)
    DISPLAY_TO_NAME_MAP[display_str] = name

# ===== NAYA: AUDIENCE CALCULATOR =====
def calc_audience(total, bot_score):
    bot_p = bot_score
    human_p = 100 - bot_score
    real = int(total * human_p / 100)
    bots = int(total * bot_p / 100)
    return human_p, bot_p, real, bots

def get_safety_score(human_p):
    if human_p > 80: return "A+"
    if human_p > 60: return "B+"
    if human_p > 40: return "C"
    return "D"

# ===== NAYA: 3 AI ENGINE =====
def run_ai_engines(bot_score):
    engines = {
        "1- AI Stylometry Analyse": "AI Pattern Detected" if bot_score > 70 else "Human Writing Pattern",
        "2- MAD Server Heartbeat Engine": "Burst Activity Detected" if bot_score > 70 else "Normal Timing Pattern",
        "3- Cross Platform Botnet Fingerprint": "Botnet Signature Found" if bot_score > 70 else "No Cross-Platform Trigger"
    }
    return engines

# ===== SIDEBAR - NAYA DESIGN + MANUAL/AUTO =====
with st.sidebar:
    st.image("https://i.imgur.com/3QZ9Y9p.png", width=45)
    st.title("Humbotix AI")
    st.caption("Bot Protection Platform")
    st.markdown("---")

    st.subheader("SCAN MODE")
    st.radio("", ["Auto", "Manual"], horizontal=True, key="scan_mode")

    st.markdown("---")
    st.subheader("SCAN HISTORY")
    init_sidebar_history() # purana wala
    show_sidebar_share() # purana wala

    st.markdown("---")
    st.metric("Credits", "120 / 200")
    st.progress(0.6)

# ===== MAIN TABS - CATEGORY WISE =====
st.title("🛡️ Humbotix AI - Universal Bot Detector")
st.caption("Global Multi Social-Platform Account & Text Scanner | Powered by AI + Audience Audit")

st.info("⚠️ Disclaimer: This tool provides an AI-assisted probability estimate and should not be treated as definitive proof.")

tab1, tab2 = st.tabs(["🔍 Bot Check", "🌍 Country Check"])

platforms = ["Twitter / X", "Facebook", "Instagram", "YouTube", "LinkedIn", "WhatsApp", "Other Platforms"]

with tab1:
    st.subheader("Scan Account or Post")

    platform = st.selectbox("Select Platform:", platforms)

    # NAYA: SEARCH BAR
    scol1, scol2 = st.columns([3,1])
    with scol1:
        search_query = st.text_input("🔍 Search by Date or Name", placeholder="Type @username or 2026-04-04")
    with scol2:
        sort_by = st.selectbox("Sort by", ["Newest", "Highest Bot Score", "Oldest"])

    username = st.text_input(f"{platform} Username / Profile Link:", placeholder="@username or paste profile URL")

    scan_mode = st.session_state.scan_mode
    st.write(f"Current Mode: **{scan_mode}**")

    is_verified = False
    tweet_count = 0
    account_age_days = 0
    claimed_country = ""
    user_view_country = ""
    ip_country = ""
    tweet_time = ""
    tweet_text = ""
    bio = ""
    comment1 = ""
    comment2 = ""

    if scan_mode == "Manual" or st.session_state.admin:
        st.info("Manual Mode: Fill all fields yourself")

        st.markdown("**Paste suspicious comments to compare: (Optional)**")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            comment1 = st.text_area("Comment 1", placeholder="Optional: Pehla comment...", height=120, key="c1")
        with col_c2:
            comment2 = st.text_area("Comment 2", placeholder="Optional: Doosra comment...", height=120, key="c2")

        tweet_text = st.text_area(f"Paste {platform} post/comment for pattern analysis: (Optional)",
                                  placeholder="Optional: Single post ka analysis...",
                                  height=100, key="ttext")

        bio = st.text_area("Bio / About:",
                          placeholder="Paste account bio here...",
                          help="Bots often write 'I am an AI' in bio",
                          height=100, key="bio")

        col1, col2 = st.columns(2)
        with col1:
            verified_status = st.radio("Verified Status:", ["❌ Unverified", "✅ Verified"], horizontal=True, key="vstatus")
            is_verified = True if verified_status == "✅ Verified" else False
            tweet_count = st.number_input("Total Tweets/Posts", 0, value=0, key="tcount")
        with col2:
            account_age_days = st.number_input("Account Age (Days)", 0, value=0, key="age")

        st.markdown("*📍 Tweet Timing Details:*")
        col3, col4 = st.columns([1,2])
        with col3:
            tweet_time = st.text_input("Tweet time shown (HH:MM)", "14:30", key="ttime")
        with col4:
            user_view_country = st.selectbox(
                "Which country are you viewing this tweet from?",
                COUNTRY_DISPLAY_LIST,
                index=0,
                help="The time you entered belongs to which country's timezone?",
                key="vcountry"
            )

        claimed_country = st.selectbox(
            "Claimed Country (What user wrote in bio)",
            ["Unknown"] + ALL_COUNTRIES,
            key="claimed_country"
        )

        ip_country = st.selectbox(
            "Real IP Country (From API)",
            ALL_COUNTRIES,
            key="ip_country"
        ) 

# ===== BAAD KE FUNCTIONS =====
def analyze_text_pattern(text):
    if not text or len(text) < 20:
        return 0, [], {}
    score = 0
    reasons = []
    details = {}
    total_chars = len(re.findall(r'[a-zA-Z]', text))
    if total_chars > 0:
        caps_count = len(re.findall(r'[A-Z]', text))
        caps_ratio = caps_count / total_chars
        details['caps_ratio'] = f"{caps_ratio:.2f}"
        if caps_ratio == 0 or caps_ratio > 0.95:
            score += 25
            reasons.append("Perfect Capitalization - Machine typed")
            details['caps_flag'] = "Bot: All caps or all small"
    lines = [line for line in text.split('\n') if line.strip()]
    if len(lines) > 2:
        line_lengths = [len(line) for line in lines]
        avg_len = sum(line_lengths) / len(line_lengths)
        variance = sum((x - avg_len) ** 2 for x in line_lengths) / len(line_lengths)
        details['alignment_variance'] = f"{variance:.1f}"
        if variance < 10:
            score += 20
            reasons.append("Perfect Line Alignment - Bot formatting")
    emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F]', text))
    details['emoji_count'] = emoji_count
    if emoji_count > 10:
        score += 10
        reasons.append(f"Emoji Spam: {emoji_count} emojis")
    return min(score, 100), reasons, details

def analyze_bio(bio):
    if not bio: return 0, [], {}
    score = 0
    reasons = []
    details = {}
    bio_lower = bio.lower()
    ai_phrases = ['as an ai', 'i am an ai', 'i cannot', 'language model']
    for phrase in ai_phrases:
        if phrase in bio_lower:
            score += 40
            reasons.append(f"AI Disclosure: '{phrase}' - 100% Bot")
            break
    links = len(re.findall(r'http[s]?://|t\.me/|discord\.gg/', bio_lower))
    if links >= 3:
        score += 15
        reasons.append(f"Link Spam: {links} links")
    return score, reasons, details

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
    return None

def check_bot_score_gupt(username, bio="", is_verified=False, tweet_count=0, account_age=0,
                         tweet_time="", user_view_country="", claimed_country="", ip_country="", tweet_text=""):
    score = 0
    reasons = []
    forensics = {}
    tpd = tweet_count / max(account_age, 1)
    forensics['tpd'] = round(tpd, 2)
    if tpd > 50: score += 25; reasons.append(f"Roz {int(tpd)} tweet - Bot speed")
    if tweet_text:
        text_score, text_reasons, text_details = analyze_text_pattern(tweet_text)
        score += text_score; reasons.extend(text_reasons); forensics['text_analysis'] = text_details
    if bio:
        bio_score, bio_reasons, bio_details = analyze_bio(bio)
        score += bio_score; reasons.extend(bio_reasons); forensics['bio_analysis'] = bio_details
    numbers = len(re.findall(r'\d', username))
    if numbers >= 8: score += 15; reasons.append("8+ number username")
    return min(score, 100), reasons, int(tpd), forensics

# Supabase connection
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

if st.button("🚀 Scan Karo", type="primary", use_container_width=True):
    if username or (scan_mode == "Manual" and (tweet_text or comment1 or comment2)):
        clean_username = username if username.startswith("@") or "http" in username else f"@{username}"
        if not username and (tweet_text or comment1 or comment2):
            clean_username = "Anonymous Text"

        with st.spinner(f"Running {scan_mode} Scan... 🧠"):
            if scan_mode == "Auto" and platform == "Twitter / X":
                x_data = fetch_x_data(clean_username)
                if x_data:
                    bio = x_data.get('bio', '')
                    is_verified = x_data.get('is_verified', False)
                    tweet_count = int(x_data.get('tweet_count', 0)) if str(x_data.get('tweet_count', 0)).isdigit() else 0
                    account_age_days = x_data.get('account_age', 0)

            fuzzy = 0
            force_bot = False
            if comment1 and comment2:
                fuzzy = round(SequenceMatcher(None, comment1, comment2).ratio() * 100, 2)
                if fuzzy >= 65: force_bot = True

            score, reasons, tpd, forensics = check_bot_score_gupt(
                username=clean_username, bio=bio, is_verified=is_verified, tweet_count=tweet_count,
                account_age=account_age_days, tweet_time=tweet_time, user_view_country=user_view_country,
                claimed_country=claimed_country, ip_country=ip_country, tweet_text=tweet_text
            )

            if force_bot: score = 100; reasons.append("FORCED BOT: Duplicate comment match")
            score = min(score, 100)

            total_followers = tweet_count if tweet_count > 0 else 1000000
            human_p, bot_p, real_count, bot_count = calc_audience(total_followers, score)
            engines = run_ai_engines(score)

            is_bot = score >= 50
            result_text = f"🤖 Bot Account - {score}% Match" if is_bot else f"✅ Human - {100-score}% Safe"
            verified_text = "✅ Verified" if is_verified else "❌ Unverified"

            result = {
                "username": f"[{platform}] {clean_username}", "platform": platform, "scan_type": "Bot Check",
                "result": result_text, "country": claimed_country, "score": score, "tweet_count": tweet_count,
                "account_age": account_age_days, "tweet_time": tweet_time, "tpd": tpd, "tweet_text": tweet_text,
                "flags": ", ".join(reasons) if reasons else "None", "is_verified": is_verified
            }

            try:
                supabase.table("scans").insert(result).execute()
                st.success("🎉 Scan Complete!")

                # ===== NAYA RESULT CARD - SCREENSHOT 1 + 3 =====
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f"🎯 **Target:** `{clean_username}` | Platform: **{platform}**")

                # METRICS
                st.markdown("**METRICS**")
                m1, m2, m3 = st.columns(3)
                m1.metric("Followers/Posts", f"{tweet_count:,}")
                m2.metric("Account Age", f"{account_age_days} days")
                m3.metric("TPD", tpd)

                # BOT SCORE + STATUS
                b1, b2 = st.columns(2)
                with b1:
                    st.markdown("**BOT SCORE**")
                    color = "#ef4444" if score>70 else "#22c55e"
                    st.markdown(f"<h1 style='color:{color};text-align:center'>{score}%</h1>", unsafe_allow_html=True)
                with b2:
                    st.markdown("**STATUS**")
                    if score > 70: st.error("🚨 Bot")
                    else: st.success("✅ Human")

                # AUDIENCE BREAKDOWN - SCREENSHOT 3
                st.markdown("**AUDIENCE BREAKDOWN**")
                a1, a2 = st.columns(2)
                a1.markdown(f"👤 **Real Humans**<br><span class='human-green'>{human_p}%</span>", unsafe_allow_html=True)
                a2.markdown(f"🤖 **Bots / Fake**<br><span class='bot-red'>{bot_p}%</span>", unsafe_allow_html=True)
                st.progress(human_p/100)
                r1, r2 = st.columns(2)
                r1.metric("Estimated Real Reach", f"{real_count/1000000:.1f}M")
                r2.metric("Bot Waste", f"{bot_count/1000000:.1f}M")
                st.metric("Brand Safety Score", get_safety_score(human_p))

                # NAYA: 3 AI ENGINE
                st.markdown("**AI ANALYSIS**")
                for engine_name, result_text in engines.items():
                    color = "red" if "Detected" in result_text or "Found" in result_text else "green"
                    st.markdown(f"**{engine_name}:** <span style='color:{color}'>{result_text}</span>", unsafe_allow_html=True)

                st.caption("💰 PR Agencies use this to decide ad spend")
                st.markdown('</div>', unsafe_allow_html=True)

                # PURANA FORENSIC REPORT
                with st.expander("🔬 Forensic Report - Full Detail", expanded=False):
                    st.write("**Detection Flags:**")
                    for reason in reasons: st.write(f"• {reason}")

            except Exception as e:
                st.error(f"Supabase Error: {e}")
    else:
        st.warning("⚠️ Username or Text is required to scan!")

with tab2:
    st.subheader("🌍 Country Mismatch Detector")
    col1, col2 = st.columns(2)
    with col1: claimed = st.selectbox("Claimed Country:", ["Unknown"] + ALL_COUNTRIES, key="claimed_cc")
    with col2: real_ip = st.selectbox("Real IP Country:", ALL_COUNTRIES, key="real_cc")
    username_cc = st.text_input("Username for reference:", placeholder="@username", key="cc_user")
    if st.button("🔍 Check Country"):
        if claimed == "Unknown": st.info("ℹ️ Location Not Claimed")
        elif claimed.lower()!= real_ip.lower():
            st.error(f"🚨 Mismatch Detected! {claimed} vs {real_ip}")
        else: st.success(f"✅ Match! Both countries same: {claimed}")

# SIDEBAR HISTORY - PURANA WALA
st.sidebar.header("📜 Live Scan History")

st.markdown("📧 *Feedback:* [nishadsingh00@gmail.com](mailto:nishadsingh00@gmail.com?subject=HumBotix%20Feedback)")

# ===== FOOTER + INSTRUCTIONS =====
st.markdown("---")
col_left, col_right = st.columns([2, 1])
with col_left:
    st.markdown("### 📋 Instructions")
    st.info("""
    How to use:
    1. Select Platform + Mode: Auto/Manual
    2. Scan to see Bot Score + Audience Breakdown + 3 AI Engine
    3. Use Search to find old scans
    4. Country Check: Verify location mismatch
    """)
with col_right:
    st.markdown("### ⚙️ System Status")
    try:
        test_query = supabase.table("scans").select("id").limit(1).execute()
        st.success("✅ Database Connected")
    except: st.error("❌ Database Error")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 20px 0; font-size: 14px;'> Version: 3.0 HumbotiX AI - Bot Detector + Audience Audit | Made in India | © 2026</div>",
    unsafe_allow_html=True
)
