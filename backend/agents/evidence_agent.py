import os
import json
from groq import Groq

from config import load_backend_env

load_backend_env()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_evidence(resume_analysis: dict, matching_analysis: dict) -> dict:
    prompt = f"""
You are an Evidence Generation Agent.

Your task is to explain where each matched skill is supported in the candidate's resume.

Use the resume projects, skills, experience, and evidence fields.
Do not invent anything.
Prefer project-level evidence over skills-section evidence.
Return evidence for matched skills only.
If a skill appears in a project technology stack or project description, name the project.
Use confident, professional language that demonstrates the skill through actual project work.

Language Guide:
- Instead of "Inferred from", use: "Demonstrated in", "Showcased in", "Evidenced in", "Applied in", "Built with", "Implemented in"
- Always reference the specific project name when available
- Sound confident and professional, not tentative

Bad:
- Git: Skills section
- Inferred from project descriptions, particularly 'Context-aware Question Answering' in Retrievium.

Good:
- GitHub: Used across Retrievium, AetherQuery, and QuickShare projects.
- Data Structures and Algorithms: Demonstrated through semantic retrieval and context-aware question answering systems in Retrievium.
- REST APIs: Showcased through the QuickShare project with multiple RESTful endpoints.

If evidence only exists in the skills section, say:
"Listed in Technical Skills section; project-level examples would strengthen this skill."

Return ONLY valid JSON in this exact structure:

{{
  "skill_evidence": {{
    "skill_name": "evidence from resume"
  }},
  "top_strengths": [],
  "weak_or_inferred_matches": {{
    "skill_name": "why this is only partially supported"
  }},
  "missing_skill_explanations": {{
    "skill_name": "why this skill is missing or not clearly shown"
  }}
}}

Resume Analysis:
{json.dumps(resume_analysis, indent=2)}

Matching Analysis:
{json.dumps(matching_analysis, indent=2)}
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
