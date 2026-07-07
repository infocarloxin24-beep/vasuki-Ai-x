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
from difflib import SequenceMatcher
import urllib.parse

# 1. INITIALIZE SIDEBAR HISTORY AND SHARE (Fallbacks if missing from custom local analysis module)
if 'init_sidebar_history' not in globals():
    def init_sidebar_history(): pass
if 'show_sidebar_share' not in globals():
    def show_sidebar_share(): pass

init_sidebar_history()
show_sidebar_share()

st.set_page_config(
    page_title="Humbotix AI - Free Bot Detector",
    page_icon="assets/logo.png",
    layout="wide"
)

# Google description setup
st.markdown("""
    <meta name="description" content="Humbotix is a free AI bot detector. Check if Twitter, Instagram, or Reddit accounts are bots. Scan any text for AI content. 100% Free Tool.">
    <meta name="keywords" content="bot detector, ai detector, free bot checker,Humbotix, twitter bot check, fake account detector">
""", unsafe_allow_html=True)

# SECRETS CONFIGURATION
ADMIN_PASS = st.secrets.get("ADMIN_PASS", "admin123")
X_BEARER_TOKEN = st.secrets.get("X_BEARER_TOKEN")
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# PLACEHOLDERS FOR YOUR API / OAUTH KEYS
GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID_HERE"
GITHUB_CLIENT_ID = "YOUR_GITHUB_CLIENT_ID_HERE"

if 'admin' not in st.session_state:
    st.session_state.admin = False

# Initialize Captcha Puzzle Session State if not present
if 'captcha_num1' not in st.session_state:
    st.session_state.captcha_num1 = random.randint(1, 9)
    st.session_state.captcha_num2 = random.randint(1, 9)

def refresh_captcha_puzzle():
    st.session_state.captcha_num1 = random.randint(1, 9)
    st.session_state.captcha_num2 = random.randint(1, 9)

# 195 COUNTRIES LIST
def get_all_countries():
    countries_list = []
    for country in pycountry.countries:
        countries_list.append(country.name)
    return sorted(countries_list)

# TIMEZONE WALE COUNTRIES
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

# TEXT PATTERN ANALYSIS
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

    emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF]', text))
    if emoji_count > 10:
        score += 10
        reasons.append(f"Emoji Spam: {emoji_count} emojis")

    return min(score, 100), reasons, details

# BIO DEEP SCAN
def analyze_bio(bio):
    if not bio:
        return 0, [], {}

    score = 0
    reasons = []
    details = {}
    bio_lower = bio.lower()

    ai_phrases = ['as an ai', 'i am an ai', 'i cannot', 'language model', 'as a large language']
    for phrase in ai_phrases:
        if phrase in bio_lower:
            score += 40
            reasons.append(f"AI Disclosure: '{phrase}'")
            break

    return score, reasons, details

def fetch_x_data(username):
    username = username.replace("@", "").strip()
    try:
        url = f"https://nitter.net/{username}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            bio = soup.find('div', class_='profile-bio')
            bio = bio.text.strip() if bio else ""
            return {'bio': bio, 'followers': "0", 'tweet_count': "0", 'is_verified': False, 'account_age': 0}
    except: return None
    return None

def check_bot_score_gupt(username, bio="", is_verified=False, tweet_count=0, account_age=0,
                         tweet_time="", user_view_country="", claimed_country="", ip_country="", tweet_text=""):
    score = 0
    reasons = []
    forensics = {}
    tpd = tweet_count / max(account_age, 1)
    forensics['tpd'] = round(tpd, 2)

    if tpd > 50:
        score += 25
        reasons.append(f"High post frequency: {int(tpd)}/day")

    if tweet_text:
        text_score, text_reasons, text_details = analyze_text_pattern(tweet_text)
        score += text_score
        reasons.extend(text_reasons)

    if bio:
        bio_score, bio_reasons, bio_details = analyze_bio(bio)
        score += bio_score
        reasons.extend(bio_reasons)

    if claimed_country !="Unknown" and ip_country and claimed_country.lower() != ip_country.lower():
        score += 40
        reasons.append(f"Country Mismatch: {claimed_country} vs {ip_country}")

    return min(score, 100), reasons, int(tpd), forensics

def get_world_timing_grid_195(tweet_time_str):
    if not tweet_time_str: return []
    try:
        hour, minute = map(int, tweet_time_str.split(":"))
        result = []
        for country in pycountry.countries:
            try:
                tz_list = pytz.country_timezones.get(country.alpha_2)
                if tz_list:
                    tz = pytz.timezone(tz_list[0])
                    now = datetime.now(tz).replace(hour=hour, minute=minute)
                    result.append({
                        "name": country.name,
                        "time": now.strftime('%H:%M'),
                        "icon": "🌙" if 0 <= now.hour <= 6 else "☀️",
                        "hour": now.hour,
                        "flag": country.flag if hasattr(country, 'flag') else "🏳️"
                    })
            except: pass
        return sorted(result, key=lambda x: x["name"])
    except: return []

# FETCH CURRENT USER STATUS
try:
    session = supabase.auth.get_session()
    current_user = session.user if session else None
except:
    current_user = None

user_email = current_user.email if current_user else "anonymous_guest"

user_scan_count = 0
if current_user:
    try:
        scans_check = supabase.table("scans").select("id", count="exact").eq("scanned_by", user_email).execute()
        user_scan_count = scans_check.count if scans_check.count else 0
    except: pass

scans_left = max(0, 5 - user_scan_count)

# SIDEBAR DASHBOARD
st.sidebar.title("🤖 HumbotiX AI Dashboard")
if current_user:
    st.sidebar.success(f"👤 Account: `{user_email}`")
    st.sidebar.metric("Free Scans Remaining", f"{scans_left} / 5")
else:
    st.sidebar.warning("🔒 Login to save history.")

st.sidebar.markdown("---")
st.sidebar.header("📜 Your Personal Scan History")

if current_user:
    try:
        scans = supabase.table("scans").select("*").eq("scanned_by", user_email).order("created_at", desc=True).limit(5).execute()
        if scans.data:
            for scan in scans.data:
                score = scan.get('score', 0)
                username_raw = scan.get('username', 'Unknown Account')
                username_display = str(username_raw).split(']')[-1].strip()
                verdict_icon = "🤖 Bot" if score >= 50 else "✅ Human"
                
                share_text = f"🤖 *Humbotix Bot Report*:\n\n👤 *Account*: {username_display}\n📊 *Bot Score*: {score}%\n⚠️ *Verdict*: {verdict_icon}\nCheck here: https://humbotixai.in"
                whatsapp_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(share_text)}"

                st.sidebar.markdown(f"""
                <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 10px; margin-bottom: 8px; font-size: 11px;">
                    <div style="font-weight: bold; color: white; display: flex; justify-content: space-between;">
                        <span>{username_display}</span> 
                        <span style="color: {'#ef4444' if score >= 50 else '#22c55e'}">{score}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                        <span style="color: #64748b;">{verdict_icon}</span>
                        <a href="{whatsapp_url}" target="_blank" style="text-decoration: none; background: #25D366; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold;">🟢 Share</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else: st.sidebar.info("No scans triggered yet.")
    except Exception as e: st.sidebar.error("History load error")
else:
    st.sidebar.info("💡 Open right authentication card panel to log in.")

# MAIN INTERFACE LAYOUT
main_col, side_panel = st.columns([7, 3])

with main_col:
    st.title("HumbotiX Ai - Universal Bot Detector")
    st.caption("Global Multi Social-Platform Account & Text Scanner | Powered by AI")

    tab1, tab2 = st.tabs(["🔍 Bot Check", "🌍 Country Check"])

    with tab1:
        platform = st.selectbox("Select Platform:", ["Twitter / X", "Facebook", "Instagram", "YouTube", "LinkedIn", "WhatsApp", "TikTok", "Telegram", "Other Platforms"])
        username = st.text_input(f"{platform} Username / Profile Link:", placeholder="@username or paste profile URL")
        scan_mode = st.radio("Scan Mode:", ["Auto - X API/Nitter se data lao", "Manual - Khud bharo"], horizontal=True)

        is_verified, tweet_count, account_age_days = False, 0, 0
        claimed_country, user_view_country, ip_country = "Unknown", COUNTRY_DISPLAY_LIST[0], ALL_COUNTRIES[0]
        tweet_time, tweet_text, bio, comment1, comment2 = "", "", "", "", ""

        if scan_mode == "Manual - Khud bharo":
            comment1 = st.text_area("Comment 1", placeholder="Optional text...", height=80)
            comment2 = st.text_area("Comment 2", placeholder="Optional comparison text...", height=80)
            tweet_text = st.text_area("Post text:", height=80)
            bio = st.text_area("Account Bio:", height=80)
            
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                v_toggle = st.checkbox("Verified Profile")
                is_verified = True if v_toggle else False
                tweet_count = st.number_input("Total Posts", 0, value=0)
            with col_m2:
                account_age_days = st.number_input("Account Age (Days)", 0, value=0)
                tweet_time = st.text_input("Post Time (HH:MM)", "12:00")

            col_m3, col_m4 = st.columns(2)
            with col_m3:
                claimed_country = st.selectbox("Claimed Location:", ["Unknown"] + ALL_COUNTRIES)
            with col_m4:
                ip_country = st.selectbox("Real System IP Location:", ALL_COUNTRIES)

        if st.button("🚀 Scan Karo", use_container_width=True):
            if not current_user:
                st.error("AI Access Blocked! Registration configuration required. Please use the 'User Login / Sign Up' portal on the right card panel to begin.")
            elif scans_left <= 0:
                st.error("Diagnostic Counter Exhausted! You have executed your 5 standard free queries. Please upgrade profile tier.")
            elif not username and not tweet_text and not comment1:
                st.warning("Please feed username context metrics first.")
            else:
                with st.spinner("Processing Forensics Engine..."):
                    clean_user = username if username else "Anonymous Content"
                    if scan_mode == "Auto - X API/Nitter se data lao" and platform == "Twitter / X":
                        res_nit = fetch_x_data(clean_user)
                        if res_nit: bio = res_nit['bio']

                    score, reasons, tpd, forensics = check_bot_score_gupt(
                        username=clean_user, bio=bio, is_verified=is_verified, tweet_count=tweet_count,
                        account_age=account_age_days, tweet_time=tweet_time, user_view_country=user_view_country,
                        claimed_country=claimed_country, ip_country=ip_country, tweet_text=tweet_text
                    )

                    if comment1 and comment2:
                        match_r = SequenceMatcher(None, comment1, comment2).ratio() * 100
                        if match_r > 70:
                            score = max(score, 85)
                            reasons.append(f"Coordinated Comment Blueprint ({round(match_r)}% similarity match)")

                    is_bot = score >= 50
                    result_text = f"🤖 Bot Profile - {score}% Risk Value" if is_bot else f"✅ Certified Human Account"

                    save_packet = {
                        "username": f"[{platform}] {clean_user}",
                        "platform": platform,
                        "scan_type": "Bot Check",
                        "result": result_text,
                        "country": claimed_country,
                        "score": score,
                        "tweet_count": tweet_count,
                        "account_age": account_age_days,
                        "tweet_time": tweet_time,
                        "tpd": tpd,
                        "tweet_text": tweet_text[:100] if tweet_text else "",
                        "flags": ", ".join(reasons) if reasons else "None",
                        "is_verified": is_verified,
                        "scanned_by": user_email
                    }
                    try:
                        supabase.table("scans").insert(save_packet).execute()
                        st.metric("Probability Factor", f"{score}%", delta="High Risk" if is_bot else "Safe", delta_color="inverse" if is_bot else "normal")
                        st.progress(score/100)
                        if reasons:
                            st.write("🔬 **Identified Bot Signature Footprints:**")
                            for r in reasons: st.write(f"• {r}")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e: st.error(f"Storage Sync Fault: {e}")

    with tab2:
        st.subheader("🌍 Country Mismatch Filter Gateway")
        c_claim = st.selectbox("Declared Profile Country:", ["Unknown"] + ALL_COUNTRIES, key="tab2_claim")
        c_real = st.selectbox("Calculated Infrastructure IP Country:", ALL_COUNTRIES, key="tab2_real")
        
        if st.button("Verify Country Data Consistency", use_container_width=True):
            if not current_user:
                st.error("AI Access Blocked! Registration layout required. Complete portal login on the right section.")
            elif scans_left <= 0:
                st.error("Diagnostic Counter Exhausted!")
            elif c_claim == "Unknown":
                st.info("No location tags verified.")
            elif c_claim.lower() != c_real.lower():
                st.error(f"🚨 Identity Spatial Fraud Flagged! Profile location asserts '{c_claim}' while core network payload tracks back to '{c_real}'. Proxy script or bot farm routing likely.")
            else:
                st.success(f"Consistency validated. Target matching region parameters successfully confirmed: {c_claim}")

# RIGHT EXPANDER PANEL (USER LOGIN / MOBILE OTP / PUZZLE CAPTCHA SYSTEM)
with side_panel:
    st.markdown("### 🔐 Authentication Hub")
    with st.container(border=True):
        if current_user:
            st.success(f"Logged in as: \n`{user_email}`")
            if st.button("🚪 Terminate Session", use_container_width=True, type="primary"):
                try:
                    supabase.auth.sign_out()
                    st.success("Session closed!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")
        else:
            auth_mode = st.radio("Select Gateway Mode:", ["Login Session", "Register New Profile"], horizontal=True)
            
            # --- Anti-Bot Mathematical Puzzle Captcha System ---
            st.markdown("<div style='background-color:#1e293b; padding:8px; border-radius:5px; margin-bottom:10px; border-left:4px solid #3b82f6;'><b>🤖 Security Verification</b><br><small>Solve the math puzzle below to verify you are a human operator.</small></div>", unsafe_allow_html=True)
            
            cap_col1, cap_col2 = st.columns([2, 1])
            with cap_col1:
                st.markdown(f"#### Challenge: **${st.session_state.captcha_num1} + {st.session_state.captcha_num2} = ?**")
            with cap_col2:
                if st.button("🔄 Refresh", help="Click to generate a new anti-bot puzzle number combo"):
                    refresh_captcha_puzzle()
                    st.rerun()
                    
            user_captcha_ans = st.number_input("Your Solution:", step=1, value=0, key="captcha_user_input_field")
            correct_captcha_sum = st.session_state.captcha_num1 + st.session_state.captcha_num2

            login_tabs = st.tabs(["📧 Email Access", "📱 Mobile OTP Access", "🚀 OAuth Connect"])

            # 1. Email Channel
            with login_tabs[0]:
                em_user = st.text_input("Registered Email Address:", key="em_u")
                em_pass = st.text_input("Account Access Secret Password:", type="password", key="em_p")
                
                if auth_mode == "Login Session":
                    if st.button("Process Secure Login", use_container_width=True, type="primary"):
                        if user_captcha_ans != correct_captcha_sum:
                            st.error("❌ Bot Blocked! Incorrect security puzzle answer. Click Refresh to try again.")
                        else:
                            try:
                                supabase.auth.sign_in_with_password({"email": em_user, "password": em_pass})
                                st.success("Access Granted! Profile session verified.")
                                refresh_captcha_puzzle()
                                time.sleep(1)
                                st.rerun()
                            except Exception as e: st.error(f"Credentials Rejected: {str(e)}")
                else:
                    reg_name = st.text_input("Operator Legal Full Name:", placeholder="Your Name")
                    if st.button("Generate System Credentials", use_container_width=True, type="primary"):
                        if user_captcha_ans != correct_captcha_sum:
                            st.error("❌ Bot Blocked! Incorrect security puzzle answer.")
                        else:
                            try:
                                supabase.auth.sign_up({"email": em_user, "password": em_pass, "options": {"data": {"full_name": reg_name}}})
                                st.success("Registration Success packet generated! Check email link.")
                                refresh_captcha_puzzle()
                            except Exception as e: st.error(f"Registration Failed: {str(e)}")

            # 2. Global Mobile OTP Gateway (195+ Countries)
            with login_tabs[1]:
                st.markdown("##### 📱 Mobile OTP Gateway (Global Access)")
                
                COMMON_DIAL_CODES = {
                    "IN": "+91", "US": "+1", "GB": "+44", "PK": "+92", "BD": "+880", 
                    "AE": "+971", "SA": "+966", "CA": "+1", "AU": "+61", "DE": "+49", 
                    "FR": "+33", "JP": "+81", "CN": "+86", "BR": "+55", "ZA": "+27"
                }

                final_global_phone_list = []
                for name, data in sorted(COUNTRIES_TZ.items()):
                    c_code = data['code']
                    dial_prefix = COMMON_DIAL_CODES.get(c_code, "+")
                    display_row = f"{data['flag']} {name} ({dial_prefix if len(dial_prefix)>1 else 'Select'})"
                    final_global_phone_list.append(display_row)

                phone_cc_global = st.selectbox(
                    "Select Country/Region Code", 
                    final_global_phone_list, 
                    index=final_global_phone_list.index([x for x in final_global_phone_list if "India" in x][0]) if [x for x in final_global_phone_list if "India" in x] else 0,
                    key="phone_cc_select_global"
                )
                phone_num = st.text_input("Mobile Number Sequence:", key="ph_num", placeholder="Enter local mobile number")
                
                if st.button("Transmit Secure Verification OTP", use_container_width=True):
                    if user_captcha_ans != correct_captcha_sum:
                        st.error("❌ Bot Blocked! Solve the anti-bot numbers puzzle accurately first.")
                    elif phone_num:
                        extracted_code = re.findall(r'\(\+(.*?)\)', phone_cc_global)
                        clean_prefix = f"+{extracted_code[0]}" if extracted_code else "+"
                        
                        if clean_prefix in ["+Select", "+"]:
                            st.error("Please pick a nation structure with a valid country dialing indicator.")
                        else:
                            full_phone_string = f"{clean_prefix}{phone_num}".replace(" ", "").replace("-", "")
                            try:
                                supabase.auth.sign_in_with_otp({"phone": full_phone_string})
                                st.info(f"OTP pushed successfully to {full_phone_string}")
                                st.session_state.phone_auth_triggered = full_phone_string
                            except Exception as e: st.error(f"OTP Request Failure: {str(e)}")
                    else: st.warning("Specify local numerical sequence configuration first.")
                
                if st.session_state.get("phone_auth_triggered"):
                    st.markdown("---")
                    otp_token = st.text_input("Enter 6-Digit SMS OTP:", type="password", key="otp_global_field")
                    if st.button("Verify OTP token", use_container_width=True, type="primary"):
                        try:
                            supabase.auth.verify_otp({
                                "phone": st.session_state.phone_auth_triggered,
                                "token": otp_token,
                                "type": "sms"
                            })
                            st.success("Mobile Registration Session Validated!")
                            refresh_captcha_puzzle()
                            time.sleep(1)
                            st.rerun()
                        except Exception as e: st.error(f"Token Verification Failed: {str(e)}")

            # 3. Social Integration Channels
            with login_tabs[2]:
                if user_captcha_ans != correct_captcha_sum:
                    st.error("⚠️ Fill security puzzle challenge above before initializing OAuth workflows.")
                else:
                    SUPABASE_URL = st.secrets["SUPABASE_URL"]
                    g_url = f"{SUPABASE_URL}/auth/v1/authorize?provider=google"
                    gh_url = f"{SUPABASE_URL}/auth/v1/authorize?provider=github"
                    
                    st.markdown(f'<a href="{g_url}" target="_self" style="display:block; text-align:center; padding:8px; margin:5px; background:white; color:#3c4043; border:1px solid #dadce0; border-radius:5px; text-decoration:none; font-weight:bold;">Connect with Google Account</a>', unsafe_allow_html=True)
                    st.markdown(f'<a href="{gh_url}" target="_self" style="display:block; text-align:center; padding:8px; margin:5px; background:#24292e; color:white; border-radius:5px; text-decoration:none; font-weight:bold;">Connect with GitHub Account</a>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666; font-size: 13px;'> HumbotiX Ai Dashboard v2 | Core Cloud Cluster Connected | © 2026</div>", unsafe_allow_html=True)
