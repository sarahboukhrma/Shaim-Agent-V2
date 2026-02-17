import streamlit as st
import os

st.set_page_config(page_title="SHAIM AI", page_icon="🔍")

# State
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.key = os.getenv('ANTHROPIC_API_KEY', '')

def call_ai(text):
    if not st.session_state.key:
        return "⚠️ Add API key in sidebar"
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=st.session_state.key)
        msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        msgs.append({"role": "user", "content": text})
        r = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=1000, messages=msgs)
        return r.content[0].text
    except Exception as e:
        return f"Error: {str(e)[:100]}"

# UI
st.title("🔍 SHAIM AI Agent")

with st.sidebar:
    if not st.session_state.key:
        k = st.text_input("API Key", type="password")
        if k:
            st.session_state.key = k
    if st.button("Reset"):
        st.session_state.messages = []
        st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if prompt := st.chat_input("Type here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        response = call_ai(prompt)
        st.write(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
