import streamlit as st
import json
from groq import Groq
import time
from streamlit_google_auth import Authenticate

st.set_page_config(page_title="ClyxessChat AI", page_icon="💬", layout="wide")

# GOOGLE LOGIN
client_id = st.secrets["google_client_id"]
client_secret = st.secrets["google_client_secret"]
redirect_uri = "https://clyxesschat.streamlit.app"

authenticator = Authenticate(client_secret, client_id, redirect_uri, "clyxesschat_cookie", "secret_123")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("""
<style>
.stApp {background-color: #212121;}
.main.block-container {max-width: 900px;}
[data-testid="stSidebar"] {background-color: #171717;}
.file-card {background:#2f2f2f; border:2px solid #173BE8; border-radius:12px; padding:15px; margin:15px 0;}
.file-name {color:#173BE8; font-size:18px; font-weight:bold; margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("💬 ClyxessChat")
    authenticator.check_authenticator()
    if st.session_state['authentication_status']:
        st.image(st.session_state['picture'], width=40)
        st.write(f"Hi, {st.session_state['name']}")
        if st.button("Logout", use_container_width=True):
            authenticator.logout(); st.rerun()

if st.session_state['authentication_status']:

    st.title("ClyxessChat")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"]=="user" else "🤖"):
            st.markdown(msg["content"], unsafe_allow_html=True)

    col1, col2 = st.columns([10,1])
    with col1:
        prompt = st.chat_input("Message ClyxessChat AI...")
    with col2:
        st.button("🎙️", disabled=True, help="Abhi band hai")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Socha ja raha hai..."):

                router = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"user","content":f"User: {prompt}. If code/website/app reply CODE. Else CHAT. Reply ONLY one word."}],
                    max_tokens=5, temperature=0
                )
                decision = router.choices[0].message.content.strip().upper()

                if "CHAT" in decision:
                    res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages, max_tokens=2000)
                    ans = res.choices[0].message.content
                    st.write(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})

                else:
                    # SAKHT PROMPT - PART BY PART FILE
                    code_prompt = f"""
                    User request: {prompt}
                    You are a senior developer. Break the project into multiple files.
                    CRITICAL: Return ONLY valid JSON. Format:
                    {{
                      "part1.html": "COMPLETE CODE FOR PART 1",
                      "part2.css": "COMPLETE CODE FOR PART 2",
                      "part3.js": "COMPLETE CODE FOR PART 3"
                    }}
                    Rules: 1. Each file must have COMPLETE runnable code 2. No ``` 3. No explanation
                    """
                    res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role":"user","content":code_prompt}],
                        max_tokens=8000,
                        temperature=0.0
                    )
                    raw = res.choices[0].message.content.replace("```json","").replace("```","").strip()
                    try:
                        files = json.loads(raw)

                        st.markdown("### 📁 Files Ban gayi - Ek ek karke download karo:")

                        # PART 1 FILE BANAO
                        # PART 1 ME CODE DALO
                        # PART 2 FILE BANAO
                        # PART 2 ME CODE DALO - AISE EK KARKE
                        for name, code in files.items():
                            with st.container():
                                st.markdown(f"<div class='file-card'><div class='file-name'>📄 {name}</div>", unsafe_allow_html=True)
                                st.download_button(f"⬇️ Download {name}", code, name, key=f"dl_{name}_{time.time()}")
                                with st.expander(f"View Code of {name}"):
                                    st.code(code, language=name.split(".")[-1])
                                st.markdown("</div>", unsafe_allow_html=True)
                                time.sleep(0.3) # Thoda delay taaki lagge file ban rahi hai

                        st.session_state.messages.append({"role": "assistant", "content": "✅ Sab files ban gayi. Upar se download kar lo"})

                    except Exception as e:
                        st.error("Error: " + str(e))
                        st.code(raw)
else:
    st.info("👈 Pehle Google se Login karo")
