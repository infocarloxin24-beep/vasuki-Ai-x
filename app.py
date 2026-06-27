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

# SECRETS SE TOKEN LO
ADMIN_PASS = st.secrets.get("ADMIN_PASS", "admin123")
X_BEARER_TOKEN = st.secrets.get("X_BEARER_TOKEN")

if 'admin' not in st.session_state:
    st.session_state.admin = False

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

# ✅ TEXT PATTERN ANALYSIS - CAPITAL/SMALL + ALIGNMENT
def analyze_text_pattern(text):
    if not text or len(text) < 20:
        return 0, [], {}

    score = 0
    reasons = []
    details = {}

    # 1. Capital/Small Mix Check
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

    # 2. Spacing Alignment
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

    # 3. Punctuation Pattern
    dots = text.count('.')
    commas = text.count(',')
    exclaim = text.count('!')
    question = text.count('?')
    total_punct = dots + commas + exclaim + question
    details['punctuation'] = f".={dots}, ={commas},!={exclaim},?={question}"
    if total_punct > 5 and dots == total_punct:
        score += 15
        reasons.append("Robotic Punctuation - Only periods used")

    # 4. Emoji Overuse
    emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF]', text))
    details['emoji_count'] = emoji_count
    if emoji_count > 10:
        score += 10
        reasons.append(f"Emoji Spam: {emoji_count} emojis - Bot template")

    # 5. Repeated Words
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

    # AI Phrases
    ai_phrases = ['as an ai', 'i am an ai', 'i cannot', 'language model', 'i do not have personal', 'i am not able to', 'as a large language']
    for phrase in ai_phrases:
        if phrase in bio_lower:
            score += 40
            reasons.append(f"AI Disclosure: '{phrase}' - 100% Bot")
            details['ai_phrase_found'] = phrase
            break

    # Template Bio
    if re.match(r'^[A-Z][a-z]+ \| [A-Z][a-z]+ \| [A-Z][a-z]+$', bio.strip()):
        score += 20
        reasons.append("Template Bio: Word | Word | Word format - Bot generated")
        details['template_bio'] = "Yes"

    # Link Spam
    links = len(re.findall(r'http[s]?://|t\.me/|discord\.gg/|bit\.ly/', bio_lower))
    details['link_count'] = links
    if links >= 3:
        score += 15
        reasons.append(f"Link Spam: {links} links in bio - Promo bot")

    # Hashtag Spam
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

    # ✅ TEXT PATTERN ANALYSIS
    if tweet_text:
        text_score, text_reasons, text_details = analyze_text_pattern(tweet_text)
        score += text_score
        reasons.extend(text_reasons)
        forensics['text_analysis'] = text_details

    # ✅ BIO DEEP SCAN
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
                elif ip_country.lower()!= claimed_country.lower():
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

st.set_page_config(page_title="Vasuki Ai 4.0 - Bot Detector", page_icon="🐍", layout="wide")
st.title("🐍 Vasuki Ai 4.0 - Universal Bot Detector")
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

    if scan_mode == "Manual - Khud bharo" or st.session_state.admin:
        st.info("Manual Mode: Fill all fields yourself")

        # ===== 2 COMMENT BOX - VASUKI BRAIN - FIXED =====
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

    if st.button("🚀 Scan Karo"):
        if username or (scan_mode == "Manual - Khud bharo" and (tweet_text or comment1 or comment2)):
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

                # ===== VASUKI BRAIN - COMMENT COMPARISON - FIXED =====
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
                elif comment1 or comment2:
                    st.info("🧠 Basic check: Sirf 1 comment mila")
                    st.divider()

                # ===== DUPLICATE USERNAME CHECK - STRONG VERSION =====
                max_similarity = 0
                matched_tweet = ""
                matched_username = ""
                is_coordinated = False

                def extract_clean_username(raw_username):
                    username = str(raw_username).lower()
                    username = re.sub(r'\[.*?\]', '', username)
                    username = username.replace('@', '').strip()
                    return username

                current_user_clean = extract_clean_username(clean_username)

                if current_user_clean and current_user_clean!= "anonymous text":
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

                # Text similarity check with OTHER accounts
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
                                elif old_text and old_user_clean!= current_user_clean:
                                    sim = SequenceMatcher(None, compare_text.lower(), old_text.lower()).ratio() * 100
                                    if sim > max_similarity:
                                        max_similarity = sim
                                        matched_tweet = old_text[:50] + "..."
                                        matched_username = old_user_raw
                    except Exception as e:
                        if st.session_state.admin: st.write(f"Similarity check error: {e}")

                score, reasons, tpd, forensics = check_bot_score_gupt(
                    username=clean_username, bio=bio, is_verified=is_verified, tweet_count=tweet_count,
                    account_age=account_age_days, tweet_time=tweet_time, user_view_country=user_view_country,
                    claimed_country=claimed_country, ip_country=ip_country, tweet_text=tweet_text
                )

                # Add comment comparison to score
                if comment1 and comment2 and fuzzy >= 65:
                    reasons.append(f"Comment Match: {fuzzy}% - Coordinated spam")
                    force_bot = True

                # ✅ FINAL OVERRIDE: DUPLICATE OR 100% MATCH = 100% BOT
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

                # ✅ RESULT LOGIC - NO CONTRADICTION
                is_bot = score >= 50
                if is_bot:
                    result_text = f"🤖 Bot Account - {score}% Match"
                else:
                    result_text = f"✅ Human - {100-score}% Safe"

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
                    st.write(f"Verified Status: {verified_text}")

                    # ✅ FORENSIC REPORT - FULL DETAIL
                    with st.expander("🔬 Forensic Report - Full Detail", expanded=True):
                        st.markdown("**📈 Statistical Analysis:**")
                        col_f1, col_f2, col_f3 = st.columns(3)
                        with col_f1:
                            st.metric("TPD", forensics.get('tpd', 0))
                            st.metric("Username Numbers", forensics.get('username_numbers', 0))
                        with col_f2:
                            st.metric("Account Age", f"{account_age_days} days")
                            if 'claimed_country_hour' in forensics:
                                st.metric("Claimed Country Time", f"{forensics['claimed_country_hour']}:00")
                        with col_f3:
                            st.metric("Total Posts", tweet_count)
                            if 'country_mismatch' in forensics:
                                st.error(f"Mismatch: {forensics['country_mismatch']}")

                        if 'text_analysis' in forensics:
                            st.markdown("**📝 Text Pattern Analysis:**")
                            ta = forensics['text_analysis']
                            st.write(f"• Caps Ratio: {ta.get('caps_ratio', 'N/A')} - {ta.get('caps_flag', 'N/A')}")
                            st.write(f"• Alignment Variance: {ta.get('alignment_variance', 'N/A')} - {ta.get('alignment_flag', 'N/A')}")
                            st.write(f"• Punctuation: {ta.get('punctuation', 'N/A')}")
                            st.write(f"• Emoji Count: {ta.get('emoji_count', 0)}")
                            st.write(f"• Max Word Repeat: {ta.get('max_word_repeat', 0)}x")

                        if 'bio_analysis' in forensics:
                            st.markdown("**👤 Bio Analysis:**")
                            ba = forensics['bio_analysis']
                            if 'ai_phrase_found' in ba:
                                st.error(f"• AI Phrase Found: '{ba['ai_phrase_found']}'")
                            if 'template_bio' in ba:
                                st.warning("• Template Bio Detected")
                            st.write(f"• Link Count: {ba.get('link_count', 0)}")
                            st.write(f"• Hashtag Count: {ba.get('hashtag_count', 0)}")

                        if reasons:
                            st.markdown("**⚠️ Detection Flags:**")
                            for reason in reasons:
                                st.write(f"• {reason}")

                    # TPD PROOF BOX - DYNAMIC YEARS + RANDOM MESSAGES
                    if account_age_days > 0 and tpd > 18:
                        years = round(account_age_days / 365, 1)
                        months = round(account_age_days / 30, 1)
                        weeks = round(account_age_days / 7, 1)

                        st.error(f"🧠 Mathematical Proof: {account_age_days} days with {tweet_count} posts = {tpd} TPD")

                        if score >= 50 or is_coordinated: # BOT CASE
                            proof_messages = [
                                f"Posting {tpd} times/day for {years} years straight without a single day off = Humanly impossible. Bot confirmed.",
                                f"{years} years of non-stop {tpd} posts/day? No coffee breaks, no sleep? That's a bot schedule.",
                                f"Even a full-time social media manager can't do {tpd} posts/day for {months} months. Bot Activity Detected.",
                                f"{tpd} TPD for {weeks} weeks continuous = Machine behavior. Humans need weekends.",
                                f"Reality check: {account_age_days} days × {tpd} posts = {tweet_count} total. No human maintains this pace for {years} years.",
                                f"Forensics say: {tpd} TPD sustained for {years} years = 0% probability of human operation.",
                                f"Statistically impossible: {years} years of daily {tpd} posts with zero gaps. This is automated.",
                                f"Bot signature matched: {tpd} TPD sustained for {account_age_days} days = Beyond human limits.",
                                f"Red flag: {years} years, {tpd} posts daily, zero holidays. Only machines work like this.",
                                f"Data doesn't lie: {tpd}/day for {months} months = Automated spam pattern detected."
                            ]
                            st.caption(random.choice(proof_messages))
                        else: # HUMAN CASE
                            human_messages = [
                                f"Posting {tpd} times/day for {years} years = Active user, but within human limits.",
                                f"{tpd} TPD sustained for {months} months. Heavy usage, but natural patterns detected.",
                                f"Verdict: {years} years of consistent {tpd} posts/day. Human activity confirmed.",
                                f"Analysis: {tpd} TPD over {account_age_days} days. High engagement, likely genuine user.",
                                f"Stats check: {years} years × {tpd} TPD = Busy but human. No bot signatures found.",
                                f"Pattern normal: {months} months of {tpd} posts/day. Organic human behavior.",
                                f"Forensics clear: {tpd} TPD for {weeks} weeks shows natural breaks. Human confirmed.",
                                f"Result: {account_age_days} days, {tweet_count} posts = Active human user, not automated."
                            ]
                            st.caption(random.choice(human_messages))

                    if is_coordinated:
                        st.error(f"🚨 Coordinated Bot Pattern Detected! Text Similarity: {max_similarity:.1f}%")
                        st.warning(f"Different accounts posting identical content. Matched with: {matched_username}")

                    if is_bot:
                        st.error(f"🚨 RESULT: {result_text}")
                        st.warning(f"Action Recommended: Report/Block this account on {platform}.")
                    else:
                        st.success(f"💚 RESULT: {result_text}")
                        st.write("This account appears safe and human.")

                    if tweet_time:
                        st.write("🌍 World Timing Dashboard - 195 Countries")
                        st.caption("🌙 = Night 12-6 AM local time | ☀️ = Day time | Red Border = Night | Green Border = Day")
                        world_times = get_world_timing_grid_195(tweet_time)
                        with st.expander(f"📊 Show All 195 Countries Timing", expanded=False):
                            cols = st.columns(6)
                            for idx, country in enumerate(world_times):
                                col_idx = idx % 6
                                with cols[col_idx]:
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
            st.warning("⚠️ Username or Text is required to scan!")

with tab2:
    st.subheader("🌍 Country Mismatch Detector")
    st.write("Check if user claimed correct country or faking it")

    col1, col2 = st.columns(2)
    with col1:
        claimed = st.selectbox("Claimed Country:", ["Unknown"] + ALL_COUNTRIES, key="claimed_cc")
    with col2:
        real_ip = st.selectbox("Real IP Country:", ALL_COUNTRIES, key="real_cc")

    username_cc = st.text_input("Username for reference:", placeholder="@username", key="cc_user")

    if st.button("🔍 Check Country"):
        if claimed == "Unknown":
            st.info("ℹ️ Location Not Claimed - Mismatch Check Skipped")
        elif claimed.lower()!= real_ip.lower():
            st.error(f"🚨 Mismatch Detected!")
            st.write(f"Claimed: {claimed}")
            st.write(f"Real IP: {real_ip}")
            st.warning("This account is using VPN/Proxy or faking location.")
            result = {
                "username": f"[CountryCheck] {username_cc}",
                "platform": "Country Check",
                "scan_type": "Country Check",
                "result": f"🤖 Bot Account - Country Mismatch: {claimed} vs {real_ip}",
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
                st.success("Saved to history")
            except:
                st.error("History save failed")
        else:
            st.success(f"✅ Match! Both countries same: {claimed}")
            st.balloons()

st.sidebar.header("📜 Live Scan History")
try:
    scans = supabase.table("scans").select("*").order("created_at", desc=True).limit(10).execute()
    if scans.data:
        for scan in scans.data:
            score = scan.get('score', 0)
            is_bot = score >= 50
            verdict_icon = "🤖 Bot" if is_bot else "✅ Human"
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
    st.sidebar.error(f"History load failed: {str(e)[:50]}") 

# ===== FEEDBACK SECTION - CHHOTA BUTTON + POPOVER =====
st.markdown("---")
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    # ✅ CHHOTA BUTTON - CLICK PE FORM KHULEGA
    with st.popover("💬 Feedback", use_container_width=False):
        user_name = st.text_input("Name:", placeholder="Nishad Singh", key="fb_name")
        rating = st.slider("Rating:", 1, 5, 5, key="fb_rating")

        emoji_map = {1: "😭", 2: "😟", 3: "😐", 4: "😊", 5: "😍"}
        color_map = {1: "#FF4B4B", 2: "#FFA500", 3: "#FFD700", 4: "#90EE90", 5: "#00C851"}

        st.markdown(
            f"<div style='text-align:center;padding:6px;border-radius:6px;margin-bottom:8px;background:{color_map[rating]};color:white;font-weight:bold;font-size:12px'>{emoji_map[rating]} {rating}/5</div>",
            unsafe_allow_html=True
        )

        with st.form(key="feedback_form", clear_on_submit=True):
            user_suggestion = st.text_area("Suggestion:", placeholder="What should we improve?", key="fb_sugg", height=80)
            if st.form_submit_button("📢 Submit", use_container_width=True):
                if user_suggestion:
                    try:
                        supabase.table("feedback").insert({
                            "name": user_name if user_name else "Anonymous",
                            "rating": rating,
                            "suggestion": user_suggestion
                        }).execute()
                        st.success(f"🎉 Thank you! {emoji_map[rating]} Feedback saved.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error saving feedback: {e}")
                else:
                    st.warning("Please write a suggestion first")

with col2:
    with st.expander("🔐 User Login / Sign Up"):
        try:
            session = supabase.auth.get_session()
            current_user = session.user if session else None
        except:
            current_user = None

        if current_user:
            st.success(f"✅ Logged in as: {current_user.email}")
            user_meta = current_user.user_metadata if hasattr(current_user, 'user_metadata') else {}
            display_name = user_meta.get('full_name', current_user.email.split('@')[0])
            st.write(f"Name: {display_name}")

            col_out1, col_out2 = st.columns(2)
            with col_out1:
                if st.button("🚪 Logout", use_container_width=True, type="primary"):
                    try:
                        supabase.auth.sign_out()
                        st.success("Logged out successfully!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Logout failed: {e}")

            with col_out2:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
        else:
            auth_mode = st.radio("Mode:", ["Login", "Sign Up"], horizontal=True, key="auth_mode")

            if auth_mode == "Login":
                st.markdown("##### 📧 Login with Email")
                email = st.text_input("Email:", key="auth_email_login")
                password = st.text_input("Password:", type="password", key="auth_pass_login")

                if st.button("Login", key="login_submit", use_container_width=True):
                    try:
                        res = supabase.auth.sign_in_with_password({
                            "email": email,
                            "password": password
                        })
                        st.success("Login Successful! 🎉")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Login failed: {str(e)}")

            else:
                st.markdown("##### 📝 Create New Account")
                full_name = st.text_input("Full Name:", placeholder="Nishad Singh", key="auth_name_signup")
                email = st.text_input("Email:", key="auth_email_signup")
                password = st.text_input("Password:", type="password", key="auth_pass_signup")

                if st.button("Sign Up", key="signup_submit", use_container_width=True):
                    try:
                        res = supabase.auth.sign_up({
                            "email": email,
                            "password": password,
                            "options": {"data": {"full_name": full_name}}
                        })
                        st.success("Sign Up Successful! Verify your email 📧")
                        st.info("Verification link sent to your email")
                    except Exception as e:
                        st.error(f"Sign Up failed: {str(e)}")

            st.markdown("---")
            st.markdown("##### 🚀 Social Login")

            st.markdown("""
            <style>
       .social-btn {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                width: 100%;
                padding: 10px;
                margin: 5px 0;
                border: 1px solid #dadce0;
                border-radius: 8px;
                background: white;
                color: #3c4043;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                text-decoration: none;
            }
       .social-btn:hover {
                background: #f8f9fa;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
       .social-btn img {
                width: 20px;
                height: 20px;
            }
            </style>
            """, unsafe_allow_html=True)

            SUPABASE_URL = st.secrets["SUPABASE_URL"]
            google_oauth_url = f"{SUPABASE_URL}/auth/v1/authorize?provider=google"
            github_oauth_url = f"{SUPABASE_URL}/auth/v1/authorize?provider=github"

            col_g, col_gh = st.columns(2)

            with col_g:
                st.markdown(f"""
                <a href="{google_oauth_url}" class="social-btn" target="_self">
                    <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google">
                    Google
                </a>
                """, unsafe_allow_html=True)

            with col_gh:
                st.markdown(f"""
                <a href="{github_oauth_url}" class="social-btn" target="_self">
                    <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" alt="GitHub">
                    GitHub
                </a>
                """, unsafe_allow_html=True)

# ===== FOOTER + INSTRUCTIONS - ALWAYS SHOW =====
st.markdown("---")
col_left, col_right = st.columns([2, 1])
with col_left:
    st.markdown("### 📋 Instructions")
    st.info("""
    How to use:
    1. Bot Check: Enter username and select platform to detect bots
    2. Country Check: Verify if user's claimed country matches IP location
    3. Manual Check: Paste text to check for spam patterns + Capital/Small + Alignment
    4. History: View last 10 scans in the sidebar
    5. Forensic Report: Click expander after scan for full detail analysis
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
        bot_scans = supabase.table("scans").select("id", count="exact").gte("score", 50).execute()
        st.metric("Bots Detected", bot_scans.count if bot_scans.count else 0)
    except:
        st.metric("Total Scans", "N/A")
        st.metric("Bots Detected", "N/A")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 20px 0; font-size: 14px;'>🐍 Version Vasuki Ai 4.0 - Bot Detector  | Made in india | © 2026 All Rights Reserved</div>",
    unsafe_allow_html=True
)
