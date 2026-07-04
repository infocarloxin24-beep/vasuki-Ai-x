import streamlit as st
import time
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumbotiX AI - Lock", page_icon="🔒", layout="wide")

# === APNA GOOGLE CLIENT ID YAHAN DAAL ===
CLIENT_ID = "PASTE_YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "PASTE_YOUR_GOOGLE_CLIENT_SECRET" 
REDIRECT_URI = "https://humbotix.streamlit.app"
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/auth", "https://accounts.google.com/o/oauth2/token", "https://accounts.google.com/o/oauth2/revoke")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
.lock-title {font-family: 'Orbitron', sans-serif; font-size: 38px; font-weight: 900; background: linear-gradient(90deg, #00FF88, #00AAFF, #AA00FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: glow 2s ease-in-out infinite; text-align: center; margin: 20px 0;}
@keyframes glow { 0%,100%{filter: brightness(1);} 50%{filter: brightness(1.5);} }
.login-card {background: #111122; border: 2px solid #00FF88; border-radius: 20px; padding: 30px; width: 450px; margin: 20px auto; box-shadow: 0 0 30px rgba(0,255,136,0.3);}
.animation-box {width: 100%; max-width: 650px; height: 350px; border: 2px solid #00AAFF; border-radius: 15px; margin: 20px auto; overflow: hidden;}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ========== LOCK SCREEN ==========
if not st.session_state.logged_in:
    
    st.markdown("<div class='lock-title'>🔒 HumbotiX AI Universal Bot Detector</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#aaa; text-align:center;'>AI Protecting Your Social Accounts from Bot Attacks</p>", unsafe_allow_html=True)

    # ANIMATED GIF - Bot Attack vs AI Shield
    st.markdown("<div class='animation-box'>", unsafe_allow_html=True)
    st.image("https://media.giphy.com/media/L1R1tvI9svkIW/giphy.gif", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        
        st.subheader("1. Security Puzzle")
        puzzle = st.text_input("Solve: 15 - 7 = ?", key="puzzle")
        
        st.subheader("2. Email & Password")
        email = st.text_input("Email", placeholder="admin@humbotix.com")
        password = st.text_input("Password", type="password")
        
        st.subheader("3. Social Login")
        result = oauth2.authorize_button("🔵 Login with Google", REDIRECT_URI, scope="openid email profile")
        if result and 'token' in result:
            st.session_state.logged_in = True
            st.session_state.user = result.get('userinfo', {'email': 'google_user@gmail.com'})
            st.switch_page("pages/dashboard.py")
        
        if st.button("🔓 Unlock Dashboard", type="primary", use_container_width=True):
            if puzzle == "8" and email and password:
                st.session_state.logged_in = True
                st.session_state.user = {'email': email}
                st.success("Access Granted!")
                time.sleep(1)
                st.switch_page("pages/dashboard.py")
            else: 
                st.error("Puzzle ya Email/Password galat hai")
        
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.switch_page("pages/dashboard.py")
