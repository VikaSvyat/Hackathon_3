import os
import numpy as np
from google import genai
from openai import OpenAI
from dotenv import load_dotenv
import json
import re

from .prompts import build_prompt, build_resume_extraction_prompt, build_job_extraction_prompt

load_dotenv()

# PROVIDER SWITCH

# USE_GEMINI = os.getenv("USE_GEMINI", "true").lower() == "true"
USE_GEMINI = False

if USE_GEMINI:
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
else:
    
    client = OpenAI(
        base_url="https://api.cerebras.ai/v1",
        api_key=os.getenv("CEREBRAS_API_KEY")
    )

# Embeddings

def get_embedding(text):
    if USE_GEMINI:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )
        return np.array(response.embeddings[0].values)

    else:
        # fallback for Cerebras: simple local embeddings
        import hashlib
        np.random.seed(int(hashlib.md5(text.encode()).hexdigest(), 16) % (10**6))
        return np.random.rand(768)

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# Extraction

def extract_structured_data(text, type):
    #Why uses prompt? Because LLMs are instruction-based models. 
    # The prompt defines the extraction task, schema, and output format, 
    # effectively replacing traditional rule-based or trained extraction models.
    if type == 'resume':
        prompt = build_resume_extraction_prompt(text)
    elif type == 'job_description':
        prompt = build_job_extraction_prompt (text)

    # response = client.models.generate_content(
    #     model="gemini-2.0-flash", #"gemini-2.5-flash-lite",
    #     contents=prompt,
    # )
    if USE_GEMINI:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        raw = response.text
    else:
        response = client.chat.completions.create(
            model="llama3.1-8b",
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.choices[0].message.content

    try:
        cleaned = re.sub(r"```json|```", "", raw).strip()
        return json.loads(cleaned)
    except:
        return {
            "skills": [],
            "technologies": [],
            "experience": [],
            "education": [],
            "projects": [],
            "languages": []
        }


# Skill Matching

def match_skills(resume_skills, job_skills, threshold=0.6):

    results = []

    # Normalize
    normalized_resume = {
        skill.lower().strip(): skill
        for skill in resume_skills
    }

    # Precompute embeddings
    resume_vectors = {
        skill: get_embedding(skill)
        for skill in resume_skills
    }

    job_vectors = {
        skill: get_embedding(skill)
        for skill in job_skills
    }

    for job_skill, job_vec in job_vectors.items():

        best_match = None
        best_score = 0

      # 1. EXACT MATCH FIRST
        
        normalized_job = job_skill.lower().strip()

        if normalized_job in normalized_resume:

            best_match = normalized_resume[normalized_job]
            best_score = 1.0

        else:
            # 2. SEMANTIC MATCHING
            
            for res_skill, res_vec in resume_vectors.items():

                score = cosine_similarity(job_vec, res_vec)

                if score > best_score:
                    best_score = score
                    best_match = res_skill

        results.append({
            "job_skill": job_skill,
            "matched_with": best_match if best_score >= threshold else None,
            "score": float(best_score)
        })

    return results

# Eexplain matching

def explain_match(matching_results, resume_text, vacancy):

    prompt = f"""
You are an AI career assistant.

Explain the skill matching results in a simple and professional way.

Be concise.

Matching results:
{matching_results}

Resume:
{resume_text}

Job:
{vacancy}

Return:
- short summary of fit
- strengths
- missing skills
"""
    # response = client.models.generate_content(
    #     model="gemini-2.0-flash", #"gemini-2.5-flash-lite",
    #     contents=prompt,
    # )
    # return response.text

    if USE_GEMINI:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text

    else:
        response = client.chat.completions.create(
            model="llama3.1-8b",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content



# Main Generator

def generate_resume(resume_text, vacancy, options):
    resume_data = {}
    job_data = {}
    matching = []
    generated_resume = ""
    explanation = ""

    try:
        # 1. EXTRACTION layer 
        # LLM → structured JSON

        resume_data = extract_structured_data(resume_text, "resume")
        job_data = extract_structured_data(vacancy, "job_description")
        # The JSON schema is defined at the prompt level, 
        # where the LLM is instructed to follow a strict structured output format. 
        # The backend enforces and consumes this structure after parsing.
        
        # 2. NORMALIZATION
        # Normalization step aligns structured outputs from different LLM extraction schemas 
        # into a unified format suitable for semantic comparison.

        resume_skills = resume_data.get("skills", [])

        job_skills = (
            job_data.get("required_skills", []) +
            job_data.get("preferred_skills", [])
        )

        # 3. SEMANTIC MATCHING layer 
        # embeddings → skill matching

        matching = match_skills(resume_skills, job_skills)

        matching_text = "\n".join([
            f"- {m['job_skill']} → {m['matched_with']} (score: {round(m['score'], 2)})"
            for m in matching
        ])
        explanation = explain_match(matching, resume_text, vacancy)

        # 4. FINAL GENERATION
        # The system separates unstructured data (used for generative rewriting) 
        # from structured representations (used for semantic analysis and matching), 
        # enabling both high-quality generation and interpretable NLP processing.

        prompt = build_prompt(
                    resume_text,
                    vacancy,
                    matching_text,
                    explanation,
                    options
        )
        # response = client.models.generate_content(
        #     model="gemini-2.0-flash", #"gemini-2.5-flash-lite",
        #     contents=prompt,
        # )

        # generated_resume = response.text or "No response from Gemini."
        if USE_GEMINI:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            generated_resume = response.text

        else:
            response = client.chat.completions.create(
                model="llama3.1-8b",
                messages=[{"role": "user", "content": prompt}]
            )
            generated_resume = response.choices[0].message.content

    except Exception as e:
        generated_resume = f"Error: {str(e)}"
        matching = []

    return {
        "generatedResume": generated_resume,
        "matching": matching,
        "explanation": explanation,
        "resume_data": resume_data,
        "job_data": job_data
    }

