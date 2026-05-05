import streamlit as st
from ai.generator import generate_resume

st.title("AI Resume Generator")

resume_text = st.text_area("Insert your resume", height=200)
job_text = st.text_area("Insert job description", height=200)

if st.button("Create resume"):
    if resume_text and job_text:
        result = generate_resume(resume_text, job_text)
        st.text_area("Result", value=result, height=300)
    else:
        st.warning("Both fields must be filled in")

