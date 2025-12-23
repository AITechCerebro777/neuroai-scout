import streamlit as st  # MUST BE LINE 1
import pandas as pd
from google import genai
from google.genai import types
import re
from datetime import datetime
import os

# --- 1. SECURITY GATE ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True
    st.text_input("Enter Password to Access ScoutMD", type="password", 
                 on_change=lambda: st.session_state.update(password_correct=st.session_state.password == st.secrets["APP_PASSWORD"]), 
                 key="password")
    return False

if not check_password():
    st.stop()

# --- 2. PREMIUM THEME CONFIGURATION ---
st.set_page_config(page_title="ScoutMD | NeuroAI", page_icon="🧠", layout="wide")

# Custom CSS for the Emerald & Gold Aesthetic
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    .stApp { background-color: #0F172A; font-family: 'Inter', sans-serif; color: #E2E8F0; }
    
    /* Professional Card Styling */
    .expert-card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-left: 5px solid #10B981; /* Emerald Accent */
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .expert-name { color: #F59E0B; font-size: 24px; font-weight: 700; margin-bottom: 5px; } /* Gold Accent */
    .expert-title { color: #94A3B8; font-size: 16px; font-style: italic; margin-bottom: 15px; }
    .link-button {
        background-color: #10B981;
        color: white !important;
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        display: inline-block;
        margin-top: 10px;
        font-weight: 600;
    }
    .email-preview {
        background-color: #334155;
        border: 1px dashed #64748B;
        padding: 15px;
        margin-top: 15px;
        font-size: 14px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color: #F59E0B;'>ScoutMD 🧠</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.info("Verified Neurology Experts Only")
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []

# --- 4. MAIN INTERFACE ---
st.title("NeuroAI Speaker Platform")
st.markdown("#### *The Emerald + Gold Standard Search Engine*")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
query = st.chat_input("Ex: Find founders building Brain-Computer Interfaces...")

if query:
    with st.spinner("Analyzing Medical Databases..."):
        # Specific instructions to the AI to provide data for the cards
        prompt = f"""
        Provide a list of 3 top neurology experts for: {query}.
        Format the response for each expert EXACTLY like this:
        NAME: [Name]
        TITLE: [Title/Affiliation]
        LINK: https://www.quora.com/What-is-a-research-profile-How-do-you-create-one
        BIO: [Short bio of achievements]
        EMAIL: [A professional 3-sentence invitation email]
        """
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        raw_text = response.text

    # Parse the AI response into visual cards
    experts = raw_text.split("NAME:")[1:] # Split into individual expert chunks
    
    for exp in experts:
        try:
            # Extract data using simple markers
            name = exp.split("TITLE:")[0].strip()
            title = exp.split("LINK:")[1].split("BIO:")[0].strip() # Swapped for display logic
            actual_title = exp.split("TITLE:")[1].split("LINK:")[0].strip()
            link = exp.split("LINK:")[1].split("BIO:")[0].strip()
            bio = exp.split("BIO:")[1].split("EMAIL:")[0].strip()
            email = exp.split("EMAIL:")[1].strip()

            # Render the Card
            st.markdown(f"""
            <div class="expert-card">
                <div class="expert-name">{name}</div>
                <div class="expert-title">{actual_title}</div>
                <p>{bio}</p>
                <a href="{link}" target="_blank" class="link-button">View Profile / Research</a>
                <div class="email-preview">
                    <strong>✉️ Draft Invitation:</strong><br>{email}
                </div>
            </div>
            """, unsafe_allow_html=True)
        except:
            continue # Skip if formatting is off

else:
    st.info("Please enter a research topic to generate your expert cards.")
