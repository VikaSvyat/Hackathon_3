
            *************************
            *  AI Resume Generator  *
            *************************

This project is a web application that generates tailored resumes based on a candidate’s existing resume and a target job description.

                Resume + Job Text
                        ↓
                Extraction (LLM)
                        ↓
                Structured JSON
                        ↓
                Embeddings Matching
                        ↓
                AI Match Analysis 
                        ↓
                Resume Generation (LLM)
                        ↓
                Final Output + UI Visualization

The system uses LLM to extract relevant information and rewrite the resume so that it better matches job requirements.

Features

    * Input resume and job description as text
    * Keyword and skill alignment with job requirements
    * Skill Matching Analysis
    * AI-powered resume rewriting
    * Simple web interface (Streamlit)


Tech Stack

    Python
    Streamlit
    LLM 
    python-dotenv


How to run it?

Terminal -> project directory -> streamlit run app.py

How it works?

User inputs resume and job description

LLM extracts and understands key information

Model rewrites resume based on job requirements

Output is a tailored, professional resume
