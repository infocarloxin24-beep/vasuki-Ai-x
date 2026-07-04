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
body {background: #0A0A0A;}
.stApp {background: #0A0A0A;}
[data-testid="stSidebar"] {display: none;}
.block-container {padding: 1.5rem 1rem; max-width: 320px; margin: auto;}

.header {text-align: center; margin-bottom: 15px;}
.logo {font-size: 40px;}
.lock-title {font-size: 20px; font-weight: 800; color: #00FF88; margin: 0;}
.lock-subtitle {color: #777; font-size: 10px;}

.login-card {background: #111; border-radius: 8px; padding: 15px;}

/* SAB CHOTA */
.stSubheader {font-size: 11px !important; color: #00AAFF !important; margin: 8px 0 4px 0 !important;}
.stTextInput>div>div>input {background: #1A1A1A; color: #eee; border: 1px solid #333; border-radius: 5px; height: 30px; font-size: 11px; padding: 0 8px;}

/* BUTTON SAB 30PX */
div[data-testid="stButton"] > button {
    height: 30px !important; 
    font-size: 11px !important; 
    font-weight: 600 !important; 
    border-radius: 5px !important; 
    margin: 4px 0 !important; 
    width: 100%;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
}
div[data-testid="stButton"] > button img {width: 12px; height: 12px;}

/* GOOGLE WHITE */
div[data-testid="stButton"] > button[kind="primary"] {
    background: #FFFFFF !important; 
    color: #000 !important; 
    border: 1px solid #ddd !important;
}

/* GITHUB BLACK */
div[data-testid="stButton"] > button[kind="secondary"] {
    background: #000 !important; 
    color: #FFFFFF !important; 
    border: 1px solid #444 !important;
}

/* UNLOCK GREEN */
.unlock-btn button {
    background: #00FF88 !important; 
    color: #000 !important;
}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    
    st.markdown("""
    <div class="header">
        <div class="logo">🛡️</div>
        <div class="lock-title">HumbotiX AI</div>
        <div class="lock-subtitle">Bot Detector</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    
    st.subheader("1. Puzzle")
    puzzle = st.text_input("", placeholder="15 - 7 = ?", key="puzzle", label_visibility="collapsed")
    
    st.subheader("2. Login")
    email = st.text_input("", placeholder="Email", key="email", label_visibility="collapsed")
    password = st.text_input("", type="password", placeholder="Password", key="pass", label_visibility="collapsed")
    
    st.subheader("3. Social")
    
    # GOOGLE BUTTON WITH ICON
    st.markdown('<button id="googleBtn" class="social">Continue with Google</button>', unsafe_allow_html=True)
    result = oauth2.authorize_button("", REDIRECT_URI, scope="openid email profile")
    st.markdown("""
    <script>
    let gBtn = parent.document.querySelector('iframe').contentDocument.querySelector('button');
    if(gBtn){gBtn.id="googleReal"; gBtn.style.display="none";}
    document.getElementById('googleBtn').onclick = ()=>{document.getElementById('googleReal').click();}
    document.getElementById('googleBtn').innerHTML = '<img src="https://www.google.com/favicon.ico">Continue with Google';
    </script>
    """, unsafe_allow_html=True)
    if result and 'token' in result:
        st.session_state.logged_in = True
        st.session_state.user = result.get('userinfo', {'email': 'google_user@gmail.com'})
        st.switch_page("pages/dashboard.py")
    
    # GITHUB BUTTON WITH ICON
    if st.button("Continue with GitHub", key="github"):
        st.warning("GitHub setup pending")
    st.markdown("""
    <script>
    let ghBtn = document.querySelector('button[kind="secondary"]');
    if(ghBtn){ghBtn.innerHTML = '<img src="https://github.githubassets.com/favicon.ico">Continue with GitHub';}
    </script>
    """, unsafe_allow_html=True)
    
    # UNLOCK
    if st.button("🔓 Unlock", key="unlock"):
        if puzzle == "8" and email and password:
            st.session_state.logged_in = True
            st.session_state.user = {'email': email}
            st.switch_page("pages/dashboard.py")
        else: 
            st.error("Galat")
    
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.switch_page("pages/dashboard.py")
