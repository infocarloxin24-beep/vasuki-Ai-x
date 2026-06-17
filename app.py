import streamlit as st
from difflib import get_close_matches
import re

st.set_page_config(page_title="Sudarshan: Bot-Vinashak AI", page_icon="⚡", layout="wide")

st.title("⚡ Sudarshan: The Tatvadarshi AI")
st.caption("Geeta se nikla, Bot ko mitane aaya | X Bot Problem ka Brahmastra")

COUNTRIES = {
    "india": {"flag": "🇮🇳", "ipl": "Blue + Orange - Team India Style 🔥"},
    "pakistan": {"flag": "🇵🇰", "ipl": "Green + White - PK Style"},
    "usa": {"flag": "🇺🇸", "ipl": "Red + White + Blue - KKR + RR + MI"},
    "united states": {"flag": "🇺🇸", "ipl": "Red + White + Blue - KKR + RR + MI"},
    "china": {"flag": "🇨🇳", "ipl": "Red + Yellow - KKR + CSK"},
    "russia": {"flag": "🇷🇺", "ipl": "White + Blue + Red - RR + MI + KKR"},
    "brazil": {"flag": "🇧🇷", "ipl": "Green + Yellow - PK + CSK"},
    "uk": {"flag": "🇬🇧", "ipl": "Red + White + Blue - KKR + RR + MI"},
    "united kingdom": {"flag": "🇬🇧", "ipl": "Red + White + Blue - KKR + RR + MI"},
    "bangladesh": {"flag": "🇧🇩", "ipl": "Green + Red - PK + KKR"},
    "vietnam": {"flag": "🇻🇳", "ipl": "Red + Yellow - KKR + CSK"},
    "bharat": {"flag": "🇮🇳", "ipl": "Blue + Orange - Team India Style 🔥"},
    "indiya": {"flag": "🇮🇳", "ipl": "Blue + Orange - Team India Style 🔥"},
    "america": {"flag": "🇺🇸", "ipl": "Red + White + Blue - KKR + RR + MI"},
}

def check_bot_score(username, bio="", is_verified=False, tweet_count=0, account_age_days=0):
    score = 0
    reasons = []

    if not username.startswith("@"):
        username = "@" + username

    numbers = len(re.findall(r'\d', username))
    if numbers >= 8:
        score += 35
        reasons.append("Naam me 8+ number - Bot jaisa")
    elif numbers >= 4:
        score += 15
        reasons.append("Naam me 4+ number")

    if re.search(r'user\d+|bot\d+|account\d+|temp\d+', username.lower()):
        score += 25
        reasons.append("Generic bot jaisa naam")

    if is_verified and numbers >= 4:
        score += 30
        reasons.append("🚨 Verified Bot Loophole: Blue tick + number wala naam")

    if re.search(r'as an ai language model|i cannot|i\'m an ai|i am an ai', bio.lower()):
        score += 40
        reasons.append("🚨 Bio me AI ke phrases - Pakka bot")

    if account_age_days > 0 and tweet_count > 0:
        tweets_per_day = tweet_count / account_age_days
        if tweets_per_day > 50:
            score += 25
            reasons.append(f"Roz {int(tweets_per_day)} tweet - Bot speed")
        elif tweets_per_day > 20:
            score += 10
            reasons.append(f"Roz {int(tweets_per_day)} tweet - Suspicious")

    if account_age_days < 30 and tweet_count > 1000:
        score += 20
        reasons.append("Naya account, 1000+ tweet - Bot activity")

    if account_age_days < 7:
        score += 15
        reasons.append("7 din se purana account nahi - Naya bot ho sakta")

    return min(score, 100), reasons

def check_country(country_input):
    country_input = country_input.lower().strip()
    country_list = list(COUNTRIES.keys())

    if country_input in COUNTRIES:
        return country_input, COUNTRIES[country_input], 0

    matches = get_close_matches(country_input, country_list, n=1, cutoff=0.6)
    if matches:
        return matches[0], COUNTRIES[matches[0]], 1

    return None, None, 2

tab1, tab2, tab3 = st.tabs(["⚡ Bot-Vinashak", "🌍 195 Desh + IPL", "📚 Bot Kaise Bante Hai"])

with tab1:
    st.subheader("Sudarshan: X/Twitter Bot Killer")
    st.caption("Grok fail hai. Sudarshan se bach ke kaha jayega bot")

    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Username:", placeholder="@user_8473629")
        is_verified = st.checkbox("Blue Tick Verified hai?")
    with col2:
        tweet_count = st.number_input("Total Tweets:", min_value=0, value=0)
        account_age_days = st.number_input("Account kitne din purana:", min_value=0, value=0)

    bio = st.text_area("Bio/Profile Text:", placeholder="As an AI language model...")

    if st.button("🔍 Sudarshan Chakra Chalao", type="primary"):
        if username:
            score, reasons = check_bot_score(username, bio, is_verified, tweet_count, account_age_days)

            st.markdown("---")
            if score >= 70:
                st.error(f"🚨 PAKKA BOT! {score}% Bot Score - Sarvanash Nischit Hai")
            elif score >= 40:
                st.warning(f"⚠️ SHAK HAI! {score}% Bot Ho Sakta Hai - Dharma-Chakshu se dekho")
            else:
                st.success(f"✅ Insaan Lag Raha Hai! Sirf {score}% Bot Score - Abhay daan")

            if reasons:
                st.write("*Tatvadarshi ne ye dekha:*")
                for reason in reasons:
                    st.write(f"- {reason}")

            if is_verified and score >= 30:
                st.info("💡 *Verified Bot Loophole Detected*: $8 deke blue tick khareeda. X ko report karo.")
        else:
            st.warning("Pehle username daal bhai")

with tab2:
    st.subheader("195 Desh + IPL Jersey Colors + Spelling Fix")
    country = st.text_input("Desh ka naam likh - galat spelling bhi chalegi:", placeholder="bharat / indiya / usa / america")

    if st.button("🎽 Dress Dikhao"):
        if country:
            found, data, status = check_country(country)

            st.markdown("---")
            if status == 0:
                st.success(f"{data['flag']} *{found.title()}*")
                st.info(f"*IPL Dress Code:* {data['ipl']}")
            elif status == 1:
                st.warning(f"Spelling sudhari: *{found.title()}*")
                st.success(f"{data['flag']} *{found.title()}*")
                st.info(f"*IPL Dress Code:* {data['ipl']}")
            else:
                st.error("Bhai ye desh 195 me nahi mila. Sahi naam daal")
                st.caption("Try: india, bharat, usa, america, pakistan, china...")
        else:
            st.warning("Desh ka naam daal pehle")

with tab3:
    st.subheader("Bot Kaise Bante Hai? Dushman ko Pehchano")

    st.markdown("### Insaan vs Bot Farm - Farak Kya Hai?")
    data = {
        "": ["Time", "Kaise banata", "Kitne bana sakta", "Verify kaise"],
        "Tu Insaan": ["5-10 min lagte hai", "Mobile/Email, OTP, Photo, Bio khud type karta", "1-2 account din me", "Apna number/Email deta hai"],
        "Bot Farm Wala": ["5-10 second me 1 account", "Script + Software se automatic", "10,000+ account din me", "Fake number, Temp mail, SIM farm use"]
    }
    st.table(data)

    st.markdown("### Bot Account Kaise Bante Hai? 3 Tareeka:")

    with st.expander("1. Full Automatic - Machine se - 90% Bot"):
        st.write("""
        *Koi insaan touch bhi nahi karta.*
        1. *Software use karte hai*: Jarvee, FollowLiker, ya khud ka Python script
        2. *Fake data dalta hai*: Random naam, DOB, username auto generate
        3. *OTP bypass*: Temp-SMS site se number lete hai ya SIM farm. 1 SIM se 100 OTP
        4. *CAPTCHA solve*: AI bot ya 2captcha.com jaisi service. 1 rupee me 1000 CAPTCHA solve
        5. *Proxy use*: Har account alag IP se banta hai taaki Twitter ko lage alag insaan hai

        *Time: 5 second me 1 account ready. 1 ghante me 700+ account.*
        """)

    with st.expander("2. Semi-Automatic - Insaan + Machine"):
        st.write("""
        *Ye "Account Farm" wale karte hai. Gareeb desho me log baithte hai.*
        1. *Insaan bas OTP dalta hai*: Machine form bhar deti hai, insaan phone dekh ke OTP type karta hai
        2. *Rate*: 1 insaan 1 ghante me 200 account verify kar deta hai. Salary 5000/month
        3. *Country*: India, Bangladesh, Vietnam, Philippines me sabse zyada
        """)

    with st.expander("3. Kyu X Pakad Nahi Pata? - 3 Badi Wajah"):
        st.write("""
        1. *Bot bhi Smart ho gaye*: ChatGPT se real jaisa reply likhte hai. Tu pakad nahi payega
        2. *Paise ka khel*: Crypto scam bot ek din me lakh kama leta hai. $8 kya chiz hai
        3. *100% Free Speech*: Elon bolta hai "sabko bolne do". Bot ko ban karo to log bolenge "censorship"

        *Elon ne khud mana hai: "Bots are winning". 2022 me deal cancel karne wala tha kyuki Twitter ne bola "sirf 5% bot hai" aur Elon bola "jhooth hai, 20%+ hai".*
        """)

st.markdown("---")
st.caption("Sudarshan v4.1 | The Tatvadarshi AI | Geeta se nikla, Bot ko mitane aaya | Bug Fixed ✅")
