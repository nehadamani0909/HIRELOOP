import os
from tavily import TavilyClient
from pypdf import PdfReader
from io import BytesIO

from config import load_backend_env

load_backend_env()

SKILLS = [
    "python", "java", "javascript", "typescript", "c++",
    "dsa", "oop", "dbms", "sql", "postgresql", "mysql",
    "mongodb", "fastapi", "react", "next.js", "node.js",
    "express", "rag", "llm", "langchain", "langgraph",
    "openai", "gemini", "groq", "machine learning",
    "git", "github", "docker", "rest api", "rest apis", "jwt",
    "pgvector", "vector database", "vector databases", "semantic search",
    "hybrid retrieval", "embeddings", "postgresql", "supabase",
    "observability", "monitoring", "latency", "precision@5", "recall@5",
    "mean reciprocal rank", "mrr", "evaluation framework", "metrics",
    "production-grade", "deployed", "deployment", "railway", "render",
    "vercel", "aws", "redis", "kubernetes", "ci/cd", "containerization",
    "agentic ai", "multi-agent", "performance optimization", "benchmarking",
    "query optimization", "scalability", "database optimization"
]

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text.strip()

def extract_skills(text: str) -> list[str]:
    text = text.lower()
    found = []

    for skill in SKILLS:
        if skill in text:
            found.append(skill)

    return sorted(list(set(found)))

def compare_skills(resume_skills: list[str], jd_skills: list[str]):
    matched = sorted(list(set(resume_skills) & set(jd_skills)))
    missing = sorted(list(set(jd_skills) - set(resume_skills)))

    if len(jd_skills) == 0:
        score = 0
    else:
        score = round((len(matched) / len(jd_skills)) * 100, 2)

    return matched, missing, score

def get_company_info(company_name: str):
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return {
            "company": company_name,
            "error": "TAVILY_API_KEY not found"
        }

    client = TavilyClient(api_key=api_key)

    query = f"{company_name} company recent news products tech stack"

    response = client.search(
        query=query,
        max_results=5
    )

    results = []

    for item in response.get("results", []):
        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "content": item.get("content")
        })

    return {
        "company": company_name,
        "query": query,
        "sources_used": len(results),
        "research_results": results
    }
