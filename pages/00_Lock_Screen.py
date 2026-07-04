import streamlit as st
import time
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumbotiX AI", page_icon="🛡️", layout="centered", initial_sidebar_state="collapsed")

CLIENT_ID = "PASTE_YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "PASTE_YOUR_GOOGLE_CLIENT_SECRET" 
REDIRECT_URI = "https://humbotix.streamlit.app"
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/auth", "https://accounts.google.com/o/oauth2/token", "https://accounts.google.com/o/oauth2/revoke")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {background: #0B0B0B;}
.stApp {background: #0B0B0B;}
[data-testid="stSidebar"] {display: none;}
.block-container {padding: 40px 16px; max-width: 380px; margin: auto; font-family: 'Inter', sans-serif;}

.brand {text-align: center; margin-bottom: 32px;}
.brand-logo {font-size: 32px; margin-bottom: 8px;}
.brand-title {font-size: 20px; font-weight: 700; color: #FFFFFF;}
.brand-sub {font-size: 13px; color: #8A8F98; margin-top: 4px;}

.card {background: #131314; border: 1px solid #222; border-radius: 12px; padding: 24px;}

.section-title {font-size: 12px; font-weight: 600; color: #8A8F98; margin: 16px 0 8px 0; text-transform: uppercase; letter-spacing: 0.5px;}

.stTextInput>div>div>input {
    background: #1A1B1E; 
    color: #E6E6E6; 
    border: 1px solid #2A2B2E; 
    border-radius: 8px; 
    height: 38px; 
    font-size: 14px; 
    padding: 0 12px;
}
.stTextInput>div>div>input:focus {border: 1px solid #00FF88 !important;}

/* SAB BUTTON SAME */
.social-btn {
    height: 38px; 
    font-size: 14px; 
    font-weight: 600; 
    border-radius: 8px; 
    margin: 8px 0; 
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    cursor: pointer;
    transition: 0.2s;
    border: 1px solid;
}
.social-btn img {width: 16px; height: 16px;}

.google-btn {
    background: #FFFFFF; 
    color: #000; 
    border-color: #E0E0E0;
}
.google-btn:hover {background: #F5F5F5;}

.github-btn {
    background: #1A1B1E; 
    color: #FFFFFF; 
    border-color: #2A2B2E;
}
.github-btn:hover {background: #222;}

.primary-btn button {
    background: #00FF88 !important; 
    color: #000 !important;
    border: none !important;
    height: 38px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}
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
    
    # GOOGLE BUTTON WITH LOGO
    st.markdown("""
    <div class="social-btn google-btn" onclick="document.getElementById('google-oauth').click()">
        <img src="https://www.google.com/favicon.ico">
        Continue with Google
    </div>
    """, unsafe_allow_html=True)
    
    result = oauth2.authorize_button("", REDIRECT_URI, scope="openid email profile")
    st.markdown('<div id="google-oauth" style="display:none"></div>', unsafe_allow_html=True)
    if result and 'token' in result:
        st.session_state.logged_in = True
        st.session_state.user = result.get('userinfo', {'email': 'google_user@gmail.com'})
        st.switch_page("pages/dashboard.py")
    
    # GITHUB BUTTON WITH LOGO
    if st.button("GitHub Placeholder", key="github_dummy"):
        st.info("GitHub OAuth setup karna hai")
    st.markdown("""
    <div class="social-btn github-btn" onclick="document.querySelector('button[kind=secondary]').click()">
        <img src="https://github.githubassets.com/favicon.ico">
        Continue with GitHub
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<style>button[kind="secondary"]{display:none}</style>', unsafe_allow_html=True)
    
    st.markdown("<div class='section-title'>Or with Email</div>", unsafe_allow_html=True)
    
    email = st.text_input("", placeholder="you@company.com", key="email", label_visibility="collapsed")
    password = st.text_input("", type="password", placeholder="Password", key="pass", label_visibility="collapsed")
    
    st.markdown("<div class='section-title'>Security Check</div>", unsafe_allow_html=True)
    puzzle = st.text_input("", placeholder="15 - 7 = ?", key="puzzle", label_visibility="collapsed")
    
    st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
    if st.button("Sign In", key="unlock"):
        if puzzle == "8" and email and password:
            st.session_state.logged_in = True
            st.session_state.user = {'email': email}
            st.switch_page("pages/dashboard.py")
        else: 
            st.error("Invalid credentials")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.switch_page("pages/dashboard.py")
