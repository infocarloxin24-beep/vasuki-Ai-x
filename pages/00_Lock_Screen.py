import streamlit as st
import time
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumbotiX AI - Lock", page_icon="🔒", layout="centered", initial_sidebar_state="collapsed")

# === APNA GOOGLE + GITHUB CLIENT ID YAHAN DAAL ===
CLIENT_ID = "PASTE_YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "PASTE_YOUR_GOOGLE_CLIENT_SECRET" 
REDIRECT_URI = "https://humbotix.streamlit.app"
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/auth", "https://accounts.google.com/o/oauth2/token", "https://accounts.google.com/o/oauth2/revoke")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

body {background: #0A0A0A;}
.stApp {background: #0A0A0A;}
[data-testid="stSidebar"] {display: none;}

.lock-title {
    font-family: 'Orbitron', sans-serif; 
    font-size: 24px; 
    font-weight: 900; 
    background: linear-gradient(90deg, #00FF88, #00AAFF); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    text-align: center; 
    margin: 15px 0 5px 0;
}
.lock-subtitle {color: #aaa; text-align: center; font-size: 12px; margin-bottom: 20px;}

/* BORDER HATA DIYA - CLEAN CARD */
.login-card {
    background: #111; 
    border-radius: 12px; 
    padding: 20px 18px; 
    width: 100%; 
    max-width: 360px; 
    margin: 0 auto; 
    box-shadow: 0 0 20px rgba(0,255,136,0.1);
}

.stSubheader {font-size: 13px !important; color: #00FF88 !important; margin-bottom: 6px !important;}
.stTextInput>div>div>input {background: #1A1A1A; color: #eee; border: 1px solid #333; border-radius: 6px; height: 34px; font-size: 12px;}
.stTextInput>div>div>input::placeholder {color: #666;}

/* GOOGLE + GITHUB BUTTON CHOTE + ICON */
.social-row {display: flex; gap: 8px; margin: 15px 0;}
.social-btn {flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; padding: 8px; border-radius: 6px; font-size: 12px; font-weight: 600; height: 34px; cursor: pointer; border: 1px solid #333;}
.google-btn {background: #FFFFFF; color: #000;}
.github-btn {background: #24292e; color: #FFFFFF;}
.social-btn img {width: 14px; height: 14px;}

.unlock-btn button {
    background: linear-gradient(90deg, #00FF88, #00AAFF) !important; 
    color: #000 !important; 
    border-radius: 6px !important; 
    height: 34px !important; 
    font-weight: 700 !important; 
    font-size: 12px !important;
}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ========== LOCK SCREEN ==========
if not st.session_state.logged_in:
    
    st.markdown("<div class='lock-title'>🔒 HumbotiX AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='lock-subtitle'>Universal Bot Detector</div>", unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    
    # 1. SECURITY PUZZLE
    st.subheader("1. Security Puzzle")
    puzzle = st.text_input("", placeholder="Solve: 15 - 7 = ?", key="puzzle")
    
    # 2. EMAIL & PASSWORD
    st.subheader("2. Email & Password")
    email = st.text_input("", placeholder="Email", key="email")
    password = st.text_input("", type="password", placeholder="Password", key="pass")
    
    # 3. SOCIAL LOGIN - GOOGLE + GITHUB
    st.subheader("3. Social Login")
    st.markdown("<div class='social-row'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="social-btn google-btn"><img src="https://www.google.com/favicon.ico">Google</div>', unsafe_allow_html=True)
        result = oauth2.authorize_button("", REDIRECT_URI, scope="openid email profile")
        if result and 'token' in result:
            st.session_state.logged_in = True
            st.session_state.user = result.get('userinfo', {'email': 'google_user@gmail.com'})
            st.switch_page("pages/dashboard.py")
    
    with col2:
        if st.button(" ", key="github_dummy", use_container_width=True):
            st.warning("GitHub OAuth setup karna hai")
        st.markdown('<div class="social-btn github-btn"><img src="https://github.githubassets.com/favicon.ico">GitHub</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
        
    # UNLOCK BUTTON
    if st.button("🔓 Unlock Dashboard", key="unlock", use_container_width=True):
        if puzzle == "8" and email and password:
            st.session_state.logged_in = True
            st.session_state.user = {'email': email}
            st.success("Access Granted!")
            time.sleep(0.5)
            st.switch_page("pages/dashboard.py")
        else: 
            st.error("Puzzle ya Email/Password galat hai")
    
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.switch_page("pages/dashboard.py")
