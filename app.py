import tempfile
import os
import re
import streamlit as st
import ui 
import json

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.3)



def clean_llm_text(content):
    """Extract clean text from Gemini if it returns a list with metadata."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        full_text = ""
        for item in content:
            if isinstance(item, dict) and "text" in item:
                full_text += item["text"]
            elif isinstance(item, str):
                full_text += item
        return full_text
    return str(content)

def normalize_keywords(text: str):
    """Return a cleaned list of useful keywords from a text string."""
    if not text:
        return []

    cleaned = re.sub(r"[^a-zA-Z0-9\s+\-]", " ", text.lower())
    tokens = cleaned.split()
    tokens = [token for token in tokens if len(token) > 2]
    return tokens


def score_candidate_breakdown(candidate_text: str, job_desc: str, custom_keywords=None):
    """Return a role-aware score breakdown with category totals and final overall score."""
    text = (candidate_text or "").lower()
    jd = (job_desc or "").lower()
    custom_keywords = custom_keywords or []

    job_tokens = normalize_keywords(jd)
    custom_tokens = normalize_keywords(" ".join(custom_keywords))
    keywords = list(dict.fromkeys(job_tokens + custom_tokens))

    if not keywords:
        keywords = [
            "experience", "projects", "leadership", "design", "strategy",
            "analysis", "team", "portfolio", "communication", "client",
            "marketing", "product", "research", "skills"
        ]

    skill_matches = sum(1 for keyword in keywords if keyword in text)
    skills_score = min(skill_matches * 4, 45)

    years = 0
    years_match = re.search(r"\b(\d+)\+?\s*years?\b", text)
    if years_match:
        years = int(years_match.group(1))

    experience_score = min((years * 2) + (5 if "experience" in text else 0), 20)

    leadership_terms = ["lead", "leader", "leadership", "managed", "directed", "mentored", "manager"]
    leadership_score = 10 if any(term in text for term in leadership_terms) else 0

    education_terms = [
        "bachelor", "master", "degree", "diploma", "certification", "university",
        "college", "computer science", "engineering", "design", "marketing", "business"
    ]
    education_score = 10 if any(term in text for term in education_terms) else 0

    project_terms = ["portfolio", "project", "projects", "case study", "worked", "built", "delivered", "client"]
    portfolio_score = 10 if any(term in text for term in project_terms) else 0

    role_fit_score = min(skill_matches * 2, 15)
    seniority_score = min(max(years * 2.5, 0), 25)

    overall = round(
        min(
            skills_score * 0.30 +
            experience_score * 0.20 +
            leadership_score * 0.15 +
            education_score * 0.10 +
            portfolio_score * 0.10 +
            role_fit_score * 0.10 +
            seniority_score * 0.05,
            100.0
        ),
        2,
    )

    return {
        "skills": round(skills_score, 2),
        "experience": round(experience_score, 2),
        "leadership": round(leadership_score, 2),
        "education": round(education_score, 2),
        "portfolio": round(portfolio_score, 2),
        "role_fit": round(role_fit_score, 2),
        "seniority": round(seniority_score, 2),
        "overall": overall,
    }


def score_candidate(candidate_text: str, job_desc: str, custom_keywords=None) -> float:
    """Return the overall role-aware score for a candidate."""
    return score_candidate_breakdown(candidate_text, job_desc, custom_keywords)["overall"]


def rank_candidates(resumes, job_desc, rank_mode="overall", custom_keywords=None):
    """Rank resume dicts by overall fit, seniority, or skills match."""
    ranked = []

    for resume in resumes:
        breakdown = score_candidate_breakdown(resume.get("text", ""), job_desc, custom_keywords)
        entry = {
            "filename": resume.get("filename", "resume.pdf"),
            "text": resume.get("text", ""),
            "score": breakdown["overall"],
            "score_breakdown": breakdown,
            "name": resume.get("filename", "resume.pdf").rsplit(".", 1)[0]
        }
        ranked.append(entry)

    if rank_mode == "seniority":
        ranked.sort(key=lambda item: (item["score_breakdown"]["seniority"], item["score_breakdown"]["overall"]), reverse=True)
    elif rank_mode == "skills":
        ranked.sort(key=lambda item: (item["score_breakdown"]["skills"], item["score_breakdown"]["overall"]), reverse=True)
    else:
        ranked.sort(key=lambda item: (item["score_breakdown"]["overall"], item["score_breakdown"]["skills"]), reverse=True)

    for index, item in enumerate(ranked, start=1):
        item["rank"] = index
        item["summary"] = (
            f"Overall fit {item['score']}/100; skills {item['score_breakdown']['skills']}, "
            f"experience {item['score_breakdown']['experience']}, seniority {item['score_breakdown']['seniority']}."
        )

    return ranked


def safe_json_load(raw_response):
    """Remove code fences and parse JSON safely."""
    clean_json = str(raw_response).strip()
    if "```" in clean_json:
        clean_json = clean_json.split("```")[1]
        if clean_json.lower().startswith("json"):
            clean_json = clean_json[4:]
        clean_json = clean_json.strip()
    return json.loads(clean_json)


def extract_text_and_bytes_from_pdfs(files):
    """Extract full text and keep raw PDF bytes for download."""
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
                "bytes": uploaded_file.getvalue()
            })
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    return extracted_docs


def build_vector_store(resumes):
    """Split each resume into chunks and store them in Chroma using embeddings."""
    documents = []
    for resume in resumes:
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
        chunks = splitter.split_text(resume["text"])
        for chunk in chunks:
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={"filename": resume["filename"]}
                )
            )

    return Chroma.from_documents(documents=documents, embedding=embeddings)


def get_relevant_context(vectorstore, job_desc, k=5):
    """Retrieve the most relevant resume chunks for the job description."""
    if vectorstore is None:
        return ""

    try:
        relevant_docs = vectorstore.similarity_search(job_desc, k=k)
        return "\n\n".join(
            f"[{doc.metadata.get('filename', 'Resume')}]\n{doc.page_content}"
            for doc in relevant_docs
        )
    except Exception:
        return ""


def main():
    st.set_page_config(
        page_title="Resume RAG System",
        layout="wide"
    )

    if "has_started" not in st.session_state:
        st.session_state.has_started = False
    if "ranking_data" not in st.session_state:
        st.session_state.ranking_data = None
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "resumes_context" not in st.session_state:
        st.session_state.resumes_context = ""
    if "multi_chat_history" not in st.session_state:
        st.session_state.multi_chat_history = []
    if "single_chat_history" not in st.session_state:
        st.session_state.single_chat_history = []
    if "single_resume_text" not in st.session_state:
        st.session_state.single_resume_text = ""

    app_mode, uploaded_files, user_query, job_desc, rank_criteria, rank_mode, start_clicked = ui.render_ui()

    if start_clicked:
        if not uploaded_files:
            st.warning("Please upload at least one candidate PDF resume above.")
        else:
            st.session_state.has_started = True

            with st.spinner("Analyzing candidate data with Gemini..."):
                try:
                    resumes = extract_text_and_bytes_from_pdfs(uploaded_files)

                    # Build once and store in session state
                    st.session_state.vectorstore = build_vector_store(resumes)
                    vectorstore = st.session_state.vectorstore

                    if app_mode == "Multi-Candidate Ranking":
                        st.session_state.multi_chat_history = []
                        # Just use the vectorstore already built above:
                        retrieved_context = get_relevant_context(
                            vectorstore, job_desc, k=8
                        )

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

RANKING MODE:
{rank_mode}

RELEVANT RETRIEVED CHUNKS:
{retrieved_context}

RESUMES:
{resumes_formatted}

INSTRUCTIONS:
1. Extract the actual full name of each candidate directly from their resume text.
2. For the 'filename' field, return the exact candidate filename from the headers above.
3. Rank them from best match (#1) to lowest match.
4. For each candidate, provide a concise 1-2 sentence executive assessment of their fit.
5. Include a numeric 'score' between 0 and 100 for each candidate.

Return your response strictly as valid JSON with this exact structure:
{{
  "rankings": [
    {{
      "rank": 1,
      "filename": "file_name.pdf",
      "name": "Full Name",
      "score": 92.0,
      "score_breakdown": {{
        "skills": 95,
        "experience": 90,
        "leadership": 85,
        "overall": 92.0
      }},
      "summary": "1-2 sentence explanation of why this candidate fits."
    }}
  ]
}}
"""
                        response = llm.invoke(prompt)
                        parsed_data = safe_json_load(clean_llm_text(response.content))

                        for candidate in parsed_data.get("rankings", []):
                            target_name = candidate.get("filename", "").lower()
                            for r in resumes:
                                if r["filename"].lower() == target_name:
                                    candidate["cv_bytes"] = r["bytes"]
                                    candidate["cv_filename"] = r["filename"]

                                    # Keep Gemini's score breakdown; only use fallback if Gemini missed it:
                                    if (
                                        "score_breakdown" not in candidate
                                        or not candidate["score_breakdown"]
                                    ):
                                        candidate["score_breakdown"] = {
                                            "skills": candidate.get(
                                                "score", 85
                                            ),
                                            "experience": candidate.get(
                                                "score", 85
                                            ),
                                            "leadership": candidate.get(
                                                "score", 80
                                            ),
                                            "overall": candidate.get(
                                                "score", 85
                                            ),
                                        }
                                    break

                        st.session_state.ranking_data = parsed_data

                    else:
                        st.session_state.single_chat_history = []
                        # Use the first resume already extracted:
                        first_candidate = resumes[0]
                        st.session_state.single_resume_text = first_candidate[
                            "text"
                        ]

                        initial_question = (
                            user_query
                            if user_query
                            else "Provide a comprehensive breakdown of key qualifications, strengths, and role fit."
                        )

                        prompt = f"""
You are an expert recruiter analyzing the following candidate resume.

RESUME CONTENT:
{st.session_state.single_resume_text}

QUESTION:
{initial_question}

Provide an objective, professional, and thorough answer based strictly on the resume.
"""
                        response = llm.invoke(prompt)
                        bot_reply = clean_llm_text(response.content)

                        st.session_state.single_chat_history.append(
                            {"role": "user", "content": initial_question}
                        )
                        st.session_state.single_chat_history.append(
                            {"role": "assistant", "content": bot_reply}
                        )

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    if app_mode == "Multi-Candidate Ranking":
        if not st.session_state.has_started or not st.session_state.ranking_data:
            ui.render_empty_state()
        else:
            st.markdown("### Results & Candidate Rankings")
            ui.render_ranking_cards(st.session_state.ranking_data.get("rankings", []))

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

                # Search for resume parts relevant to the user's question
                relevant_parts = get_relevant_context(
                    st.session_state.vectorstore, user_prompt, k=6
                )

                chat_query = f"""
You are a helpful recruitment assistant.
Answer the user's question using the retrieved resume chunks below.

RELEVANT RESUME CHUNKS:
{relevant_parts}

PREVIOUS CONVERSATION:
{history_text}

USER QUESTION:
{user_prompt}

Answer objectively and factually based strictly on their actual resume experience.
"""
                with st.spinner("Analyzing candidate details..."):
                    reply = llm.invoke(chat_query)
                    bot_reply = clean_llm_text(reply.content)

                st.session_state.multi_chat_history.append({"role": "assistant", "content": bot_reply})
                with st.chat_message("assistant"):
                    st.write(bot_reply)
    else:
        if st.session_state.has_started and st.session_state.single_chat_history:
            st.markdown("### Candidate Analysis & Q&A Chat")
            for message in st.session_state.single_chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

            single_prompt = st.chat_input("Ask a follow-up question about this candidate...")

            if single_prompt:
                st.session_state.single_chat_history.append(
                    {"role": "user", "content": single_prompt}
                )
                with st.chat_message("user"):
                    st.write(single_prompt)

                history_text = ""
                for msg in st.session_state.single_chat_history[:-1]:
                    history_text += f"{msg['role'].upper()}: {msg['content']}\n"

                # Use RAG to get the matching resume chunks
                relevant_parts = get_relevant_context(
                    st.session_state.vectorstore, single_prompt, k=4
                )

                chat_query = f"""
You are an expert recruiter assistant analyzing this candidate resume.

RELEVANT RESUME CHUNKS:
{relevant_parts}

PREVIOUS CONVERSATION:
{history_text}

USER QUESTION:
{single_prompt}

Answer objectively, factually, and thoroughly based strictly on their actual resume content.
"""
                with st.spinner("Reviewing resume..."):
                    reply = llm.invoke(chat_query)
                    bot_reply = clean_llm_text(reply.content)

                st.session_state.single_chat_history.append({"role": "assistant", "content": bot_reply})
                with st.chat_message("assistant"):
                    st.write(bot_reply)


if __name__ == "__main__":
    main()