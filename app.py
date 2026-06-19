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

# SECRETS SE TOKEN LO - dotenv hata diya
ADMIN_PASS = st.secrets.get("ADMIN_PASS", "admin123")
X_BEARER_TOKEN = st.secrets.get("X_BEARER_TOKEN")

if 'admin' not in st.session_state:
    st.session_state.admin = False

def get_all_countries():
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

COUNTRIES_TZ = get_all_countries()

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

# Supabase connection
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Vasuki Ai 4.0 - Bot Detector", page_icon="🐍", layout="wide")
st.title("🐍 Vasuki Ai 4.0 - Universal Bot Detector")
st.caption("Multi-Platform Account & Text Scanner | Powered by AI")

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

    # SOCIAL MEDIA DROPDOWN - YAHI HAI
    platform = st.selectbox(
        "सोशल मीडिया प्लेटफॉर्म चुनें (Select Platform):",
        ["Twitter / X", "Facebook", "Instagram", "YouTube", "LinkedIn", "WhatsApp", "Other Platforms"]
    )

    username = st.text_input(f"{platform} Username / Profile Link:", placeholder="@username or paste profile URL")
    scan_mode = st.radio("Scan Mode:", ["Auto - X API/Nitter se data lao", "Manual - Khud bharo"])

    # Variables default set
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

        claimed_country = st.selectbox("Claimed Country", list(COUNTRIES_TZ.keys()))
        ip_country = st.selectbox("Real IP Country", list(COUNTRIES_TZ.keys()))

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

                # TIMESTAMP HATA DIYA - SUPABASE AUTO CREATED_AT USE KAREGA
                result = {
                    "username": f"[{platform}] {clean_username}",
                    "platform": platform,
                    "scan_type": "Bot Check",
                    "result": result_text,
                    "country": claimed_country
                }

                try:
                    supabase.table("scans").insert(result).execute()
                    st.success("🎉 Scan Complete!")
                    st.subheader("📊 Bot Probability Meter")
                    st.progress(score/100)
                    st.metric("Bot Score", f"{score}%", delta=f"{'Danger' if score>=70 else 'Suspicious' if score>=50 else 'Safe'}", delta_color="inverse")
                    if is_bot:
                        st.error(f"🚨 RESULT: {result_text}")
                        if st.session_state.admin and reasons:
                            st.warning("Pakde Jaane Ke Karan:")
                            for reason in reasons:
                                st.write(f"• {reason}")
                        st.warning(f"Action Recommended: {platform} par is account ko report/block karein.")
                    else:
                        st.success(f"💚 RESULT: {result_text}")
                        st.write("यह कमेंट या अकाउंट पूरी तरह से सुरक्षित और मानवीय लग रहा है.")
                except Exception as e:
                    st.error(f"Supabase Error: {e}")
        else:
            st.warning("⚠️ Scan karne ke liye Username ya Text daalna zaroori hai bhai!")

with tab2:
    st.subheader("🌍 Country Mismatch Detector")
    st.write("Check karo ki user ne country sahi batayi hai ya fake hai")

    col1, col2 = st.columns(2)
    with col1:
        claimed = st.selectbox("Claimed Country:", list(COUNTRIES_TZ.keys()), key="claimed_cc")
    with col2:
        real_ip = st.selectbox("Real IP Country:", list(COUNTRIES_TZ.keys()), key="real_cc")

    username_cc = st.text_input("Username for reference:", placeholder="@username", key="cc_user")

    if st.button("🔍 Country Check Karo"):
        if claimed.lower()!= real_ip.lower():
            st.error(f"🚨 Mismatch Detected!")
            st.write(f"Claimed: {claimed} {COUNTRIES_TZ[claimed.lower()]['flag']}")
            st.write(f"Real IP: {real_ip} {COUNTRIES_TZ[real_ip.lower()]['flag']}")
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

# इतिहास दिखाने के लिए साइडबार - Live Public History
st.sidebar.header("📜 Live Scan History")
try:
    scans = supabase.table("scans").select("*").order("created_at", desc=True).limit(10).execute()
    if scans.data:
        for scan in scans.data:
            if "Bot" in scan['result'] or "Mismatch" in scan['result']:
                st.sidebar.markdown(f"🔴 {scan['username']}")
                st.sidebar.markdown(f"{scan['result']}")
            else:
                st.sidebar.markdown(f"🟢 {scan['username']}")
                st.sidebar.markdown(f"{scan['result']}")
            st.sidebar.caption(f"⏱️ {scan['created_at'][:19].replace('T', ' ')}")
            st.sidebar.markdown("---")
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
    *How to use:*

    1. *Bot Check*: Enter username and select platform to detect bots

    2. *Country Check*: Verify if user's claimed country matches IP location

    3. *Manual Check*: Paste text to check for spam patterns

    4. *History*: View last 10 scans in the sidebar
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

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>🐍 Vasuki Ai 4.0 - Bot Detector | Built by Nishad Singh Made in india</div>",
    unsafe_allow_html=True
)
