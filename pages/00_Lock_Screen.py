import streamlit as st
import time
import random
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumbotiX AI", page_icon="🛡️", layout="centered", initial_sidebar_state="collapsed")

CLIENT_ID = "PASTE_YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "PASTE_YOUR_GOOGLE_CLIENT_SECRET" 
REDIRECT_URI = "https://humbotix.streamlit.app"
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/auth", "https://accounts.google.com/o/oauth2/token", "https://accounts.google.com/o/oauth2/revoke")

# RANDOM PUZZLE HAR BAAR
if 'num1' not in st.session_state:
    st.session_state.num1 = random.randint(1, 20)
    st.session_state.num2 = random.randint(1, 20)
    st.session_state.answer = st.session_state.num1 + st.session_state.num2

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {background: #0B0B0B;}
.stApp {background: #0B0B0B;}
[data-testid="stSidebar"] {display: none;}
.block-container {padding: 30px 16px; max-width: 400px; margin: auto; font-family: 'Inter', sans-serif;}

.brand {text-align: center; margin-bottom: 24px;}
.brand-logo {font-size: 36px; filter: brightness(0) invert(1); margin-bottom: 8px;}
.brand-title {font-size: 20px; font-weight: 700; color: #FFFFFF;}
.brand-sub {font-size: 12px; color: #8A8F98;}

.card {background: #131314; border: 1px solid #222; border-radius: 10px; padding: 20px;}

.section-title {font-size: 11px; font-weight: 600; color: #8A8F98; margin: 14px 0 8px 0; text-transform: uppercase;}

.stTextInput>div>div>input {
    background: #1A1B1E; color: #E6E6E6; border: 1px solid #2A2B2E; 
    border-radius: 8px; height: 36px; font-size: 13px; padding: 0 12px;
}

/* SOCIAL BUTTON SIDE BY SIDE - BORDER HATA DIYA */
.social-row {display: flex; gap: 8px; margin-bottom: 16px;}
.social-btn {
    flex: 1; height: 36px; font-size: 12px; font-weight: 600; border-radius: 8px;
    display: flex; align-items: center; justify-content: center; gap: 6px;
    cursor: pointer; border: 1px solid;
}
.social-btn img {width: 14px; height: 14px; filter: brightness(0) invert(1);}
.google-btn {background: #FFFFFF; color: #000; border-color: #E0E0E0;}
.google-btn img {filter: none;}
.github-btn {background: #1A1B1E; color: #FFFFFF; border-color: #2A2B2E;}

.primary-btn button {
    background: #00FF88 !important; color: #000 !important; border: none !important;
    height: 36px !important; font-size: 13px !important; font-weight: 600 !important; border-radius: 8px !important;
    margin-top: 8px !important;
}

/* KHALI BOX HATAO */
.element-container:has(iframe) {display: none !important;}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    
    st.markdown("""
    <div class="brand">
        <div class="brand-logo">🛡️</div>
        <div class="brand-title">HumbotiX AI</div>
        <div class="brand-sub">Enterprise Bot Protection Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>Continue with</div>", unsafe_allow_html=True)
    
    # GOOGLE + GITHUB SIDE BY SIDE
    st.markdown("<div class='social-row'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="social-btn google-btn" onclick="document.getElementById(\'google-oauth\').click()"><img src="https://www.google.com/favicon.ico">Google</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="social-btn github-btn" onclick="document.querySelector(\'button[kind=secondary]\').click()"><img src="https://github.githubassets.com/favicon.ico">GitHub</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # HIDDEN OAUTH BUTTONS
    result = oauth2.authorize_button("", REDIRECT_URI, scope="openid email profile")
    st.markdown('<div id="google-oauth"></div>', unsafe_allow_html=True)
    if st.button("", key="github"): pass
    
    if result and 'token' in result:
        st.session_state.logged_in = True
        st.session_state.user = result.get('userinfo', {'email': 'google_user@gmail.com'})
        st.switch_page("pages/dashboard.py")
    
    st.markdown("<div class='section-title'>Or with Email</div>", unsafe_allow_html=True)
    
    # DEMO CREDENTIALS DIYE
    email = st.text_input("", value="demo@humbotix.ai", placeholder="you@company.com", key="email", label_visibility="collapsed")
    password = st.text_input("", value="Demo@123", type="password", placeholder="Password", key="pass", label_visibility="collapsed")
    
    st.markdown("<div class='section-title'>Security Check</div>", unsafe_allow_html=True)
    puzzle = st.text_input("", placeholder=f"{st.session_state.num1} + {st.session_state.num2} = ?", key="puzzle", label_visibility="collapsed")
    
    st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
    if st.button("Sign In", key="unlock"):  # YE BUTTON AB DIKHEGA
        if str(puzzle) == str(st.session_state.answer) and email and password:
            st.session_state.logged_in = True
            st.session_state.user = {'email': email}
            st.success("Login Successful")
            time.sleep(0.5)
            st.switch_page("pages/dashboard.py")
        else: 
            st.error("Invalid credentials or wrong answer")
            # GALAT HONE PAR PUZZLE CHANGE
            st.session_state.num1 = random.randint(1, 20)
            st.session_state.num2 = random.randint(1, 20)
            st.session_state.answer = st.session_state.num1 + st.session_state.num2
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.switch_page("pages/dashboard.py")
