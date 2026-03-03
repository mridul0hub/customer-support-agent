import os
from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Load API key
load_dotenv()

# Load knowledge base
with open("knowledge_base.txt", "r") as f:
    knowledge = f.read()

# Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# System prompt
system_prompt = f"""
You are a helpful customer support agent for a business.
Use ONLY the information below to answer questions.
If you don't know the answer, say "Let me connect you with a human agent."
Never make up information.

BUSINESS INFORMATION:
{knowledge}

Always be polite, short, and helpful.
Reply in the same language the customer uses.
"""

# Page config
st.set_page_config(
    page_title="Support Agent",
    page_icon="🤖",
    layout="centered"
)

# Professional CSS styling
st.markdown("""
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Background */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        min-height: 100vh;
    }

    /* Header box */
    .header-box {
        background: linear-gradient(135deg, #6C63FF, #3B82F6);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 8px 32px rgba(108, 99, 255, 0.3);
    }
    .header-title {
        color: white;
        font-size: 26px;
        font-weight: 700;
        margin: 0;
    }
    .header-subtitle {
        color: rgba(255,255,255,0.75);
        font-size: 14px;
        margin: 4px 0 0 0;
    }
    .online-dot {
        width: 10px;
        height: 10px;
        background: #22c55e;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.6); }
        70% { box-shadow: 0 0 0 8px rgba(34,197,94,0); }
        100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
    }

    /* Chat messages */
    .stChatMessage {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        margin-bottom: 8px !important;
        backdrop-filter: blur(10px);
    }

    /* Chat input */
    .stChatInputContainer {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(108,99,255,0.4) !important;
        border-radius: 12px !important;
    }
    .stChatInputContainer:focus-within {
        border-color: #6C63FF !important;
        box-shadow: 0 0 0 2px rgba(108,99,255,0.2) !important;
    }

    /* Text colors */
    .stChatMessage p, .stChatMessage div {
        color: #e2e8f0 !important;
    }

    /* Stats bar */
    .stats-bar {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
    }
    .stat-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 12px 18px;
        flex: 1;
        text-align: center;
    }
    .stat-number {
        color: #6C63FF;
        font-size: 20px;
        font-weight: 700;
    }
    .stat-label {
        color: rgba(255,255,255,0.5);
        font-size: 11px;
        margin-top: 2px;
    }

    /* Powered by tag */
    .powered-by {
        text-align: center;
        color: rgba(255,255,255,0.25);
        font-size: 11px;
        margin-top: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-box">
        <div style="font-size:40px;">🤖</div>
        <div>
            <p class="header-title">TechShop Support Agent</p>
            <p class="header-subtitle">
                <span class="online-dot"></span>Online · Powered by AI · Replies instantly
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Stats bar
if "messages" not in st.session_state:
    st.session_state.messages = []

msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])

st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Always Online</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{msg_count}</div>
            <div class="stat-label">Messages Today</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">&lt;2s</div>
            <div class="stat-label">Avg Response</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Welcome message
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.write("👋 Hello! I'm TechShop's AI support agent. I can help you with orders, shipping, returns, and payments. What can I help you with today?")

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input
user_input = st.chat_input("Ask me anything about our store...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Build messages with memory
    all_messages = [SystemMessage(content=system_prompt)]
    for msg in st.session_state.messages[:-1]:
        if msg["role"] == "user":
            all_messages.append(HumanMessage(content=msg["content"]))
        else:
            all_messages.append(AIMessage(content=msg["content"]))
    all_messages.append(HumanMessage(content=user_input))

    # Get response with loading spinner
    with st.spinner(""):
        response = llm.invoke(all_messages)
        agent_reply = response.content

    st.session_state.messages.append({"role": "assistant", "content": agent_reply})
    with st.chat_message("assistant"):
        st.write(agent_reply)

# Powered by footer
st.markdown('<div class="powered-by">⚡ Powered by AI Agent SaaS</div>', unsafe_allow_html=True)
