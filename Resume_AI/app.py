import streamlit as st
from ai.generator import generate_resume
import pandas as pd

# ======================
# PAGE CONFIG
# ======================

st.set_page_config(
    page_title="AI Resume Generator",
    layout="wide"
)
st.markdown("""
<style>
div.stButton > button {
    background-color: #2563EB;
    color: white;
    font-size: 22px;
    font-weight: 600;
    padding: 0.9rem 1.5rem;
    border-radius: 12px;
    border: none;
    box-shadow: 0 0 20px rgba(79, 70, 229, 0.4);
}

div.stButton > button:hover {
    background-color: #1D4ED8;
    transform: scale(1.02);
    transition: 0.2s;
}
</style>
""", unsafe_allow_html=True)

# HEADER

st.title("AI Resume Generator")

st.markdown("""
This application demonstrates a complete NLP + GenAI pipeline:

1. Resume Extraction using LLM
2. Job Description Extraction
3. Semantic Skill Matching using Embeddings
4. AI Match Analysis
5. Tailored Resume Generation
""")


# INPUTS 

col1, col2 = st.columns(2)

with col1:
    resume_text = st.text_area(
        " Resume",
        height=300,
        placeholder="Paste the candidate's resume here..."
    )

with col2:
    vacancy_text = st.text_area(
        " Job Description",
        height=300,
        placeholder="Paste the target job description here..."
    )

st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

# OPTIONS

st.subheader("Resume Generation Options")

col1, col2 = st.columns(2)

with col1:

    highlight_skills = st.checkbox(
        "Highlight Technical Skills",
        value=True
    )

    optimize_ats = st.checkbox(
        "Optimize for ATS",
        value=True
    )

with col2:

    add_summary = st.checkbox(
        "Add Professional Summary",
        value=True
    )

    add_temperature = st.checkbox(
        "Use Stronger Professional Tone",
        value=False
    )

# Collect options into dictionary
options = {
    "highlightSkills": highlight_skills,
    "optimizeATS": optimize_ats,
    "addSummary": add_summary,
    "addTemperature": add_temperature
}

# BUTTON
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    run = st.button(
        "Generate Tailored Resume",
        use_container_width=True,
        type="primary"
    )

if run:  #st.button("Generate Tailored Resume"):

    # Validation
    if not resume_text or not vacancy_text:
        st.warning("Please fill in both Resume and Job Description.")
        st.stop()

    # PROCESSING
    with st.status("Running AI pipeline...", expanded=True) as status:

        st.write("Extracting structured resume data...")
        st.write("Extracting job requirements...")
        st.write("Running semantic matching...")
        st.write("Generating AI analysis...")
        st.write("Creating tailored resume...")

        result = generate_resume(
            resume_text,
            vacancy_text,
            options
        )

        status.update(
            label="Pipeline completed",
            state="complete"
        )

    st.success("AI pipeline completed successfully!")


    # PIPELINE OUTPUTS

    st.subheader("AI Pipeline Stages")

    # Resume Extraction
    with st.expander(" Extracted Resume Data"):
        st.json(result.get("resume_data", {}))

    # Job Extraction
    with st.expander(" Extracted Job Data"):
        st.json(result.get("job_data", {}))

    # Semantic Matching

    with st.expander(" Semantic Skill Matching"):

        matching = result.get("matching", [])

        if matching:

            df = pd.DataFrame(matching)

            # CLEAN UP TABLE
            df["score"] = df["score"].round(2)
            df["matched_with"] = df["matched_with"].fillna(" No match")

        
            # SORT BY SCORE
            df = df.sort_values(by="score", ascending=False)

            # color function
            def color_score(val):
                if val >= 0.85:
                    return "background-color: #b6fcb6"
                elif val >= 0.7:
                    return "background-color: #fff3a0"
                else:
                    return "background-color: #ffb6b6"

            # styled_df = df.style.applymap(color_score, subset=["score"])
            styled_df = df.style.map(color_score, subset=["score"])

            # SHOW TABLE
            st.dataframe(styled_df, use_container_width=True)

        else:
            st.info("No matching data available.")

    # AI Explanation
    with st.expander(" AI Match Analysis"):

        explanation = result.get(
            "explanation",
            "No explanation available."
        )

        st.write(explanation)


    # FINAL RESUME

    st.subheader(" Generated Tailored Resume")

    st.text_area(
        label="Generated Resume",
        value=result.get("generatedResume", ""),
        height=500
    )