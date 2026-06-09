import os
import json
from groq import Groq
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import load_backend_env

load_backend_env()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
semantic_model = None

print(f"MATCHING AGENT LOADED: {__file__}")


SKILL_ALIASES = {
    "python": "python",
    "python programming": "python",
    "python programming skills": "python",
    "java programming": "java",
    "java programming skills": "java",
    "go": "go",
    "golang": "go",
    "c++": "cpp",
    "cpp": "cpp",
    "c plus plus": "cpp",
    "strong programming skills in python java go or c++": "programming_languages",
    "python java go or c++": "programming_languages",
    "data structures and algorithms": "dsa",
    "data structures algorithms": "dsa",
    "dsa knowledge": "dsa",
    "git": "git_github",
    "github": "git_github",
    "git github": "git_github",
    "git and github": "git_github",
    "github and git": "git_github",
    "version control": "git_github",
    "git version control": "git_github",
    "postgresql": "sql_databases",
    "sql": "sql_databases",
    "mysql": "sql_databases",
    "duckdb": "sql_databases",
    "postgresql and sql": "sql_databases",
    "sql and postgresql": "sql_databases",
    "sql databases": "sql_databases",
    "database system": "sql_databases",
    "database systems": "sql_databases",
    "database": "sql_databases",
    "relational databases": "sql_databases",
    "fastapi": "backend_frameworks",
    "backend frameworks": "backend_frameworks",
    "backend framework": "backend_frameworks",
    "fastapi or backend frameworks": "backend_frameworks",
    "fastapi or similar backend frameworks": "backend_frameworks",
    "fastapi or similar frameworks": "backend_frameworks",
    "rest api": "rest_apis",
    "rest apis": "rest_apis",
    "rest api development": "rest_apis",
    "api development": "rest_apis",
    "api design": "rest_apis",
    "api design experience": "rest_apis",
    "api architecture": "rest_apis",
    "backend api development": "rest_apis",
    "backend services and apis": "backend apis",
    "developing backend services and apis": "backend apis",
    "backend development": "backend_development",
    "backend development experience": "backend_development",
    "backend system": "backend_development",
    "backend systems": "backend_development",
    "high-scale backend services": "backend_development",
    "high scale backend services": "backend_development",
    "backend services": "backend_development",
    "distributed systems": "distributed_systems",
    "rest apis and distributed systems": "distributed_systems",
    "vector database": "vector_databases",
    "vector databases": "vector_databases",
    "vector databases and embeddings": "vector_databases",
    "embeddings and vector databases": "vector_databases",
    "pgvector": "vector_databases",
    "semantic search": "vector_databases",
    "semantic search and embeddings": "vector_databases",
    "rag": "rag",
    "rag systems": "rag",
    "retrieval system": "rag",
    "retrieval systems": "rag",
    "retrieval": "rag",
    "hybrid retrieval": "rag",
    "retrieval augmented generation": "rag",
    "retrieval augmented generation rag": "rag",
    "prompt engineering": "prompt_engineering",
    "monitoring and observability systems": "observability",
    "monitoring and observability": "observability",
    "evaluation frameworks": "observability",
    "evaluation framework": "observability",
    "evaluation and monitoring systems": "observability",
    "evaluation and monitoring": "observability",
    "monitoring evaluation and observability systems": "observability",
    "monitoring evaluation and observability": "observability",
    "monitoring systems": "observability",
    "observability systems": "observability",
    "monitoring observability": "observability",
    "monitoring": "observability",
    "observability": "observability",
    "multi-agent systems": "agentic_ai",
    "production-grade ai applications": "prod_ai",
    "production ai systems": "prod_ai",
    "production ai applications": "prod_ai",
    "production grade ai applications": "prod_ai",
    "production grade systems": "prod_ai",
    "production-grade systems": "prod_ai",
    "production systems": "prod_ai",
    "production ready systems": "prod_ai",
    "experience building production grade systems": "prod_ai",
    "experience building production-grade systems": "prod_ai",
    "deploying production ai applications": "prod_ai",
    "deployed ai applications": "prod_ai",
    "deployment of production ai applications": "prod_ai",
    "production deployment": "prod_ai",
    "production deployment experience": "prod_ai",
    "deployment experience": "prod_ai",
    "deployed production systems": "prod_ai",
    "cloud deployment": "prod_ai",
    "cloud deployment experience": "prod_ai",
    "production ready ai services": "prod_ai",
    "retrievium": "prod_ai",
    "production rag platform": "prod_ai",
    "deployed rag platform": "prod_ai",
    "llm applications": "llm_apps",
    "large language model applications": "llm_apps",
    "large language model llm applications": "llm_apps",
    "large language models": "llm_apps",
    "large language models llms": "llm_apps",
    "llms": "llm_apps",
    "agentic ai systems": "agentic_ai",
    "agentic systems": "agentic_ai",
    "agentic ai": "agentic_ai",
    "langgraph": "agentic_ai",
    "multi agent systems": "agentic_ai",
    "multi agent ai systems": "agentic_ai",
    "performance optimization": "performance_optimization",
    "performance optimization and scalability": "performance_optimization",
    "scalability": "performance_optimization",
    "database optimization": "performance_optimization",
    "aws cloud services": "aws",
    "aws azure or gcp": "cloud",
    "aws gcp azure": "cloud",
    "aws, gcp, azure": "cloud",
    "cloud platforms aws gcp azure": "cloud",
    "cloud platforms aws, gcp, azure": "cloud",
    "cloud platforms": "cloud",
    "cloud services": "cloud",
    "ci cd pipelines": "ci_cd",
    "cicd pipelines": "ci_cd",
    "ci cd": "ci_cd",
    "containerization": "docker",
    "containerization technologies": "docker",
}


def normalize(skill: str) -> str:
    skill = str(skill).lower().strip()
    skill = skill.replace("(", "")
    skill = skill.replace(")", "")
    skill = skill.replace("-", " ")
    skill = skill.replace("/", " ")
    skill = skill.replace(",", " ")
    skill = skill.replace("&", " and ")
    skill = " ".join(skill.split())

    return SKILL_ALIASES.get(skill, skill)


def normalize_skill(skill: str) -> str:
    return normalize(skill)


def get_semantic_model():
    global semantic_model

    if semantic_model is None:
        try:
            semantic_model = SentenceTransformer(
                "all-MiniLM-L6-v2",
                local_files_only=True,
            )
        except Exception:
            semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

    return semantic_model


def semantic_match(jd_skills, resume_sources, threshold=0.55):
    jd_skills = [str(skill).strip() for skill in jd_skills if str(skill).strip()]

    candidates = []
    if isinstance(resume_sources, dict):
        for source_type, source_items in resume_sources.items():
            for item in source_items:
                text = str(item).strip()
                if text:
                    candidates.append((source_type, text))
    else:
        candidates = [
            ("resume_chunks", str(chunk).strip())
            for chunk in resume_sources
            if str(chunk).strip()
        ]

    candidates = [
        candidate
        for candidate in _dedupe_text_items([f"{source_type}: {text}" for source_type, text in candidates])
    ]

    if not jd_skills or not candidates:
        return {}

    candidate_sources = []
    candidate_texts = []
    for candidate in candidates:
        source_type, text = candidate.split(": ", 1)
        candidate_sources.append(source_type)
        candidate_texts.append(text)

    model = get_semantic_model()
    jd_emb = model.encode(jd_skills)
    resume_emb = model.encode(candidate_texts)

    results = {}

    sims = cosine_similarity(jd_emb, resume_emb)

    for i, jd_skill in enumerate(jd_skills):
        best_idx = sims[i].argmax()
        best_score = sims[i][best_idx]

        if best_score >= threshold:
            results[jd_skill] = {
                "evidence": candidate_texts[best_idx],
                "source_type": candidate_sources[best_idx],
                "score": float(best_score),
            }

    return results


def _as_text_list(value) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str):
        return [value.strip()] if value.strip() else []

    return [str(value).strip()] if str(value).strip() else []


def _collect_text_chunks(value, chunks: list[str], prefix: str = "") -> None:
    if isinstance(value, dict):
        for key, nested_value in value.items():
            next_prefix = f"{prefix} {key}".strip()
            _collect_text_chunks(nested_value, chunks, next_prefix)
        return

    if isinstance(value, list):
        for item in value:
            _collect_text_chunks(item, chunks, prefix)
        return

    if isinstance(value, str):
        text = value.strip()
        if text:
            chunks.append(f"{prefix}: {text}" if prefix else text)


def _dedupe_text_items(items: list[str]) -> list[str]:
    deduped_items = []
    seen = set()

    for item in items:
        normalized_item = " ".join(str(item).split())
        if normalized_item and normalized_item not in seen:
            deduped_items.append(normalized_item)
            seen.add(normalized_item)

    return deduped_items


def build_resume_semantic_sources(resume_analysis: dict) -> dict[str, list[str]]:
    sources = {
        "resume_chunks": [],
        "resume_skills": [],
        "project_descriptions": [],
        "project_technologies": [],
        "project_inferred_skills": [],
    }

    skills = _as_text_list(resume_analysis.get("skills"))
    sources["resume_skills"].extend(skills)

    if skills:
        sources["resume_chunks"].append(f"Resume skills: {', '.join(skills)}")

    evidence = resume_analysis.get("evidence")
    if isinstance(evidence, dict):
        for skill, source in evidence.items():
            sources["resume_chunks"].append(f"Evidence for {skill}: {source}")

    for project in resume_analysis.get("projects", []):
        if not isinstance(project, dict):
            continue

        project_parts = []
        name = str(project.get("name") or "").strip()
        description = str(project.get("description") or "").strip()
        technologies = _as_text_list(project.get("technologies"))
        inferred_skills = _as_text_list(project.get("inferred_skills"))

        if name:
            project_parts.append(f"Project: {name}")
        if description:
            sources["project_descriptions"].append(
                f"{name}: {description}" if name else description
            )
            project_parts.append(f"Description: {description}")
        if technologies:
            sources["project_technologies"].extend(technologies)
            project_parts.append(f"Technologies: {', '.join(technologies)}")
        if inferred_skills:
            sources["project_inferred_skills"].extend(inferred_skills)
            project_parts.append(f"Inferred skills: {', '.join(inferred_skills)}")

        if project_parts:
            sources["resume_chunks"].append(" | ".join(project_parts))

    _collect_text_chunks(resume_analysis, sources["resume_chunks"])

    for source_name, items in sources.items():
        sources[source_name] = _dedupe_text_items(items)

    return sources


def build_resume_chunks(resume_analysis: dict) -> list[str]:
    sources = build_resume_semantic_sources(resume_analysis)
    chunks = []

    for items in sources.values():
        chunks.extend(items)

    return _dedupe_text_items(chunks)


def jd_skill_labels(jd_analysis: dict) -> list[str]:
    skills = [
        *_as_text_list(jd_analysis.get("required_skills")),
        *_as_text_list(jd_analysis.get("preferred_skills")),
    ]

    deduped_skills = []
    seen = set()

    for skill in skills:
        norm = normalize(skill)
        if norm not in seen:
            deduped_skills.append(skill)
            seen.add(norm)

    return deduped_skills


def covered_skill_norms(norms: set[str]) -> set[str]:
    covered = set()

    if norms & {"python", "java", "go", "cpp", "programming_languages"}:
        covered.update({"python", "java", "go", "cpp", "programming_languages"})

    if norms & {"fastapi", "rest_apis", "backend apis", "backend_frameworks", "backend_development"}:
        covered.update({"fastapi", "rest_apis", "backend apis", "backend_frameworks", "backend_development"})

    if norms & {"prod_ai"}:
        covered.add("prod_ai")

    if norms & {"observability"}:
        covered.add("observability")

    if norms & {"performance_optimization"}:
        covered.add("performance_optimization")

    if norms & {"rag", "llm_apps", "agentic_ai", "prompt_engineering"}:
        covered.add("prompt_engineering")

    return covered


def build_reasoning_summary(
    matched_skills: list[str],
    missing_skills: list[str],
    match_score,
) -> str:
    if isinstance(match_score, (int, float)):
        score_text = f"{round(match_score)}%"
    else:
        score_text = "the current"

    summary = (
        f"The resume matches {len(matched_skills)} JD-requested skill areas "
        f"for a {score_text} fit."
    )

    if matched_skills:
        summary += f" Strongest evidence includes {', '.join(matched_skills[:5])}."

    if missing_skills:
        summary += f" Remaining gaps include {', '.join(missing_skills[:5])}."
    else:
        summary += " No major skill gaps were identified."

    return summary


def match_resume_to_jd(resume_analysis: dict, jd_analysis: dict) -> dict:
    prompt = f"""
You are a Semantic Matching Agent.

Your task is to compare a candidate's resume analysis with a job description analysis.

IMPORTANT:

Missing skills are computed AFTER semantic matching.

Before adding a skill to missing_skills:

1. Search the entire resume analysis.
2. Search all project descriptions.
3. Search all technologies.
4. Search all inferred skills.
5. Search deployment details.
6. Search architecture details.

If semantic evidence exists anywhere in the resume,
the skill MUST NOT appear in missing_skills.

A matched skill and missing skill must be mutually exclusive.

If uncertain, prefer MATCH over MISSING.

Perform recruiter-style semantic matching.

Critical matching contract:

matched_skills must contain ONLY skills, requirements, or concepts requested by the JD.

A skill can be in matched_skills only if BOTH are true:
1. The JD asks for it directly or semantically.
2. The resume provides direct or semantic evidence for it.

Do NOT include resume-only skills in matched_skills.

Examples:
- If the resume has OpenAI API but the JD does not ask for OpenAI API, do NOT include OpenAI API in matched_skills.
- If the resume has Agentic AI but the JD does not ask for agentic systems, LangGraph, or multi-agent systems, do NOT include Agentic AI.
- If the resume has Machine Learning but the JD does not ask for ML, do NOT include Machine Learning.

missing_skills must contain ONLY JD-requested skills that are not supported by the resume.

Do NOT put the same skill or semantic equivalent in both matched_skills and missing_skills.

Use JD labels for output.
Example:
Resume: pgvector
JD: Vector Databases
Output matched_skills: ["Vector Databases"]
Not: ["pgvector"]

Resume: FastAPI
JD: REST APIs
Output matched_skills: ["REST APIs"]
Not: ["FastAPI"] unless FastAPI itself is also requested by the JD.

Do semantic matching, not exact keyword matching.
Do not rely on exact keywords.

Infer skills from:
- Technologies used
- Project descriptions
- Deployment details
- Architecture decisions
- Responsibilities

Count semantically equivalent concepts as matches only when the JD requests that concept.
Only mark a skill missing when there is insufficient evidence anywhere in the resume.

Examples:
- FastAPI matches REST APIs and backend frameworks
- PostgreSQL matches SQL databases
- pgvector matches vector databases
- RAG Systems matches Retrieval-Augmented Generation
- LangChain matches LLM applications
- Agentic AI matches LangGraph/agentic systems partially
- Next.js/React matches frontend development
- JWT Authentication matches authentication/security

Semantic matching rules:
- pgvector -> Vector Databases
- Supabase pgvector -> Vector Databases
- FastAPI -> REST APIs / Backend APIs
- PostgreSQL -> SQL Databases
- RAG Systems -> Retrieval-Augmented Generation
- LangChain -> LLM Applications
- Retrievium -> Production-grade AI Applications
- Deployed RAG Platform -> Production-grade AI Applications
- JWT Authentication -> Backend Security
- evaluation metrics, latency tracking, Precision@5, Recall@5, MRR -> Monitoring and Observability Systems
- Retrievium deployed production RAG platform -> Production-grade AI Applications
- AetherQuery performance optimization, benchmarking, caching -> Performance Optimization
- DSA -> Data Structures and Algorithms

Do NOT require exact keyword matches.
Do not mark a skill missing if it is semantically supported by project evidence.
Do not put the same skill in both matched_skills and missing_skills.
If a skill is matched semantically, do not mark it missing.

Example:
Resume: pgvector
JD: Vector Databases
=> MATCH

Resume: Retrievium Production RAG Platform
JD: Production-grade AI Applications
=> MATCH

Scoring rules:
- match_score must be a percentage number between 0 and 100.
- Do NOT return decimals like 0.8.
- If 8 out of 10 important skills match, return 80, not 0.8.
- Count semantic matches as valid matches.
- Count partial matches as half matches.
- Do not mark pgvector as missing if the JD asks for vector databases.
- Do not mark production-grade AI applications as missing if the resume has a deployed RAG/LLM project.

Return ONLY valid JSON in this exact structure:

{{
  "matched_skills": [],
  "missing_skills": [],
  "semantic_matches": {{
    "resume_skill": "jd_skill"
  }},
  "partial_matches": {{
    "resume_skill": "jd_skill"
  }},
  "match_score": 0,
  "reasoning_summary": ""
}}

Resume Analysis:
{json.dumps(resume_analysis, indent=2)}

JD Analysis:
{json.dumps(jd_analysis, indent=2)}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
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

        if not raw_text.startswith("{"):
            json_start = raw_text.find("{")
            json_end = raw_text.rfind("}")

            if json_start != -1 and json_end != -1:
                raw_text = raw_text[json_start:json_end + 1]

        parsed_response = json.loads(raw_text)

        expected_keys = {
            "matched_skills": [],
            "missing_skills": [],
            "semantic_matches": {},
            "partial_matches": {},
            "match_score": 0,
            "reasoning_summary": "",
        }

        for key, default_value in expected_keys.items():
            parsed_response.setdefault(key, default_value)

        if not isinstance(parsed_response["matched_skills"], list):
            parsed_response["matched_skills"] = []
        if not isinstance(parsed_response["missing_skills"], list):
            parsed_response["missing_skills"] = []
        if not isinstance(parsed_response["semantic_matches"], dict):
            parsed_response["semantic_matches"] = {}
        if not isinstance(parsed_response["partial_matches"], dict):
            parsed_response["partial_matches"] = {}

        jd_skills = jd_skill_labels(jd_analysis)
        resume_sources = build_resume_semantic_sources(resume_analysis)
        semantic_results = {}

        try:
            semantic_results = semantic_match(jd_skills, resume_sources)
        except Exception as semantic_error:
            print(f"SEMANTIC EMBEDDING MATCH FAILED: {semantic_error}")

        parsed_response["semantic_evidence"] = semantic_results

        def infer_resume_capabilities(resume_analysis: dict) -> set[str]:
            text = json.dumps(resume_analysis).lower()
            caps = set()

            rules = {
                "python": ["python"],
                "java": ["java"],
                "dsa": ["dsa", "data structures", "algorithms"],
                "fastapi": ["fastapi"],
                "backend_frameworks": ["fastapi", "backend framework", "backend"],
                "rest_apis": ["rest api", "restful api", "api development", "api design", "fastapi"],
                "sql_databases": ["postgresql", "mysql", "sql", "duckdb"],
                "git_github": ["git", "github", "version control"],
                "llm": ["llm", "large language model", "openai", "gemini", "groq", "langchain"],
                "llm_apps": ["llm", "large language model", "openai", "gemini", "groq", "langchain"],
                "rag": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
                "prompt_engineering": ["prompt", "prompt engineering", "rag", "langchain"],
                "vector_databases": ["pgvector", "vector database", "semantic search", "embedding"],
                "prod_ai": [
                    "retrievium",
                    "production rag platform",
                    "deployed rag platform",
                    "deployed",
                    "deployment",
                    "cloud deployment",
                    "production deployment",
                    "production deployment experience",
                    "production-grade",
                    "production grade",
                ],
                "observability": ["latency", "precision@5", "recall@5", "mrr", "metrics", "monitoring", "evaluation framework"],
                "performance_optimization": [
                    "aetherquery",
                    "benchmark",
                    "benchmarking",
                    "caching",
                    "latency",
                    "optimization",
                    "performance",
                    "query optimization",
                    "query speedup",
                    "throughput",
                    "18x",
                    "18×",
                ],
                "backend_development": ["fastapi", "backend", "rest api", "api"],
                "agentic_ai": ["langgraph", "agentic ai", "multi-agent", "multi agent"],
                "docker": ["docker", "container"],
                "redis": ["redis"],
                "aws": ["aws"],
                "kubernetes": ["kubernetes", "k8s"],
                "ci_cd": ["ci/cd", "ci cd", "pipeline"],
            }

            for capability, keywords in rules.items():
                if any(keyword in text for keyword in keywords):
                    caps.add(capability)

            if "retrievium" in text:
                caps.add("prod_ai")
                caps.add("rag")
            if "langchain" in text:
                caps.add("llm_apps")
            if "langgraph" in text:
                caps.add("agentic_ai")

            return caps

        resume_caps = infer_resume_capabilities(resume_analysis)
        semantic_result_by_norm = {
            normalize(skill): result
            for skill, result in semantic_results.items()
        }

        matched = parsed_response.get("matched_skills", [])
        missing = parsed_response.get("missing_skills", [])

        clean_matched = []
        matched_norms = set()

        for skill in matched:
            norm = normalize(skill)
            if norm not in matched_norms:
                clean_matched.append(str(skill))
                matched_norms.add(norm)

        for skill in jd_skills:
            norm = normalize(skill)
            if norm in semantic_result_by_norm and norm not in matched_norms:
                evidence = semantic_result_by_norm[norm].get("evidence", norm)
                clean_matched.append(str(skill))
                matched_norms.add(norm)
                parsed_response["semantic_matches"][str(evidence)] = str(skill)

        clean_missing = []
        for skill in missing:
            skill_str = str(skill)
            norm = normalize_skill(skill_str)

            if norm in matched_norms:
                continue

            if norm in covered_skill_norms(matched_norms | resume_caps):
                continue

            if norm in resume_caps:
                clean_matched.append(skill_str)
                matched_norms.add(norm)
                parsed_response["semantic_matches"][norm] = skill_str
                continue

            clean_missing.append(skill_str)

        parsed_response["matched_skills"] = clean_matched
        parsed_response["missing_skills"] = clean_missing

        deduped_matched = []
        seen = set()

        for skill in parsed_response["matched_skills"]:
            norm = normalize_skill(str(skill))
            if norm not in seen:
                deduped_matched.append(skill)
                seen.add(norm)

        parsed_response["matched_skills"] = deduped_matched

        matched_count = len(parsed_response["matched_skills"])
        missing_count = len(parsed_response["missing_skills"])
        partial_count = len(parsed_response.get("partial_matches", {}))

        total = matched_count + missing_count + partial_count

        if total > 0:
            parsed_response["match_score"] = round(
                ((matched_count + 0.5 * partial_count) / total) * 100
            )

        parsed_response["reasoning_summary"] = build_reasoning_summary(
            parsed_response["matched_skills"],
            parsed_response["missing_skills"],
            parsed_response["match_score"],
        )

        print("CLEANUP EXECUTED")
        print("\nFINAL MATCHED")
        print(parsed_response["matched_skills"])

        print("\nFINAL MISSING")
        print(parsed_response["missing_skills"])

        print("\nFINAL SCORE")
        print(parsed_response["match_score"])

        return parsed_response

    except Exception as e:
        return {
            "error": str(e)
        }
