import streamlit as st
import requests
from datetime import datetime
from supabase import create_client, Client
import os

# Supabase configuration - Streamlit secrets use karo
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Page configuration
st.set_page_config(
    page_title="Bot Country Checker",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
 .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
 .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
 .stButton > button:hover {
        background-color: #0d5a8a;
    }
</style>
""", unsafe_allow_html=True)

# Application title
st.markdown('<h1 class="main-header">🤖 Bot Country Checker</h1>', unsafe_allow_html=True)
st.markdown("### Check if a username is a bot and verify country mismatch")
st.markdown("---")

# Function to save scan results
def save_scan(result):
    try:
        supabase.table("scans").insert(result).execute()
        return True
    except Exception as e:
        st.error(f"Failed to save scan: {e}")
        return False

# Function to get IP geolocation
def get_ip_location(ip_address):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        data = response.json()
        if data["status"] == "success":
            return data["country"]
        return "Unknown"
    except:
        return "Unknown"

# Function to check if username is bot - placeholder logic
def check_bot_status(username, platform):
    # Replace this with your actual bot detection logic
    bot_keywords = ["bot", "fake", "spam", "test123"]
    username_lower = username.lower()

    for keyword in bot_keywords:
        if keyword in username_lower:
            return True, "Bot patterns detected in username"

    if len(username) < 4:
        return True, "Username too short"

    if username.isdigit():
        return True, "Username contains only numbers"

    return False, "No bot patterns detected"

# --- Live Scan History Sidebar ---
st.sidebar.markdown("### 📜 Live Scan History")
st.sidebar.markdown("---")

try:
    scans = supabase.table("scans").select("*").order("created_at", desc=True).limit(10).execute()
    if scans.data:
        for scan in scans.data:
            result_emoji = "✅" if "REAL" in scan.get("result", "") or "Match" in scan.get("result", "") else "❌"

            with st.sidebar.container():
                st.markdown(f"{result_emoji} *{scan.get('username', 'N/A')}*")
                st.markdown(f"{scan.get('result', 'N/A')}")
                st.caption(f"📍 {scan.get('country', 'N/A')} | ⏱️ {scan['created_at'][:19].replace('T', ' ')}")
                st.markdown("---")
    else:
        st.sidebar.info("No scans yet")
except Exception as e:
    st.sidebar.error(f"Failed to load history: {e}")

# --- Main Application ---
col1, col2 = st.columns([2, 1])

with col1:
    tab1, tab2, tab3 = st.tabs(["🔍 Bot Check", "🌍 Country Check", "📊 Manual Check"])

    with tab1:
        st.header("Bot Detection Check")
        st.markdown("Check if a social media username exhibits bot-like behavior")

        platform = st.selectbox(
            "Select Platform",
            ["Instagram", "Twitter", "TikTok", "YouTube", "Facebook", "LinkedIn"],
            key="bot_platform"
        )

        username = st.text_input(
            "Enter Username",
            placeholder="e.g. john_doe123",
            key="bot_username"
        )

        claimed_country = st.selectbox(
            "Claimed Country",
            ["USA", "India", "UK", "Canada", "Australia", "Germany", "France", "Brazil", "Japan", "Other"],
            key="bot_country"
        )

        if st.button("🚀 Check Bot Status", key="bot_check_btn"):
            if username:
                clean_username = username.strip().replace("@", "")

                with st.spinner("Analyzing username..."):
                    is_bot, reason = check_bot_status(clean_username, platform)

                    if is_bot:
                        result_text = f"❌ BOT DETECTED: {reason}"
                        st.error(result_text)
                    else:
                        result_text = "✅ REAL USER: No bot patterns detected"
                        st.success(result_text)

                    st.info(f"*Platform:* {platform}")
                    st.info(f"*Username:* {clean_username}")
                    st.info(f"*Claimed Country:* {claimed_country}")

                    # Save to Supabase
                    result = {
                        "username": f"[{platform}] {clean_username}",
                        "platform": platform,
                        "scan_type": "Bot Check",
                        "result": result_text,
                        "country": claimed_country
                    }
                    if save_scan(result):
                        st.rerun()
            else:
                st.warning("⚠️ Please enter a username")

    with tab2:
        st.header("Country Verification Check")
        st.markdown("Verify if claimed country matches actual IP geolocation")

        username_cc = st.text_input(
            "Enter Username for Country Check",
            placeholder="e.g. user123",
            key="country_username"
        )

        claimed = st.selectbox(
            "Claimed Country",
            ["USA", "India", "UK", "Canada", "Australia", "Germany", "France", "Brazil", "Japan", "Other"],
            key="country_claimed"
        )

        ip_address = st.text_input(
            "Enter IP Address (Optional)",
            placeholder="e.g. 8.8.8.8",
            key="ip_input"
        )

        if st.button("🌍 Verify Country", key="country_check_btn"):
            if username_cc:
                with st.spinner("Verifying location..."):
                    if ip_address:
                        real_country = get_ip_location(ip_address)
                    else:
                        real_country = "Unknown"

                    if claimed == real_country:
                        result_text = f"✅ Country Match: {claimed}"
                        st.success(result_text)
                        st.balloons()
                    else:
                        result_text = f"❌ Country Mismatch: Claimed {claimed} vs Detected {real_country}"
                        st.error(result_text)

                    st.info(f"*Username:* {username_cc}")
                    st.info(f"*Claimed Country:* {claimed}")
                    st.info(f"*Detected Country:* {real_country}")

                    # Save to Supabase
                    result = {
                        "username": f"[CountryCheck] {username_cc}",
                        "platform": "Country Check",
                        "scan_type": "Country Check",
                        "result": result_text,
                        "country": claimed
                    }
                    if save_scan(result):
                        st.rerun()
            else:
                st.warning("⚠️ Please enter a username")

    with tab3:
        st.header("Manual Text Analysis")
        st.markdown("Paste any text to analyze for bot patterns")

        manual_text = st.text_area(
            "Enter text to analyze",
            height=150,
            placeholder="Paste suspicious text, comments, or bio here..."
        )

        if st.button("🔬 Analyze Text", key="manual_check_btn"):
            if manual_text:
                with st.spinner("Analyzing text..."):
                    # Simple bot detection logic for text
                    spam_keywords = ["buy now", "click here", "free money", "crypto", "investment", "whatsapp me"]
                    text_lower = manual_text.lower()

                    spam_found = [kw for kw in spam_keywords if kw in text_lower]

                    if spam_found:
                        result_text = f"❌ SPAM DETECTED: Found keywords {spam_found}"
                        st.error(result_text)
                    else:
                        result_text = "✅ CLEAN: No spam patterns detected"
                        st.success(result_text)

                    st.info(f"*Text Length:* {len(manual_text)} characters")
                    st.info(f"*Word Count:* {len(manual_text.split())} words")

                    # Save to Supabase
                    result = {
                        "username": "[Manual] Text Analysis",
                        "platform": "Manual Check",
                        "scan_type": "Manual Check",
                        "result": result_text,
                        "country": "N/A"
                    }
                    if save_scan(result):
                        st.rerun()
            else:
                st.warning("⚠️ Please enter some text to analyze")

with col2:
    st.markdown("### 📋 Instructions")
    st.info("""
    *How to use:*

    1. *Bot Check*: Enter username and select platform to detect bots

    2. *Country Check*: Verify if user's claimed country matches IP location

    3. *Manual Check*: Paste text to check for spam patterns

    4. *History*: View last 10 scans in the sidebar
    """)

    st.markdown("### ⚙️ System Status")
    try:
        test_query = supabase.table("scans").select("id").limit(1).execute()
        st.success("✅ Database Connected")
    except:
        st.error("❌ Database Error")

    st.markdown("### 📊 Quick Stats")
    try:
        total_scans = supabase.table("scans").select("id", count="exact").execute()
        st.metric("Total Scans", total_scans.count)
    except:
        st.metric("Total Scans", "N/A")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Bot Country Checker v2.0 | Built with Streamlit & Supabase</div>",
    unsafe_allow_html=True
)
