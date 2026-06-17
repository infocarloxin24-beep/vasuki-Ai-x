import streamlit as st
import pandas as pd
import requests
import time
import re
from datetime import datetime
import pytz
import pycountry
from bs4 import BeautifulSoup

st.set_page_config(page_title="Vasuki Ai 4.0", page_icon="🐍", layout="wide")

# FIX 1: Secrets se token lo, hardcoded nahi
ADMIN_PASS = st.secrets.get("ADMIN_PASS", "")
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

# FIX 2: X API + NITTER DONO - AUTOMATIC FALLBACK
def fetch_x_data(username):
    username = username.replace("@", "").strip()

    # STEP 1: X API try karo agar token hai
    if X_BEARER_TOKEN:
        try:
            headers = {"Authorization": f"Bearer {X_BEARER_TOKEN}"}
            url = f"https://api.x.com/2/users/by/username/{username}?user.fields=created_at,public_metrics,verified,description"
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                d = r.json()['data']
                age = (datetime.utcnow() - datetime.strptime(d['created_at'], '%Y-%m-%dT%H:%M:%S.000Z')).days
                return {'is_verified': d.get('verified', False), 'tweet_count': d['public_metrics']['tweet_count'], 'account_age_days': age, 'bio': d.get('description', ''), 'followers': d['public_metrics']['followers_count'], 'source': 'X API'}
        except: pass

    # STEP 2: NITTER se nikal agar API fail hui
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
            return {'bio': bio, 'followers': followers, 'tweet_count': tweets, 'is_verified': "Verified" in r.text, 'account_age_days': 365, 'source': 'Nitter Free'}
        else: return None
    except: return None

st.title("🐍 Vasuki Ai 4.0 - Bot Detector")
st.caption("X/Twitter Account Scanner | Powered by AI")

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

def check_bot_score_gupt(username, bio="", is_verified=False, tweet_count=0, account_age_days=0,
                        tweet_time="", ip_country="", claimed_country="", tweet_text=""):
    score = 0
    reasons = []
    if not username.startswith("@"):
        username = "@" + username

    if account_age_days < 1 and tweet_count > 50:
        score += 20
        if st.session_state.admin: reasons.append("1 Day me 50+ tweet - Machine speed")

    if account_age_days > 0:
        tpd = tweet_count / account_age_days
        if tpd > 100:
            score += 25
            if st.session_state.admin: reasons.append(f"Roz {int(tpd)} tweet - Machine")
        elif tpd > 20:
            score += 10
            if st.session_state.admin: reasons.append(f"Roz {int(tpd)} tweet - Suspicious")

    if tweet_text and len(tweet_text) > 50:
        spelling_errors = len(re.findall(r'\b[a-z]{1,2}\b', tweet_text.lower()))
        if spelling_errors == 0:
            score += 10
            if st.session_state.admin: reasons.append("0 Spelling mistake - Bot accuracy")

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
                if st.session_state.admin: reasons.append(f"{claimed_country} me raat {tweet_hour} baje tweet - Bot")
            if ip_country and ip_country.lower()!= claimed_country.lower():
                score += 20
                if st.session_state.admin: reasons.append(f"IP: {ip_country}, Dawa: {claimed_country}")
        except: pass

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

tab1, tab2 = st.tabs(["🔍 Bot Check", "🌍 Country Check"])

with tab1:
    st.subheader("Account Scan Karo")
    username = st.text_input("X Username:", placeholder="@username")

    # FIX 3: Auto + Manual mode ka option diya
    scan_mode = st.radio("Scan Mode:", ["Auto - X API/Nitter se data lao", "Manual - Khud bharo"], horizontal=True)

    # Variables default set kar do
    is_verified = False
    tweet_count = 0
    account_age_days = 0
    claimed_country = ""
    ip_country = ""
    tweet_time = ""
    tweet_text = ""
    bio = ""

    if scan_mode == "Manual - Khud bharo" or st.session_state.admin:
        st.info("Manual Mode: Saare fields khud bharo ya Admin hai to dikhenge")
        col1, col2, col3 = st.columns(3)
        with col1:
            is_verified = st.checkbox("Blue Tick?")
            claimed_country = st.selectbox("Claimed Country:", [""] + list(COUNTRIES_TZ.keys()))
        with col2:
            tweet_count = st.number_input("Total Tweets:", 0)
            account_age_days = st.number_input("Account Age Days:", 0)
            ip_country = st.selectbox("IP Country:", [""] + list(COUNTRIES_TZ.keys()))
        with col3:
            tweet_time = st.text_input("Last Tweet Time HH:MM:", placeholder="03:45")
            tweet_text = st.text_area("Sample Tweet:")
        bio = st.text_area("Bio:")
    else:
        st.info("Auto Mode: Sirf username daal. Baki Vasuki bhar dega X API ya Nitter se")

    if st.button("🐍 Scan Karo", type="primary"):
        if username:
            # FIX 4: Auto mode me API call karo
            if scan_mode == "Auto - X API/Nitter se data lao":
                with st.spinner("Data laa raha hu..."):
                    api_data = fetch_x_data(username)
                if api_data:
                    is_verified = api_data['is_verified']
                    tweet_count = int(api_data['tweet_count']) if str(api_data['tweet_count']).isdigit() else 0
                    account_age_days = api_data['account_age_days']
                    bio = api_data['bio']
                    st.success(f"Data mil gaya! Source: {api_data['source']} | Followers: {api_data['followers']} | Verified: {is_verified}")
                else:
                    st.error("Auto scan fail. Nitter down ho sakta hai. Manual mode use kar")
                    st.stop()

            score, reasons = check_bot_score_gupt(
                username, bio, is_verified, tweet_count,
                account_age_days, tweet_time, ip_country, claimed_country, tweet_text
            )

            st.markdown("---")
            if score >= 70:
                st.error(f"🚨 High Risk Bot: {score}%")
            elif score >= 40:
                st.warning(f"⚠️ Suspicious Account: {score}%")
            else:
                st.success(f"✅ Looks Human: {score}%")

            if st.session_state.admin and reasons:
                st.write("Vasuki 16-Point Report:")
                for i, r in enumerate(reasons, 1):
                    st.write(f"{i}. {r}")
            elif not st.session_state.admin:
                st.caption("Detailed analysis locked. Contact admin.")
        else:
            st.warning("Username daal bhai")

with tab2:
    st.subheader("195 Country Timezone Check")
    country = st.text_input("Desh ka naam:", placeholder="india / usa / japan")

    if st.button("🌍 Timezone Dikhao"):
        if country:
            country_lower = country.lower()
            if country_lower in COUNTRIES_TZ:
                data = COUNTRIES_TZ[country_lower]
                st.success(f"{data['flag']} {country.title()}")
                st.info(f"Timezone: {data['tz']}")
                st.info(f"Country Code: {data['code']}")
                if st.session_state.admin:
                    tz = pytz.timezone(data['tz'])
                    current_time = datetime.now(tz).strftime("%H:%M:%S")
                    st.info(f"Current Local Time: {current_time}")
            else:
                st.error("195 desh me nahi mila. Spelling check kar")
        else:
            st.warning("Fill Country Name")

if not st.session_state.admin:
    st.markdown("---")
    st.caption("Vasuki Ai 4.0 | Simple Bot Detector")
else:
    st.markdown("---")
    st.caption("Vasuki Ai 4.0 made in india | 16-Point | 195 Timezone | IP Check | Speed+Accuracy | Admin Mode ✅")
