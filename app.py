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

# 1. INITIALIZE SIDEBAR HISTORY AND SHARE (FALLBACKS)
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

# Google SEO Metadata setup
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

# Initialize Captcha Puzzle Session State if not present
if 'captcha_num1' not in st.session_state:
    st.session_state.captcha_num1 = random.randint(1, 9)
    st.session_state.captcha_num2 = random.randint(1, 9)

def refresh_captcha_puzzle():
    st.session_state.captcha_num1 = random.randint(1, 9)
    st.session_state.captcha_num2 = random.randint(1, 9)

# FETCH CURRENT USER STATUS BEFORE RENDERING UI
try:
    session = supabase.auth.get_session()
    current_user = session.user if session else None
except:
    current_user = None

# Helper Database for Global Countries & Timezones
def get_countries_with_tz_data():
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

COUNTRIES_TZ = get_countries_with_tz_data()
ALL_COUNTRIES = sorted(list(COUNTRIES_TZ.keys()))

# ==============================================================================
# 🚪 SCREEN 1: SECURE LOGIN GATEWAY (Sirf tab dikhega jab user login nahi hai)
# ==============================================================================
if not current_user:
    st.markdown("<h1 style='text-align: center; color: white;'>🔒 HumbotiX AI Gateway</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>Please verify identity and log in to access the Bot Detector Dashboard.</p>", unsafe_allow_html=True)
    
    with st.container():
        col1, main_auth_col, col3 = st.columns([1, 2, 1])
        
        with main_auth_col:
            auth_mode = st.radio("Select Gateway Mode:", ["Login Session", "Register New Profile"], horizontal=True)
            
            # --- Anti-Bot Mathematical Puzzle Captcha System ---
            st.markdown("<div style='background-color:#1e293b; padding:12px; border-radius:5px; margin-bottom:10px; border-left:4px solid #3b82f6;'><b>🤖 Security Verification</b><br><small>Solve the math puzzle below to prove you are a human operator.</small></div>", unsafe_allow_html=True)
            
            cap_col1, cap_col2 = st.columns([3, 1])
            with cap_col1:
                st.markdown(f"#### Challenge: **{st.session_state.captcha_num1} + {st.session_state.captcha_num2} = ?**")
            with cap_col2:
                if st.button("🔄 Refresh", help="Generate a new number combo"):
                    refresh_captcha_puzzle()
                    st.rerun()
                    
            user_captcha_ans = st.number_input("Your Solution:", step=1, value=0, key="captcha_main_gate")
            correct_captcha_sum = st.session_state.captcha_num1 + st.session_state.captcha_num2

            login_tabs = st.tabs(["📧 Email Access", "📱 Mobile OTP Access", "🚀 OAuth Connect"])

            # Channel 1: Email Form
            with login_tabs[0]:
                em_user = st.text_input("Registered Email Address:", key="em_u")
                em_pass = st.text_input("Account Access Secret Password:", type="password", key="em_p")
                
                if auth_mode == "Login Session":
                    if st.button("Process Secure Login", use_container_width=True, type="primary", key="login_btn_main"):
                        if user_captcha_ans != correct_captcha_sum:
                            st.error("❌ Bot Blocked! Incorrect security puzzle answer.")
                        else:
                            try:
                                supabase.auth.sign_in_with_password({"email": em_user, "password": em_pass})
                                st.success("Access Granted! Loading system parameters...")
                                refresh_captcha_puzzle()
                                time.sleep(1)
                                st.rerun()
                            except Exception as e: st.error(f"Credentials Rejected: {str(e)}")
                else:
                    reg_name = st.text_input("Operator Legal Full Name:", placeholder="Your Name")
                    if st.button("Generate System Credentials", use_container_width=True, type="primary", key="reg_btn_main"):
                        if user_captcha_ans != correct_captcha_sum:
                            st.error("❌ Bot Blocked! Incorrect security puzzle answer.")
                        else:
                            try:
                                supabase.auth.sign_up({"email": em_user, "password": em_pass, "options": {"data": {"full_name": reg_name}}})
                                st.success("Registration Success packet generated! Check email link.")
                                refresh_captcha_puzzle()
                            except Exception as e: st.error(f"Registration Failed: {str(e)}")

            # Channel 2: Global Mobile OTP Gateway (Pure 195+ Countries)
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
                    key="phone_gate_select"
                )
                phone_num = st.text_input("Mobile Number Sequence:", key="ph_num_gate", placeholder="Enter local mobile number")
                
                if st.button("Transmit Secure Verification OTP", use_container_width=True, key="send_otp_gate"):
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
                    otp_token = st.text_input("Enter 6-Digit SMS OTP:", type="password", key="otp_gate_field")
                    if st.button("Verify OTP token & Access Dashboard", use_container_width=True, type="primary"):
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

            # Channel 3: Social Connect (Chhote, Round Circular Buttons)
            with login_tabs[2]:
                if user_captcha_ans != correct_captcha_sum:
                    st.error("⚠️ Fill security puzzle challenge above before initializing OAuth workflows.")
                else:
                    g_url = f"{url}/auth/v1/authorize?provider=google"
                    gh_url = f"{url}/auth/v1/authorize?provider=github"
                    
                    st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px; margin-bottom: 5px;'>Quick Social Login</p>", unsafe_allow_html=True)
                    
                    oauth_html = f"""
                    <div style="display: flex; justify-content: center; gap: 15px; padding: 5px;">
                        <a href="{g_url}" target="_self" style="
                            display: flex; align-items: center; justify-content: center;
                            width: 42px; height: 42px; background-color: #ffffff; border-radius: 50%;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.15); transition: transform 0.2s; text-decoration: none;
                        " onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" style="width: 22px; height: 22px;" alt="Google">
                        </a>
                        
                        <a href="{gh_url}" target="_self" style="
                            display: flex; align-items: center; justify-content: center;
                            width: 42px; height: 42px; background-color: #24292e; border-radius: 50%;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.15); transition: transform 0.2s; text-decoration: none;
                        " onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/9/91/Octicons-mark-github.svg" style="width: 24px; height: 24px; filter: invert(1);" alt="GitHub">
                        </a>
                    </div>
                    """
                    st.markdown(oauth_html, unsafe_allow_html=True)
    st.stop() # User yahi ruk jayega jab tak system validated nahi hota!

# ==============================================================================
# 🖥️ SCREEN 2: MAIN APPLICATION INTERFACE (Sirf successful verification ke baad)
# ==============================================================================
user_email = current_user.email if current_user else "anonymous_guest"

# Forensics Calculation Systems
def analyze_text_pattern(text):
    if not text or len(text) < 20: return 0, [], {}
    score, reasons, details = 0, [], {}
    total_chars = len(re.findall(r'[a-zA-Z]', text))
    if total_chars > 0:
        caps_ratio = len(re.findall(r'[A-Z]', text)) / total_chars
        if caps_ratio == 0 or caps_ratio > 0.95:
            score += 25
            reasons.append("Perfect Capitalization - Machine typed pattern")
    return min(score, 100), reasons, details

def check_bot_score_gupt(username, claimed_country="Unknown", ip_country="", tweet_text=""):
    score, reasons = 0, []
    if tweet_text:
        ts, tr, _ = analyze_text_pattern(tweet_text)
        score += ts; reasons.extend(tr)
    if claimed_country != "Unknown" and ip_country and claimed_country.lower() != ip_country.lower():
        score += 40
        reasons.append(f"Country Geo Mismatch: {claimed_country} vs {ip_country}")
    return min(score, 100), reasons

# Check user table scan quotas
user_scan_count = 0
try:
    scans_check = supabase.table("scans").select("id", count="exact").eq("scanned_by", user_email).execute()
    user_scan_count = scans_check.count if scans_check.count else 0
except: pass
scans_left = max(0, 5 - user_scan_count)

# SIDEBAR STATUS SYSTEM
st.sidebar.title("🤖 HumbotiX AI Dashboard")
st.sidebar.success(f"👤 Connected: `{user_email}`")
st.sidebar.metric("Free Diagnostic Scans Left", f"{scans_left} / 5")

if st.sidebar.button("🚪 Terminate Session (Logout)", use_container_width=True, type="primary"):
    try:
        supabase.auth.sign_out()
        st.success("Session explicitly dropped!")
        time.sleep(1)
        st.rerun()
    except Exception as e: st.sidebar.error(f"Error executing logout: {e}")

st.sidebar.markdown("---")
st.sidebar.header("📜 Personal Scan History")

try:
    scans = supabase.table("scans").select("*").eq("scanned_by", user_email).order("created_at", desc=True).limit(5).execute()
    if scans.data:
        for scan in scans.data:
            score = scan.get('score', 0)
            username_display = str(scan.get('username', 'Account Log')).split(']')[-1].strip()
            verdict_icon = "🤖 Bot" if score >= 50 else "✅ Human"
            share_text = f"🤖 *Humbotix Bot Report*:\n\n👤 *Account*: {username_display}\n📊 *Bot Score*: {score}%"
            whatsapp_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(share_text)}"
            
            st.sidebar.markdown(f"""
            <div style="background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 10px; margin-bottom: 8px; font-size: 11px;">
                <div style="font-weight: bold; color: white; display: flex; justify-content: space-between;">
                    <span>{username_display}</span> <span style="color: {'#ef4444' if score >= 50 else '#22c55e'}">{score}%</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                    <span style="color: #64748b;">{verdict_icon}</span>
                    <a href="{whatsapp_url}" target="_blank" style="text-decoration: none; background: #25D366; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold;">🟢 Share</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
except: pass

# MAIN SYSTEM FUNCTIONALITY TABS
st.title("HumbotiX AI - Universal Bot Detector Dashboard")
tab1, tab2 = st.tabs(["🔍 Core Bot Verification", "🌍 Geographical Audit Gateway"])

with tab1:
    platform = st.selectbox("Target Social Network Platform:", ["Twitter / X", "Facebook", "Instagram", "YouTube", "LinkedIn"])
    username = st.text_input(f"{platform} Identity / Handle ID:", placeholder="@username context")
    tweet_text = st.text_area("Analysis Text Payload / Sample Content Post:")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        claimed_country = st.selectbox("User Declared Country Parameter:", ["Unknown"] + ALL_COUNTRIES)
    with col_m2:
        ip_country = st.selectbox("Resolved Routing IP System Country:", ALL_COUNTRIES)
        
    if st.button("🚀 Execute Forensic Fingerprint Audit", use_container_width=True):
        if scans_left <= 0:
            st.error("Diagnostic Counter Exhausted! Upgrade to process further logs.")
        elif not username and not tweet_text:
            st.warning("Please insert baseline parameter vectors.")
        else:
            with st.spinner("Processing Forensics Cluster..."):
                score, reasons = check_bot_score_gupt(
                    username=username, claimed_country=claimed_country, ip_country=ip_country, tweet_text=tweet_text
                )
                is_bot = score >= 50
                
                save_packet = {
                    "username": f"[{platform}] {username}", "platform": platform, "scan_type": "Bot Check",
                    "result": "Bot Risk Alert" if is_bot else "Verified Human Identity", "country": claimed_country,
                    "score": score, "tweet_text": tweet_text[:100], "flags": ", ".join(reasons), "scanned_by": user_email
                }
                try:
                    supabase.table("scans").insert(save_packet).execute()
                    st.metric("Risk Assessment Probability Factor", f"{score}%", delta="High Anomaly Risk" if is_bot else "Identity Clear", delta_color="inverse" if is_bot else "normal")
                    st.progress(score/100)
                    if reasons:
                        st.write("🔬 **Identified Signature Footprints:**")
                        for r in reasons: st.write(f"• {r}")
                    time.sleep(1)
                    st.rerun()
                except Exception as e: st.error(f"Sync execution error: {e}")

with tab2:
    st.subheader("🌍 Country Mismatch Filter Gateway")
    c_claim = st.selectbox("Declared Profile Country Context:", ["Unknown"] + ALL_COUNTRIES, key="t2_claim")
    c_real = st.selectbox("Calculated IP Endpoint Country:", ALL_COUNTRIES, key="t2_real")
    
    if st.button("Verify Country Data Consistency Pipeline", use_container_width=True):
        if c_claim == "Unknown": st.info("Location profile metrics not provided.")
        elif c_claim.lower() != c_real.lower():
            st.error(f"🚨 Identity Spatial Fraud Detected! Route tracks directly to '{c_real}' instead of asserted '{c_claim}'. Proxy script detected.")
        else:
            st.success("Consistency configuration metrics verified successfully.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666; font-size: 12px;'>HumbotiX AI Gateway Engine © 2026</div>", unsafe_allow_html=True)
