import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import os
from google.api_core import exceptions

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Vouch.ai | Enterprise Compliance",
    page_icon="⚖️",
    layout="centered"
)

# --- 2. CSS HACK (Hide Streamlit Branding) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 3. SIDEBAR & AUTH ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield.png", width=60)
    st.title("Vouch.ai")
    st.caption("v1.1.0 Safety Mode")
    
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ License Active")
        genai.configure(api_key=api_key)
    else:
        api_key = st.text_input("🔑 API Key", type="password")
        if api_key:
            genai.configure(api_key=api_key)

# --- 4. MAIN INTERFACE ---
st.title("⚖️ Vouch.ai")
st.markdown("### Automated Legal & Compliance Audit")
st.markdown("---")

# --- 5. SAFETY SHIELD ---
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

# --- 6. FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload Media Asset (MP4, MOV)", type=['mp4', 'mov', 'avi'])

if uploaded_file and api_key:
    st.video(uploaded_file)
    
    if st.button("🚀 Run Compliance Audit", disabled=not legal_agreement):
        
        with st.spinner("🕵️‍♂️ Analyzing visual & audio vectors..."):
            temp_filename = "temp_video.mp4"
            
            try:
                # A. Save file temporarily
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.read())
                
                # B. Upload to "The Vault" (Gemini)
                video_file = genai.upload_file(path=temp_filename)
                
                # C. Wait for processing (with timeout safety)
                processing_time = 0
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    processing_time += 2
                    video_file = genai.get_file(video_file.name)
                    if processing_time > 60:
                        st.error("Time out: Video is taking too long to process on Google's servers.")
                        break

                if video_file.state.name == "FAILED":
                    st.error("Error: Video processing failed. Please try a different format.")
                
                else:
                    # D. The "Lawyer" Prompt
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
                    
                    # E. THE "SAFE LIST" (Guaranteed to exist)
                    models_to_try = [
                        "gemini-1.5-flash",       # Standard
                        "gemini-1.5-flash-latest",# Latest Alias
                        "gemini-pro"              # The Backup (Old but reliable)
                    ]
                    
                    response = None
                    success_model = None
                    last_error = None

                    # Loop through models until one works
                    for model_name in models_to_try:
                        try:
                            model = genai.GenerativeModel(model_name=model_name)
                            response = model.generate_content([prompt, video_file])
                            success_model = model_name
                            break # Success! Exit the loop
                        except Exception as e:
                            last_error = e
                            time.sleep(1)
                            continue

                    # F. Display Report
                    if response:
                        st.success(f"✅ Audit Complete (Engine: {success_model})")
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
                    else:
                        st.error(f"⚠️ System Busy. Please try again. (Details: {str(last_error)})")

            except Exception as e:
                st.error(f"Application Error: {str(e)}")
            
            # Cleanup
            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

elif not api_key:
    st.info("👈 Initialize via Sidebar System Settings")