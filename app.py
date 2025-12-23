import streamlit as st  # MUST BE LINE 1
import pandas as pd
from google import genai
from google.genai import types
import re
from datetime import datetime
import os

# --- 1. SECURITY GATE (For Mobile & Web Privacy) ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True
    
    st.markdown("<h2 style='text-align: center; color: #F59E0B;'>ScoutMD Private Access</h2>", unsafe_allow_html=True)
    st.text_input("Enter Password to Access Platform", type="password", 
                 on_change=lambda: st.session_state.update(password_correct=st.session_state.password == st.secrets["APP_PASSWORD"]), 
                 key="password")
    return False

if not check_password():
    st.stop()

# --- 2. PREMIUM THEME CONFIGURATION ---
st.set_page_config(page_title="ScoutMD | NeuroAI", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    .stApp { background-color: #0F172A; font-family: 'Inter', sans-serif; color: #E2E8F0; }
    
    /* The Emerald + Gold Card Design */
    .expert-card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-left: 6px solid #10B981; /* Emerald border */
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .expert-name { color: #F59E0B; font-size: 26px; font-weight: 800; margin-bottom: 5px; } /* Gold name */
    .expert-title { color: #94A3B8; font-size: 16px; margin-bottom: 15px; font-weight: 600; }
    
    .link-button {
        background-color: #10B981;
        color: white !important;
        padding: 12px 24px;
        border-radius: 8px;
        text-decoration: none;
        display: inline-block;
        font-weight: 700;
        margin-top: 15px;
        text-align: center;
    }
    .email-preview {
        background-color: #1e293b;
        border: 1px dashed #475569;
        padding: 15px;
        margin-top: 20px;
        border-radius: 8px;
        font-size: 14px;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color: #F59E0B;'>ScoutMD 🧠</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.success("Verified Neurology Engine")
    if 'expert_data' in st.session_state:
        st.download_button("📥 Save Search Results", 
                          data=st.session_state.expert_data, 
                          file_name=f"NeuroScout_{datetime.now().strftime('%m%d')}.txt",
                          use_container_width=True)

# --- 4. MAIN INTERFACE ---
st.title("NeuroAI Speaker Platform")
st.markdown("#### *The Emerald + Gold Standard Search Engine*")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
query = st.chat_input("Ex: Find founders in Brain-Computer Interfaces...")

if query:
    with st.spinner("Analyzing Global Databases..."):
        # This prompt forces the AI to use specific tags so the card-builder doesn't break
        prompt = f"Find 3 real-world neurology experts for: {query}. Use these exact labels for each expert: [NAME], [TITLE], [LINK], [BIO], [EMAIL]"
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        st.session_state.expert_data = response.text

    # BUILDING THE CARDS
    expert_entries = response.text.split("[NAME]")[1:]
    for entry in expert_entries:
        try:
            name = entry.split("[TITLE]")[0].strip()
            title = entry.split("[TITLE]")[1].split("[LINK]")[0].strip()
            link = entry.split("[LINK]")[1].split("[BIO]")[0].strip()
            bio = entry.split("[BIO]")[1].split("[EMAIL]")[0].strip()
            email = entry.split("[EMAIL]")[1].strip()

            st.markdown(f"""
            <div class="expert-card">
                <div class="expert-name">{name}</div>
                <div class="expert-title">{title}</div>
                <p style="color: #cbd5e1;">{bio}</p>
                <a href="{link}" target="_blank" class="link-button">View Profile / Research</a>
                <div class="email-preview">
                    <strong style="color: #F59E0B;">✉️ Outreach Draft:</strong><br>{email}
                </div>
            </div>
            """, unsafe_allow_html=True)
        except:
            continue
else:
    st.info("System Ready. Enter a research topic to generate your expert cards.")
