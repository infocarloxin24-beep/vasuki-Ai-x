import streamlit as st

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="ClyxessChat AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------
# SESSION
# -----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------
# CSS
# -----------------------
st.markdown("""
<style>

.stApp{
    background:#0f1117;
}

[data-testid="stSidebar"]{
    background:#161b22;
}

.main-title{
    color:#173BE8;
    font-size:30px;
    font-weight:700;
}

.sub-title{
    color:#9ca3af;
    font-size:14px;
}

.stButton button{
    background:#173BE8 !important;
    color:white !important;
    border:none !important;
    border-radius:12px !important;
    height:46px !important;
    font-weight:600 !important;
}

.chat-box{
    padding:10px;
    border-radius:12px;
}

@media (max-width:768px){

.main-title{
    font-size:24px;
}

}

</style>
""", unsafe_allow_html=True)

# -----------------------
# LOGIN PAGE
# -----------------------
if not st.session_state.logged_in:

    st.markdown(
        "<h1 class='main-title' style='text-align:center;'>⚡ ClyxessChat AI</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p class='sub-title' style='text-align:center;'>Professional Coding Assistant</p>",
        unsafe_allow_html=True
    )

    st.write("")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    login_btn = st.button(
        "Login",
        use_container_width=True
    )

    if login_btn:

        if email and password:

            st.session_state.logged_in = True
            st.rerun()

        else:
            st.error("Please enter email and password")

# -----------------------
# CHAT PAGE
# -----------------------
else:

    with st.sidebar:

        st.markdown("## ⚡ ClyxessChat")

        if st.button("➕ New Chat"):
            st.session_state.messages = []
            st.rerun()

        st.divider()

        st.markdown("### History")

        if len(st.session_state.messages) == 0:
            st.caption("No chats yet")

        st.divider()

        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()

    st.markdown(
        "<h2 class='main-title'>⚡ ClyxessChat AI</h2>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p class='sub-title'>Ask anything...</p>",
        unsafe_allow_html=True
    )

    # OLD MESSAGES
    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # CHAT INPUT
    prompt = st.chat_input(
        "Type your message..."
    )

    if prompt:

        st.session_state.messages.append(
            {
                "role":"user",
                "content":prompt
            }
        )

        st.session_state.messages.append(
            {
                "role":"assistant",
                "content":"Part 1 complete. AI integration Part 2 me add hoga."
            }
        )

        st.rerun() 

# =====================================================
# PART 2 START
# Better History + Welcome Features
# Paste Below Part 1
# =====================================================

# Extra Session Variables

if "chat_titles" not in st.session_state:
    st.session_state.chat_titles = []

if "total_messages" not in st.session_state:
    st.session_state.total_messages = 0

# Save Chat Title

try:

    if len(st.session_state.messages) > 0:

        first_user_message = None

        for m in st.session_state.messages:

            if m["role"] == "user":

                first_user_message = m["content"]
                break

        if first_user_message:

            title = first_user_message[:40]

            if title not in st.session_state.chat_titles:

                st.session_state.chat_titles.append(title)

except:
    pass


# Dashboard Area

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Chats",
        len(st.session_state.chat_titles)
    )

with col2:
    st.metric(
        "Messages",
        len(st.session_state.messages)
    )

with col3:
    st.metric(
        "Status",
        "Online"
    )

# Welcome Cards

if st.session_state.logged_in:

    if len(st.session_state.messages) == 0:

        st.markdown("### 🚀 Quick Start")

        c1, c2 = st.columns(2)

        with c1:

            st.info(
                "Build Website\n\nExample:\nCreate an ecommerce website"
            )

        with c2:

            st.info(
                "Build App\n\nExample:\nCreate a Flutter mobile app"
            )

        c3, c4 = st.columns(2)

        with c3:

            st.info(
                "Fix Code\n\nPaste code and ask for bug fixes"
            )

        with c4:

            st.info(
                "Generate API\n\nCreate FastAPI or Flask APIs"
            )

# Upcoming Features Card

if st.session_state.logged_in:

    st.divider()

    st.markdown("### 🔥 Features Coming Next")

    st.write("🎤 Voice Input")
    st.write("📷 Camera Capture")
    st.write("🖼 Image Upload")
    st.write("🌍 Multi Language Support")
    st.write("💻 Advanced Code Generator")

# Footer

if st.session_state.logged_in:

    st.divider()

    st.caption(
        "ClyxessChat AI • Part 2 Installed"
    )

# =====================================================
# PART 3 START
# Voice + Upload + Camera Foundation
# =====================================================

st.divider()

st.markdown("## 🎛 AI Tools")

tool_col1, tool_col2, tool_col3 = st.columns(3)

with tool_col1:

    voice_btn = st.button(
        "🎤 Voice Input",
        use_container_width=True
    )

    if voice_btn:

        st.info(
            "Voice Module will be activated in Part 4"
        )

with tool_col2:

    camera_btn = st.button(
        "📷 Camera",
        use_container_width=True
    )

    if camera_btn:

        st.info(
            "Camera Module will be activated in Part 5"
        )

with tool_col3:

    upload_btn = st.button(
        "🖼 Upload",
        use_container_width=True
    )

    if upload_btn:

        st.info(
            "Upload Module will be activated in Part 5"
        )

# -----------------------------------------------------
# Upload Area
# -----------------------------------------------------

uploaded_image = st.file_uploader(
    "Upload Screenshot / UI Design",
    type=["png", "jpg", "jpeg"],
    help="Upload any website or app screenshot"
)

if uploaded_image:

    st.image(
        uploaded_image,
        use_container_width=True
    )

    st.success(
        "Image received successfully"
    )

# -----------------------------------------------------
# Camera Area
# -----------------------------------------------------

camera_image = st.camera_input(
    "Take Photo"
)

if camera_image:

    st.image(
        camera_image,
        use_container_width=True
    )

    st.success(
        "Camera image captured"
    )

# -----------------------------------------------------
# Language Section
# -----------------------------------------------------

st.divider()

st.markdown("### 🌍 Supported Languages")

st.caption(
"""
English,
Hindi,
Hinglish,
Spanish,
French,
German,
Arabic,
Tamil,
Telugu,
Bengali,
Marathi,
Gujarati,
Punjabi
"""
)

# -----------------------------------------------------
# Developer Status
# -----------------------------------------------------

st.divider()

st.success(
    "Part 3 Installed Successfully"
)

