import os
import json
from groq import Groq

from config import load_backend_env

load_backend_env()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_resume_information(resume_text: str) -> dict:
    try:
        prompt = f"""
You are a Resume Extraction Agent.

Analyze the resume and extract BOTH explicitly listed skills AND inferred skills from project descriptions.

For each project, extract technologies used AND inferred_skills (skills demonstrated by the project):
- RAG, semantic search, retrieval systems → infer "Retrieval-Augmented Generation", "Semantic Search"
- Vector databases (pgvector, Pinecone, Weaviate) → infer "Vector Databases", "Embeddings"
- LLMs, language models, GPT, Claude → infer "Large Language Models"
- Data structures in descriptions → infer "Data Structures and Algorithms"
- FastAPI, REST endpoints → infer "REST APIs"
- PostgreSQL, databases → infer "SQL", "Database Design"
- Authentication, JWT → infer "Authentication & Security"
- Monitoring, logging, observability → infer "Monitoring and Observability"
- CI/CD, Docker, deployment → infer "DevOps", "Deployment"
- Optimization, benchmarking → infer "Performance Optimization"
- Real-time, WebSockets, streaming → infer "Real-time Systems"

Return ONLY valid JSON in this exact structure:
{{
  "skills": [],
  "projects": [
    {{
      "name": "",
      "description": "",
      "technologies": [],
      "inferred_skills": []
    }}
  ],
  "experience": [],
  "education": [],
  "evidence": {{
    "skill_name": "where this skill was identified from"
  }}
}}

Resume text:
{resume_text}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ]
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
