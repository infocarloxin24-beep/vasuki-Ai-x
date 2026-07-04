import streamlit as st
import time
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumbotiX AI - Lock", page_icon="🔒", layout="centered", initial_sidebar_state="collapsed")

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

.lock-title {
    font-family: 'Orbitron', sans-serif; 
    font-size: 26px; 
    font-weight: 900; 
    background: linear-gradient(90deg, #00FF88, #00AAFF, #FFFFFF); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    text-align: center; 
    margin: 20px 0 5px 0;
}
.lock-subtitle {color: #888; text-align: center; font-size: 12px; margin-bottom: 25px;}

.login-card {
    background: #111; 
    border-radius: 10px; 
    padding: 20px; 
    width: 100%; 
    max-width: 350px; 
    margin: 0 auto;
}

.stSubheader {font-size: 12px !important; color: #00FF88 !important; margin: 10px 0 6px 0 !important;}
.stTextInput>div>div>input {background: #1A1A1A; color: #eee; border: 1px solid #333; border-radius: 6px; height: 32px; font-size: 12px;}

/* SAB BUTTON EK SIZE */
.btn-common {height: 34px !important; font-size: 12px !important; font-weight: 600 !important; border-radius: 6px !important; margin: 6px 0 !important;}

/* GOOGLE BUTTON */
.google-real {background: #FFFFFF !important; color: #000 !important; border: 1px solid #ddd !important;}

/* GITHUB BUTTON WHITE LOGO */
.github-real {background: #000 !important; color: #FFFFFF !important; border: 1px solid #444 !important;}
.github-real img {filter: invert(1); width: 14px; margin-right: 6px;}

.unlock-real {background: linear-gradient(90deg, #00FF88, #00AAFF) !important; color: #000 !important;}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    
    st.markdown("<div class='lock-title'>🔒 Secure HumbotiX AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='lock-subtitle'>AI + Human Defense System</div>", unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    
    # 1. PUZZLE
    st.subheader("1. Security Puzzle")
    puzzle = st.text_input("", placeholder="15 - 7 = ?", key="puzzle")
    
    # 2. EMAIL
    st.subheader("2. Email & Password")
    email = st.text_input("", placeholder="Email", key="email")
    password = st.text_input("", type="password", placeholder="Password", key="pass")
    
    # 3. SOCIAL LOGIN - VERTICAL EK KE NICHE EK
    st.subheader("3. Social Login")
    
    # GOOGLE BUTTON
    result = oauth2.authorize_button("Continue with Google", REDIRECT_URI, scope="openid email profile")
    st.markdown("""
    <script>
    document.querySelector('button[kind="primary"]').classList.add('btn-common', 'google-real');
    </script>
    """, unsafe_allow_html=True)
    if result and 'token' in result:
        st.session_state.logged_in = True
        st.session_state.user = result.get('userinfo', {'email': 'google_user@gmail.com'})
        st.switch_page("pages/dashboard.py")
    
    # GITHUB BUTTON
    if st.button("Continue with GitHub", key="github", use_container_width=True):
        st.warning("GitHub OAuth setup karna hai")
    st.markdown("""
    <script>
    document.querySelector('button[kind="secondary"]').classList.add('btn-common', 'github-real');
    let ghBtn = document.querySelector('button[kind="secondary"]');
    ghBtn.innerHTML = '<img src="https://github.githubassets.com/favicon.ico">Continue with GitHub';
    </script>
    """, unsafe_allow_html=True)
    
    # UNLOCK BUTTON SAME SIZE
    if st.button("🔓 Unlock", key="unlock", use_container_width=True):
        if puzzle == "8" and email and password:
            st.session_state.logged_in = True
            st.session_state.user = {'email': email}
            st.success("Access Granted!")
            time.sleep(0.3)
            st.switch_page("pages/dashboard.py")
        else: 
            st.error("Details galat")
    st.markdown("""
    <script>
    document.querySelector('button[kind="primary"][data-testid="baseButton-secondary"]').classList.add('btn-common', 'unlock-real');
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.switch_page("pages/dashboard.py")
