import streamlit as st
import time
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumbotiX AI - Lock", page_icon="🔒", layout="centered", initial_sidebar_state="collapsed")

CLIENT_ID = "PASTE_YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "PASTE_YOUR_GOOGLE_CLIENT_SECRET" 
REDIRECT_URI = "https://humbotix.streamlit.app"
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/auth", "https://accounts.google.com/o/oauth2/token", "https://accounts.google.com/o/oauth2/revoke")

# COMPACT BLACK CSS
st.markdown("""
<style>
body {background-color: #000;}
.stApp {background: #000;}
[data-testid="stSidebar"] {display: none;}
.main {display: flex; justify-content: center; align-items: center;}
.lock-container {text-align: center; color: white; max-width: 500px; margin-top: 30px;}
.lock-title {font-size: 36px; font-weight: 900; background: linear-gradient(90deg, #00FF88, #00AAFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.lock-subtitle {color: #888; font-size: 14px; margin-bottom: 15px;}
.robot-box {width: 480px; height: 320px; border: 1px solid #222; border-radius: 12px; margin: 15px auto; overflow: hidden;}
.login-box {background: #0A0A0A; border: 1px solid #222; border-radius: 12px; padding: 25px; width: 360px; margin: auto;}
.puzzle-box {background: #111; padding: 10px; border-radius: 8px; margin-bottom: 12px; border-left: 2px solid #00FF88;}

/* CHOTE PROFESSIONAL BUTTON */
.social-btn {display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; padding: 8px 12px; margin: 6px 0; border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer; height: 36px;}
.google-btn {background: #FFFFFF; color: #3c4043; border: 1px solid #dadce0;}
.github-btn {background: #21262d; color: #f0f6fc; border: 1px solid #30363d;}
.social-btn img {width: 16px; height: 16px;}
.stButton>button {height: 36px; font-size: 13px; padding: 0 12px;}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    
    st.markdown("<div class='lock-container'>", unsafe_allow_html=True)
    st.markdown("<div class='lock-title'>🔒 HumbotiX AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='lock-subtitle'>AI + Human Defense System</div>", unsafe_allow_html=True)

    # ===== 360 DEGREE ROBOT =====
    st.markdown("<div class='robot-box'>", unsafe_allow_html=True)
    # Spline 3D Robot - Automatic 360 ghumta hai
    st.components.v1.iframe(
        src="https://my.spline.design/robotfollowcursor-abc123def456/",
        width=480,
        height=320,
        scrolling=False
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00FF88; font-size:12px;'>🤖 Neural Shield Active</p>", unsafe_allow_html=True)

    # ===== COMPACT LOGIN BOX =====
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    
    st.markdown("<div class='puzzle-box'>", unsafe_allow_html=True)
    st.write("**Security Check**")
    puzzle = st.text_input("12 + 6 = ?", key="puzzle", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("**Continue with**")
    
    # Google Button - CHOTA + WHITE + ICON
    st.markdown('<div class="social-btn google-btn"><img src="https://www.google.com/favicon.ico">Continue with Google</div>', unsafe_allow_html=True)
    result = oauth2.authorize_button("", REDIRECT_URI, scope="openid email profile")
    if result and 'token' in result:
        st.session_state.logged_in = True
        st.session_state.user = result.get('userinfo', {'email': 'google_user@gmail.com'})
        st.switch_page("pages/dashboard.py")
    
    # GitHub Button - CHOTA + BLACK + ICON  
    if st.button(" ", key="github_click", use_container_width=True):
        st.warning("GitHub OAuth setup pending")
    st.markdown('<div class="social-btn github-btn"><img src="https://github.githubassets.com/favicon.ico">Continue with GitHub</div>', unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid #222; margin: 12px 0;'>", unsafe_allow_html=True)
    
    email = st.text_input("Email", placeholder="admin@humbotix.com")
    password = st.text_input("Password", type="password")
    
    if st.button("🔓 Unlock", type="primary", use_container_width=True):
        if puzzle == "18" and email and password:
            st.session_state.logged_in = True
            st.session_state.user = {'email': email}
            st.success("Access Granted!")
            time.sleep(0.3)
            st.switch_page("pages/dashboard.py")
        else: 
            st.error("Wrong details")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

else:
    st.switch_page("pages/dashboard.py")
