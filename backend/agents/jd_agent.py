import os
import json
from groq import Groq

from config import load_backend_env

load_backend_env()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_jd_information(job_description: str) -> dict:
    prompt = f"""
You are a Job Description Extraction Agent.

Analyze the job description and return ONLY valid JSON.

Extract required skills, preferred skills, responsibilities, role title, and company name.

Return this exact JSON structure:

{{
  "role_title": "",
  "company_name": "",
  "required_skills": [],
  "preferred_skills": [],
  "responsibilities": [],
  "experience_requirements": []
}}

Job Description:
{job_description}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        raw_text = response.choices[0].message.content.strip()

        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "").strip()

        return json.loads(raw_text)

    except Exception as e:
        return {
            "error": str(e)
        }
