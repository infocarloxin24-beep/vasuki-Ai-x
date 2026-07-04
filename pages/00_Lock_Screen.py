import streamlit as st
import time
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumbotiX AI - Lock", page_icon="🔒", layout="centered", initial_sidebar_state="collapsed")

CLIENT_ID = "PASTE_YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "PASTE_YOUR_GOOGLE_CLIENT_SECRET" 
REDIRECT_URI = "https://humbotix.streamlit.app"
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/auth", "https://accounts.google.com/o/oauth2/token", "https://accounts.google.com/o/oauth2/revoke")

# DARK PRO CSS - PHOTO JAISE
st.markdown("""
<style>
body {background: #0F0F0F;}
.stApp {background: #0F0F0F;}
[data-testid="stSidebar"] {display: none;}
.main {padding-top: 4rem;}

.lock-container {max-width: 400px; margin: auto; text-align: center; color: white;}
.logo {font-size: 40px; margin-bottom: 10px;}
.lock-title {font-size: 26px; font-weight: 700; color: #FFFFFF; margin-bottom: 4px;}
.lock-subtitle {color: #00AEEF; font-size: 15px; margin-bottom: 30px; font-weight: 500;}

.login-card {background: #1A1A1A; border-radius: 12px; padding: 30px 25px;}

/* BADA BLACK GOOGLE BUTTON */
.google-main-btn {background: #000; color: white; border: none; border-radius: 50px; padding: 10px 20px; font-size: 14px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 10px; width: 100%; height: 44px; margin-bottom: 15px; cursor: pointer;}
.google-main-btn img {width: 18px;}

/* 3 CHOTE ICON BUTTON */
.icon-row {display: flex; gap: 10px; justify-content: center; margin-bottom: 20px;}
.icon-btn {background: #2A2A2A; border: none; border-radius: 12px; width: 50px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer;}
.icon-btn img {width: 20px; height: 20px;}
.icon-btn:hover {background: #333;}

.divider {display: flex; align-items: center; color: #555; font-size: 12px; margin: 20px 0;}
.divider::before, .divider::after {content: ''; flex: 1; border-bottom: 1px solid #333;}
.divider span {padding: 0 10px;}

/* CHOTE INPUT */
.stTextInput>div>div>input {background: #2A2A2A; color: white; border: 1px solid #333; border-radius: 8px; height: 40px; font-size: 13px;}
.stTextInput>div>div>input::placeholder {color: #777;}

/* GREEN UNLOCK BUTTON */
.unlock-btn button {background: #00FF88 !important; color: #000 !important; border-radius: 8px !important; height: 40px !important; font-weight: 600 !important; font-size: 14px !important;}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    
    st.markdown("<div class='lock-container'>", unsafe_allow_html=True)
    st.markdown("<div class='logo'>🔒</div>", unsafe_allow_html=True)
    st.markdown("<div class='lock-title'>Secure HumbotiX AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='lock-subtitle'>AI + Human Defense in minutes</div>", unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    
    # 1. PUZZLE
    puzzle = st.text_input("", placeholder="Security: 12 + 6 = ?", key="puzzle")
    
    # 2. BADA GOOGLE BUTTON
    st.markdown('<button class="google-main-btn"><img src="https://www.google.com/favicon.ico"> Continue with Google</button>', unsafe_allow_html=True)
    result = oauth2.authorize_button("", REDIRECT_URI, scope="openid email profile")
    if result and 'token' in result:
        st.session_state.logged_in = True
        st.session_state.user = result.get('userinfo', {'email': 'google_user@gmail.com'})
        st.switch_page("pages/dashboard.py")
    
    # 3. 3 CHOTE ICON BUTTON - GOOGLE, GITHUB, APPLE
    st.markdown("<div class='icon-row'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="icon-btn"><img src="https://github.githubassets.com/favicon.ico"></div>', unsafe_allow_html=True)
        if st.button(" ", key="gh"): st.warning("GitHub pending")
    with col2:
        st.markdown('<div class="icon-btn"><img src="https://apple.com/favicon.ico"></div>', unsafe_allow_html=True)
        if st.button("  ", key="apple"): st.warning("Apple pending")
    with col3:
        st.markdown('<div class="icon-btn"><img src="https://facebook.com/favicon.ico"></div>', unsafe_allow_html=True)
        if st.button("   ", key="fb"): st.warning("FB pending")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 4. OR DIVIDER
    st.markdown("<div class='divider'><span>OR</span></div>", unsafe_allow_html=True)
    
    # 5. EMAIL PASSWORD
    email = st.text_input("", placeholder="✉️ Continue with Email", key="email")
    password = st.text_input("", type="password", placeholder="🔒 Password", key="pass")
    
    if st.button("🔓 Unlock Dashboard", key="unlock", use_container_width=True):
        if puzzle == "18" and email and password:
            st.session_state.logged_in = True
            st.session_state.user = {'email': email}
            st.success("Access Granted!")
            time.sleep(0.2)
            st.switch_page("pages/dashboard.py")
        else: 
            st.error("Galat details")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

else:
    st.switch_page("pages/dashboard.py")
