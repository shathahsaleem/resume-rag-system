import streamlit as st
import streamlit.components.v1 as components


def apply_custom_css():
    st.markdown("""
        <style>
        .stApp {
            background-color: #f5f2eb;
            color: #0f0f0f;
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        }

        section[data-testid="stSidebar"] {
            display: none;
        }

        .pro-card {
            background: #faf8f5;
            border: 1px solid #d6cebe;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(15, 15, 15, 0.03);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #faf8f5 !important;
            border: 1px solid #d6cebe !important;
            border-radius: 16px !important;
            padding: 20px !important;
            margin-bottom: 20px !important;
            box-shadow: 0 4px 12px rgba(15, 15, 15, 0.03) !important;
        }

  
        div[data-testid="stChatMessage"] {
            background-color: #faf8f5 !important;
            border: 1px solid #d6cebe !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            margin-bottom: 10px !important;
        }

        iframe {
            border: none !important;
            background: transparent !important;
        }

        div[data-testid="stVerticalBlock"] > div:empty,
        div[data-testid="element-container"]:empty {
            display: none !important;
        }

        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp span, .stApp label, .stApp div {
            color: #0f0f0f !important;
        }

        .stTextInput input, .stTextArea textarea, .stSelectbox select, div[data-baseweb="select"] {
            background-color: #ffffff !important;
            color: #0f0f0f !important;
            border: 1px solid #d6cebe !important;
            border-radius: 8px !important;
        }

        [data-testid="stFileUploader"], 
        [data-testid="stFileUploadDropzone"], 
        section[data-testid="stFileUploader"] > div,
        div[data-testid="stFileUploadDropzone"] {
            background-color: #ffffff !important;
            border: 1px dashed #d6cebe !important;
            border-radius: 12px !important;
        }

        [data-testid="stFileUploadDropzone"] * {
            color: #0f0f0f !important;
        }

        .instruction-card {
            background: #eae5d9;
            border: 1px solid #c8beab;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 20px;
            color: #0f0f0f;
            font-size: 0.95rem;
            line-height: 1.5;
        }


        .stButton>button, .stDownloadButton>button {
            background-color: #a3957d !important;
            color: #0f0f0f !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-weight: 700 !important;
            transition: background-color 0.2s ease !important;
        }

        .stButton>button:hover, .stDownloadButton>button:hover {
            background-color: #8c7f68 !important;
            color: #0f0f0f !important;
        }

        .empty-state-box {
            background-color: #a3957d;
            border-radius: 12px;
            padding: 16px 20px;
            margin-top: 10px;
            margin-bottom: 20px;
        }

        .empty-state-box p {
            color: #0f0f0f !important;
            font-weight: 600;
            margin: 0;
        }
        </style>
    """, unsafe_allow_html=True)



def get_rank_badge_style(rank_index, total_candidates):
    if total_candidates <= 1:
        return "background-color: #756752; color: #ffffff;"
    
    factor = rank_index / (total_candidates - 1)

    r = int(117 + (226 - 117) * factor)
    g = int(103 + (218 - 103) * factor)
    b = int(82 + (205 - 82) * factor)

    bg_hex = f"#{r:02x}{g:02x}{b:02x}"
    text_color = "#ffffff" if factor < 0.6 else "#26211a"

    return f"background-color: {bg_hex}; color: {text_color} !important;"



def render_header():
    st.markdown("""
        <div class="pro-card" style="margin-bottom: 12px;">
            <h1 style="margin-top: 0; margin-bottom: 6px; font-size: 2.2rem; font-weight: 800;">
                AI Resume Intelligence & Ranking Platform
            </h1>
            <p style="margin: 0; font-size: 1rem; opacity: 0.8;">
                Vector-backed retrieval powered by Gemini & ChromaDB
            </p>
        </div>
    """, unsafe_allow_html=True)

    hero_wave_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; overflow: hidden; background: transparent; }
            canvas { display: block; width: 100%; height: 110px; border-radius: 12px; }
        </style>
    </head>
    <body>
        <canvas id="waveCanvas"></canvas>
        <script>
            const canvas = document.getElementById('waveCanvas');
            const ctx = canvas.getContext('2d');

            function resize() {
                canvas.width = window.innerWidth;
                canvas.height = 110;
            }
            resize();
            window.addEventListener('resize', resize);

            let step = 0;
            let mouse = { x: canvas.width / 2, y: canvas.height / 2 };

            window.addEventListener('mousemove', (e) => {
                const rect = canvas.getBoundingClientRect();
                mouse.x = e.clientX - rect.left;
                mouse.y = e.clientY - rect.top;
            });

            function drawWave(color, speed, height, frequency) {
                ctx.beginPath();
                ctx.moveTo(0, canvas.height / 2);

                for (let x = 0; x < canvas.width; x += 4) {
                    const dist = Math.abs(x - mouse.x);
                    const mouseEffect = Math.max(0, (160 - dist) / 160) * 22;

                    const y = Math.sin(x * frequency + step * speed) * (height + mouseEffect) + canvas.height / 2;
                    ctx.lineTo(x, y);
                }

                ctx.strokeStyle = color;
                ctx.lineWidth = 1.8;
                ctx.stroke();
            }

            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                drawWave('rgba(120, 105, 85, 0.7)', 0.03, 10, 0.009);
                drawWave('rgba(160, 142, 118, 0.5)', 0.02, 16, 0.007);
                drawWave('rgba(90, 78, 62, 0.4)', 0.04, 8, 0.012);
                step += 1;
                requestAnimationFrame(animate);
            }
            animate();
        </script>
    </body>
    </html>
    """
    components.html(hero_wave_code, height=120)


def render_ui():
    apply_custom_css()
    render_header()

    app_mode = st.radio(
        "Select Analysis Mode",
        ["Single Candidate Analysis", "Multi-Candidate Ranking"],
        horizontal=True
    )

    if "current_mode" not in st.session_state:
        st.session_state["current_mode"] = app_mode
    elif st.session_state["current_mode"] != app_mode:
        st.session_state["has_started"] = False
        st.session_state["ranking_data"] = None
        st.session_state["multi_chat_history"] = []
        st.session_state["single_chat_history"] = []
        st.session_state["single_resume_text"] = ""
        st.session_state["current_mode"] = app_mode

    instructions = {
        "Single Candidate Analysis": (
            "💡 Single Candidate Guidance: Upload one candidate resume PDF below. "
            "Once processed, you can ask direct questions to analyze specific skills, "
            "work history, or role fit."
        ),
        "Multi-Candidate Ranking": (
            "💡 Multi-Candidate Guidance: Upload multiple resume PDFs below. "
            "Specify your target requirements and custom ranking criteria to view "
            "the top candidate matches."
        )
    }

    st.markdown(f"""
        <div class="instruction-card">
            {instructions[app_mode]}
        </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload Candidate PDF Resumes", 
        type=["pdf"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    user_query = ""
    job_desc = ""
    rank_criteria = ""
    start_clicked = False

    with st.container(border=True):
        if app_mode == "Single Candidate Analysis":
            st.markdown("### Analysis Parameters")
            user_query = st.text_input(
                "Focus Area / Specific Question",
                placeholder="e.g., Summarize top 3 technical strengths or verify leadership experience..."
            )
            if st.button("Start Analysis"):
                start_clicked = True

        else:
            st.markdown("### Ranking Criteria")
            col_a, col_b = st.columns(2)
            with col_a:
                job_desc = st.text_area(
                    "Target Job Description / Role Requirements",
                    placeholder="Paste job description or key requirements here...",
                    height=130
                )
            with col_b:
                rank_criteria = st.text_input(
                    "Rank Based On",
                    placeholder="e.g., Specific skills, leadership experience, project scale..."
                )
                must_have_skills = st.text_input(
                    "Must-Have Skills / Keywords",
                    placeholder="e.g., Python, Vector Databases, LangChain..."
                )
            
            if st.button("Start Ranking"):
                start_clicked = True

    return app_mode, uploaded_files, user_query, job_desc, rank_criteria, start_clicked



def render_ranking_cards(rankings_list):
    """Draws ranked cards with dark-to-light beige numbers and a Download CV button."""
    total_count = len(rankings_list)
    with st.container(border=True):
        for i, candidate in enumerate(rankings_list):
            rank_num = candidate.get("rank", i + 1)
            real_name = candidate.get("name", "Unknown Candidate")
            summary = candidate.get("summary", "No details provided.")
            pdf_bytes = candidate.get("cv_bytes", None)
            pdf_filename = candidate.get("cv_filename", f"resume_{i+1}.pdf")
            
            badge_style = get_rank_badge_style(i, total_count)
            
            col_rank, col_info, col_action = st.columns([1, 5, 2])
            
            with col_rank:
                st.markdown(f"""
                    <div style="
                        {badge_style}
                        border-radius: 12px; 
                        padding: 14px; 
                        text-align: center; 
                        font-weight: 800; 
                        font-size: 1.4rem;">
                        #{rank_num}
                    </div>
                """, unsafe_allow_html=True)
                
            with col_info:
                st.markdown(f"**Candidate:** {real_name}")
                st.markdown(f"**Evaluation:** {summary}")
                
            with col_action:
                if pdf_bytes:
                    st.download_button(
                        label="Download CV",
                        data=pdf_bytes,
                        file_name=pdf_filename,
                        mime="application/pdf",
                        key=f"download_cv_{i}"
                    )
            
            if i < total_count - 1:
                st.markdown("<hr style='border: 0.5px solid #d6cebe; margin: 12px 0;'>", unsafe_allow_html=True)


def render_empty_state():
    st.markdown("### Results & Candidate Rankings")
    st.markdown("""
        <div class="empty-state-box">
            <p>Nothing to show here yet. Upload CVs, fill in your criteria, and click 'Start' above to view results.</p>
        </div>
    """, unsafe_allow_html=True)