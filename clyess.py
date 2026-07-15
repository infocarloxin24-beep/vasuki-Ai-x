import streamlit as st
import json
from groq import Groq
import time
import base64

st.set_page_config(page_title="ClyxessChat AI", page_icon="💬", layout="wide")

HIDDEN_GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
ACTIVE_GROQ_MODEL = "llama-3.3-70b-versatile"

# SESSION INIT
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

# LOGO KO BASE64 ME CONVERT KARNE KE LIYE
def get_base64_of_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# CSS
st.markdown("""
<style>
.stApp {background-color: #212121;}
.main.block-container {max-width: 800px; padding-top: 1rem;}
[data-testid="stSidebar"] {background-color: #171717;}
div[data-testid="stChatInput"] {background:#2f2f2f; border-radius:24px; border:1px solid #444;}
div[data-testid="stChatInput"] input {background:transparent; color:white; border:none;}
.file-card {background:#2f2f2f; border:1px solid #173BE8; border-radius:12px; padding:12px; margin:8px 0;}
.logo-center {text-align: center; margin-bottom: 20px;}
.logo-center img {width: 400px;}
</style>
""", unsafe_allow_html=True)

# SIDEBAR - SIRF HISTORY, NEW CHAT BUTTON HATA DIYA
with st.sidebar:
    st.title("💬 History")

    for chat_name in list(st.session_state.all_chats.keys())[::-1]:
        col1, col2 = st.columns([4,1])
        with col1:
            if st.button(chat_name, key=f"btn_{chat_name}", use_container_width=True):
                st.session_state.current_chat = chat_name
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{chat_name}"):
                if len(st.session_state.all_chats) > 1:
                    del st.session_state.all_chats[chat_name]
                    st.session_state.current_chat = list(st.session_state.all_chats.keys())[0]
                    st.rerun()

# LOGO CENTER ME TOP PE
st.markdown('<div class="logo-center">', unsafe_allow_html=True)
st.image("An_aGiLNTLUuWptCFY6UhqlOD3kC_kSiREkOJsHBSE0TcZt1fAKnHi9GvWGAt54NXFW9QCvmBuIbVtVHL7PldmJjUJTxwlq7d6pPmeotx4W0mYffpU9pHcY", use_column_width=False, width=400)
st.markdown('</div>', unsafe_allow_html=True)

# CURRENT CHAT TITLE
st.markdown(f"### {st.session_state.current_chat}")

# CHAT HISTORY
for msg in st.session_state.all_chats[st.session_state.current_chat]:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"]=="user" else "🤖"):
        st.markdown(msg["content"], unsafe_allow_html=True)

prompt = st.chat_input("Message ClyxessChat AI...")

if prompt:
    # USER MSG SAVE
    st.session_state.all_chats[st.session_state.current_chat].append({"role": "user", "content": prompt})

    # PEHLE MSG SE AUTO RENAME
    if st.session_state.current_chat == "Chat 1" and len(st.session_state.all_chats[st.session_state.current_chat]) == 1:
        new_name = prompt[:35] + "..."
        st.session_state.all_chats[new_name] = st.session_state.all_chats.pop(st.session_state.current_chat)
        st.session_state.current_chat = new_name
        st.rerun()

    client = Groq(api_key=HIDDEN_GROQ_API_KEY)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Code likh raha hun..."):

            router = client.chat.completions.create(
                model=ACTIVE_GROQ_MODEL,
                messages=[{"role":"user","content":f"User asked: {prompt}. If they want code/website/app reply CODE. Else CHAT. Reply ONLY one word."}],
                max_tokens=5, temperature=0
            )
            decision = router.choices[0].message.content.strip().upper()

            if "CHAT" in decision:
                res = client.chat.completions.create(
                    model=ACTIVE_GROQ_MODEL,
                    messages=st.session_state.all_chats[st.session_state.current_chat],
                    max_tokens=2000
                )
                ans = res.choices[0].message.content
                st.write(ans)
                st.session_state.all_chats[st.session_state.current_chat].append({"role": "assistant", "content": ans})

            else: # CODE MODE - AB PAKKA FILE BANEGA
                code_prompt = f"""
                You are a senior developer. User wants: {prompt}
                RULES:
                1. You MUST return ONLY valid JSON. No extra text.
                2. Each key is filename. Each value is COMPLETE code.
                3. Example: {{"index.html": "<!DOCTYPE html>...full code...", "style.css": "body{{}}...full code..."}}
                4. Do NOT use ```. Do NOT explain.
                """
                res = client.chat.completions.create(
                    model=ACTIVE_GROQ_MODEL,
                    messages=[{"role":"user","content":code_prompt}],
                    max_tokens=8000,
                    temperature=0.0
                )
                raw = res.choices[0].message.content.strip()
                raw = raw.replace("```json","").replace("```","").strip()

                try:
                    files = json.loads(raw)
                    st.markdown("### 📁 Files Ready - Download karo:")
                    success_msg = "Code Generated:<br>"

                    for name, code in files.items():
                        st.markdown(f"<div class='file-card'><b>📄 {name}</b></div>", unsafe_allow_html=True)
                        st.download_button(f"⬇️ Download {name}", code, name, mime="text/plain", key=f"dl_{name}_{time.time()}")
                        with st.expander(f"View {name}"):
                            st.code(code, language=name.split(".")[-1])
                        success_msg += f"<b>{name}</b> ✅<br>"

                    st.session_state.all_chats[st.session_state.current_chat].append({"role": "assistant", "content": success_msg})

                except json.JSONDecodeError as e:
                    st.error("AI ne JSON kharab diya. Phir se try karo")
                    st.code(raw, language="json")
                    st.session_state.all_chats[st.session_state.current_chat].append({"role": "assistant", "content": "Error: Code nahi ban paya"})
