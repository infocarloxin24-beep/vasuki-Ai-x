import streamlit as st
import json
import re
from groq import Groq
import time

st.set_page_config(page_title="ClyxessChat AI", page_icon="💬", layout="wide")

HIDDEN_GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
ACTIVE_GROQ_MODEL = "llama-3.3-70b-versatile"

# FIX 1: HISTORY SAVE KE LIYE DICT BANAYA
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

# CHATGPT JAISE CSS
st.markdown("""
<style>
.stApp {background-color: #212121;}
.main.block-container {max-width: 800px; padding-top: 2rem;}
[data-testid="stSidebar"] {background-color: #171717;}
.stChatInputContainer {background: transparent;}
div[data-testid="stChatInput"] {background:#2f2f2f; border-radius:24px; border:1px solid #444;}
div[data-testid="stChatInput"] input {background:transparent; color:white; border:none;}
div[data-testid="stChatInput"] button[kind="secondary"] {right: 10px;}
</style>
""", unsafe_allow_html=True)

# FIX 2: SIDEBAR + DELETE DALA
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

st.title("💬 ClyxessChat")
st.caption("Next-Gen Portable Multi-File Code Engine")

# CHAT HISTORY - AB DICT SE AAYEGI
for msg in st.session_state.all_chats[st.session_state.current_chat]:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"]=="user" else "🤖"):
        st.markdown(msg["content"], unsafe_allow_html=True)

# INPUT
prompt = st.chat_input("Message ClyxessChat AI...")

# FIX 3: MIC BUTTON HATA DIYA

if prompt:
    st.session_state.all_chats[st.session_state.current_chat].append({"role": "user", "content": prompt})

    # AUTO RENAME - PEHLE MSG SE
    if st.session_state.current_chat == "Chat 1" and len(st.session_state.all_chats[st.session_state.current_chat]) == 1:
        new_name = prompt[:35]
        st.session_state.all_chats[new_name] = st.session_state.all_chats.pop(st.session_state.current_chat)
        st.session_state.current_chat = new_name
        st.rerun()

    client = Groq(api_key=HIDDEN_GROQ_API_KEY)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Generating..."):

            router = client.chat.completions.create(
                model=ACTIVE_GROQ_MODEL,
                messages=[{"role":"user","content":f"User asked: {prompt}. If they want code/website/app reply CODE. Else CHAT. Reply ONLY one word."}],
                max_tokens=5, temperature=0
            )
            decision = router.choices[0].message.content.strip().upper()

            if "CHAT" in decision:
                res = client.chat.completions.create(
                    model=ACTIVE_GROQ_MODEL,
                    messages=st.session_state.all_chats[st.session_state.current_chat], # PURA HISTORY BHEJA
                    max_tokens=2000
                )
                ans = res.choices[0].message.content
                st.write(ans)
                st.session_state.all_chats[st.session_state.current_chat].append({"role": "assistant", "content": ans})

            else:
                # FIX 4: SAKHT PROMPT + JSON SAF KRNA
                code_prompt = f"""SYSTEM: Output ONLY valid JSON. No text. No ```
USER: {prompt}
FORMAT: {{"index.html":"full code","style.css":"full code"}}"""

                res = client.chat.completions.create(
                    model=ACTIVE_GROQ_MODEL,
                    messages=[{"role":"user","content":code_prompt}],
                    max_tokens=8000,
                    temperature=0.0
                )
                raw = res.choices[0].message.content.strip()
                # JSON NIKALNA
                json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                if json_match: raw = json_match.group()

                try:
                    files = json.loads(raw)
                    success_msg = ""
                    for name, code in files.items():
                        st.download_button(f"⬇️ Download {name}", code, name, key=f"dl_{name}_{time.time()}")
                        with st.expander(f"📄 View {name}"):
                            st.code(code, language=name.split(".")[-1])
                        success_msg += f"<b>{name}</b> ✅<br>"

                    st.session_state.all_chats[st.session_state.current_chat].append({"role": "assistant", "content": f"Code Generated:<br>{success_msg}"})

                except json.JSONDecodeError as e:
                    error_msg = f"<b>Error:</b><br>AI ne sahi JSON nahi diya<br><pre>{raw}</pre>"
                    st.error("Error in code generation")
                    st.code(raw, language="json")
                    st.session_state.all_chats[st.session_state.current_chat].append({"role": "assistant", "content": error_msg})
