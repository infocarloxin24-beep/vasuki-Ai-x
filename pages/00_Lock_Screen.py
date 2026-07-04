import streamlit as st
import time
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumbotiX AI - Lock", page_icon="🔒", layout="centered", initial_sidebar_state="collapsed")

CLIENT_ID = "PASTE_YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "PASTE_YOUR_GOOGLE_CLIENT_SECRET" 
REDIRECT_URI = "https://humbotix.streamlit.app"
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/auth", "https://accounts.google.com/o/oauth2/token", "https://accounts.google.com/o/oauth2/revoke")

# BLUE GREEN WHITE PRO CSS
st.markdown("""
<style>
body {background: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%);}
.stApp {background: transparent;}
[data-testid="stSidebar"] {display: none;}
.main {padding-top: 2rem;}

.lock-container {max-width: 380px; margin: auto; text-align: center;}
.lock-title {font-size: 28px; font-weight: 900; color: #00A86B; margin-bottom: 4px;}
.lock-subtitle {color: #004D40; font-size: 12px; margin-bottom: 20px; font-weight: 500;}

.login-card {background: #FFFFFF; border-radius: 16px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.15);}
.puzzle-box {background: #E0F7FA; padding: 8px 12px; border-radius: 8px; margin-bottom: 12px; border-left: 3px solid #00C9FF;}
.puzzle-box p {font-size: 12px; margin: 0; color: #004D40; font-weight: 600;}

.social-row {display: flex; gap: 8px; margin: 12px 0;}
.social-btn {flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px; padding: 6px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; height: 32px; cursor: pointer; border: 1px solid #ddd;}
.google-btn {background: #FFFFFF; color: #3c4043;}
.github-btn {background: #24292e; color: #FFFFFF;}
.social-btn img {width: 14px; height: 14px;}

.stTextInput>div>div>input {height: 32px; font-size: 12px; padding: 0 10px;}
.stButton>button {height: 32px; font-size: 12px; font-weight: 600; border-radius: 6px; padding: 0;}
.unlock-btn {background: linear-gradient(90deg, #00C9FF, #92FE9D); color: #000; border: none;}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    
    st.markdown("<div class='lock-container'>", unsafe_allow_html=True)
    st.markdown("<div class='lock-title'>🔒 HumbotiX AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='lock-subtitle'>AI + Human Defense System</div>", unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    
    # PUZZLE
    st.markdown("<div class='puzzle-box'><p>Security: 12 + 6 = ?</p></div>", unsafe_allow_html=True)
    puzzle = st.text_input("", key="puzzle", placeholder="Answer")
    
    # SOCIAL LOGIN - EK SATH SIDE BY SIDE
    st.markdown("<p style='font-size:11px; color:#555; margin:8px 0;'>Continue with</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="social-btn google-btn"><img src="https://www.google.com/favicon.ico">Google</div>', unsafe_allow_html=True)
        result = oauth2.authorize_button("", REDIRECT_URI, scope="openid email profile")
        if result and 'token' in result:
            st.session_state.logged_in = True
            st.session_state.user = result.get('userinfo', {'email': 'google_user@gmail.com'})
            st.switch_page("pages/dashboard.py")
    
    with col2:
        if st.button(" ", key="gh"):
            st.warning("GitHub setup pending")
        st.markdown('<div class="social-btn github-btn"><img src="https://github.githubassets.com/favicon.ico">GitHub</div>', unsafe_allow_html=True)
    
    st.markdown("<hr style='margin:12px 0; border:1px solid #eee;'>", unsafe_allow_html=True)
    
    # EMAIL PASSWORD
    email = st.text_input("", placeholder="Email", key="email")
    password = st.text_input("", type="password", placeholder="Password", key="pass")
    
    if st.button("🔓 Unlock Dashboard", key="unlock", use_container_width=True):
        if puzzle == "18" and email and password:
            st.session_state.logged_in = True
            st.session_state.user = {'email': email}
            st.success("Access Granted!")
            time.sleep(0.2)
            st.switch_page("pages/dashboard.py")
        else: 
            st.error("Details galat hai")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

else:
    st.switch_page("pages/dashboard.py")
