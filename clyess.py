import streamlit as st
import json
import re
from groq import Groq
import time

st.set_page_config(page_title="ClyxessChat AI", page_icon="💬", layout="wide")

HIDDEN_GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
ACTIVE_GROQ_MODEL = "llama-3.3-70b-versatile"

if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

st.markdown("""
<style>
.stApp {background-color: #212121;}
.main.block-container {max-width: 800px; padding-top: 1rem;}
[data-testid="stSidebar"] {background-color: #171717;}
div[data-testid="stChatInput"] {background:#2f2f2f; border-radius:24px; border:1px solid #444;}
div[data-testid="stChatInput"] input {background:transparent; color:white; border:none;}
.file-card {background:#2f2f2f; border:1px solid #173BE8; border-radius:12px; padding:12px; margin:8px 0;}
.title-center {text-align: center; margin-bottom: 20px; color: #173BE8; font-size: 28px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

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

# LOGO KI JAGAH TITLE DAAL DIYA CENTER ME
st.markdown('<div class="title-center">💬 ClyxessChat</div>', unsafe_allow_html=True)

st.markdown(f"### {st.session_state.current_chat}")

for msg in st.session_state.all_chats[st.session_state.current_chat]:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"]=="user" else "🤖"):
        st.markdown(msg["content"], unsafe_allow_html=True)

prompt = st.chat_input("Message ClyxessChat AI...")

if prompt:
    st.session_state.all_chats[st.session_state.current_chat].append({"role": "user", "content": prompt})

    if st.session_state.current_chat == "Chat 1" and len(st.session_state.all_chats[st.session_state.current_chat]) == 1:
        new_name = prompt[:35] + "..."
        st.session_state.all_chats[new_name] = st.session_state.all_chats.pop(st.session_state.current_chat)
        st.session_state.current_chat = new_name
        st.rerun()

    client = Groq(api_key=HIDDEN_GROQ_API_KEY)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Generating..."):

            router = client.chat.completions.create(
                model=ACTIVE_GROQ_MODEL,
                messages=[{"role":"user","content":f"User: {prompt}. Code chahiye ya chat? Reply ONLY: CODE or CHAT"}],
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

            else:
                code_prompt = f"""You MUST return ONLY a valid JSON object. No text before or after.
Task: Create complete code for: {prompt}
Format: {{"filename.html": "full code", "filename.css": "full code"}}
Do NOT use markdown. Do NOT explain."""

                for attempt in range(2):
                    res = client.chat.completions.create(
                        model=ACTIVE_GROQ_MODEL,
                        messages=[{"role":"user","content":code_prompt}],
                        max_tokens=8000,
                        temperature=0.0
                    )
                    raw = res.choices[0].message.content.strip()
                    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                    if json_match:
                        raw = json_match.group()

                    try:
                        files = json.loads(raw)
                        st.markdown("### 📁 Files Ready:")
                        success_msg = "✅ Code Generated:<br>"

                        for name, code in files.items():
                            st.markdown(f"<div class='file-card'><b>📄 {name}</b></div>", unsafe_allow_html=True)
                            st.download_button(f"⬇️ Download {name}", code, name, mime="text/plain", key=f"dl_{name}_{time.time()}_{attempt}")
                            with st.expander(f"View {name}"):
                                st.code(code, language=name.split(".")[-1])
                            success_msg += f"<b>{name}</b> ✅<br>"

                        st.session_state.all_chats[st.session_state.current_chat].append({"role": "assistant", "content": success_msg})
                        break

                    except json.JSONDecodeError:
                        if attempt == 1:
                            st.error("AI ne 2 baar bhi sahi JSON nahi diya")
                            st.code(raw, language="json")
