import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Vouch.ai | Enterprise Compliance",
    page_icon="⚖️",
    layout="centered"
)

# --- 2. CSS HACK ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 3. DYNAMIC MODEL FINDER (The Fix) ---
def get_active_model():
    """Finds a working model in your account instead of guessing."""
    try:
        # List all models available to your API key
        all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority list (Try these first)
        priorities = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-2.0-flash']
        
        # 1. Check for priority models
        for p in priorities:
            if p in all_models:
                return p
        
        # 2. If no priority model, take the first valid Gemini model
        for m in all_models:
            if "gemini" in m:
                return m
                
        # 3. Absolute fallback
        return "models/gemini-1.5-flash" 
        
    except Exception as e:
        # Fallback if list_models fails (e.g., API key issue)
        return "models/gemini-1.5-flash"

# --- 4. SIDEBAR & AUTH ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield.png", width=60)
    st.title("Vouch.ai")
    st.caption("v1.1.1 Auto-Discovery")
    
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ License Active")
        genai.configure(api_key=api_key)
    else:
        api_key = st.text_input("🔑 API Key", type="password")
        if api_key:
            genai.configure(api_key=api_key)

# --- 5. MAIN INTERFACE ---
st.title("⚖️ Vouch.ai")
st.markdown("### Automated Legal & Compliance Audit")
st.markdown("---")

# --- 6. SAFETY SHIELD ---
with st.expander("⚠️ LEGAL DISCLAIMER (READ FIRST)", expanded=True):
    st.warning(
        """
        **CONFIDENTIALITY NOTICE:**
        1. This is an automated AI assessment tool for **preliminary screening**.
        2. It is **NOT** a substitute for professional legal counsel. 
        3. **DO NOT** upload sensitive or unreleased client assets to this server.
        """
    )
    legal_agreement = st.checkbox("I acknowledge this is an automated draft analysis.")

# --- 7. FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload Media Asset (MP4, MOV)", type=['mp4', 'mov', 'avi'])

if uploaded_file and api_key:
    st.video(uploaded_file)
    
    if st.button("🚀 Run Compliance Audit", disabled=not legal_agreement):
        
        with st.spinner("🕵️‍♂️ Connecting to Compliance Engine..."):
            temp_filename = "temp_video.mp4"
            
            try:
                # A. FIND THE MODEL (The new logic)
                active_model_name = get_active_model()
                # st.toast(f"Connected to: {active_model_name}") # Debug message
                
                # B. Save file
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.read())
                
                # C. Upload to Vault
                video_file = genai.upload_file(path=temp_filename)
                
                # D. Wait for processing
                processing_time = 0
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    processing_time += 2
                    video_file = genai.get_file(video_file.name)
                    if processing_time > 60:
                        st.error("Time out: Video processing took too long.")
                        break

                if video_file.state.name == "FAILED":
                    st.error("Error: Video processing failed.")
                
                else:
                    # E. The "Lawyer" Prompt
                    prompt = """
                    Act as a Senior Compliance Officer for the Indian Censor Board (CBFC). 
                    Analyze this video for legal risks under Indian Law.
                    
                    Focus on:
                    1. IPC 295A & BNS 299 (Religious Sentiments).
                    2. IPC 153A & BNS 196 (Promoting Enmity).
                    3. COTPA 2003 (Tobacco Disclaimers).
                    4. Map Accuracy (Criminal Law Amendment Act).

                    Output a structured audit report:
                    - **Timestamp**: [MM:SS]
                    - **Risk Category**: [Category]
                    - **Severity**: [High/Medium/Low]
                    - **Observation**: [What happened]
                    - **Remediation**: [How to fix it]
                    
                    If safe, state "No Compliance Violations Detected."
                    """
                    
                    # F. GENERATE (Using the discovered model)
                    model = genai.GenerativeModel(model_name=active_model_name)
                    response = model.generate_content([prompt, video_file])

                    # G. Display Report
                    st.success(f"✅ Audit Complete (Engine: {active_model_name})")
                    st.markdown("### 📋 Executive Summary")
                    st.write(response.text)
                    
                    # Footer
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    audit_id = int(time.time())
                    st.markdown("---")
                    st.markdown(
                        f"""
                        <div style="text-align: center; color: #888; font-size: 12px; font-family: sans-serif;">
                            <b>CONFIDENTIAL REPORT</b><br>
                            Generated by Vouch.ai Compliance Engine v1.0<br>
                            Timestamp: {timestamp} IST • Audit ID: #V{audit_id}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            except Exception as e:
                st.error(f"System Error: {str(e)}")
            
            # Cleanup
            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

elif not api_key:
    st.info("👈 Initialize via Sidebar System Settings")