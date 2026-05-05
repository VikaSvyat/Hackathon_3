import os

from google import genai
from ai.prompts import build_prompt
from dotenv import load_dotenv

load_dotenv()


def generate_resume():
    
    prompt = build_prompt("extracted_text", "vacancy", '''{parsed_options}''')

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))   
    
    try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
            )
            generated_resume = response.text if response.text else "No response from Gemini."
    
    except Exception as e:
            generated_resume = f"Gemini error: {str(e)}"

    return {
            "fileName": 'filename',
            "generatedResume": generated_resume,
        }