import streamlit as st
import time
import random
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumbotiX AI", page_icon="🛡️", layout="centered", initial_sidebar_state="collapsed")

CLIENT_ID = "PASTE_YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "PASTE_YOUR_GOOGLE_CLIENT_SECRET" 
REDIRECT_URI = "https://humbotix.streamlit.app"
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/auth", "https://accounts.google.com/o/oauth2/token", "https://accounts.google.com/o/oauth2/revoke")

def new_puzzle():
    st.session_state.num1 = random.randint(1, 20)
    st.session_state.num2 = random.randint(1, 20)
    st.session_state.answer = st.session_state.num1 + st.session_state.num2

if 'num1' not in st.session_state:
    new_puzzle()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@800;900&display=swap');

html, body {background: #0A0A0A;}
[data-testid="stSidebar"] {display: none;}
.block-container {padding: 30px 20px; max-width: 420px; margin: auto;}

@keyframes gradientMove {
 0% {background-position: 0% 50%;}
 50% {background-position: 100% 50%;}
 100% {background-position: 0% 50%;}
}

.brand {text-align: center; margin-bottom: 25px;}
.brand-logo {
    font-size: 42px; margin-bottom: 6px;
    background: linear-gradient(90deg, #00FF88, #00AAFF);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientMove 3s ease infinite;
}
.brand-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 24px; font-weight: 900;
    background: linear-gradient(90deg, #00FF88, #00AAFF, #FFFFFF);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientMove 4s ease infinite;
}
.brand-sub {font-size: 12px; color: #999; margin-top: 4px;}

.card {background: #121212; border: 1px solid #1E1E1E; border-radius: 12px; padding: 22px;}
.section-title {font-size: 11px; font-weight: 600; color: #888; margin: 14px 0 8px 0; text-transform: uppercase; letter-spacing: 0.5px;}

.stTextInput>div>div>input {
    background: #1A1A1A; color: #FFF; border: 1px solid #2A2A2A; 
    border-radius: 8px; height: 40px; font-size: 14px; padding: 0 14px;
}

/* GOOGLE GITHUB BUTTON SAME SIZE + ORIGINAL LOGO */
.social-row {display: flex; gap: 10px; margin-bottom: 18px;}
.social-btn button {
    width: 100% !important; height: 40px !important; font-size: 14px !important; font-weight: 600 !important; 
    border-radius: 8px !important; border: 1px solid !important; display: flex !important; align-items: center !important; justify-content: center !important; gap: 8px !important;
}
.social-btn img {width: 18px !important; height: 18px !important;}
.google-btn button {background: #FFF !important; color: #000 !important; border-color: #DDD !important;}
.github-btn button {background: #1A1A1A !important; color: #FFF !important; border-color: #2A2A2A !important;}

/* PUZZLE + REFRESH */
.puzzle-row {display: flex; gap: 8px; align-items: center;}
.puzzle-row > div {flex: 1;}
.refresh-btn button {
    height: 40px !important; width: 40px !important; padding: 0 !important;
    background: #1A1A1A !important; border: 1px solid #2A2A2A !important;
    font-size: 18px !important; border-radius: 8px !important; color: #00FF88 !important;
}

/* SIGN IN BUTTON FULL WIDTH */
.primary-btn button {
    background: linear-gradient(90deg, #00FF88, #00AAFF) !important; color: #000 !important; border: none !important;
    height: 40px !important; font-size: 15px !important; font-weight: 700 !important; border-radius: 8px !important;
    margin-top: 14px !important; width: 100% !important;
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
    
    st.markdown("<div class='section-title'>CONTINUE WITH</div>", unsafe_allow_html=True)
    
    # GOOGLE + GITHUB SAME SIZE ORIGINAL LOGO
    st.markdown("<div class='social-row'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="social-btn google-btn">', unsafe_allow_html=True)
        if st.button('<img src="https://www.google.com/favicon.ico"> Google', key="google_login"):
            result = oauth2.authorize_button("Login", REDIRECT_URI, scope="openid email profile")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="social-btn github-btn">', unsafe_allow_html=True)
        st.button('<img src="https://github.githubassets.com/favicon.ico"> GitHub', key="github_login", disabled=False)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if 'result' in locals() and result and 'token' in result:
        st.session_state.logged_in = True
        st.session_state.user = result.get('userinfo', {'email': 'google_user@gmail.com'})
        st.switch_page("pages/dashboard.py")
    
    st.markdown("<div class='section-title'>OR WITH EMAIL</div>", unsafe_allow_html=True)
    
    email = st.text_input("", value="demo@humbotix.ai", placeholder="Email", key="email", label_visibility="collapsed")
    password = st.text_input("", value="Demo@123", type="password", placeholder="Password", key="pass", label_visibility="collapsed")
    
    st.markdown("<div class='section-title'>SECURITY CHECK</div>", unsafe_allow_html=True)
    
    # PUZZLE + REFRESH
    st.markdown("<div class='puzzle-row'>", unsafe_allow_html=True)
    col_p, col_r = st.columns([5, 1])
    with col_p:
        puzzle = st.text_input("", placeholder=f"{st.session_state.num1} + {st.session_state.num2} = ?", key="puzzle", label_visibility="collapsed")
    with col_r:
        st.markdown("<div class='refresh-btn'>", unsafe_allow_html=True)
        if st.button("🔄", key="refresh"):
            new_puzzle()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # SIRF 1 SIGN IN BUTTON
    st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
    if st.button("Sign In", key="unlock_final"):
        if str(puzzle) == str(st.session_state.answer) and email and password:
            st.session_state.logged_in = True
            st.session_state.user = {'email': email}
            st.success("Login Successful")
            time.sleep(0.5)
            st.switch_page("pages/dashboard.py")
        else: 
            st.error("Invalid credentials or wrong answer")
            new_puzzle()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.switch_page("pages/dashboard.py")
