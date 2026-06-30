import streamlit as st
st.set_page_config(
    page_title="BotRadar - Free Bot Detector",
    page_icon="assets/logo.png",
    layout="wide"
)

# Google ke liye Description daal de
st.markdown("""
    <meta name="description" content="BotRadar is a free AI bot detector. Check if Twitter, Instagram, or Reddit accounts are bots. Scan any text for AI content. 100% Free Tool.">
    <meta name="keywords" content="bot detector, ai detector, free bot checker, BotRadar, twitter bot check, fake account detector">
""", unsafe_allow_html=True)

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
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

# NLTK requirements check quietly
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

# SECRETS SE TOKEN LO
ADMIN_PASS = st.secrets.get("ADMIN_PASS", "admin123")
X_BEARER_TOKEN = st.secrets.get("X_BEARER_TOKEN")

if 'admin' not in st.session_state:
    st.session_state.admin = False

# --- FRESH 3 FEATURES ENGINE CLASS ---
class ScanXAdvancedEngine:
    def __init__(self):
        pass

    def analyze_stylometry(self, text_list):
        if not text_list or len(text_list) == 0:
            return {"ai_probability": 0, "status": "No Data", "verdict": "No Data", "avg_sentence_length": 0, "text_uniformity_variance": 0}
        total_words = 0
        total_sentences = 0
        sentence_lengths = []
        special_char_count = 0
        for text in text_list:
            if not text: continue
            sentences = sent_tokenize(text)
            words = word_tokenize(text)
            total_sentences += len(sentences)
            total_words += len(words)
            if len(sentences) > 0:
                sentence_lengths.append(len(words) / len(sentences))
            special_char_count += len(re.findall(r"[!@#$%^&*()_+={}\[\]|\\:]", text))
        avg_sentence_length = (np.mean(sentence_lengths) if sentence_lengths else 0)
        length_variance = np.var(sentence_lengths) if sentence_lengths else 100
        ai_score = 0
        if 12 <= avg_sentence_length <= 25:
            ai_score += 35
        if length_variance < 15:
            ai_score += 45
        if (special_char_count / (total_words if total_words > 0 else 1) > 0.15):
            ai_score += 20
        return {
            "ai_probability": min(ai_score, 100),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "text_uniformity_variance": round(length_variance, 2),
            "verdict": "AI Generated" if ai_score >= 70 else "Human Written",
        }

    def analyze_server_heartbeat(self, timestamp_strings):
        if len(timestamp_strings) < 2:
            return {
                "heartbeat_detected": False,
                "bot_probability": 0,
                "reason": "Insufficient timestamp data",
                "verdict": "Organic or Manual Entry",
                "flags_triggered": [],
                "time_delta_variance_seconds": 0,
                "median_gap_seconds": 0,
                "median_absolute_deviation_mad": 0,
                "avg_gap_seconds": 0
            }
        timestamps = []
        for ts in timestamp_strings:
            try:
                ts = ts.strip()
                if ":" in ts and "-" in ts:
                    timestamps.append(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"))
                elif ":" in ts:
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    if len(ts.split(":")) == 2:
                        timestamps.append(datetime.strptime(f"{today_str} {ts}:00", "%Y-%m-%d %H:%M:%S"))
                    else:
                        timestamps.append(datetime.strptime(f"{today_str} {ts}", "%Y-%m-%d %H:%M:%S"))
            except ValueError:
                continue
        timestamps.sort()
        time_deltas = []
        for i in range(len(timestamps) - 1):
            delta = (timestamps[i + 1] - timestamps[i]).total_seconds()
            time_deltas.append(delta)
        if not time_deltas:
            return {
                "heartbeat_detected": False,
                "bot_probability": 0,
                "reason": "No valid intervals",
                "verdict": "No valid intervals",
                "flags_triggered": [],
                "time_delta_variance_seconds": 0,
                "median_gap_seconds": 0,
                "median_absolute_deviation_mad": 0,
                "avg_gap_seconds": 0
            }
        np_deltas = np.array(time_deltas)
        delta_variance = np.var(np_deltas)
        avg_delta = np.mean(np_deltas)
        median_delta = np.median(np_deltas)
        mad = np.median(np.abs(np_deltas - median_delta))
        bot_probability = 0
        reasons = []
        if delta_variance < 2.0 and avg_delta > 0:
            bot_probability += 60
            reasons.append("Ultra-low time variance detected (Static Interval)")
        elif delta_variance < 15.0:
            bot_probability += 40
            reasons.append("Low time variance detected (Scheduled Script)")
        if mad < 5.0 and avg_delta > 0:
            bot_probability += 40
            reasons.append("High pattern consistency caught by MAD (Smart/Jitter Bot)")
        elif mad < 12.0:
            bot_probability += 20
            reasons.append("Moderate pattern consistency caught by MAD")
        bot_probability = min(bot_probability, 100)
        if bot_probability >= 80:
            verdict = "🚨 100% Automated Script/Server Detected"
        elif bot_probability >= 50:
            verdict = "⚠️ High Probability of Scheduled/Smart Bot"
        else:
            verdict = "Normal Human Timing (Organic)"
        return {
            "heartbeat_detected": True if bot_probability >= 50 else False,
            "time_delta_variance_seconds": round(delta_variance, 4),
            "median_gap_seconds": round(median_delta, 2),
            "median_absolute_deviation_mad": round(mad, 4),
            "avg_gap_seconds": round(avg_delta, 2),
            "bot_probability": bot_probability,
            "flags_triggered": reasons,
            "verdict": verdict,
        }

    def cross_platform_persona_tracker(self, username, post_text):
        crypto_links = re.findall(r"(t\.me|telegram|discord|crypto|whatsapp)", post_text.lower())
        platforms_found = []
        suspicious_score = 0
        if len(crypto_links) > 0:
            platforms_found.append("Telegram / Discord Channels")
            suspicious_score += 50
        if re.search(r"\d{5,}", username):
            platforms_found.append("Coordinated Multi-Platform Name Grid")
            suspicious_score += 40
        return {
            "cross_platform_spam": True if suspicious_score >= 50 else False,
            "detected_networks": platforms_found if platforms_found else ["None Isolated"],
            "coordinated_risk_score": suspicious_score,
            "verdict": "Coordinated Inauthentic Behavior (CIB) Flagged" if suspicious_score >= 50 else "Safe",
        }

# Initialize Advanced Engine
advanced_engine = ScanXAdvancedEngine()

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

# ✅ TEXT PATTERN ANALYSIS
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
        elif 0.05 < caps_ratio < 0.4:
            details['caps_flag'] = "Human: Natural mix"
    lines = [line for line in text.split('\n') if line.strip()]
    if len(lines) > 2:
        line_lengths = [len(line) for line in lines]
        avg_len = sum(line_lengths) / len(line_lengths)
        variance = sum((x - avg_len) ** 2 for x in line_lengths) / len(line_lengths)
        details['alignment_variance'] = f"{variance:.1f}"
        if variance < 10:
            score += 20
            reasons.append("Perfect Line Alignment - Bot formatting")
            details['alignment_flag'] = "Bot: Too perfect"
        else:
            details['alignment_flag'] = "Human: Natural variance"
    dots = text.count('.')
    commas = text.count(',')
    exclaim = text.count('!')
    question = text.count('?')
    total_punct = dots + commas + exclaim + question
    details['punctuation'] = f".={dots}, ={commas},!={exclaim},?={question}"
    if total_punct > 5 and dots == total_punct:
        score += 15
        reasons.append("Robotic Punctuation - Only periods used")
    emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF]', text))
    details['emoji_count'] = emoji_count
    if emoji_count > 10:
        score += 10
        reasons.append(f"Emoji Spam: {emoji_count} emojis - Bot template")
    words = text.lower().split()
    if len(words) > 10:
        word_freq = {}
        for word in words:
            if len(word) > 4:
                word_freq[word] = word_freq.get(word, 0) + 1
        max_repeat = max(word_freq.values()) if word_freq else 0
        details['max_word_repeat'] = max_repeat
        if max_repeat > 5:
            score += 15
            reasons.append(f"Word Repetition: '{max(word_freq, key=word_freq.get)}' {max_repeat}x - Bot loop")
    return min(score, 100), reasons, details

# ✅ BIO DEEP SCAN
def analyze_bio(bio):
    if not bio:
        return 0, [], {}
    score = 0
    reasons = []
    details = {}
    bio_lower = bio.lower()
    ai_phrases = ['as an ai', 'i am an ai', 'i cannot', 'language model', 'i do not have personal', 'i am not able to', 'as a large language']
    for phrase in ai_phrases:
        if phrase in bio_lower:
            score += 40
            reasons.append(f"AI Disclosure: '{phrase}' - 100% Bot")
            details['ai_phrase_found'] = phrase
            break
    if re.match(r'^[A-Z][a-z]+ \| [A-Z][a-z]+ \| [A-Z][a-z]+$', bio.strip()):
        score += 20
        reasons.append("Template Bio: Word | Word | Word format - Bot generated")
        details['template_bio'] = "Yes"
    links = len(re.findall(r'http[s]?://|t\.me/|discord\.gg/|bit\.ly/', bio_lower))
    details['link_count'] = links
    if links >= 3:
        score += 15
        reasons.append(f"Link Spam: {links} links in bio - Promo bot")
    hashtags = len(re.findall(r'#\w+', bio))
    details['hashtag_count'] = hashtags
    if hashtags > 8:
        score += 10
        reasons.append(f"Hashtag Spam: {hashtags} tags - SEO bot")
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
    try:
        url = f"https://nitter.net/{username}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            bio = soup.find('div', class_='profile-bio')
            bio = bio.text.strip() if bio else "Bio not found"
            followers = soup.find('a', href=f'/{username}/followers')
            followers = followers.text.split()[0] if followers else "0"
            tweets = soup.find('a', href=f'/{username}')
            tweets = tweets.text.split()[0] if tweets else "0"
            return {'bio': bio, 'followers': followers, 'tweet_count': tweets, 'is_verified': False, 'account_age': 0}
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
        reasons.append(f"Roz {int(tpd)} tweet - Bot speed")
    elif tpd > 20:
        score += 10
        reasons.append(f"Roz {int(tpd)} tweet - Suspicious")

    if tweet_text:
        text_score, text_reasons, text_details = analyze_text_pattern(tweet_text)
        score += text_score
        reasons.extend(text_reasons)
        forensics['text_analysis'] = text_details

    if bio:
        bio_score, bio_reasons, bio_details = analyze_bio(bio)
        score += bio_score
        reasons.extend(bio_reasons)
        forensics['bio_analysis'] = bio_details

    numbers = len(re.findall(r'\d', username))
    forensics['username_numbers'] = numbers
    if numbers >= 8:
        score += 15
        reasons.append("8+ number username - Auto generated")
    if re.search(r'user\d+|bot\d+|temp\d+|test\d+', username.lower()):
        score += 20
        reasons.append("Fake/Bot jaisa username")

    if tweet_time and user_view_country and claimed_country and ip_country:
        try:
            tweet_hour, tweet_min = map(int, tweet_time.split(":"))
            user_country_name = DISPLAY_TO_NAME_MAP.get(user_view_country)

            if user_country_name and user_country_name in COUNTRIES_TZ:
                user_tz_str = COUNTRIES_TZ[user_country_name]["tz"]
                user_tz = pytz.timezone(user_tz_str)

                if claimed_country == "Unknown":
                    claimed_tz_str = 'Asia/Kolkata'
                elif claimed_country in COUNTRIES_TZ:
                    claimed_tz_str = COUNTRIES_TZ[claimed_country]["tz"]
                else:
                    claimed_tz_str = 'Asia/Kolkata'
                claimed_tz = pytz.timezone(claimed_tz_str)

                today = datetime.now().date()
                user_dt = user_tz.localize(datetime(today.year, today.month, today.day, tweet_hour, tweet_min))
                claimed_dt = user_dt.astimezone(claimed_tz)
                country_hour = claimed_dt.hour
                forensics['claimed_country_hour'] = country_hour

                if 0 <= country_hour <= 6:
                    score += 15
                    reasons.append(f"{claimed_country} me raat {country_hour}:00 baje tweet - Suspicious")

                if claimed_country == "Unknown":
                    reasons.append("Location Not Claimed - Mismatch Check Skipped")
                elif ip_country.lower() != claimed_country.lower():
                    score += 60
                    reasons.append(f"Country Mismatch: {claimed_country} vs {ip_country} - High Risk")
                    forensics['country_mismatch'] = f"{claimed_country} vs {ip_country}"
        except Exception as e:
            reasons.append(f"Time check error: {str(e)}")

    if is_verified and numbers >= 4:
        score += 30
        reasons.append("Verified Bot Loophole Detected")

    if tweet_text and re.search(r'(.{10,})\1{3,}', tweet_text):
        score += 15
        reasons.append("Copy-paste pattern - Bot signature")

    return min(score, 100), reasons, int(tpd), forensics

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
                    tz = pytz.timezone(tz_list[0])
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
        result = sorted(result, key=lambda x: x["name"])
        return result
    except: return []

# Supabase connection
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("BotRadar Ai - Universal Bot Detector")
st.caption("Multi-Platform Account & Text Scanner | Powered by AI")
st.info("⚠️ Disclaimer: This tool provides an AI-assisted probability estimate and should not be treated as definitive proof.")

with st.sidebar:
    if not st.session_state.admin:
        password = st.text_input("Admin Access:", type="password")
        if st.button("Login"):
            if password == ADMIN_PASS:
                st.session_state.admin = True
                st.rerun()
            else:
                st.error("Wrong Password")
    else:
        st.success("Admin Mode: ON")
        if st.button("Logout"):
            st.session_state.admin = False
            st.rerun()

tab1, tab2 = st.tabs(["🔍 Bot Check", "🌍 Country Check"])

with tab1:
    st.subheader("Scan Account or Post")
    platform = st.selectbox(
        "Select Platform:",
        ["Twitter / X", "Facebook", "Instagram", "YouTube", "LinkedIn", "WhatsApp", "Other Platforms"]
    )
    username = st.text_input(f"{platform} Username / Profile Link:", placeholder="@username or paste profile URL")
    scan_mode = st.radio("Scan Mode:", ["Auto - X API/Nitter se data lao", "Manual - Khud bharo"])

    # ✅ TEEN NEW FEATURES KE TOGGLE BUTTONS ADDED HERE
    st.markdown("### 🛠️ Scan X Advanced Engines Settings")
    enable_stylo = st.toggle("✍️ Enable AI Stylometry Analysis", value=True)
    enable_heartbeat = st.toggle("💓 Enable MAD Server Heartbeat Engine", value=True)
    enable_tracker = st.toggle("🌐 Enable Cross-Platform Persona Tracker", value=True)

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
    multiple_timestamps = ""
    past_posts_corpus = ""

    if scan_mode == "Manual - Khud bharo" or st.session_state.admin:
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
        
        # ✅ INPUTS FOR THE NEW FEATURES IN MANUAL MODE
        if enable_stylo:
            past_posts_corpus = st.text_area("✍️ Stylometry Corpus (Paste multiple past posts separated by new lines):", 
                                             placeholder="Post 1\nPost 2\nPost 3...", height=100)
        if enable_heartbeat:
            multiple_timestamps = st.text_area("💓 Heartbeat Timestamps (Format HH:MM or YYYY-MM-DD HH:MM:SS, one per line):",
                                                placeholder="14:30\n14:35\n14:40", height=100)

        bio = st.text_area("Bio / About:", placeholder="Paste account bio here...", height=100, key="bio")

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
            user_view_country = st.selectbox("Which country are you viewing this tweet from?", COUNTRY_DISPLAY_LIST, index=0, key="vcountry")

        claimed_country = st.selectbox("Claimed Country (What user wrote in bio)", ["Unknown"] + ALL_COUNTRIES, key="claimed_country")
        ip_country = st.selectbox("Real IP Country (From API)", ALL_COUNTRIES, key="ip_country")

    if st.button("🚀 Scan Karo"):
        if username or (scan_mode == "Manual - Khud bharo" and (tweet_text or comment1 or comment2 or past_posts_corpus or multiple_timestamps)):
            clean_username = username if username.startswith("@") or "http" in username else f"@{username}"
            if not username and (tweet_text or comment1 or comment2):
                clean_username = "Anonymous Text"

            with st.spinner(f"Vasuki Ai Brain Scanning {platform} data... 🧠"):
                if scan_mode == "Auto - X API/Nitter se data lao" and platform == "Twitter / X":
                    x_data = fetch_x_data(clean_username)
                    if x_data:
                        bio = x_data.get('bio', '')
                        is_verified = x_data.get('is_verified', False)
                        tweet_count = int(x_data.get('tweet_count', 0)) if str(x_data.get('tweet_count', 0)).isdigit() else 0
                        account_age_days = x_data.get('account_age', 0)
                        st.success("✅ Data fetched from X API/Nitter")
                    else:
                        st.warning("⚠️ Data not found. Use Manual mode.")

                fuzzy = 0
                force_bot = False
                if comment1 and comment2:
                    fuzzy = round(SequenceMatcher(None, comment1, comment2).ratio() * 100, 2)
                    st.markdown("### 🧠 Vasuki Brain: Comment Comparison")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Fuzzy Match", f"{fuzzy}%")
                    if fuzzy >= 65:
                        c2.metric("Risk", "HIGH 🚨")
                        st.error("**BOT DETECTED:** Comments 65%+ match. Spam activity.")
                        force_bot = True
                    else:
                        c2.metric("Risk", "LOW ✅")
                        st.success("**SAFE:** Comments alag hain.")
                    st.divider()

                max_similarity = 0
                matched_username = ""
                is_coordinated = False

                def extract_clean_username(raw_username):
                    u = str(raw_username).lower()
                    u = re.sub(r'\[.*?\]', '', u)
                    u = u.replace('@', '').strip()
                    return u

                current_user_clean = extract_clean_username(clean_username)
                if current_user_clean and current_user_clean != "anonymous text":
                    try:
                        all_scans = supabase.table("scans").select("username, score, created_at").execute()
                        if all_scans.data:
                            for scan in all_scans.data:
                                db_user_clean = extract_clean_username(scan.get('username', ''))
                                if db_user_clean == current_user_clean:
                                    old_score = scan.get('score', 0)
                                    old_date = scan.get('created_at', '')[:10]
                                    st.error(f"🚨 DUPLICATE ACCOUNT: @{current_user_clean} already scanned on {old_date}")
                                    st.warning(f"Previous Bot Score: {old_score}% | FORCING 100% BOT NOW")
                                    force_bot = True
                                    st.divider()
                                    break
                    except Exception as e:
                        if st.session_state.admin: st.write(f"DB check error: {e}")

                compare_text = comment1 if comment1 else tweet_text
                if compare_text and len(compare_text.strip()) > 20:
                    try:
                        past_scans = supabase.table("scans").select("tweet_text, username").limit(100).execute()
                        if past_scans.data:
                            for s in past_scans.data:
                                old_text = s.get('tweet_text', '')
                                old_user_raw = s.get('username', '')
                                old_user_clean = extract_clean_username(old_user_raw)
                                if old_text and old_text.strip() == compare_text.strip() and old_user_clean == current_user_clean:
                                    st.error("🚨 EXACT DUPLICATE: Same account + same content scanned before.")
                                    force_bot = True
                                    st.stop()
                                elif old_text and old_user_clean != current_user_clean:
                                    sim = SequenceMatcher(None, compare_text.lower(), old_text.lower()).ratio() * 100
                                    if sim > max_similarity:
                                        max_similarity = sim
                                        matched_username = old_user_raw
                    except Exception as e:
                        if st.session_state.admin: st.write(f"Similarity check error: {e}")

                # RUNNING NEW ENGINES IF TOGGLED
                stylo_report = {"ai_probability": 0, "verdict": "Disabled", "avg_sentence_length": 0, "text_uniformity_variance": 0}
                if enable_stylo:
                    text_corpus = [t for t in past_posts_corpus.split("\n") if t.strip()] if past_posts_corpus else [t for t in [tweet_text, comment1, comment2] if t]
                    stylo_report = advanced_engine.analyze_stylometry(text_corpus)

                heartbeat_report = {"bot_probability": 0, "verdict": "Disabled", "flags_triggered": [], "median_absolute_deviation_mad": 0, "time_delta_variance_seconds": 0}
                if enable_heartbeat:
                    timestamps_corpus = [t for t in multiple_timestamps.split("\n") if t.strip()] if multiple_timestamps else ([tweet_time] if tweet_time else [])
                    heartbeat_report = advanced_engine.analyze_server_heartbeat(timestamps_corpus)

                tracker_report = {"coordinated_risk_score": 0, "verdict": "Disabled", "detected_networks": ["Disabled"]}
                if enable_tracker:
                    tracker_report = advanced_engine.cross_platform_persona_tracker(clean_username, tweet_text if tweet_text else "")

                score, reasons, tpd, forensics = check_bot_score_gupt(
                    username=clean_username, bio=bio, is_verified=is_verified, tweet_count=tweet_count,
                    account_age=account_age_days, tweet_time=tweet_time, user_view_country=user_view_country,
                    claimed_country=claimed_country, ip_country=ip_country, tweet_text=tweet_text
                )

                # ADJUSTING SCORES BASED ON ACTIVE ENGINES
                if enable_stylo and stylo_report["ai_probability"] >= 70:
                    score += 15
                    reasons.append(f"Advanced Stylometry Check: {stylo_report['verdict']} ({stylo_report['ai_probability']}% Match)")
                if enable_heartbeat and heartbeat_report["bot_probability"] >= 50:
                    score += 20
                    for flag in heartbeat_report["flags_triggered"]:
                        reasons.append(f"Timing Engine: {flag}")
                if enable_tracker and tracker_report["coordinated_risk_score"] >= 50:
                    score += 15
                    reasons.append(f"Persona Tracker: {tracker_report['verdict']}")

                if comment1 and comment2 and fuzzy >= 65:
                    reasons.append(f"Comment Match: {fuzzy}% - Coordinated spam")
                    force_bot = True

                if force_bot or (comment1 and comment2 and fuzzy == 100):
                    score = 100
                    is_coordinated = True
                    reasons.append("FORCED BOT: Duplicate account or 100% comment match detected")
                elif max_similarity > 85 and matched_username:
                    score = 100
                    is_coordinated = True
                    reasons.append(f"Coordinated Bot: {max_similarity:.1f}% text match with {matched_username}")
                else:
                    if max_similarity > 70 and matched_username:
                        score += 20
                        reasons.append(f"High Text Similarity: {max_similarity:.1f}% with {matched_username}")
                    score = min(score, 100)

                is_bot = score >= 50
                result_text = f"🤖 Bot Account - {score}% Match" if is_bot else f"✅ Human - {100-score}% Safe"
                verified_text = "✅ Verified" if is_verified else "❌ Unverified"

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
                    "tweet_text": tweet_text,
                    "flags": ", ".join(reasons) if reasons else "None",
                    "is_verified": is_verified
                }

                try:
                    supabase.table("scans").insert(result).execute()
                    st.success("🎉 Scan Complete!")
                    st.subheader("📊 Bot Probability Meter")
                    st.progress(score/100)
                    st.metric("Bot Score", f"{score}%", delta=f"{'Danger' if score>=70 else 'Suspicious' if score>=50 else 'Safe'}", delta_color="inverse")

                    with st.expander("🔬 Forensic Report - Full Detail", expanded=True):
                        st.markdown("### 🚀 Scan X Advanced Insights (New Features Active)")
                        col_adv1, col_adv2, col_adv3 = st.columns(3)
                        with col_adv1:
                            st.markdown("**✍️ AI Stylometry Analysis**")
                            st.write(f"Verdict: `{stylo_report['verdict']}`")
                            st.write(f"AI Probability: `{stylo_report['ai_probability']}%`")
                            st.write(f"Avg Sentence Length: `{stylo_report['avg_sentence_length']}`")
                        with col_adv2:
                            st.markdown("**💓 MAD Timing Engine**")
                            st.write(f"Verdict: `{heartbeat_report['verdict']}`")
                            st.write(f"Bot Probability: `{heartbeat_report['bot_probability']}%`")
                            st.write(f"MAD Variance: `{heartbeat_report['time_delta_variance_seconds']}s`")
                        with col_adv3:
                            st.markdown("**🌐 Cross-Platform Tracker**")
                            st.write(f"Verdict: `{tracker_report['verdict']}`")
                            st.write(f"Risk Score: `{tracker_report['coordinated_risk_score']}`")
                            st.write(f"Networks: `{', '.join(tracker_report['detected_networks'])}`")
                        
                        st.divider()
                        st.markdown("**📈 Statistical Analysis:**")
                        col_f1, col_f2, col_f3 = st.columns(3)
                        with col_f1:
                            st.metric("TPD", forensics.get('tpd', 0))
                            st.metric("Username Numbers", forensics.get('username_numbers', 0))
                        with col_f2:
                            st.metric("Account Age", f"{account_age_days} days")
                        with col_f3:
                            st.metric("Total Posts", tweet_count)

                        if reasons:
                            st.markdown("**⚠️ Detection Flags:**")
                            for reason in reasons:
                                st.write(f"• {reason}")

                    if is_bot:
                        st.error(f"🚨 RESULT: {result_text}")
                    else:
                        st.success(f"💚 RESULT: {result_text}")
                except Exception as e:
                    st.error(f"Supabase Error: {e}")
        else:
            st.warning("⚠️ Username or Text is required to scan!")

with tab2:
    st.subheader("🌍 Country Mismatch Detector")
    col1, col2 = st.columns(2)
    with col1:
        claimed = st.selectbox("Claimed Country:", ["Unknown"] + ALL_COUNTRIES, key="claimed_cc")
    with col2:
        real_ip = st.selectbox("Real IP Country:", ALL_COUNTRIES, key="real_cc")
    username_cc = st.text_input("Username for reference:", placeholder="@username", key="cc_user")

    if st.button("🔍 Check Country"):
        if claimed == "Unknown":
            st.info("ℹ️ Location Not Claimed - Mismatch Check Skipped")
        elif claimed.lower() != real_ip.lower():
            st.error(f"🚨 Mismatch Detected!")
        else:
            st.success(f"✅ Match! Both countries same: {claimed}")

st.sidebar.header("📜 Live Scan History")
try:
    scans = supabase.table("scans").select("*").order("created_at", desc=True).limit(10).execute()
    if scans.data:
        for scan in scans.data:
            score = scan.get('score', 0)
            is_bot = score >= 50
            verdict_icon = "🤖 Bot" if is_bot else "✅ Human"
            username_display = str(scan.get('username', '')).replace('[Twitter / X] ', '')[:20]
            st.sidebar.markdown(f"**{username_display}** - {score}% {verdict_icon}")
except: pass

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666; font-size: 14px;'> Version: 2 BotRadar Ai | © 2026 All Rights Reserved</div>", unsafe_allow_html=True)
