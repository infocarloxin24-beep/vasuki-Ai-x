import streamlit as st
import pandas as pd
import requests
import time
import re
from datetime import datetime
import pytz
import pycountry

st.set_page_config(page_title="Vasuki Ai 4.0", page_icon="🐍", layout="wide")

# Admin Password - Isko badal dena. Public ko ye nahi pata chalega
ADMIN_PASS = st.secrets.get("ADMIN_PASS", "vasuki2026")

# Session me admin check
if 'admin' not in st.session_state:
    st.session_state.admin = False

# 195 Countries + Timezone - Auto Generated
def get_all_countries():
    countries = {}
    for country in pycountry.countries:
        try:
            tz_list = pytz.country_timezones.get(country.alpha_2)
            if tz_list:
                countries[country.name.lower()] = {
                    "flag": country.flag,
                    "tz": tz_list[0], # Main timezone
                    "code": country.alpha_2
                }
        except:
            pass
    return countries

COUNTRIES_TZ = get_all_countries()

# Public Mode: Simple UI
st.title("🐍 Vasuki Ai 4.0 - Bot Detector")
st.caption("X/Twitter Account Scanner | Powered by AI")

# Admin Login - Chhupa hua
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

    # Ye 16-point logic public ko nahi dikhega
    if not username.startswith("@"):
        username = "@" + username

    # 1. Account Creation Speed
    if account_age_days < 1 and tweet_count > 50:
        score += 20
        if st.session_state.admin: reasons.append("1 Day me 50+ tweet - Machine speed")

    # 2. Post Frequency
    if account_age_days > 0:
        tpd = tweet_count / account_age_days
        if tpd > 100:
            score += 25
            if st.session_state.admin: reasons.append(f"Roz {int(tpd)} tweet - Machine")
        elif tpd > 20:
            score += 10
            if st.session_state.admin: reasons.append(f"Roz {int(tpd)} tweet - Suspicious")

    # 3. Writing Mistake
    if tweet_text and len(tweet_text) > 50:
        spelling_errors = len(re.findall(r'\b[a-z]{1,2}\b', tweet_text.lower()))
        if spelling_errors == 0:
            score += 10
            if st.session_state.admin: reasons.append("0 Spelling mistake - Bot accuracy")

    # 4. Username Pattern
    numbers = len(re.findall(r'\d', username))
    if numbers >= 8:
        score += 15
        if st.session_state.admin: reasons.append("8+ number username - Auto generated")

    if re.search(r'user\d+|bot\d+|temp\d+|test\d+', username.lower()):
        score += 20
        if st.session_state.admin: reasons.append("Fake/Bot jaisa username")

    # 5. Timezone + IP Mismatch - 195 Desh Check
    if tweet_time and claimed_country.lower() in COUNTRIES_TZ:
        try:
            tz = pytz.timezone(COUNTRIES_TZ[claimed_country.lower()]["tz"])
            tweet_hour = datetime.strptime(tweet_time, "%H:%M").hour
            # Raat 12-6 baje tweet = Sus
            if tweet_hour >= 0 and tweet_hour <= 6:
                score += 15
                if st.session_state.admin: reasons.append(f"{claimed_country} me raat {tweet_hour} baje tweet - Bot")

            # IP vs Country Mismatch
            if ip_country and ip_country.lower()!= claimed_country.lower():
                score += 20
                if st.session_state.admin: reasons.append(f"IP: {ip_country}, Dawa: {claimed_country}")
        except: pass

    # 6. Verified Bot Loophole
    if is_verified and numbers >= 4:
        score += 30
        if st.session_state.admin: reasons.append("Verified Bot Loophole Detected")

    # 7. Bio AI Phrases
    if re.search(r'as an ai language model|i cannot|i\'m an ai|i am an ai', bio.lower()):
        score += 40
        if st.session_state.admin: reasons.append("Bio me AI phrases - Pakka bot")

    # 8. Pattern Repeat
    if tweet_text and re.search(r'(.{10,})\1{3,}', tweet_text):
        score += 15
        if st.session_state.admin: reasons.append("Copy-paste pattern - Bot signature")

    return min(score, 100), reasons

# Public UI - Simple
tab1, tab2 = st.tabs(["🔍 Bot Check", "🌍 Country Check"])

with tab1:
    st.subheader("Account Scan Karo")
    username = st.text_input("X Username:", placeholder="@username")

    # Admin ko extra field dikhenge
    if st.session_state.admin:
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
        # Public ko bas ye dikhega
        is_verified = False
        tweet_count = 0
        account_age_days = 0
        claimed_country = ""
        ip_country = ""
        tweet_time = ""
        tweet_text = ""
        bio = ""
        st.info("Basic scan. Detailed 16-point report ke liye admin login kare.")

    if st.button("🐍 Scan Karo", type="primary"):
        if username:
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

            # Admin ko hi reasons dikhenge
            if st.session_state.admin and reasons:
                st.write("*Vasuki 16-Point Report:*")
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
                st.success(f"{data['flag']} *{country.title()}*")
                st.info(f"*Timezone:* {data['tz']}")
                st.info(f"*Country Code:* {data['code']}")
                if st.session_state.admin:
                    tz = pytz.timezone(data['tz'])
                    current_time = datetime.now(tz).strftime("%H:%M:%S")
                    st.info(f"*Current Local Time:* {current_time}")
            else:
                st.error("195 desh me nahi mila. Spelling check kar")
        else:
            st.warning("Desh daal pehle")

# Footer me bhi features hide
if not st.session_state.admin:
    st.markdown("---")
    st.caption("Vasuki Ai 4.0 | Simple Bot Detector")
else:
    st.markdown("---")
    st.caption("Vasuki Ai 4.0 Gupt Astra | 16-Point | 195 Timezone | IP Check | Speed+Accuracy | Admin Mode ✅")
