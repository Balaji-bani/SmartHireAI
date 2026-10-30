import re

import csv

from skill_matcher import (
    normalize_text,
    find_skill_evidence,
    calculate_weighted_score,
    classify_skill_evidence,
)

import io

from io import BytesIO



import streamlit as st

import numpy as np

from pypdf import PdfReader

from docx import Document






# ==================================================

# SMART HIRE AI — DAY 6

# Accuracy improvements + recruiter dashboard

# ==================================================



st.set_page_config(

    page_title="SmartHire AI | Recruiter Workspace",

    page_icon="🎯",

    layout="wide",

    initial_sidebar_state="expanded",

)



# Professional styling: native Streamlit components remain accessible.

st.markdown(

    """

    <style>

    /* Improve text contrast across the dashboard */

    [data-testid="stAppViewContainer"] {

        background: #f6f8fc;

        color: #172033;

    }



    [data-testid="stHeader"] {

        background: #f6f8fc;

    }



    [data-testid="stMarkdownContainer"],

    [data-testid="stMarkdownContainer"] p,

    [data-testid="stMarkdownContainer"] li,

    [data-testid="stWidgetLabel"] p,

    [data-testid="stCaptionContainer"] {

        color: #172033;

    }



    h1, h2, h3, h4, label {

        color: #172033;

    }



    [data-testid="stMetric"] {

        background: #ffffff;

        color: #172033;

    }



    [data-testid="stMetricLabel"],

    [data-testid="stMetricValue"] {

        color: #172033;

    }



    [data-testid="stTextInput"] input,

    [data-testid="stTextArea"] textarea {

        background: #ffffff;

        color: #172033;

    }

    .block-container {padding-top: 1.6rem; padding-bottom: 2.5rem; max-width: 1400px;}

    [data-testid="stAppViewContainer"] {background: #f6f8fc;}

    [data-testid="stSidebar"] {background: #eef2f8;}

    .hero {

        padding: 1.35rem 1.5rem; border-radius: 18px;

        background: linear-gradient(120deg, #14233b 0%, #2456a6 100%);

        color: white; margin-bottom: 1.1rem;

    }

    .hero h1 {color: white; margin: 0; font-size: 2rem;}

    .hero p {color: #e5edff; margin: .45rem 0 0 0;}

    .section-note {color: #5b6475; font-size: .92rem;}

    div[data-testid="stMetric"] {

        background: white; border: 1px solid #e5eaf2;

        padding: 14px 16px; border-radius: 14px;

    }

    div[data-testid="stDataFrame"] {

        border: 1px solid #e5eaf2; border-radius: 12px; overflow: hidden;

    }

    </style>

    """,

    unsafe_allow_html=True,

)



st.markdown(

    """

    <div class="hero">

      <h1>🎯 SmartHire AI</h1>

      <p>Recruiter workspace · Evidence-based resume matching · Local AI processing</p>

    </div>

    """,

    unsafe_allow_html=True,

)

st.caption(

    "Decision-support tool only. Scores are indicators for human review, not hiring decisions."

)





# --------------------------------------------------

# SKILL DICTIONARY AND ALIASES

# --------------------------------------------------

# SKILL_ALIASES = {

#     "machine learning": ["ml", "machine-learning"],

#     "artificial intelligence": ["ai"],

#     "natural language processing": ["nlp"],

#     "c plus plus": ["c++"],

#     "javascript": ["js", "java script"],

#     "structured query language": ["sql"],

#     "microsoft excel": ["excel", "ms excel"],

#     "power bi": ["powerbi"],

#     "amazon web services": ["aws"],

#     "continuous integration/continuous delivery": ["ci/cd", "cicd"],

#     "object oriented programming": ["oop", "object-oriented programming"],

#     "scikit-learn": ["sklearn", "scikit learn"],

#     "pytorch": ["torch"],

#     "tensorflow": ["tf"],

#     "natural language generation": ["nlg"],

#     "large language models": ["llm", "llms", "large language model"],

#     "retrieval augmented generation": ["rag", "retrieval-augmented generation"],

#     "version control": ["git", "version-control"],

#     "user interface": ["ui"],

#     "user experience": ["ux"],

#     "microsoft azure": ["azure"],

#     "google cloud platform": ["gcp", "google cloud"],

# }



# # Common phrases are normalized to avoid treating hyphens/punctuation as meaningful.

# def normalize_text(text):

#     text = (text or "").lower()

#     text = text.replace("&", " and ")

#     text = re.sub(r"[\u2010-\u2015]", "-", text)

#     text = re.sub(r"[^a-z0-9+#./\\\-\s]", " ", text)

#     text = re.sub(r"\s+", " ", text)

#     return text.strip()





# def skill_terms(skill):

#     normalized_skill = normalize_text(skill)

#     terms = [normalized_skill]

#     for canonical, aliases in SKILL_ALIASES.items():

#         group = [canonical] + aliases

#         normalized_group = [normalize_text(item) for item in group]

#         if normalized_skill in normalized_group or any(

#             normalized_skill == normalize_text(item) for item in aliases

#         ):

#             terms.extend(normalized_group)

#     # Preserve order and remove duplicates.

#     return list(dict.fromkeys(term for term in terms if term))





# def find_skill_evidence(resume_text, required_skills):

#     """Return matched skills, missing skills, and a short text evidence snippet."""

#     normalized_resume = normalize_text(resume_text)

#     matched, missing, evidence = [], [], {}



#     for skill in sorted(required_skills):

#         found_term = None

#         found_match = None



#         for term in skill_terms(skill):

#             # Boundaries prevent false matches such as 'R' inside 'programmer'.

#             pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"

#             match = re.search(pattern, normalized_resume)

#             if match:

#                 found_term = term

#                 found_match = match

#                 break



#         if found_match:

#             matched.append(skill)

#             start = max(0, found_match.start() - 75)

#             end = min(len(normalized_resume), found_match.end() + 100)

#             evidence[skill] = normalized_resume[start:end].strip()

#         else:

#             missing.append(skill)



#     return matched, missing, evidence





# --------------------------------------------------

# RESUME EXTRACTION

# --------------------------------------------------

def extract_resume_text(uploaded_file):

    file_bytes = uploaded_file.getvalue()

    name = uploaded_file.name.lower()



    if name.endswith(".pdf"):

        reader = PdfReader(BytesIO(file_bytes))

        return "\n".join(page.extract_text() or "" for page in reader.pages)



    if name.endswith(".docx"):

        document = Document(BytesIO(file_bytes))

        parts = [p.text for p in document.paragraphs if p.text.strip()]



        # Include text in tables, which often contain resume skills/experience.

        for table in document.tables:

            for row in table.rows:

                parts.append(" | ".join(cell.text.strip() for cell in row.cells))

        return "\n".join(parts)



    return ""





def split_into_chunks(text, max_words=180, overlap=35):

    """Create overlapping text chunks so a long resume is not encoded as one block."""

    words = re.findall(r"\S+", text or "")

    if not words:

        return []

    chunks = []

    step = max(1, max_words - overlap)

    for start in range(0, len(words), step):

        chunk = " ".join(words[start:start + max_words])

        if chunk:

            chunks.append(chunk)

        if start + max_words >= len(words):

            break

    return chunks





@st.cache_resource

def load_semantic_model():

    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(

        "sentence-transformers/all-MiniLM-L6-v2",

        device="cpu",

    )





def calculate_semantic_similarity(model, job_description, resume_text):

    """

    Compare the job description with resume chunks.

    Returns mean of up to the three most similar chunks, not a probability.

    """

    chunks = split_into_chunks(resume_text)

    if not chunks:

        return None



    embeddings = model.encode(

        [job_description] + chunks,

        normalize_embeddings=True,

        show_progress_bar=False,

    )

    similarities = np.dot(embeddings[1:], embeddings[0])

    top_values = np.sort(similarities)[-min(3, len(similarities)):]

    return round(float(np.mean(top_values)), 4)





# --------------------------------------------------

# SIDEBAR: ROLE SETUP

# --------------------------------------------------

with st.sidebar:

    st.header("Job setup")

    job_title = st.text_input("Job title", value="AI / Data Analyst")

    job_skills_text = st.text_area(

        "Required skills (comma-separated)",

        value="Python, SQL, Machine Learning, Communication",

        height=90,

    )

    critical_skills_text = st.text_input(

        "Critical skills (comma-separated)",

        value="Python, SQL",

    )

    job_description = st.text_area(

        "Job description",

        value=(

            "We are looking for a candidate with experience in Python, SQL, "

            "machine learning, data analysis, problem-solving, and communication. "

            "The candidate should analyze data, develop solutions, and work with a technical team."

        ),

        height=190,

    )

    st.divider()

    st.caption("Local model: all-MiniLM-L6-v2 · CPU inference")

    st.caption("PDF and DOCX files are processed in this app session.")





# --------------------------------------------------

# MAIN WORKSPACE

# --------------------------------------------------

main_left, main_right = st.columns([1.5, 1])

with main_left:

    st.subheader("Candidate intake")

    uploaded_files = st.file_uploader(

        "Upload resumes",

        type=["pdf", "docx"],

        accept_multiple_files=True,

        help="Upload multiple resumes to compare candidates in one analysis.",

    )

with main_right:

    st.subheader("Scoring method")

    st.markdown(

        """

        - **Weighted skill match:** explicit required-skill evidence.

        - **Semantic similarity:** job-description relatedness to resume text chunks.

        - **Combined ranking:** 80% weighted skill match + 20% semantic similarity.
        - **Critical skills:** missing critical skills are flagged for human review.

        """

    )



analyze = st.button("Analyze candidates", type="primary", width="stretch")



if analyze:

    required_skills = {

        normalize_text(skill) for skill in job_skills_text.split(",") if skill.strip()

    }

    critical_skills = {

        normalize_text(skill) for skill in critical_skills_text.split(",") if skill.strip()

    }

    invalid_critical = critical_skills - required_skills



    if not job_title.strip():

        st.warning("Enter a job title.")

    elif not required_skills:

        st.warning("Enter at least one required skill.")

    elif invalid_critical:

        st.warning(

            "Every critical skill must also be in Required Skills. Check: "

            + ", ".join(sorted(invalid_critical))

        )

    elif not job_description.strip():

        st.warning("Enter a job description.")

    elif not uploaded_files:

        st.warning("Upload at least one PDF or DOCX resume.")

    else:

        results = []

        total_points = calculate_weighted_score([],required_skills,critical_skills,)[1]



        # Avoid duplicate filenames in the same upload from overwriting each other visually.

        seen_names = {}

        for uploaded_file in uploaded_files:

            seen_names[uploaded_file.name] = seen_names.get(uploaded_file.name, 0) + 1

            display_name = uploaded_file.name

            if seen_names[uploaded_file.name] > 1:

                display_name = f"{uploaded_file.name} ({seen_names[uploaded_file.name]})"



            try:

                resume_text = extract_resume_text(uploaded_file)

                if not resume_text.strip():

                    st.warning(

                        f"No selectable text found in {uploaded_file.name}. "

                        "Scanned/image-only PDFs need OCR, which is not enabled in this version."

                    )

                    continue



                matched, missing, evidence = find_skill_evidence(

                    resume_text, required_skills

                )

                earned_points, total_points, skill_score = calculate_weighted_score(
                    matched,
                    required_skills,
                    critical_skills,
                )



                results.append({

                    "Candidate": display_name,

                    "Match Score (%)": skill_score,

                    "Matched Skills": matched,

                    "Missing Skills": missing,

                    "Evidence": evidence,

                    "Resume Text": resume_text,

                    "Points Earned": earned_points,

                    "Total Points": total_points,

                    "Semantic Similarity": None,

                })

            except Exception as error:

                st.error(f"Could not process {uploaded_file.name}: {error}")



        if results:

            try:


                with st.status(
                    "Analyzing resumes with local AI...",
                    expanded=False,
                ) as status:
                    status.write("Loading semantic model...")
                    model = load_semantic_model()

                    status.write("Comparing job descriptions with resume sections...")
                    for candidate in results:
                        candidate["Semantic Similarity"] = calculate_semantic_similarity(
                            model, job_description, candidate["Resume Text"]
                        )

                    status.update(
                        label="AI analysis completed!",
                        state="complete",
                        expanded=False,
                    )


            except Exception as error:

                st.error(

                    "Semantic matching could not be completed. Skill matching remains available. "

                    f"Details: {error}"

                )



            # Build a transparent combined ranking score after semantic analysis.
            # Semantic cosine similarity is converted to a 0-100 scale.
            for candidate in results:
                semantic = candidate["Semantic Similarity"]

                if semantic is not None:
                    semantic_percentage = max(0.0, min(1.0, semantic)) * 100
                    candidate["Combined Ranking Score (%)"] = round(
                        0.80 * candidate["Match Score (%)"]
                        + 0.20 * semantic_percentage,
                        2,
                    )
                else:
                    # Keep the app usable if semantic analysis is unavailable.
                    candidate["Combined Ranking Score (%)"] = candidate["Match Score (%)"]

                candidate["Critical Skills Missing"] = sorted(
                    set(candidate["Missing Skills"]) & critical_skills
                )
                candidate["Critical Skills Status"] = (
                    "Review required"
                    if candidate["Critical Skills Missing"]
                    else "No critical skills missing"
                )

            # Candidates missing configured critical skills are placed in a
            # separate review group; they are not automatically rejected.
            results.sort(
                key=lambda item: (
                    bool(item["Critical Skills Missing"]),
                    -item["Combined Ranking Score (%)"],
                    -item["Match Score (%)"],
                    item["Candidate"].casefold(),
                )
            )

            st.session_state["smarthire_day6_results"] = results

            st.session_state["smarthire_day6_job"] = job_title

            st.session_state["smarthire_day6_skills"] = sorted(required_skills)

            st.session_state["smarthire_day6_critical"] = sorted(critical_skills)





# Persist results across normal Streamlit reruns (filters/search don't require re-analysis).

results = st.session_state.get("smarthire_day6_results", [])

if results:

    st.divider()

    st.subheader(f"Recruiter overview · {st.session_state.get('smarthire_day6_job', 'Job')}")

    total_candidates = len(results)

    average_score = round(float(np.mean([x["Match Score (%)"] for x in results])), 1)

    highest_skill_score = max(
        candidate["Match Score (%)"] for candidate in results
    )

    semantic_values = [

        x["Semantic Similarity"] for x in results if x["Semantic Similarity"] is not None

    ]

    average_semantic = round(float(np.mean(semantic_values)), 3) if semantic_values else None



    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Candidates analyzed", total_candidates)

    m2.metric("Average skill match", f"{average_score}%")

    m3.metric("Highest skill match", f"{highest_skill_score}%")

    m4.metric(

        "Average semantic score",

        f"{average_semantic:.3f}" if average_semantic is not None else "Unavailable",

    )



    st.caption(

        "Semantic score is a cosine-similarity measure, not a percentage or probability. "

        "The chunk-based method can help long resumes, but must be evaluated on representative examples."

    )



    tab_overview, tab_compare, tab_evidence, tab_export = st.tabs(

        ["📊 Overview", "⚖️ Compare", "🔎 Skill evidence", "📥 Export"]

    )



    with tab_overview:

        search = st.text_input("Search candidate filename", key="candidate_search")

        min_score, max_score = st.slider(

            "Filter by weighted skill match (%)",

            min_value=0,

            max_value=100,

            value=(0, 100),

        )

        filtered = [

            candidate for candidate in results

            if search.lower() in candidate["Candidate"].lower()

            and min_score <= candidate["Match Score (%)"] <= max_score

        ]



        overview_rows = []

        for rank, candidate in enumerate(results, start=1):

            if candidate not in filtered:

                continue

            overview_rows.append({

                "Rank (combined score)": rank,

                "Candidate": candidate["Candidate"],

                "Combined ranking score (%)": candidate["Combined Ranking Score (%)"],

                "Skill match (%)": candidate["Match Score (%)"],

                "Critical skills status": candidate["Critical Skills Status"],

                "Semantic similarity": (

                    candidate["Semantic Similarity"]

                    if candidate["Semantic Similarity"] is not None else "Unavailable"

                ),

                "Matched skills": ", ".join(candidate["Matched Skills"]) or "None",

                "Missing skills": ", ".join(candidate["Missing Skills"]) or "None",

            })

        st.dataframe(overview_rows, width="stretch", hide_index=True)

        st.subheader("Weighted skill match")

        st.bar_chart(

            {candidate["Candidate"]: candidate["Match Score (%)"] for candidate in filtered},

            y_label="Weighted skill match (%)",

        )

        semantic_filtered = [

            candidate for candidate in filtered

            if candidate["Semantic Similarity"] is not None

        ]

        if semantic_filtered:

            st.subheader("Semantic similarity (cosine)")

            st.bar_chart(

                {

                    candidate["Candidate"]: candidate["Semantic Similarity"]

                    for candidate in semantic_filtered

                },

                y_label="Cosine similarity",

            )



    with tab_compare:

        names = [candidate["Candidate"] for candidate in results]

        selected_names = st.multiselect(

            "Select candidates to compare",

            options=names,

            default=names[:min(3, len(names))],

        )

        selected = [candidate for candidate in results if candidate["Candidate"] in selected_names]

        if selected:

            cols = st.columns(min(len(selected), 3))

            for index, candidate in enumerate(selected):

                with cols[index % len(cols)]:

                    st.markdown(f"#### {candidate['Candidate']}")

                    st.metric("Weighted skill match", f"{candidate['Match Score (%)']}%")
                    st.metric(
                        "Combined ranking score",
                        f"{candidate['Combined Ranking Score (%)']}%",
                    )
                    if candidate["Critical Skills Missing"]:
                        st.warning(
                            "Critical skills requiring review: "
                            + ", ".join(candidate["Critical Skills Missing"])
                        )
                    else:
                        st.success("No configured critical skills are missing.")

                    semantic = candidate["Semantic Similarity"]

                    st.metric(

                        "Semantic similarity",

                        f"{semantic:.4f}" if semantic is not None else "Unavailable",

                    )

                    st.write("**Matched skills**")

                    st.write(", ".join(candidate["Matched Skills"]) or "None")

                    st.write("**Not found in resume text**")

                    st.write(", ".join(candidate["Missing Skills"]) or "None")



    with tab_evidence:
        # Use candidate display names as keys for a direct, consistent lookup.
        # Duplicate uploaded filenames are disambiguated earlier during analysis.
        evidence_candidates = {
            candidate["Candidate"]: candidate
            for candidate in results
        }

        chosen = st.selectbox(
            "Choose a candidate",
            options=list(evidence_candidates.keys()),
            key="skill_evidence_candidate",
        )

        candidate = evidence_candidates[chosen]

        st.markdown(f"### {candidate['Candidate']}")
        st.progress(candidate["Match Score (%)"] / 100)
        st.write(
            f"**Weighted skill match:** {candidate['Match Score (%)']}% "
            f"({candidate['Points Earned']} of {candidate['Total Points']} points)"
        )


        st.markdown("#### Evidence found in resume")
        st.caption(
            "A keyword match indicates that related text was found. "
            "It does not prove skill proficiency. Review the context "
            "before making a recruitment decision."
        )

        if candidate["Evidence"]:
            for skill, snippet in candidate["Evidence"].items():
                with st.expander(f"✓ {skill} — Review evidence"):
                    category = classify_skill_evidence(skill, snippet)

                    st.markdown("**Suggested evidence category**")
                    st.info(category)

                    st.markdown("**Detected text**")
                    st.write(f"“{snippet}”")

                    st.markdown("**Evidence review**")
                    st.write(
                        "Check whether this excerpt demonstrates the "
                        "specific skill, describes a relevant project, "
                        "or merely mentions the skill."
                    )

                    st.markdown("**Suggested evidence categories**")
                    st.write(
                        "- Skill mentioned\n"
                        "- Project evidence\n"
                        "- Professional experience\n"
                        "- Needs manual review"
                    )
                    st.caption(
                        "These categories are suggestions for human review; "
                        "the application has not automatically verified them."
                    )
        else:
            st.write(
                "No required skills were detected by the configured keyword matcher."
            )


        st.markdown("#### Skills not found in resume text")
        if candidate["Missing Skills"]:
            st.write(", ".join(candidate["Missing Skills"]))
            st.caption(
                "A missing keyword is not proof that the candidate lacks the skill. "
                "Check alternative wording and verify through interview or assessment."
            )
        else:
            st.write("All listed skills were detected by the keyword matcher.")

        with st.expander("View extracted resume text"):
            st.text(candidate["Resume Text"])

    with tab_export:

        export_rows = []

        for rank, candidate in enumerate(results, start=1):

            export_rows.append({

                "Rank (combined score)": rank,

                "Candidate": candidate["Candidate"],

                "Job title": st.session_state.get("smarthire_day6_job", ""),

                "Combined ranking score (%)": candidate["Combined Ranking Score (%)"],

                "Weighted skill match (%)": candidate["Match Score (%)"],

                "Critical skills status": candidate["Critical Skills Status"],

                "Critical skills missing": ", ".join(candidate["Critical Skills Missing"]),

                "Semantic similarity (cosine)": (

                    candidate["Semantic Similarity"]

                    if candidate["Semantic Similarity"] is not None else ""

                ),

                "Matched skills": ", ".join(candidate["Matched Skills"]),

                "Missing skills": ", ".join(candidate["Missing Skills"]),

                "Points earned": candidate["Points Earned"],

                "Total points": candidate["Total Points"],

            })

        csv_buffer = io.StringIO()

        writer = csv.DictWriter(csv_buffer, fieldnames=list(export_rows[0].keys()))

        writer.writeheader()

        writer.writerows(export_rows)

        st.download_button(

            "Download candidate report (CSV)",

            data=("\ufeff" + csv_buffer.getvalue()).encode("utf-8"),

            file_name="smarthire_day6_candidate_report.csv",

            mime="text/csv",

            type="primary",

        )

        st.caption("The report excludes full resume text to reduce unnecessary personal-data exposure.")



else:

    st.info("Configure the job in the sidebar, upload resumes, and select **Analyze candidates** to begin.")

    st.markdown(

        """

        **Accuracy improvements in this version**

        - DOCX tables are included in text extraction.

        - Skill matching supports a configurable alias dictionary and shows text evidence.

        - Semantic similarity compares the job description against overlapping resume chunks.

        - Skill score and semantic similarity remain separate to avoid an unvalidated combined score.

        """

    )
