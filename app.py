
import streamlit as st
import time
from agent import run_agent

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="🕷️ Spidyy AI",
    page_icon="🕷️",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>

.stApp{
    background-color:#F7F7F8;
}

/* Sidebar */
[data-testid="stSidebar"]{
    background:white;
    border-right:1px solid #E5E7EB;
}

/* Hero section */
.hero{
    background:linear-gradient(
        135deg,
        #E0F2FE,
        #EDE9FE,
        #FCE7F3
    );

    padding:40px;
    border-radius:30px;
    text-align:center;
    margin-bottom:25px;
    box-shadow:0px 4px 15px rgba(0,0,0,0.08);
}

.main-title{
    font-size:60px;
    font-weight:bold;
    color:#111827;
}

.sub-title{
    font-size:20px;
    color:#4B5563;
}

/* Cards */
.card{
    background:white;
    padding:20px;
    border-radius:20px;
    border:1px solid #E5E7EB;
    box-shadow:0px 2px 8px rgba(0,0,0,0.05);
}

/* Chat */
.stChatMessage{
    background:white;
    border-radius:20px;
    padding:15px;
    border:1px solid #E5E7EB;
}

/* Buttons */
.stButton>button{
    background:#2563EB;
    color:white;
    border:none;
    border-radius:15px;
    width:100%;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.title("🕷️ Spidyy AI")

    if st.button("🗑️ New Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    st.subheader("🕒 Recent Chats")

    if len(st.session_state.history) == 0:
        st.write("No chats yet")

    else:
        for chat in reversed(st.session_state.history[-10:]):
            st.write(f"💬 {chat}")

    st.markdown("---")

    st.subheader("🛠 Tools")

    st.write("🌤 Weather")
    st.write("📈 Stocks")
    st.write("💻 Commands")

# ---------------- HERO ----------------
st.markdown(
"""
<div class='hero'>

<div class='main-title'>
🕷️ Spidyy AI
</div>

<div class='sub-title'>
Weather • Stocks • Commands • AI Assistant
</div>

</div>
""",
unsafe_allow_html=True
)

# ---------------- CARDS ----------------
col1,col2,col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='card'>
    <h3>🌤 Weather</h3>
    Current weather anywhere
    </div>
    """,unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='card'>
    <h3>📈 Stocks</h3>
    Live stock prices
    </div>
    """,unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='card'>
    <h3>💻 Commands</h3>
    Execute system commands
    </div>
    """,unsafe_allow_html=True)

st.divider()

# ---------------- OLD MESSAGES ----------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- INPUT ----------------
prompt = st.chat_input("Ask Spidyy AI anything...")

if prompt:

    if prompt not in st.session_state.history:
        st.session_state.history.append(prompt)

    st.session_state.messages.append(
        {
            "role":"user",
            "content":prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Spinning the web..."):
            answer = run_agent(prompt)

        placeholder = st.empty()

        full_text = ""

        for word in answer.split():

            full_text += word + " "

            placeholder.markdown(full_text + "▌")

            time.sleep(0.02)

        placeholder.markdown(full_text)

    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":answer
        }
    )
