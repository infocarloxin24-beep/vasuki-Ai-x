import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import os
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIG - YAHAN APNE KEYS DAAL ==========
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID") 
APPLE_TEAM_ID = os.getenv("APPLE_TEAM_ID")
APPLE_KEY_ID = os.getenv("APPLE_KEY_ID")
APPLE_PRIVATE_KEY = os.getenv("APPLE_PRIVATE_KEY")

REDIRECT_URI = "http://localhost:8501"  # Deploy ke baad apni domain daal dena
# ==================================================

def google_login():
    client = OAuth2Session(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, scope="openid email profile", redirect_uri=REDIRECT_URI)
    uri, state = client.create_authorization_url('https://accounts.google.com/o/oauth2/auth')
    st.session_state.oauth_state = state
    return uri

def google_callback(code):
    client = OAuth2Session(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, state=st.session_state.oauth_state, redirect_uri=REDIRECT_URI)
    token = client.fetch_token('https://oauth2.googleapis.com/token', code=code)
    user = client.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
    st.session_state.user = user
    st.session_state.logged_in = True

def apple_login():
    # Apple ka URL
    url = f"https://appleid.apple.com/auth/authorize?response_type=code&response_mode=form_post&client_id={APPLE_CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=name email"
    return url

def send_otp(phone):
    st.session_state.sent_otp = "1234" # Yahan MSG91/Twilio API
    st.session_state.phone = phone
    return True

def verify_otp(user_otp):
    return user_otp == st.session_state.get("sent_otp")

def login_page():
    st.markdown("""
    <style>
        html, body {background: #020314;}
        .main-card {background: linear-gradient(180deg, #0a0d24 0%, #04061a 100%); border: 1px solid rgba(80, 90, 255, 0.3); border-radius: 28px; padding: 45px 35px; max-width: 430px; margin: 50px auto;}
        .logo-text {font-size: 34px; font-weight: 700; color: white; text-align:center;}
        .logo-h {background: linear-gradient(135deg, #4facfe 0%, #7b2fff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 44px; font-weight: 800;}
        .logo-ai {background: linear-gradient(135deg, #4facfe 0%, #7b2fff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    </style>
    """, unsafe_allow_html=True)
    
    # URL se code pakadna callback ke liye
    query_params = st.query_params
    if "code" in query_params:
        google_callback(query_params["code"])
        st.rerun()
    
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.markdown('<div class="logo-text"><span class="logo-h">H</span>umbotix<span class="logo-ai">Ai</span></div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:white;">Scan multiple accounts with <span style="color:#7b2fff;">HumbotixAi</span></p>', unsafe_allow_html=True)

        # REAL GOOGLE BUTTON
        google_url = google_login()
        st.link_button("🌐 Continue with Google", google_url, use_container_width=True)
            
        # REAL APPLE BUTTON  
        apple_url = apple_login()
        st.link_button("🍎 Continue with Apple", apple_url, use_container_width=True)
            
        # OTP
        if st.button("📱 Continue with Number", use_container_width=True): 
            st.session_state.page = "otp"
            st.rerun()

        if st.session_state.get("page") == "otp":
            phone = st.text_input("Enter Mobile Number")
            if st.button("Send OTP") and phone: send_otp(phone)
            otp = st.text_input("Enter OTP")
            if st.button("Verify OTP"):
                if verify_otp(otp):
                    st.session_state.logged_in = True
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
def dashboard_page():
    import streamlit as st
    from analysis import run_all_analysis, init_sidebar_history, show_sidebar_share
    
    # Sidebar
    init_sidebar_history()
    show_sidebar_share()
    
    with st.sidebar:
        st.title("🤖 HumbotixAi")
        st.write(f"Welcome: {st.session_state.get('phone', 'User')}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    
    # Dashboard
    st.title("HumbotixAi Dashboard")
    st.success("Login Successful!")
  
