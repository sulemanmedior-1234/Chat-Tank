"""
Chat Tank — a Streamlit chatbot powered by the Groq API.
Deploy free on Streamlit Community Cloud.
"""

import os

import streamlit as st
from groq import Groq, APIError, AuthenticationError, RateLimitError

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Chat Tank", page_icon="🛡️", layout="centered")

FALLBACK_MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]
NON_CHAT_KEYWORDS = ("whisper", "tts", "guard", "embed", "orpheus", "playai")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_api_key() -> str | None:
    """Read the key from Streamlit secrets, then env var, then the sidebar."""
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass  # no secrets.toml present locally
    return os.environ.get("GROQ_API_KEY")


@st.cache_data(ttl=3600, show_spinner=False)
def list_chat_models(api_key: str) -> list[str]:
    """Fetch the live list of chat models from Groq (cached for 1 hour)."""
    try:
        models = Groq(api_key=api_key).models.list().data
        ids = sorted(
            m.id
            for m in models
            if getattr(m, "active", True)
            and not any(k in m.id.lower() for k in NON_CHAT_KEYWORDS)
        )
        return ids or FALLBACK_MODELS
    except Exception:
        return FALLBACK_MODELS


def stream_reply(client: Groq, model: str, messages: list, temperature: float, max_tokens: int):
    """Yield text chunks from a streaming Groq chat completion."""
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_completion_tokens=max_tokens,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("⚡ Settings")

    api_key = get_api_key()
    if not api_key:
        api_key = st.text_input(
            "Groq API key",
            type="password",
            help="Get a free key at https://console.groq.com/keys",
        )

    if api_key:
        models = list_chat_models(api_key)
        default_idx = models.index(FALLBACK_MODELS[0]) if FALLBACK_MODELS[0] in models else 0
        model = st.selectbox("Model", models, index=default_idx)
    else:
        model = None

    system_prompt = st.text_area(
        "System prompt",
        value="You are a helpful, concise assistant.",
        height=100,
    )
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
    max_tokens = st.slider("Max response tokens", 256, 8192, 2048, 256)

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Powered by [Groq](https://groq.com) · Built with Streamlit")


# ---------------------------------------------------------------------------
# Main chat area
# ---------------------------------------------------------------------------
st.title("🛡️ Chat Tank")
st.caption("A heavy-duty AI chatbot, powered by Groq")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not api_key:
    st.info("👈 Add your Groq API key in the sidebar (or in app secrets) to start chatting.")
    st.stop()

client = Groq(api_key=api_key)

if prompt := st.chat_input("Ask me anything…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    with st.chat_message("assistant"):
        try:
            reply = st.write_stream(
                stream_reply(client, model, api_messages, temperature, max_tokens)
            )
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except AuthenticationError:
            st.error("Invalid Groq API key. Check your key and try again.")
            st.session_state.messages.pop()
        except RateLimitError:
            st.warning("Rate limit reached on Groq's free tier. Wait a moment and retry.")
            st.session_state.messages.pop()
        except APIError as e:
            st.error(f"Groq API error: {e}")
            st.session_state.messages.pop()
