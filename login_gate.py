import streamlit as st

st.set_page_config(page_title="Humbotix AI", layout="centered", page_icon="🛡️")

# ===== PROFESSIONAL DARK THEME CSS =====
st.markdown("""
<style>
.stApp {background: #0e1117;}
[data-testid="stForm"] {border: 1px solid #262730; border-radius: 12px; padding: 25px; background: #161a23;}
.stTextInput>div>div>input {background-color: #262730; color: white; border-radius: 8px; border: 1px solid #3a3f4b;}
.stButton>button {width: 100%; background: #3a3f4b; color: white; border-radius: 8px; border: none; padding: 10px; font-weight: 600;}
.stButton>button:hover {background: #4a5060;}
.title {color: #38bdf8 !important; font-size: 38px; font-weight: 800; text-align: center; letter-spacing: 1px;}
.subtitle {color: #94a3b8 !important; font-size: 14px; text-align: center;}
h3 {color: white !important;}
hr {border: 1px solid #262730;}
</style>
""", unsafe_allow_html=True)

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ===== LOGIN / SIGNUP PAGE =====
def login_page():
    # Header
    st.markdown("<div style='text-align: center; font-size: 60px;'>🛡️</div>", unsafe_allow_html=True)
    st.markdown("<h1 class='title'>Humbotix AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Enterprise Bot Protection Platform</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("login_form"):
        # Mode
        mode = st.radio("Mode:", ["Login", "Sign Up"], horizontal=True)
        
        st.markdown("### 📧 Login with Email")
        
        email = st.text_input("Email:", placeholder="example@mail.com")
        password = st.text_input("Password:", type="password", placeholder="Enter password")
        
        # Login + Refresh
        col1, col2 = st.columns([6,1])
        with col1:
            submitted = st.form_submit_button("Login", use_container_width=True)
        with col2:
            if st.form_submit_button("🔄"):
                st.rerun()
        
        st.caption("Ujjwal")

    # Social Login
    st.markdown("---")
    st.markdown("### 🚀 Social Login")
    col1, col2 = st.columns(2)
    with col1:
        st.button("G Google", use_container_width=True, disabled=True, help="Baad me API jodna")
    with col2:
        st.button("💻 GitHub", use_container_width=True, disabled=True, help="Baad me API jodna")

    # Login logic
    if submitted:
        # Random demo password - tu yaha change kar sakta hai
        if email == "admin@humbotix.ai" and password == "Humbo@2026":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Galat Email ya Password")

# ===== DASHBOARD =====
def dashboard():
    st.title("📊 Humbotix AI Dashboard")
    st.success("Login Successful! Welcome to the Dashboard")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Bots Blocked", "12,450")
    col2.metric("Active Users", "328")
    col3.metric("Threat Level", "Low")
    
    st.line_chart([5, 10, 8, 15, 12, 20, 18])
    
    st.markdown("---")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ===== MAIN ROUTER =====
if st.session_state.logged_in:
    dashboard()
else:
    login_page()
