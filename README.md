# Resume RAG System

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-5B21B6?style=for-the-badge)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

An AI-powered resume intelligence and ranking platform that uses PDF extraction, Gemini embeddings, ChromaDB vector retrieval, and Gemini-generated analysis to evaluate candidate resumes against job requirements.

The application provides two analysis workflows:

- **Single Candidate Analysis** — Upload one resume, receive an objective recruiter-style evaluation, and ask follow-up questions.
- **Multi-Candidate Ranking** — Upload multiple resumes, rank candidates against a target role, inspect score breakdowns, download original CVs, and chat with the recruiter assistant about the results.

---

## Overview

**Resume RAG System** is a Streamlit application built around a retrieval-augmented generation workflow for resume analysis.

The application:

1. Accepts one or more candidate PDF resumes.
2. Extracts their text with `PyPDFLoader`.
3. Splits resume content into overlapping chunks.
4. Creates Gemini embeddings for the chunks.
5. Stores the embedded documents in ChromaDB.
6. Retrieves the most relevant resume sections for a job description or recruiter question.
7. Uses Gemini to generate structured candidate analysis and ranking output.
8. Maintains chat history in Streamlit session state for follow-up questions.

---

## Key Features

### Single Candidate Analysis

Upload one candidate PDF and ask a targeted question such as:

```text
Summarize the top three technical strengths and verify leadership experience.
```

The application uses the resume content to provide an objective, professional, and thorough answer based strictly on the candidate's resume.

After the initial analysis, the recruiter can continue asking follow-up questions using the candidate-specific chat interface.

### Multi-Candidate Ranking

Upload multiple candidate PDF resumes and provide:

- Target job description or role requirements
- Custom ranking criteria
- Must-have skills or keywords
- Ranking priority

Available ranking priorities:

- **Best overall fit**
- **Most senior**
- **Strongest skills match**

The application returns ranked candidate cards containing:

- Candidate name
- Candidate rank
- Overall score
- Skills score
- Experience score
- Leadership score
- Executive fit summary
- Downloadable original CV

### Retrieval-Augmented Recruiter Chat

The application retrieves relevant resume chunks before answering follow-up questions.

For multi-candidate mode, the recruiter can ask questions such as:

```text
Compare Sarah and Ahmad's experience.
```

For single-candidate mode, the recruiter can ask questions such as:

```text
What evidence is there of project leadership?
```

The assistant is instructed to answer objectively and factually based strictly on the retrieved resume content.

### Role-Aware Candidate Scoring

The system includes a deterministic scoring engine that produces a score breakdown across several categories:

- Skills
- Experience
- Leadership
- Education
- Portfolio
- Role fit
- Seniority
- Overall score

The scoring logic can be used independently through functions such as `score_candidate`, `score_candidate_breakdown`, and `rank_candidates`.

### Original CV Downloads

The application preserves the uploaded PDF bytes in memory and attaches them to ranking results so users can download the original CV directly from each candidate card.

### Clean Streamlit UI

The interface includes:

- Wide-layout Streamlit application
- Single-candidate and multi-candidate mode selector
- Custom CSS styling
- Responsive ranking cards
- Rank badges with gradient styling
- Upload controls for PDF resumes
- Interactive chat messages
- Empty states before analysis begins
- Download buttons for candidate CVs

---

## Architecture

```text
                        [Upload PDF Resume(s)]
                                 │
                     [Extract Text (PyPDFLoader)]
                                 │
                       [Split into Chunks]
                                 │
                   [Create Gemini Embeddings]
                                 │
                        [Store in ChromaDB]
                                 │
                         < Analysis Mode >
                               ╱   ╲
           ┌──────────────────┘     └──────────────────┐
           ▼                                           ▼
   [Single Candidate]                          [Multi-Candidate]
           │                                           │
  [Initial Resume Analysis]                 [Retrieve Chunks (Job Req)]
           │                                           │
    ┌──────┴───────────────┐                  [Gemini Ranking JSON]
    │  Candidate Q&A Chat  │                           │
    │  ┌─────────────────┐ │                 [Ranked Candidate Cards]
    │  │ Retrieve Chunks │ │                           │
    │  │       │         │ │                 ┌─────────┴──────────────┐
    │  │ Gemini Response │ │                 │ Recruiter Comparison   │
    │  └─────────────────┘ │                 │ Chat (RAG Loop)        │
    └──────────────────────┘                 └────────────────────────┘
```

### Retrieval-Augmented Generation Flow

```text
PDF files
   ↓
PyPDFLoader
   ↓
Full resume text
   ↓
RecursiveCharacterTextSplitter
   ↓
Resume chunks with filename metadata
   ↓
Google Gemini embeddings
   ↓
ChromaDB vector store
   ↓
Similarity search
   ↓
Relevant resume context
   ↓
Google Gemini analysis or recruiter chat response
```

---

## Project Structure

```text
.
├── app.py          # RAG pipeline, scoring logic, ranking, analysis, and chat flow
├── ui.py           # Streamlit layout, styling, controls, ranking cards, and empty state
├── test_app.py     # Pytest coverage for scoring, ranking, and JSON parsing
├── LICENSE         # MIT License
└── .gitignore      # Virtual environments, secrets, ChromaDB, and test caches
```

The supplied archive also contains local runtime artifacts such as `venv/`, `chroma_db/`, `chroma_db_test/`, and `.pytest_cache/`. These should remain local and should not be committed to a public repository.

---

## Technology Stack

| Technology | Purpose |
| :--- | :--- |
| Python | Application logic and scoring engine |
| Streamlit | Interactive web interface |
| LangChain | Document loading, splitting, embeddings, and model integration |
| `PyPDFLoader` | PDF text extraction |
| `RecursiveCharacterTextSplitter` | Splitting resume text into retrieval chunks |
| Google Gemini Embeddings | Converting resume chunks into vectors |
| ChromaDB | Local vector storage and similarity search |
| Google Gemini Chat Model | Resume analysis, candidate ranking, and recruiter chat |
| Pydantic-backed LangChain components | Structured AI integration through the LangChain ecosystem |
| Pytest | Automated tests for local scoring and ranking behavior |

---

## Data Flow by Feature

### Single Candidate Analysis

1. The user selects **Single Candidate Analysis**.
2. The user uploads one or more PDFs; the first uploaded resume is used for the initial candidate analysis.
3. The PDF is written temporarily and loaded with `PyPDFLoader`.
4. The extracted resume text is stored in Streamlit session state.
5. The user provides a focus area or specific question.
6. Gemini generates an objective response based on the resume.
7. The response is displayed in the candidate analysis chat.
8. Follow-up questions trigger ChromaDB similarity search before Gemini generates the next response.

### Multi-Candidate Ranking

1. The user selects **Multi-Candidate Ranking**.
2. The user uploads multiple candidate PDF resumes.
3. The user enters target job requirements and custom ranking criteria.
4. The user chooses an overall, seniority, or skills ranking priority.
5. Each resume is extracted, chunked, embedded, and stored in ChromaDB.
6. The system retrieves relevant resume chunks using the job description.
7. Gemini receives the job requirements, ranking criteria, ranking mode, retrieved chunks, and full resume text.
8. Gemini returns rankings as JSON.
9. The application safely parses the JSON response.
10. Each candidate is matched back to the uploaded PDF so the original CV can be downloaded.
11. The ranking cards and recruiter comparison chat are displayed.

---

## Embeddings and Vector Store

### Embedding Model

The project initializes Gemini embeddings with:

```python
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)
```

### Text Chunking

Each resume is split with:

```python
RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120
)
```

Each chunk is stored as a LangChain `Document` with the source filename in its metadata:

```python
Document(
    page_content=chunk,
    metadata={"filename": resume["filename"]}
)
```

### Similarity Retrieval

The helper `get_relevant_context` searches the ChromaDB vector store and returns the most relevant chunks with their source filenames.

The application uses different retrieval sizes for different workflows:

- Multi-candidate initial ranking: `k=8`
- Multi-candidate recruiter chat: `k=6`
- Single-candidate follow-up chat: `k=4`

---

## Candidate Scoring Engine

The scoring engine is implemented in `app.py` and can be used independently of the Streamlit UI.

### Keyword Normalization

`normalize_keywords`:

- Converts text to lowercase
- Removes most punctuation
- Preserves alphanumeric tokens, plus signs, and hyphens
- Removes tokens with two or fewer characters

### Score Categories

The role-aware score breakdown includes:

| Category | Description |
| :--- | :--- |
| `skills` | Matches normalized job-description and custom-keyword terms against the resume |
| `experience` | Uses detected years of experience and the presence of experience-related language |
| `leadership` | Checks leadership-related terms such as lead, managed, directed, and mentored |
| `education` | Checks education-related terms such as bachelor, master, degree, university, and engineering |
| `portfolio` | Checks terms such as portfolio, projects, case study, built, delivered, and client |
| `role_fit` | Derives an additional role-alignment score from keyword matches |
| `seniority` | Derives a score from detected years of experience |
| `overall` | Weighted combination of the category scores, capped at 100 |

### Score Calculation

The weighted overall score is calculated using:

```text
skills       × 0.30
experience   × 0.20
leadership   × 0.15
education    × 0.10
portfolio    × 0.10
role_fit     × 0.10
seniority    × 0.05
```

The final score is rounded to two decimal places and capped at `100.0`.

### Ranking Modes

`rank_candidates` supports three ranking modes:

```python
rank_candidates(resumes, job_desc, rank_mode="overall")
rank_candidates(resumes, job_desc, rank_mode="seniority")
rank_candidates(resumes, job_desc, rank_mode="skills")
```

The sorting behavior is:

- `overall` — overall score, then skills score
- `seniority` — seniority score, then overall score
- `skills` — skills score, then overall score

---

## Gemini Ranking Output

For multi-candidate ranking, the application instructs Gemini to return valid JSON using this structure:

```json
{
  "rankings": [
    {
      "rank": 1,
      "filename": "file_name.pdf",
      "name": "Full Name",
      "score": 92.0,
      "score_breakdown": {
        "skills": 95,
        "experience": 90,
        "leadership": 85,
        "overall": 92.0
      },
      "summary": "1-2 sentence explanation of why this candidate fits."
    }
  ]
}
```

The helper `safe_json_load` removes Markdown code fences when necessary before parsing the response with Python's JSON parser.

If Gemini does not provide a `score_breakdown`, the application creates a fallback breakdown from the candidate's score.

---

## Prerequisites

Install the following before running the application:

- Python 3.10+
- A Google API key with access to the configured Gemini models
- Internet access for Gemini API calls
- A modern web browser

The application uses the following configured models:

```text
Embedding model: models/gemini-embedding-001
Chat model: gemini-3.8-flash
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/shathahsaleem/resume-rag-system
cd resume-rag-system
```

### 2. Create and activate a virtual environment

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

The project does not currently include a `requirements.txt` file. Install the imported application and testing dependencies with:

```bash
pip install streamlit langchain-community langchain-text-splitters langchain-google-genai langchain-chroma langchain-core python-dotenv pypdf pytest
```

### 4. Configure the Google API key

Create a local `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

The application loads the key with `python-dotenv`.

---

## How to Run

Start the Streamlit application from the project root:

```bash
streamlit run app.py
```

Streamlit will display a local URL, usually:

```text
http://localhost:8501
```

### Single Candidate Analysis

1. Open the Streamlit URL.
2. Select **Single Candidate Analysis**.
3. Upload a candidate PDF resume.
4. Enter a focus area or specific question.
5. Click **Start Analysis**.
6. Review the initial response.
7. Ask follow-up questions in the candidate analysis chat.

### Multi-Candidate Ranking

1. Select **Multi-Candidate Ranking**.
2. Upload multiple candidate PDF resumes.
3. Paste the target job description or role requirements.
4. Enter custom ranking criteria.
5. Add must-have skills or keywords.
6. Select a ranking priority.
7. Click **Start Ranking**.
8. Review the ranked candidate cards.
9. Download original CVs when needed.
10. Ask comparison questions in the recruiter chat.

---

## Running Tests

Run the automated tests with:

```bash
pytest
```

The current test suite covers:

- Technical resume scoring
- Non-technical/design resume scoring
- Score breakdown categories
- Seniority-based candidate ranking
- JSON parsing from Markdown code blocks

To run the test file directly:

```bash
pytest test_app.py -v
```

---

## Example Usage

### Programmatic Scoring

The scoring functions can be imported independently:

```python
from app import score_candidate, score_candidate_breakdown

resume_text = "Python, SQL, AWS, 5 years experience in ML and leadership"
job_description = "Python SQL AWS ML leadership"

score = score_candidate(resume_text, job_description)
breakdown = score_candidate_breakdown(resume_text, job_description)

print(score)
print(breakdown)
```

### Programmatic Candidate Ranking

```python
from app import rank_candidates

resumes = [
    {
        "filename": "junior.pdf",
        "text": "Junior designer with 2 years of experience in branding and illustration",
    },
    {
        "filename": "senior.pdf",
        "text": "Senior design lead with 10 years of experience in branding, art direction, leadership, and client management",
    },
]

ranked = rank_candidates(
    resumes,
    "Senior visual designer",
    rank_mode="seniority",
)

for candidate in ranked:
    print(candidate["rank"], candidate["filename"], candidate["score"])
```

---

## Session State

The Streamlit application maintains the following state values:

| State key | Purpose |
| :--- | :--- |
| `has_started` | Tracks whether analysis has begun |
| `ranking_data` | Stores multi-candidate ranking output |
| `vectorstore` | Stores the active ChromaDB vector store |
| `resumes_context` | Stores formatted resume text for ranking context |
| `multi_chat_history` | Stores recruiter comparison chat messages |
| `single_chat_history` | Stores single-candidate chat messages |
| `single_resume_text` | Stores the active single-candidate resume text |
| `current_mode` | Detects mode changes and resets relevant state |

Changing analysis mode resets the mode-specific state and clears previous results and chat history.

---

## Error Handling

The application includes several defensive behaviors:

- Displays a warning when the user tries to start without uploading a PDF.
- Uses temporary files for PDF parsing and removes them afterward.
- Catches application errors and displays them through Streamlit.
- Returns an empty retrieval context when vector-store search fails.
- Cleans Gemini responses that may arrive as strings, lists, or dictionaries with text fields.
- Removes Markdown code fences before parsing JSON ranking responses.
- Uses score-breakdown fallbacks when Gemini omits the requested breakdown.

---

## License

This project is open-source software licensed under the **MIT License**.

Copyright (c) 2026 Shathah Saleem.

---
