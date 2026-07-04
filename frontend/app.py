import streamlit as st
import requests
import json
import os
from typing import List, Dict, Any

# Configure streamlit page parameters
st.set_page_config(
    page_title="Admission Assistant - Greenwood School",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = "http://localhost:8000/api/v1"

# Inject beautiful CSS for custom premium School branding
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        color: #1e3a8a;
        margin-bottom: 5px;
    }
    
    .school-accent-text {
        color: #059669;
        font-weight: 600;
    }
    
    .stButton>button {
        border-radius: 8px;
        background-color: #1e3a8a;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #0d9488;
        border-color: #0d9488;
    }
    
    .citation-card {
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    
    .citation-header {
        font-weight: 600;
        color: #065f46;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"parent_{os.urandom(4).hex()}"
if "last_response" not in st.session_state:
    st.session_state.last_response = None


# Layout structure: Sidebar Configuration
with st.sidebar:
    # App Logo and Branding
    st.markdown("<h2 style='text-align: center;'>🏫 Greenwood</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; font-size: 0.9em;'>Admissions Enquiry Assistant Portal</p>", unsafe_allow_html=True)
    st.divider()
    
    # Navigation tabs or sections
    menu = st.radio("Portal Navigation", ["💬 Chat Assistant", "📅 Schedule a Visit", "📝 Submit Feedback", "🗄️ Document Management"])
    
    st.divider()
    
    # Quick clear history
    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.last_response = None
        st.success("Chat history cleared!")
        st.rerun()

    # System Status Indicator
    st.sidebar.markdown("### 🟢 ERP Service Status")
    try:
        health_resp = requests.get(f"{API_URL}/health", timeout=2)
        if health_resp.status_code == 200:
            h_data = health_resp.json()
            st.sidebar.caption(f"✓ SQL ERP Sync: Connected")
            st.sidebar.caption(f"✓ Vector Knowledge-base: {h_data.get('vector_db_size', 0)} chunks loaded")
        else:
            st.sidebar.caption("⚠ RAG Server unresponsive")
    except Exception:
        st.sidebar.caption("⚠ RAG Backend offline (Start FastAPI server)")


# MAIN VIEW HANDLERS

if menu == "💬 Chat Assistant":
    # Hero Title block
    st.markdown("<h1 class='main-header'>Admissions Inquiry Desk</h1>", unsafe_allow_html=True)
    st.markdown("Welcome to the **Greenwood International School** smart chatbot. Ask me about admission schedules, fees, bus routes, academic streams, extra-curricular clubs, or school timings. I retrieve official real-time ERP information to ground my responses.", unsafe_allow_html=True)
    st.divider()

    # Display Conversation History
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input box
    if prompt := st.chat_input("Enter your question (e.g. 'What are the fees for Grade 1?')"):
        # Display user query
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Append user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Generate response from FastAPI
        with st.chat_message("assistant"):
            with st.spinner("Retrieving database indices and formulating response..."):
                payload = {
                    "session_id": st.session_state.session_id,
                    "question": prompt,
                    "history": st.session_state.chat_history[:-1]  # Exclude current query from history parameter
                }
                
                try:
                    res = requests.post(f"{API_URL}/chat", json=payload, timeout=30)
                    if res.status_code == 200:
                        data = res.json()
                        answer = data["answer"]
                        st.markdown(answer)
                        
                        # Store last response for RAG inspector tabs
                        st.session_state.last_response = data
                        
                        # Save response to history
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                        st.rerun()
                    else:
                        st.error(f"Error ({res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Connection failed. Please ensure the backend is running. Exception: {str(e)}")

    # RAG Context and Citation Inspector (Displays beneath active chats)
    if st.session_state.last_response:
        resp_data = st.session_state.last_response
        st.divider()
        with st.expander("🔍 Inspection Panel: RAG Context & Source Citations", expanded=False):
            st.markdown(f"**Confidence Matching Score:** `{resp_data['confidence_score'] * 100}%`")
            if resp_data.get("query_rewritten"):
                st.info(f"**Query Rewriter Output:** Search term was optimized to: *\"{resp_data['query_rewritten']}\"*")
                
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📚 Retrieved Context Chunks")
                for citation in resp_data.get("citations", []):
                    st.markdown(f"""
                    <div class="citation-card">
                        <div class="citation-header">📌 Source: {citation['source']} (Match Score: {round(citation['score']*100, 1)}%)</div>
                        <div style="font-size:0.9rem; color:#1e293b; margin-top:5px;">{citation['chunk_text']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            with col2:
                st.subheader("🛠️ Active ERP System Rules")
                st.caption("Structured SQL entries fetched dynamically to avoid hallucinations:")
                st.json(resp_data.get("citations", []))


elif menu == "📅 Schedule a Visit":
    st.markdown("<h2 class='main-header'>Schedule a Campus Visit</h2>", unsafe_allow_html=True)
    st.write("Complete this form to request an interactive guided tour of Greenwood School's campus, class rooms, sports arena, and science laboratories.")
    
    with st.form("visit_form"):
        name = st.text_input("Parent's / Guardian's Full Name", placeholder="e.g. Richard Hendricks")
        email = st.text_input("Email Address", placeholder="richard@example.com")
        phone = st.text_input("Mobile Contact Number", placeholder="+1-555-0100")
        
        col1, col2 = st.columns(2)
        with col1:
            visit_date = st.date_input("Preferred Date")
        with col2:
            visit_time = st.selectbox("Preferred Time Slot", ["09:00 AM - 10:30 AM", "11:00 AM - 12:30 PM", "01:30 PM - 03:00 PM"])
            
        notes = st.text_area("Special Interests or Class Levels of Interest (Nursery to Grade 10)")
        
        submitted = st.form_submit_button("📅 Book Campus Tour")
        
        if submitted:
            if not name or not email or not phone:
                st.error("Please fill in all mandatory contact fields.")
            else:
                payload = {
                    "parent_name": name,
                    "parent_email": email,
                    "parent_phone": phone,
                    "visit_date": str(visit_date),
                    "visit_time": visit_time,
                    "notes": notes
                }
                try:
                    resp = requests.post(f"{API_URL}/visit", json=payload)
                    if resp.status_code == 200:
                        visit_id = resp.json().get("visit_id")
                        st.success(f"🎉 Success! Campus visit scheduled. Reference ID: GW-VISIT-{visit_id}. Our admissions coordinator will contact you shortly.")
                    else:
                        st.error("Booking failed. Please check parameters.")
                except Exception as e:
                    st.error(f"Backend offline: {str(e)}")


elif menu == "📝 Submit Feedback":
    st.markdown("<h2 class='main-header'>Admissions Chatbot Feedback</h2>", unsafe_allow_html=True)
    st.write("Help us refine our RAG pipelines. Let us know how well the bot was able to answer your questions.")
    
    with st.form("feedback_form"):
        f_email = st.text_input("Your Email Address", placeholder="e.g. feedback@example.com")
        f_rating = st.slider("Rate your Chat Experience (1 to 5 Stars)", 1, 5, 5)
        f_comments = st.text_area("Comments / Improvement suggestions")
        
        submitted = st.form_submit_button("Submit Feedback")
        
        if submitted:
            if not f_email:
                st.error("Email address is required.")
            else:
                payload = {
                    "user_email": f_email,
                    "rating": f_rating,
                    "comment": f_comments
                }
                try:
                    resp = requests.post(f"{API_URL}/feedback", json=payload)
                    if resp.status_code == 200:
                        st.success("Thank you for your valuable feedback! It has been logged in our SQL ERP database.")
                    else:
                        st.error("Error submitting feedback.")
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")


elif menu == "🗄️ Document Management":
    st.markdown("<h2 class='main-header'>Knowledge Base Document Management</h2>", unsafe_allow_html=True)
    st.write("Super-administrators and admissions staff can use this panel to upload physical policy sheets, brochure DOCX files, or school schedules to dynamically expand the chatbot's knowledge base using RAG.")
    
    st.divider()
    
    st.subheader("📤 Upload Policy Document")
    uploaded_file = st.file_uploader("Select PDF, DOCX, TXT, CSV, or Excel file", type=["pdf", "docx", "txt", "csv", "xlsx", "xls", "json"])
    
    if uploaded_file:
        if st.button("⚡ Index and Feed to Vector Store", use_container_width=True):
            with st.spinner("Uploading and indexing..."):
                try:
                    # 1. Upload file
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    upload_res = requests.post(f"{API_URL}/upload", files=files, timeout=30)
                    
                    if upload_res.status_code == 200:
                        # 2. Trigger index
                        filename = upload_res.json()["filename"]
                        index_res = requests.post(f"{API_URL}/index", params={"filename": filename}, timeout=60)
                        
                        if index_res.status_code == 200:
                            st.success(f"🎉 Success! '{filename}' successfully uploaded, chunked, and parsed. RAG pipeline synchronized.")
                            st.json(index_res.json())
                        else:
                            st.error(f"Failed to chunk document: {index_res.text}")
                    else:
                        st.error(f"Failed to upload document: {upload_res.text}")
                except Exception as e:
                    st.error(f"Error connecting to backend: {str(e)}")
                    
    st.divider()
    st.subheader("📚 Active Knowledge Base Files")
    if st.button("🔄 Sync with Knowledge Base"):
        try:
            doc_resp = requests.get(f"{API_URL}/documents")
            if doc_resp.status_code == 200:
                docs = doc_resp.json().get("documents", [])
                if not docs:
                    st.info("No physical documents indexed yet. The chatbot is currently retrieving context solely from the seeded SQL relational ERP database.")
                else:
                    for d in docs:
                        st.markdown(f"- 📄 `{d}`")
            else:
                st.error("Failed to load list.")
        except Exception as e:
            st.error(f"Backend connection error: {str(e)}")
