import tempfile
import os
import streamlit as st
import ui 
import json

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

st.set_page_config(
    page_title="Resume RAG System", 
    layout="wide"
)

# 1. Initialize Persistent Session States
if "has_started" not in st.session_state:
    st.session_state.has_started = False
if "ranking_data" not in st.session_state:
    st.session_state.ranking_data = None
if "resumes_context" not in st.session_state:
    st.session_state.resumes_context = ""
if "multi_chat_history" not in st.session_state:
    st.session_state.multi_chat_history = []
if "single_chat_history" not in st.session_state:
    st.session_state.single_chat_history = []
if "single_resume_text" not in st.session_state:
    st.session_state.single_resume_text = ""

# 2. Render all inputs from ui.py
app_mode, uploaded_files, user_query, job_desc, rank_criteria, start_clicked = ui.render_ui()


# 3. Helper to extract full text and preserve raw PDF bytes
def extract_text_and_bytes_from_pdfs(files):
    extracted_docs = []
    for uploaded_file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            loader = PyPDFLoader(tmp_path)
            pages = loader.load()
            full_text = "\n".join([p.page_content for p in pages])
            extracted_docs.append({
                "filename": uploaded_file.name,
                "text": full_text,
                "bytes": uploaded_file.getvalue()  # Store raw bytes for downloading
            })
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    return extracted_docs


# 4. Handle "Start" button click
if start_clicked:
    if not uploaded_files:
        st.warning("Please upload at least one candidate PDF resume above.")
    else:
        st.session_state.has_started = True

        with st.spinner("Analyzing candidate data with Gemini..."):
            try:
                llm = ChatGoogleGenerativeAI(model="models/gemini-3.6-flash")

                # MULTI-CANDIDATE RANKING
                if app_mode == "Multi-Candidate Ranking":
                    st.session_state.multi_chat_history = []  # Reset multi-chat
                    resumes = extract_text_and_bytes_from_pdfs(uploaded_files)

                    resumes_formatted = ""
                    for i, r in enumerate(resumes, start=1):
                        resumes_formatted += f"\n--- CANDIDATE FILE {i} ({r['filename']}) ---\n{r['text']}\n"

                    st.session_state.resumes_context = resumes_formatted

                    prompt = f"""
You are an expert, objective recruiter with 20+ years of hiring experience.
Evaluate the candidates strictly on merit, qualifications, and role alignment.

TARGET JOB REQUIREMENTS:
{job_desc}

SPECIFIC RANKING CRITERIA:
{rank_criteria}

RESUMES:
{resumes_formatted}

INSTRUCTIONS:
1. Extract the actual full name of each candidate directly from their resume text.
2. For the 'filename' field, return the exact candidate filename from the headers above.
3. Rank them from best match (#1) to lowest match.
4. For each candidate, provide a concise 1-2 sentence executive assessment of their fit.

Return your response strictly as valid JSON with this exact structure:
{{
  "rankings": [
    {{
      "rank": 1,
      "filename": "file_name.pdf",
      "name": "Full Name",
      "summary": "1-2 sentence explanation of why this candidate fits."
    }}
  ]
}}
"""
                    chain = llm | StrOutputParser()
                    raw_response = chain.invoke(prompt)

                    if isinstance(raw_response, list):
                        raw_response = "".join(str(item) for item in raw_response)
                    else:
                        raw_response = str(raw_response)

                    clean_json = raw_response.strip()
                    if "```" in clean_json:
                        clean_json = clean_json.split("```")[1]
                        if clean_json.startswith("json"):
                            clean_json = clean_json[4:]
                        clean_json = clean_json.strip()

                    parsed_data = json.loads(clean_json)

                    # Match each candidate with their original PDF bytes for downloading
                    file_map = {r["filename"].lower(): r for r in resumes}
                    
                    for idx, candidate in enumerate(parsed_data.get("rankings", [])):
                        fname = candidate.get("filename", "").lower()
                        matched = file_map.get(fname)
                        
                        # Fallback match by index if filename differed slightly
                        if not matched and idx < len(resumes):
                            matched = resumes[idx]
                            
                        if matched:
                            candidate["cv_bytes"] = matched["bytes"]
                            candidate["cv_filename"] = matched["filename"]
                        else:
                            candidate["cv_bytes"] = None
                            candidate["cv_filename"] = "resume.pdf"

                    st.session_state.ranking_data = parsed_data

                # SINGLE CANDIDATE ANALYSIS
                else:
                    st.session_state.single_chat_history = []  # Reset single-chat
                    single_resumes = extract_text_and_bytes_from_pdfs(uploaded_files[:1])
                    st.session_state.single_resume_text = single_resumes[0]["text"]

                    initial_question = user_query if user_query else "Provide a comprehensive breakdown of key qualifications, strengths, and role fit."
                    
                    prompt = f"""
You are an expert recruiter analyzing the following candidate resume.

RESUME CONTENT:
{st.session_state.single_resume_text}

QUESTION:
{initial_question}

Provide an objective, professional, and thorough answer based strictly on the resume.
"""
                    chain = llm | StrOutputParser()
                    bot_reply = chain.invoke(prompt)

                    if isinstance(bot_reply, list):
                        bot_reply = "".join(str(item) for item in bot_reply)
                    else:
                        bot_reply = str(bot_reply)

                    # Store initial question and answer in single chat history
                    st.session_state.single_chat_history.append({"role": "user", "content": initial_question})
                    st.session_state.single_chat_history.append({"role": "assistant", "content": bot_reply})

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")


# ==========================================
# 5. DISPLAY RESULTS & CHAT SECTION
# ==========================================
if app_mode == "Multi-Candidate Ranking":
    if not st.session_state.has_started or not st.session_state.ranking_data:
        ui.render_empty_state()
    else:
        st.markdown("### Results & Candidate Rankings")
        
        # 1. Render Ranked Cards with 'Download CV' button
        ui.render_ranking_cards(st.session_state.ranking_data.get("rankings", []))

        # 2. Interactive Recruiter Chat
        st.markdown("### Candidate Comparison & Recruiter Chat")

        for message in st.session_state.multi_chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        user_prompt = st.chat_input("Ask about candidates (e.g., 'Compare Sarah and Ahmad's experience' or 'Summarize skills')...")

        if user_prompt:
            st.session_state.multi_chat_history.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.write(user_prompt)

            history_text = ""
            for msg in st.session_state.multi_chat_history[:-1]:
                history_text += f"{msg['role'].upper()}: {msg['content']}\n"

            llm = ChatGoogleGenerativeAI(model="models/gemini-3.6-flash")
            chat_query = f"""
You are an expert, objective recruiter assistant.
You have analyzed and ranked the candidate resumes below.

JOB REQUIREMENTS:
{job_desc}

RANKING CRITERIA:
{rank_criteria}

RESUME CONTEXT:
{st.session_state.resumes_context}

PREVIOUS CONVERSATION:
{history_text}

USER QUESTION:
{user_prompt}

Answer objectively and factually based strictly on their actual resume experience.
"""
            with st.spinner("Analyzing candidate details..."):
                chat_chain = llm | StrOutputParser()
                bot_reply = chat_chain.invoke(chat_query)

                if isinstance(bot_reply, list):
                    bot_reply = "".join(str(item) for item in bot_reply)
                else:
                    bot_reply = str(bot_reply)

            st.session_state.multi_chat_history.append({"role": "assistant", "content": bot_reply})
            with st.chat_message("assistant"):
                st.write(bot_reply)

else:
    # SINGLE CANDIDATE CHAT SECTION
    if st.session_state.has_started and st.session_state.single_chat_history:
        st.markdown("### Candidate Analysis & Q&A Chat")

        # Display full conversation thread
        for message in st.session_state.single_chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Follow-up Chat Input
        single_prompt = st.chat_input("Ask a follow-up question about this candidate...")

        if single_prompt:
            st.session_state.single_chat_history.append({"role": "user", "content": single_prompt})
            with st.chat_message("user"):
                st.write(single_prompt)

            history_text = ""
            for msg in st.session_state.single_chat_history[:-1]:
                history_text += f"{msg['role'].upper()}: {msg['content']}\n"

            llm = ChatGoogleGenerativeAI(model="models/gemini-3.6-flash")
            chat_query = f"""
You are an expert recruiter assistant analyzing this candidate resume.

RESUME CONTENT:
{st.session_state.single_resume_text}

PREVIOUS CONVERSATION:
{history_text}

USER QUESTION:
{single_prompt}

Answer objectively, factually, and thoroughly based strictly on their actual resume content.
"""
            with st.spinner("Reviewing resume..."):
                chat_chain = llm | StrOutputParser()
                bot_reply = chat_chain.invoke(chat_query)

                if isinstance(bot_reply, list):
                    bot_reply = "".join(str(item) for item in bot_reply)
                else:
                    bot_reply = str(bot_reply)

            st.session_state.single_chat_history.append({"role": "assistant", "content": bot_reply})
            with st.chat_message("assistant"):
                st.write(bot_reply)