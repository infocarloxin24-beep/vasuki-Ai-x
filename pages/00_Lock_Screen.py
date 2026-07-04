import streamlit as st
import time
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumbotiX AI - Lock", page_icon="🔒", layout="centered", initial_sidebar_state="collapsed")

CLIENT_ID = "PASTE_YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "PASTE_YOUR_GOOGLE_CLIENT_SECRET" 
REDIRECT_URI = "https://humbotix.streamlit.app"
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/auth", "https://accounts.google.com/o/oauth2/token", "https://accounts.google.com/o/oauth2/revoke")

# CLEAN DARK CSS - GREEN BLACK WHITE
st.markdown("""
<style>
body {background: #0A0A0A;}
.stApp {background: #0A0A0A;}
[data-testid="stSidebar"] {display: none;}
.main {padding-top: 3rem;}

.lock-container {max-width: 340px; margin: auto; text-align: center;}

/* GREEN BLACK WHITE TITLE */
.lock-title {font-size: 24px; font-weight: 800; margin-bottom: 6px;}
.lock-title .green {color: #00FF88;}
.lock-title .white {color: #FFFFFF;}
.lock-title .black {background: #000; color: #00FF88; padding: 2px 8px; border-radius: 4px;}
.lock-subtitle {color: #888; font-size: 11px; margin-bottom: 25px;}

.login-card {background: #111; border: 1px solid #222; border-radius: 10px; padding: 20px 18px;}

/* PUZZLE CHOTA */
.stTextInput>div>div>input {background: #1A1A1A; color: #eee; border: 1px solid #333; border-radius: 6px; height: 34px; font-size: 12px;}
.stTextInput>div>div>input::placeholder {color: #666;}

/* 2 BUTTON SIDE BY SIDE CHOTE */
.social-row {display: flex; gap: 8px; margin: 15px 0;}
.social-btn {flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; padding: 8px; border-radius: 6px; font-size: 12px; font-weight: 600; height: 34px; border: 1px solid #333;}
.google-btn {background: #FFFFFF; color: #000;}
.github-btn {background: #000; color: #FFFFFF; border: 1px solid #444;}
.social-btn img {width: 14px; height: 14px;}
.social-btn:hover {opacity: 0.8;}

/* UNLOCK BUTTON */
.unlock-btn button {background: #00FF88 !important; color: #000 !important; border-radius: 6px !important; height: 34px !important; font-weight: 700 !important; font-size: 12px !important;}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    
    st.markdown("<div class='lock-container'>", unsafe_allow_html=True)
    st.markdown("<div class='lock-title'><span class='green'>Secure</span> <span class='white'>Humboti</span><span class='black'>X</span> <span class='green'>AI</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='lock-subtitle'>AI + Human Defense System</div>", unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    
    # 1. PUZZLE CHOTA
    puzzle = st.text_input("", placeholder="Security: 12 + 6 = ?", key="puzzle")
    
    # 2. GOOGLE + GITHUB EK LINE ME CHOTE
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
        if st.button(" ", key="gh_btn", use_container_width=True):
            st.warning("GitHub OAuth setup karna hai")
        st.markdown('<div class="social-btn github-btn"><img src="https://github.githubassets.com/favicon.ico">GitHub</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 3. EMAIL PASSWORD
    email = st.text_input("", placeholder="Email", key="email")
    password = st.text_input("", type="password", placeholder="Password", key="pass")
    
    if st.button("🔓 Unlock", key="unlock", use_container_width=True):
        if puzzle == "18" and email and password:
            st.session_state.logged_in = True
            st.session_state.user = {'email': email}
            st.success("Access Granted!")
            time.sleep(0.2)
            st.switch_page("pages/dashboard.py")
        else: 
            st.error("Details galat")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

else:
    st.switch_page("pages/dashboard.py")
