import streamlit as st
import time
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumbotiX AI - Lock", page_icon="🔒", layout="wide", initial_sidebar_state="collapsed")

# === APNA GOOGLE CLIENT ID YAHAN DAAL ===
CLIENT_ID = "PASTE_YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "PASTE_YOUR_GOOGLE_CLIENT_SECRET" 
REDIRECT_URI = "https://humbotix.streamlit.app"
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/auth", "https://accounts.google.com/o/oauth2/token", "https://accounts.google.com/o/oauth2/revoke")

# BLACK BACKGROUND + CSS
st.markdown("""
<style>
body {background-color: #000000;}
.stApp {background: #000000;}
[data-testid="stSidebar"] {display: none;} /* Sidebar hide */
.lock-container {display: flex; flex-direction: column; align-items: center; justify-content: center; height: 90vh; color: white;}
.lock-title {font-size: 48px; font-weight: 900; background: linear-gradient(90deg, #00FF88, #00AAFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;}
.lock-subtitle {color: #888; font-size: 16px; margin-bottom: 40px;}
.login-box {background: #0A0A0A; border: 1px solid #333; border-radius: 15px; padding: 40px; width: 420px; box-shadow: 0 0 40px rgba(0,255,136,0.2);}
.puzzle-box {background: #111; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 3px solid #00FF88;}
.google-btn {display: flex; align-items: center; justify-content: center; gap: 10px; width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #4285F4; background: white; color: #3c4043; font-size: 16px; font-weight: 500; cursor: pointer;}
.github-btn {display: flex; align-items: center; justify-content: center; gap: 10px; width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #333; background: #24292e; color: white; font-size: 16px; font-weight: 500; cursor: pointer;}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ========== BLACK LOCK SCREEN ==========
if not st.session_state.logged_in:
    
    st.markdown("<div class='lock-container'>", unsafe_allow_html=True)
    st.markdown("<div class='lock-title'>🔒 HumbotiX AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='lock-subtitle'>Universal Bot Detector - Secure Access</div>", unsafe_allow_html=True)

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    
    # 1. PUZZLE
    st.markdown("<div class='puzzle-box'>", unsafe_allow_html=True)
    st.write("**Security Check**")
    puzzle = st.text_input("Solve: 12 + 6 = ?", key="puzzle", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 2. SOCIAL LOGIN WITH ORIGINAL LOGO
    st.write("**Login with**")
    
    # Google Button with Logo
    st.markdown("""
    <div class="google-btn">
        <img src="https://www.google.com/favicon.ico" width="20">
        Continue with Google
    </div>
    """, unsafe_allow_html=True)
    result = oauth2.authorize_button("", REDIRECT_URI, scope="openid email profile") # invisible button
    if result and 'token' in result:
        st.session_state.logged_in = True
        st.session_state.user = result.get('userinfo', {'email': 'google_user@gmail.com'})
        st.switch_page("pages/dashboard.py")
    
    # GitHub Button with Logo
    st.markdown("""
    <div class="github-btn">
        <img src="https://github.githubassets.com/favicon.ico" width="20">
        Continue with GitHub
    </div>
    """, unsafe_allow_html=True)
    if st.button(" ", key="github_dummy"): # dummy to capture click
        st.warning("GitHub OAuth abhi setup nahi hai. Google se login kar le.")
    
    st.markdown("<hr style='border: 1px solid #222; margin: 20px 0;'>", unsafe_allow_html=True)
    
    # 3. EMAIL PASSWORD
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("🔓 Unlock Dashboard", type="primary", use_container_width=True):
        if puzzle == "18" and email and password:
            st.session_state.logged_in = True
            st.session_state.user = {'email': email}
            st.success("Access Granted!")
            time.sleep(0.5)
            st.switch_page("pages/dashboard.py")
        else: 
            st.error("Puzzle ya Email/Password galat hai")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

else:
    st.switch_page("pages/dashboard.py")
