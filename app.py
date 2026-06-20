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

# PURI DUNIYA KE 195 COUNTRY - COMPACT GRID
def get_world_timing_grid_195(tweet_time_str):
    if not tweet_time_str:
        return []
    try:
        hour, minute = map(int, tweet_time_str.split(":"))
        now = datetime.now()
        input_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        result = []
        for country in pycountry.countries:
            try:
                tz_list = pytz.country_timezones.get(country.alpha_2)
                if tz_list:
                    tz = pytz.timezone(tz_list[0]) # Pehla timezone le lo
                    ist = pytz.timezone('Asia/Kolkata')
                    local_dt = ist.localize(input_dt)
                    utc_dt = local_dt.astimezone(pytz.utc)
                    country_time = utc_dt.astimezone(tz)
                    flag_icon = "🌙" if 0 <= country_time.hour <= 6 else "☀️"
                    result.append({
                        "name": country.name,
                        "time": country_time.strftime('%H:%M'),
                        "icon": flag_icon,
                        "hour": country_time.hour,
                        "flag": country.flag if hasattr(country, 'flag') else "🏳️"
                    })
            except: pass
        # Name se sort kar do
        result = sorted(result, key=lambda x: x["name"])
        return result
    except: return []

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
            verified_status = st.radio("Verified Status:", ["❌ Unverified", "✅ Verified"], horizontal=True)
            is_verified = True if verified_status == "✅ Verified" else False
            tweet_count = st.number_input("Total Tweets/Posts", 0, value=0)
        with col2:
            account_age_days = st.number_input("Account Age (Days)", 0, value=0)
            tweet_time = st.text_input("Last Tweet Time (HH:MM)", "14:30")

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
                tpd = int(tweet_count / max(account_age_days, 1))
                verified_text = "✅ Verified" if is_verified else "❌ Unverified"

                # SUPABASE MEIN SAB SAVE KARO
                result = {
                    "username": f"[{platform}] {clean_username}",
                    "platform": platform,
                    "scan_type": "Bot Check",
                    "result": result_text,
                    "country": claimed_country,
                    "score": score,
                    "tweet_count": tweet_count,
                    "account_age": account_age_days,
                    "tweet_time": tweet_time,
                    "tpd": tpd,
                    "flags": ", ".join(reasons) if reasons else "None",
                    "is_verified": is_verified
                }

                try:
                    supabase.table("scans").insert(result).execute()
                    st.success("🎉 Scan Complete!")
                    st.subheader("📊 Bot Probability Meter")
                    st.progress(score/100)
                    st.metric("Bot Score", f"{score}%", delta=f"{'Danger' if score>=70 else 'Suspicious' if score>=50 else 'Safe'}", delta_color="inverse")

                    # VERIFIED STATUS - DOUBLE ICON FIX KIYA
                    st.write(f"*Verified Status:* {verified_text}")

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

                    # 195 COUNTRY KA COMPACT DASHBOARD
                    if tweet_time:
                        st.write("*🌍 World Timing Dashboard - 195 Countries*")
                        st.caption("🌙 = Raat 12-6 baje | ☀️ = Din ka time | Red Border = Raat | Green Border = Din")

                        world_times = get_world_timing_grid_195(tweet_time)

                        # Expander mein daal diya taki UI clean rahe
                        with st.expander(f"📊 Show All 195 Countries Timing", expanded=False):
                            # 6 COLUMNS MEIN GRID - COMPACT
                            cols = st.columns(6)
                            for idx, country in enumerate(world_times):
                                col_idx = idx % 6
                                with cols[col_idx]:
                                    # NIGHT TIME KO RED BORDER, DAY KO GREEN
                                    border_color = "#ef4444" if 0 <= country["hour"] <= 6 else "#22c55e"
                                    st.markdown(f"""
                                    <div style="
                                        background: #1e293b;
                                        border: 2px solid {border_color};
                                        border-radius: 6px;
                                        padding: 4px;
                                        margin-bottom: 4px;
                                        text-align: center;
                                        font-size: 9px;
                                        line-height: 1.1;
                                    ">
                                        <div style="font-size: 12px; margin-bottom: 1px;">
                                            {country['flag']}
                                        </div>
                                        <div style="font-weight: bold; color: #e2e8f0; margin-bottom: 2px; font-size: 8px;">
                                            {country['name'][:10]}
                                        </div>
                                        <div style="font-size: 11px; color: white;">
                                            {country['time']} {country['icon']}
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Supabase Error: {e}")
        else:
            st.warning("⚠️ Scan karne ke liye Username ya Text daalna zaroori hai bhai!")

with tab2:
    st.subheader("🌍 Country Mismatch Detector")
    st.write("Check karo ki user ne country sahi batayi hai ya fake hai")

    col1, col2 = st.columns(2)
    with col1:
        claimed = st.selectbox("Claimed Country:", ALL_COUNTRIES, key="claimed_cc")
    with col2:
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
                "country": claimed,
                "score": 100,
                "tweet_count": 0,
                "account_age": 0,
                "tweet_time": "",
                "tpd": 0,
                "flags": f"Country Mismatch: {claimed} vs {real_ip}",
                "is_verified": False
            }
            try:
                supabase.table("scans").insert(result).execute()
                st.success("History me save ho gaya")
            except:
                st.error("History save nahi hui")
        else:
            st.success(f"✅ Match! Dono country same hain: {claimed}")
            st.balloons()

# SIDEBAR - DOUBLE ICON FIX KIYA
st.sidebar.header("📜 Live Scan History")
try:
    scans = supabase.table("scans").select("*").order("created_at", desc=True).limit(10).execute()
    if scans.data:
        for scan in scans.data:
            is_bot = "Bot" in str(scan.get('result', ''))
            verdict_icon = "🤖 Bot" if is_bot else "✅ Human"
            score = scan.get('score', 0)

            username_raw = scan.get('username', '')
            username_display = str(username_raw).replace('[Twitter / X] ', '').replace('[CountryCheck] ', '').replace('[Facebook] ', '').replace('[Instagram] ', '').replace('[YouTube] ', '').replace('[LinkedIn] ', '').replace('[WhatsApp] ', '').replace('[Other Platforms] ', '') if username_raw else 'Unknown'

            tpd = scan.get('tpd', 0) or 0
            account_age = scan.get('account_age', 0) or 0
            tweet_time = scan.get('tweet_time', 'N/A') or 'N/A'
            total_posts = scan.get('tweet_count', 0) or 0
            flags = scan.get('flags', 'None') or 'None'
            verified_text = "✅ Verified" if scan.get('is_verified', False) else "❌ Unverified"
            created_at = scan.get('created_at', '')
            time_display = created_at[:16].replace('T', ' ') if created_at else 'N/A'

            # LABEL SE ICON HATA DIYA - AB DOUBLE NAHI DIKHEGA
            st.sidebar.markdown(f"""
            <div style="
                background: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 8px;
                margin-bottom: 8px;
                font-size: 11px;
                line-height: 1.4;
                color: #e2e8f0;
            ">
                <div style="font-weight: bold; margin-bottom: 4px; color: white;">
                    {username_display} {score}% {verdict_icon}
                </div>
                <div>📊 Tweets/Day: {tpd}</div>
                <div>📅 Account Age: {account_age} days</div>
                <div>⏰ Last Tweet: {tweet_time}</div>
                <div>📝 Total Posts: {total_posts}</div>
                <div>Verified: {verified_text}</div>
                <div style="margin-top: 4px;">⚠️ Flags:</div>
                <div style="font-size: 10px; color: #94a3b8;">• {str(flags).replace(', ', '<br>• ')}</div>
                <div style="color: #64748b; font-size: 9px; margin-top: 4px;">
                    {time_display}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.info("No scans")
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
