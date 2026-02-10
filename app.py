import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Vouch.ai", page_icon="🛡️")

# --- 2. AUTHENTICATION ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shield.png", width=60)
    st.title("Vouch.ai")
    st.caption("v1.5 Final Stable")
    
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ License Active")
        genai.configure(api_key=api_key)
    else:
        api_key = st.text_input("🔑 API Key", type="password")
        if api_key:
            genai.configure(api_key=api_key)

# --- 3. MAIN INTERFACE ---
st.title("⚖️ Vouch.ai")
st.markdown("### Automated Legal & Compliance Audit")

# --- 4. UPLOAD & PROCESSING ---
uploaded_file = st.file_uploader("Upload Video", type=['mp4', 'mov', 'avi'])

if uploaded_file and api_key:
    st.video(uploaded_file)
    
    if st.button("🚀 Run Compliance Audit"):
        
        with st.spinner("Processing video..."):
            temp_filename = "temp_video.mp4"
            try:
                # A. Save locally
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.read())
                
                # B. Upload to Google
                video_file = genai.upload_file(path=temp_filename)
                
                # C. Wait for processing loop
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)

                if video_file.state.name == "FAILED":
                    st.error("Video processing failed on Google's side.")
                else:
                    # D. THE FIX: Using the generic alias from your list
                    # This avoids the "Limit: 0" error on version 2.0
                    target_model = "models/gemini-flash-latest"
                    
                    model = genai.GenerativeModel(model_name=target_model)
                    
                    prompt = """
                    Act as a Senior Compliance Officer for the Indian Censor Board (CBFC). 
                    Analyze this video for violations of:
                    1. IPC 295A (Religious Sentiments)
                    2. BNS 196 (Promoting Enmity)
                    3. COTPA 2003 (Smoking Disclaimers)
                    
                    Provide a timestamped list of risks.
                    """
                    
                    response = model.generate_content([prompt, video_file])
                    
                    st.success(f"✅ Audit Complete (Engine: {target_model})")
                    st.markdown("### 📋 Analysis Report")
                    st.write(response.text)

            except Exception as e:
                # Detailed error handling
                st.error(f"Error: {str(e)}")
            
            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

elif not api_key:
    st.info("👈 Enter your API Key in the sidebar to start.")