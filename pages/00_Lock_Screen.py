import streamlit as st
import random

st.set_page_config(
    page_title="Humbotix AI",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================
# CAPTCHA SESSION
# =========================

if "a" not in st.session_state:
    st.session_state.a = random.randint(1, 20)
    st.session_state.b = random.randint(1, 20)

def refresh_captcha():
    st.session_state.a = random.randint(1, 20)
    st.session_state.b = random.randint(1, 20)

# =========================
# PREMIUM CSS
# =========================

st.markdown("""
<style>

#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header{visibility:hidden;}

.stApp{
background:
linear-gradient(
135deg,
#020617,
#0B1120,
#111827
);
}

/* Main Card */

.login-card{
max-width:520px;
margin:auto;
margin-top:25px;
padding:35px;

background:#111827;

border-radius:24px;

border:1px solid rgba(23,59,232,.30);

box-shadow:
0px 0px 40px rgba(23,59,232,.15);
}

/* Logo */

.logo{
text-align:center;
font-size:55px;
color:#4DA3FF;
}

/* Title */

.main-title{
text-align:center;
font-size:42px;
font-weight:800;
color:#4DA3FF;
margin-bottom:0;
}

/* Subtitle */

.sub-title{
text-align:center;
font-size:15px;
color:#D1D5DB;
margin-bottom:25px;
}

/* Divider */

.divider{
text-align:center;
color:#94A3B8;
margin-top:15px;
margin-bottom:15px;
font-size:12px;
letter-spacing:2px;
}

/* Inputs */

.stTextInput input{
background:#0F172A !important;
color:white !important;
border-radius:12px !important;
border:1px solid #1E40AF !important;
}

/* Buttons */

.stButton button{
width:100%;
height:50px;
border-radius:12px;
font-weight:700;
}

/* Mobile */

@media(max-width:768px){

.main-title{
font-size:28px;
}

.login-card{
padding:20px;
}

}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

st.markdown("""
<div class="login-card">

<div class="logo">
🛡️
</div>

<div class="main-title">
Humbotix AI
</div>

<div class="sub-title">
Enterprise Bot Protection Platform
</div>

</div>
""", unsafe_allow_html=True)

# =========================
# GOOGLE LOGIN
# =========================

st.button(
    "🔵 Continue with Google",
    use_container_width=True
)

# =========================
# SOCIAL LOGIN
# =========================

col1,col2 = st.columns(2)

with col1:
    st.button(
        "🐙 GitHub",
        use_container_width=True
    )

with col2:
    st.button(
        "📘 Facebook",
        use_container_width=True
    )

# =========================
# DIVIDER
# =========================

st.markdown(
"""
<div class="divider">
──────── OR ────────
</div>
""",
unsafe_allow_html=True
)

# =========================
# EMAIL LOGIN
# =========================

email = st.text_input(
    "Email Address",
    placeholder="Enter your email"
)

password = st.text_input(
    "Password",
    type="password",
    placeholder="Enter password"
)

# =========================
# PHONE LOGIN
# =========================

phone = st.text_input(
    "Phone Number",
    placeholder="+91XXXXXXXXXX"
)

# =========================
# CAPTCHA
# =========================

st.markdown("### Security Verification")

c1,c2 = st.columns([4,1])

with c1:
    captcha = st.text_input(
        f"{st.session_state.a} + {st.session_state.b} = ?",
        placeholder="Answer"
    )

with c2:
    st.write("")
    st.write("")

    if st.button("🔄"):
        refresh_captcha()
        st.rerun()

# =========================
# LOGIN BUTTON
# =========================

st.button(
    "🛡️ Secure Login",
    use_container_width=True
)

# =========================
# FOOTER
# =========================

st.markdown("""
<center>

<small style="color:#94A3B8">

By continuing you agree to our
Terms of Service and Privacy Policy

</small>

</center>
""", unsafe_allow_html=True) 

# ==========================================
# OAUTH CONFIGURATION
# ==========================================

GOOGLE_CLIENT_ID = ""
GOOGLE_CLIENT_SECRET = ""

GITHUB_CLIENT_ID = ""
GITHUB_CLIENT_SECRET = ""

FACEBOOK_CLIENT_ID = ""
FACEBOOK_CLIENT_SECRET = ""

# ==========================================
# SESSION VARIABLES
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "login_provider" not in st.session_state:
    st.session_state.login_provider = ""

# ==========================================
# OAUTH STATUS
# ==========================================

google_ready = (
    GOOGLE_CLIENT_ID != ""
    and
    GOOGLE_CLIENT_SECRET != ""
)

github_ready = (
    GITHUB_CLIENT_ID != ""
    and
    GITHUB_CLIENT_SECRET != ""
)

facebook_ready = (
    FACEBOOK_CLIENT_ID != ""
    and
    FACEBOOK_CLIENT_SECRET != ""
)

st.markdown("### Platform Status")

s1,s2,s3 = st.columns(3)

with s1:
    if google_ready:
        st.success("Google")
    else:
        st.warning("Google")

with s2:
    if github_ready:
        st.success("GitHub")
    else:
        st.warning("GitHub")

with s3:
    if facebook_ready:
        st.success("Facebook")
    else:
        st.warning("Facebook")

# ==========================================
# EMAIL VALIDATION
# ==========================================

def valid_email(email):

    if "@" not in email:
        return False

    if "." not in email:
        return False

    return True

# ==========================================
# PASSWORD CHECK
# ==========================================

def strong_password(password):

    if len(password) < 8:
        return False

    return True

# ==========================================
# LOGIN ACTION
# ==========================================

login_clicked = st.button(
    "🚀 Login Now",
    use_container_width=True,
    key="final_login_btn"
)

if login_clicked:

    captcha_ok = False

    try:

        expected = (
            st.session_state.a +
            st.session_state.b
        )

        captcha_ok = (
            int(captcha) == expected
        )

    except:
        captcha_ok = False

    if not captcha_ok:

        st.error(
            "Security verification failed."
        )

    elif not valid_email(email):

        st.error(
            "Enter valid email."
        )

    elif not strong_password(password):

        st.error(
            "Password must contain at least 8 characters."
        )

    else:

        st.session_state.logged_in = True

        st.session_state.user_email = email

        st.session_state.login_provider = "Email"

        st.success(
            "Login successful."
        )

# ==========================================
# DASHBOARD CARD
# ==========================================

if st.session_state.logged_in:

    st.markdown("---")

    st.success(
        f"Welcome {st.session_state.user_email}"
    )

    st.info(
        f"Provider : {st.session_state.login_provider}"
    )

    st.markdown("""
    ### 🛡️ Security Dashboard

    Account Status : Active

    Bot Protection : Enabled

    Threat Monitoring : Running

    API Security : Protected

    Session Status : Secure
    """)

# ==========================================
# LOGOUT
# ==========================================

    if st.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.user_email = ""

        st.session_state.login_provider = ""

        st.rerun()

# ==========================================
# FUTURE OAUTH SECTION
# ==========================================

st.markdown("---")

with st.expander(
    "OAuth Configuration"
):

    st.text_input(
        "Google Client ID",
        value=GOOGLE_CLIENT_ID
    )

    st.text_input(
        "Google Client Secret",
        value=GOOGLE_CLIENT_SECRET
    )

    st.text_input(
        "GitHub Client ID",
        value=GITHUB_CLIENT_ID
    )

    st.text_input(
        "GitHub Client Secret",
        value=GITHUB_CLIENT_SECRET
    )

    st.text_input(
        "Facebook Client ID",
        value=FACEBOOK_CLIENT_ID
    )

    st.text_input(
        "Facebook Client Secret",
        value=FACEBOOK_CLIENT_SECRET
    )
