import os
from dotenv import load_dotenv
import streamlit as st
import json
from datetime import datetime
from groq import Groq

# Load environment variables from .env if present
load_dotenv()

# ─────────────────────────────────────────────
#  Page config  — WIDE so sidebar never overlaps
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Groq AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CSS — full redesign
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ── Global (light) ── */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}
.stApp {
    background: #ffffff;
    color: #0b1220;
}

/* ── Constrain main area width ── */
.block-container {
    max-width: 820px !important;
    padding: 2rem 2rem 6rem 2rem !important;
    margin: 0 auto !important;
}

/* ── Sidebar (light) ── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e6e8eb !important;
    min-width: 290px !important;
    max-width: 290px !important;
}
section[data-testid="stSidebar"] > div { padding: 1.2rem 1rem; }

.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1.2rem;
}
.sidebar-logo .logo-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.sidebar-logo .logo-text {
    font-size: 1rem;
    font-weight: 700;
    color: #0b1220;
    letter-spacing: -0.3px;
}
.sidebar-logo .logo-sub {
    font-size: 0.65rem;
    color: #6b7280;
    font-family: 'JetBrains Mono', monospace;
}

/* Sidebar section headers */
.sb-section {
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b7280;
    margin: 1.2rem 0 0.5rem 0;
}

/* Sidebar inputs */
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stTextArea textarea,
section[data-testid="stSidebar"] .stSelectbox select {
    background: #ffffff !important;
    color: #0b1220 !important;
    border: 1px solid #e6e8eb !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.9rem !important;
}
section[data-testid="stSidebar"] label {
    color: #6b7280 !important;
    font-size: 0.85rem !important;
}
section[data-testid="stSidebar"] .stSlider { padding: 0 2px; }

/* Buttons */
.stButton > button {
    font-family: 'Sora', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    background: #ffffff;
    color: #0b1220;
    border: 1px solid #e6e8eb;
    border-radius: 8px;
    padding: 0.5rem 0.9rem;
    transition: all 0.12s ease;
    width: 100%;
}
.stButton > button:hover {
    background: #f7f8fa;
    color: #0b1220;
    border-color: #cfd6dd;
    transform: translateY(-1px);
}
.stButton > button:active { transform: translateY(0); }

/* ── Page header ── */
.page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e6e8eb;
    margin-bottom: 1.5rem;
}
.page-header h1 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0b1220;
    margin: 0;
    letter-spacing: -0.4px;
}
.page-header .subtitle {
    font-size: 0.72rem;
    color: #6b7280;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 2px;
}
.model-pill {
    background: #f1f5f9;
    border: 1px solid #e6e8eb;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.62rem;
    font-family: 'JetBrains Mono', monospace;
    color: #0b1220;
    white-space: nowrap;
}

/* ── Chat messages (native Streamlit chat_message) ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 0.5rem 0 !important;
    gap: 10px !important;
}

/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: #e6f2ff !important;
    border: 1px solid #cfe9ff !important;
    border-radius: 18px 4px 18px 18px !important;
    color: #0b1220 !important;
    padding: 0.7rem 1rem !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
    max-width: 75% !important;
    box-shadow: 0 2px 8px rgba(99,130,255,0.06) !important;
}

/* Assistant bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: #f7f8fa !important;
    border: 1px solid #eef1f4 !important;
    border-radius: 4px 18px 18px 18px !important;
    color: #0b1220 !important;
    padding: 0.7rem 1rem !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
    max-width: 75% !important;
    box-shadow: 0 2px 6px rgba(15,23,42,0.04) !important;
}

/* Avatar circles */
[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"] {
    width: 32px !important;
    height: 32px !important;
    border-radius: 50% !important;
    flex-shrink: 0 !important;
}
[data-testid="chatAvatarIcon-user"] {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
}

/* ── Timestamp ── */
.msg-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #6b7280;
    margin-top: 3px;
    padding: 0 4px;
}
.msg-time-right { text-align: right; }
.msg-time-left  { text-align: left;  }

/* ── Welcome card ── */
.welcome-card {
    text-align: center;
    padding: 3rem 2rem;
    margin: 2rem 0;
}
.welcome-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}
.welcome-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #0b1220;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}
.welcome-sub {
    font-size: 0.85rem;
    color: #6b7280;
    line-height: 1.6;
    max-width: 400px;
    margin: 0 auto 2rem auto;
}
.suggestion-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    max-width: 460px;
    margin: 0 auto;
}
.suggestion-btn {
    background: #ffffff;
    border: 1px solid #e6e8eb;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 0.9rem;
    color: #0b1220;
    text-align: left;
    cursor: pointer;
    transition: all 0.12s;
    line-height: 1.4;
}
.suggestion-btn:hover {
    border-color: #cfd6dd;
    color: #0b1220;
    background: #f7f8fa;
}
.suggestion-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #3b82f6;
    margin-bottom: 3px;
}

/* ── Status indicator ── */
.status-dot {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #22c55e;
    margin-right: 5px;
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

/* ── Stat card ── */
.stat-row {
    display: flex;
    gap: 6px;
    margin-top: 0.8rem;
}
.stat-card {
    flex: 1;
    background: #ffffff;
    border: 1px solid #e6e8eb;
    border-radius: 8px;
    padding: 6px 8px;
    text-align: center;
}
.stat-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem;
    font-weight: 600;
    color: #3b82f6;
}
.stat-lbl {
    font-size: 0.58rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Chat input ── */
[data-testid="stChatInputContainer"] {
    background: #ffffff !important;
    border-top: 1px solid #e6e8eb !important;
    padding: 0.8rem 1rem !important;
}
[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 1px solid #e6e8eb !important;
    border-radius: 12px !important;
    color: #0b1220 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.92rem !important;
}
[data-testid="stChatInput"]:focus {
    border-color: #cfd6dd !important;
    box-shadow: 0 0 0 2px rgba(99,130,255,0.06) !important;
}

/* ── Divider ── */
hr { border-color: #e6e8eb !important; margin: 0.8rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #ffffff; }
::-webkit-scrollbar-thumb { background: #e6e8eb; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Constants & defaults
# ─────────────────────────────────────────────
MODELS = {
    "⚡ llama-3.1-8b-instant  (fast & free)":  "llama-3.1-8b-instant",
    "🧠 llama-3.3-70b-versatile (smarter)":    "llama-3.3-70b-versatile",
    "🔀 mixtral-8x7b-32768 (large context)":   "mixtral-8x7b-32768",
}
HISTORY_FILE  = "chat_history.json"
DEFAULT_SYSTEM = (
    "You are a helpful, friendly, and knowledgeable AI assistant. "
    "You provide clear, concise, and accurate responses. "
    "You are honest about what you know and don't know, and you always "
    "aim to be genuinely useful. Keep responses well-structured and easy to read."
)

# ─────────────────────────────────────────────
#  Session state init
# ─────────────────────────────────────────────
defaults = {
    "messages": [],
    "system_prompt": DEFAULT_SYSTEM,
    "groq_client": None,
    "selected_model": "llama-3.1-8b-instant",
    "temperature": 0.7,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def save_history(messages: list):
    payload = {
        "saved_at": datetime.now().isoformat(),
        "model": st.session_state.selected_model,
        "messages": messages,
    }
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

def stream_response(client, system_prompt, messages, model, temperature):
    api_messages = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]} for m in messages
    ]
    stream = client.chat.completions.create(
        model=model,
        messages=api_messages,
        stream=True,
        temperature=temperature,
        max_tokens=1024,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

def approx_tokens(messages):
    total = sum(len(m["content"].split()) for m in messages)
    return int(total * 1.35)

# ─────────────────────────────────────────────
#  ── SIDEBAR ──
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo'>
      <div class='logo-icon'>🤖</div>
      <div>
        <div class='logo-text'>Groq Chat</div>
        <div class='logo-sub'>powered by groq api</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── API Key ──
    st.markdown("<div class='sb-section'>🔑 Authentication</div>", unsafe_allow_html=True)
    # Try to load API key from environment first
    env_api_key = os.getenv("GROQ_API_KEY", "")
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        value=env_api_key,
        placeholder="gsk_..." if not env_api_key else "Loaded from .env",
        help="Get a free key at console.groq.com or set GROQ_API_KEY in .env",
        label_visibility="collapsed",
    )
    resolved_key = api_key or env_api_key
    if resolved_key:
        try:
            st.session_state.groq_client = Groq(api_key=resolved_key)
            source = " (.env)" if resolved_key == env_api_key and env_api_key else ""
            st.success(f"Connected ✓{source}", icon="🟢")
        except Exception as e:
            st.error(f"Invalid key: {e}")
    else:
        st.caption("Enter your Groq API key to start chatting or add it to a .env file.")

    st.divider()

    # ── Model selector ──
    st.markdown("<div class='sb-section'>🧠 Model</div>", unsafe_allow_html=True)
    model_label = st.selectbox(
        "Model",
        options=list(MODELS.keys()),
        label_visibility="collapsed",
    )
    st.session_state.selected_model = MODELS[model_label]

    # ── Temperature ──
    st.markdown("<div class='sb-section'>🌡️ Creativity (Temperature)</div>", unsafe_allow_html=True)
    st.session_state.temperature = st.slider(
        "Temperature",
        min_value=0.0, max_value=1.5,
        value=st.session_state.temperature,
        step=0.05,
        label_visibility="collapsed",
    )
    st.caption(f"Current: `{st.session_state.temperature:.2f}` — {'🥶 Focused' if st.session_state.temperature < 0.4 else '🌤️ Balanced' if st.session_state.temperature < 0.9 else '🔥 Creative'}")

    st.divider()

    # ── Persona ──
    st.markdown("<div class='sb-section'>🎭 System Persona</div>", unsafe_allow_html=True)
    new_prompt = st.text_area(
        "Persona",
        value=st.session_state.system_prompt,
        height=130,
        label_visibility="collapsed",
    )
    if st.button("✅ Apply Persona"):
        st.session_state.system_prompt = new_prompt
        st.success("Persona updated!")

    st.divider()

    # ── Chat History ──
    st.markdown("<div class='sb-section'>💾 Chat History</div>", unsafe_allow_html=True)

    if st.button("📥 Save Chat to JSON"):
        if st.session_state.messages:
            save_history(st.session_state.messages)
            st.success("Saved → chat_history.json")
        else:
            st.info("Nothing to save yet.")

    uploaded = st.file_uploader("Upload JSON to restore", type="json", label_visibility="collapsed")
    if uploaded:
        try:
            data = json.load(uploaded)
            st.session_state.messages = data.get("messages", [])
            st.success(f"Loaded {len(st.session_state.messages)} messages!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # ── Stats ──
    msg_count = len(st.session_state.messages)
    token_est  = approx_tokens(st.session_state.messages)
    st.markdown(f"""
    <div class='stat-row'>
      <div class='stat-card'>
        <div class='stat-val'>{msg_count}</div>
        <div class='stat-lbl'>Messages</div>
      </div>
      <div class='stat-card'>
        <div class='stat-val'>~{token_est}</div>
        <div class='stat-lbl'>Tokens</div>
      </div>
    </div>
    <div style='margin-top:10px;font-family:"JetBrains Mono",monospace;font-size:0.6rem;color:#374151'>
      <span class='status-dot'></span>
      {st.session_state.selected_model}
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ── MAIN AREA ──
# ─────────────────────────────────────────────
active_model = st.session_state.selected_model

# Page header
st.markdown(f"""
<div class='page-header'>
  <div>
    <h1>💬 Groq AI Assistant</h1>
    <div class='subtitle'><span class='status-dot'></span>Streaming · Multi-turn · {'Connected' if st.session_state.groq_client else 'Not connected'}</div>
  </div>
  <div class='model-pill'>{active_model}</div>
</div>
""", unsafe_allow_html=True)

# Welcome screen
if not st.session_state.messages:
    st.markdown("""
    <div class='welcome-card'>
      <div class='welcome-icon'>✨</div>
      <div class='welcome-title'>How can I help you today?</div>
      <div class='welcome-sub'>Ask me anything — I can help you write, code, analyse, explain, or just chat.</div>
      <div class='suggestion-grid'>
        <div class='suggestion-btn'><div class='suggestion-label'>✍️ Write</div>Draft a professional email to my team</div>
        <div class='suggestion-btn'><div class='suggestion-label'>💻 Code</div>Explain how async/await works in Python</div>
        <div class='suggestion-btn'><div class='suggestion-label'>🔍 Research</div>Summarise the key ideas of stoicism</div>
        <div class='suggestion-btn'><div class='suggestion-label'>🧮 Analyse</div>Help me break down this problem step by step</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# Render history
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        ts = msg.get("time", "")
        if ts:
            align = "msg-time-right" if msg["role"] == "user" else "msg-time-left"
            st.markdown(f"<div class='msg-time {align}'>{ts}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Chat input
# ─────────────────────────────────────────────
prompt = st.chat_input("Message Groq AI…")

if prompt:
    if not st.session_state.groq_client:
        st.error("⚠️ Please enter your Groq API key in the sidebar first.")
        st.stop()

    now = datetime.now().strftime("%H:%M")

    # User bubble
    st.session_state.messages.append({"role": "user", "content": prompt, "time": now})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
        st.markdown(f"<div class='msg-time msg-time-right'>{now}</div>", unsafe_allow_html=True)

    # Assistant streaming bubble
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""

        for token in stream_response(
            st.session_state.groq_client,
            st.session_state.system_prompt,
            st.session_state.messages,
            active_model,
            st.session_state.temperature,
        ):
            full_response += token
            placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)
        resp_time = datetime.now().strftime("%H:%M")
        st.markdown(f"<div class='msg-time msg-time-left'>{resp_time}</div>", unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "time": resp_time,
    })