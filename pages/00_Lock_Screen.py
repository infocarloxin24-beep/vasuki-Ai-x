import streamlit as st
import time
from streamlit_oauth import OAuth2Component

st.set_page_config(page_title="HumbotiX AI - Lock", page_icon="🔒", layout="wide", initial_sidebar_state="collapsed")

CLIENT_ID = "PASTE_YOUR_GOOGLE_CLIENT_ID"
CLIENT_SECRET = "PASTE_YOUR_GOOGLE_CLIENT_SECRET" 
REDIRECT_URI = "https://humbotix.streamlit.app"
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, "https://accounts.google.com/o/oauth2/auth", "https://accounts.google.com/o/oauth2/token", "https://accounts.google.com/o/oauth2/revoke")

# BLACK + ROBOT CSS
st.markdown("""
<style>
body {background-color: #000;}
.stApp {background: #000;}
[data-testid="stSidebar"] {display: none;}
.lock-container {display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; color: white;}
.lock-title {font-size: 42px; font-weight: 900; background: linear-gradient(90deg, #00FF88, #00AAFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px;}
.lock-subtitle {color: #888; font-size: 15px; margin-bottom: 20px;}
.robot-box {width: 500px; height: 400px; border: 2px solid #00AAFF; border-radius: 15px; margin: 20px 0; overflow: hidden; box-shadow: 0 0 30px rgba(0,170,255,0.4);}
.login-box {background: #0A0A0A; border: 1px solid #333; border-radius: 15px; padding: 30px; width: 420px; box-shadow: 0 0 40px rgba(0,255,136,0.2);}
.puzzle-box {background: #111; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 3px solid #00FF88;}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    
    st.markdown("<div class='lock-container'>", unsafe_allow_html=True)
    st.markdown("<div class='lock-title'>🔒 HumbotiX AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='lock-subtitle'>AI + Human Defense System</div>", unsafe_allow_html=True)

    # ===== 360 DEGREE ROBOT ANIMATION =====
    st.markdown("<div class='robot-box'>", unsafe_allow_html=True)
    
    # Ye wala 3D robot automatic 360 ghumega
    st.components.v1.iframe(
        src="https://my.spline.design/robotspecular-8b5a3e8e1e5e3b5e3b5e3b5e3b5e3b5e/",
        width=500,
        height=400,
        scrolling=False
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Agar upar wala link na chale to ye GIF use kar
    # st.image("https://media.giphy.com/media/3o7aCTfyhYawdOXcFW/giphy.gif", width=500)
    
    st.markdown("<p style='color:#00FF88; font-size:14px;'>🤖 AI Shield Active | Protecting Accounts 24x7</p>", unsafe_allow_html=True)

    # ===== LOGIN BOX =====
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    
    st.markdown("<div class='puzzle-box'>", unsafe_allow_html=True)
    st.write("**Security Check**")
    puzzle = st.text_input("Solve: 12 + 6 = ?", key="puzzle", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("**Login with**")
    
    # Google
    result = oauth2.authorize_button("🔵 Continue with Google", REDIRECT_URI, scope="openid email profile")
    if result and 'token' in result:
        st.session_state.logged_in = True
        st.session_state.user = result.get('userinfo', {'email': 'google_user@gmail.com'})
        st.switch_page("pages/dashboard.py")
    
    # GitHub
    if st.button("⚫ Continue with GitHub", use_container_width=True):
        st.warning("GitHub OAuth setup karna hai")
    
    st.markdown("<hr style='border: 1px solid #222; margin: 15px 0;'>", unsafe_allow_html=True)
    
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
