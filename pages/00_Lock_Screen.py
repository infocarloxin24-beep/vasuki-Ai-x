import streamlit as st
import time
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumbotiX AI - Lock", page_icon="🛡️", layout="centered", initial_sidebar_state="collapsed")

CLIENT_ID = "PASTE_YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "PASTE_YOUR_GOOGLE_CLIENT_SECRET" 
REDIRECT_URI = "https://humbotix.streamlit.app"
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/auth", "https://accounts.google.com/o/oauth2/token", "https://accounts.google.com/o/oauth2/revoke")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');

body {background: #0A0A0A;}
.stApp {background: #0A0A0A;}
[data-testid="stSidebar"] {display: none;}
.block-container {padding-top: 2rem;}

.header {text-align: center; margin-bottom: 20px;}
.logo {font-size: 50px; margin-bottom: 5px;}
.lock-title {
    font-family: 'Orbitron', sans-serif; 
    font-size: 22px; 
    font-weight: 900; 
    background: linear-gradient(90deg, #00FF88, #00AAFF); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    margin: 0;
}
.lock-subtitle {color: #888; font-size: 11px;}

.login-card {
    background: #111; 
    border: 1px solid #222; 
    border-radius: 10px; 
    padding: 20px; 
    width: 100%; 
    max-width: 340px; 
    margin: 0 auto;
}

.stSubheader {font-size: 12px !important; color: #00FF88 !important; margin: 10px 0 5px 0 !important; font-weight: 600;}
.stTextInput>div>div>input {background: #1A1A1A; color: #eee; border: 1px solid #333; border-radius: 6px; height: 32px; font-size: 12px;}

/* SAB BUTTON EK JAISE */
div[data-testid="stButton"] > button {
    height: 34px !important; 
    font-size: 12px !important; 
    font-weight: 600 !important; 
    border-radius: 6px !important; 
    margin: 5px 0 !important; 
    width: 100%;
}

/* GOOGLE */
div[data-testid="stButton"] > button[kind="primary"] {
    background: #FFFFFF !important; 
    color: #000 !important; 
    border: 1px solid #ddd !important;
}

/* GITHUB */
div[data-testid="stButton"] > button[kind="secondary"] {
    background: #000 !important; 
    color: #FFFFFF !important; 
    border: 1px solid #444 !important;
}
div[data-testid="stButton"] > button[kind="secondary"] img {
    width: 14px; 
    height: 14px; 
    margin-right: 6px; 
    vertical-align: middle;
}

/* UNLOCK */
.unlock-btn button {
    background: linear-gradient(90deg, #00FF88, #00AAFF) !important; 
    color: #000 !important;
}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    
    # LOGO + TITLE CENTER
    st.markdown("""
    <div class="header">
        <div class="logo">🛡️</div>
        <div class="lock-title">Secure HumbotiX AI</div>
        <div class="lock-subtitle">Universal Bot Detector</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    
    # 1. PUZZLE
    st.subheader("1. Security Puzzle")
    puzzle = st.text_input("", placeholder="15 - 7 = ?", key="puzzle")
    
    # 2. EMAIL
    st.subheader("2. Email & Password")
    email = st.text_input("", placeholder="Email", key="email")
    password = st.text_input("", type="password", placeholder="Password", key="pass")
    
    # 3. SOCIAL LOGIN - VERTICAL
    st.subheader("3. Social Login")
    
    # GOOGLE
    result = oauth2.authorize_button("Continue with Google", REDIRECT_URI, scope="openid email profile")
    if result and 'token' in result:
        st.session_state.logged_in = True
        st.session_state.user = result.get('userinfo', {'email': 'google_user@gmail.com'})
        st.switch_page("pages/dashboard.py")
    
    # GITHUB
    if st.button("Continue with GitHub", key="github"):
        st.warning("GitHub OAuth setup karna hai")
    
    # GITHUB ME ICON INJECT KARNE KE LIYE
    st.markdown("""
    <script>
    let gh = document.querySelector('button[kind="secondary"]');
    if(gh && !gh.querySelector('img')){
        gh.innerHTML = '<img src="https://github.githubassets.com/favicon.ico">Continue with GitHub';
    }
    </script>
    """, unsafe_allow_html=True)
    
    # UNLOCK
    if st.button("🔓 Unlock", key="unlock"):
        if puzzle == "8" and email and password:
            st.session_state.logged_in = True
            st.session_state.user = {'email': email}
            st.success("Access Granted!")
            time.sleep(0.3)
            st.switch_page("pages/dashboard.py")
        else: 
            st.error("Details galat")
    
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.switch_page("pages/dashboard.py")
