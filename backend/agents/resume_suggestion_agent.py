import os
import json
from groq import Groq

from config import load_backend_env
from agents.matching_agent import normalize_skill

load_backend_env()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


SUGGESTION_KEYS = (
    "strengths_to_highlight",
    "projects_to_emphasize",
    "resume_improvements",
    "skills_to_learn",
    "section_order_suggestions",
)


INFRA_SKILLS = {
    "aws",
    "cloud",
    "ci_cd",
    "docker",
    "kubernetes",
    "redis",
}


COVERED_BY_MATCHED_SKILLS = {
    "backend_frameworks": {"backend_frameworks", "fastapi", "rest_apis", "backend_development"},
    "fastapi": {"backend_frameworks", "fastapi", "rest_apis", "backend_development"},
    "rest_apis": {"backend_frameworks", "fastapi", "rest_apis", "backend_development"},
    "backend_development": {"backend_frameworks", "fastapi", "rest_apis", "backend_development"},
    "sql_databases": {"sql_databases"},
    "observability": {"observability"},
    "git_github": {"git_github"},
    "prod_ai": {"prod_ai"},
    "prompt_engineering": {"rag", "llm_apps", "agentic_ai", "prompt_engineering"},
}


TARGET_PROJECTS = ("Retrievium", "AetherQuery")


INFRA_SUGGESTION = (
    "Build and deploy a production-ready project using Docker, AWS, Redis, "
    "Kubernetes, and CI/CD pipelines to close the largest infrastructure skill gaps."
)


PROJECT_ORDER_SUGGESTION = (
    "Move Retrievium and AetherQuery to the top of the Projects section because "
    "they align most closely with AI platform and GenAI engineering roles."
)


METRICS_SUGGESTION = (
    "Add measurable metrics to Retrievium and AetherQuery, such as latency "
    "reduction, retrieval accuracy, query speedup, and benchmark results."
)


STRONG_MATCH_IMPACT_SUGGESTION = (
    "Quantify project impact with latency reduction, retrieval accuracy, query "
    "speedup, throughput, or benchmark metrics."
)


STRONG_MATCH_DEPLOYMENT_SUGGESTION = (
    "Highlight deployment scale, production usage patterns, and reliability "
    "details for the strongest AI projects."
)


STRONG_MATCH_FALLBACK_ORDER_SUGGESTION = (
    "Reorder projects so the most role-relevant AI platform and retrieval work "
    "appears first."
)


INFRA_DUPLICATE_MARKERS = (
    "infrastructure-focused project",
    "deployment-focused project",
    "cloud deployment details",
    "cloud platforms",
    "learn aws",
    "learn docker",
    "learn kubernetes",
    "learn redis",
    "learn about cloud-native",
    "learn about cloud infrastructure",
    "cloud-native ai infrastructure",
    "cloud infrastructure",
    "aws, azure, or gcp",
    "aws, azure or gcp",
    "ci/cd pipelines to strengthen",
    "docker, redis, aws",
    "docker, aws, redis",
)


def _as_list(value) -> list[str]:
    if not isinstance(value, list):
        return []

    return [str(item).strip() for item in value if str(item).strip()]


def _skill_norms(skills: list[str]) -> set[str]:
    return {normalize_skill(skill) for skill in skills if str(skill).strip()}


def _project_names(resume_analysis: dict) -> set[str]:
    names = set()

    for project in resume_analysis.get("projects", []):
        if not isinstance(project, dict):
            continue

        name = str(project.get("name") or "").strip()
        if name:
            names.add(name.lower())

    return names


def _has_target_projects(resume_analysis: dict) -> bool:
    names = _project_names(resume_analysis)
    return all(
        any(project.lower() in name for name in names)
        for project in TARGET_PROJECTS
    )


def _suggestion_mentions_skill(suggestion: str, skill: str) -> bool:
    suggestion_norm = normalize_skill(suggestion)
    skill_norm = normalize_skill(skill)

    if suggestion_norm == skill_norm:
        return True

    suggestion_text = suggestion.lower()
    skill_text = str(skill).lower()

    return skill_text in suggestion_text or skill_norm.replace("_", " ") in suggestion_text


def _has_infra_gap(missing_skills: list[str]) -> bool:
    return any(normalize_skill(skill) in INFRA_SKILLS for skill in missing_skills)


def _resume_supports_backend_frameworks(resume_analysis: dict) -> bool:
    text = json.dumps(resume_analysis).lower()
    return any(
        keyword in text
        for keyword in ("fastapi", "rest api", "restful api", "backend framework", "backend")
    )


def _resume_supports_prompt_engineering(resume_analysis: dict) -> bool:
    text = json.dumps(resume_analysis).lower()
    return any(
        keyword in text
        for keyword in ("prompt", "rag", "retrieval", "langchain", "llm")
    )


def _filter_covered_missing_skills(
    missing_skills: list[str],
    matched_skills: list[str],
    resume_analysis: dict,
) -> list[str]:
    matched_norms = _skill_norms(matched_skills)
    filtered = []

    for skill in missing_skills:
        norm = normalize_skill(skill)
        covered_by = COVERED_BY_MATCHED_SKILLS.get(norm, set())

        if norm in matched_norms or covered_by & matched_norms:
            continue

        if norm == "backend_frameworks" and _resume_supports_backend_frameworks(resume_analysis):
            continue

        if norm == "prompt_engineering" and _resume_supports_prompt_engineering(resume_analysis):
            continue

        filtered.append(skill)

    return filtered


def _is_infra_duplicate(suggestion: str) -> bool:
    suggestion_text = suggestion.lower()
    return any(marker in suggestion_text for marker in INFRA_DUPLICATE_MARKERS)


def _is_matched_observability_suggestion(suggestion: str, matched_norms: set[str]) -> bool:
    if "observability" not in matched_norms:
        return False

    suggestion_text = suggestion.lower()
    return (
        "evaluation and monitoring" in suggestion_text
        or "monitoring and observability" in suggestion_text
        or "observability" in suggestion_text
    )


def _is_rule_leak(suggestion: str) -> bool:
    suggestion_text = suggestion.lower()
    return (
        "group related gaps" in suggestion_text
        or "prioritize missing skills" in suggestion_text
        or "weak evidence over already-strong matches" in suggestion_text
    )


def _is_project_order_guess(suggestion: str) -> bool:
    suggestion_text = suggestion.lower()
    return (
        ("move" in suggestion_text or "moving" in suggestion_text)
        and "project" in suggestion_text
        and "top" in suggestion_text
    )


def _append_once(items: list[str], suggestion: str) -> None:
    suggestion_norm = " ".join(suggestion.lower().split())
    existing = {" ".join(item.lower().split()) for item in items}

    if suggestion_norm not in existing:
        items.append(suggestion)


def _dedupe_across_sections(parsed_response: dict) -> dict:
    seen = set()

    for key in SUGGESTION_KEYS:
        deduped = []

        for suggestion in _as_list(parsed_response.get(key)):
            suggestion_norm = " ".join(suggestion.lower().split())
            if suggestion_norm in seen:
                continue

            deduped.append(suggestion)
            seen.add(suggestion_norm)

        parsed_response[key] = deduped

    return parsed_response


def _build_missing_skill_suggestions(missing_skills: list[str]) -> dict:
    suggestions = {
        "strengths_to_highlight": [],
        "projects_to_emphasize": [],
        "resume_improvements": [],
        "skills_to_learn": [],
        "section_order_suggestions": [],
    }

    other_missing = [skill for skill in missing_skills if normalize_skill(skill) not in INFRA_SKILLS]

    if _has_infra_gap(missing_skills):
        suggestions["resume_improvements"].append(INFRA_SUGGESTION)

    if other_missing:
        suggestions["skills_to_learn"].append(
            f"Build or document practical experience with {', '.join(other_missing[:3])}."
        )

    return suggestions


def _build_strong_match_suggestions(resume_analysis: dict) -> dict:
    section_order_suggestion = (
        PROJECT_ORDER_SUGGESTION
        if _has_target_projects(resume_analysis)
        else STRONG_MATCH_FALLBACK_ORDER_SUGGESTION
    )

    return {
        "strengths_to_highlight": [],
        "projects_to_emphasize": [],
        "resume_improvements": [
            STRONG_MATCH_IMPACT_SUGGESTION,
            STRONG_MATCH_DEPLOYMENT_SUGGESTION,
        ],
        "skills_to_learn": [],
        "section_order_suggestions": [section_order_suggestion],
    }


def sanitize_resume_suggestions(
    parsed_response: dict,
    matching_analysis: dict,
    resume_analysis: dict | None = None,
) -> dict:
    resume_analysis = resume_analysis or {}
    matched_skills = _as_list(matching_analysis.get("matched_skills"))
    missing_skills = _filter_covered_missing_skills(
        _as_list(matching_analysis.get("missing_skills")),
        matched_skills,
        resume_analysis,
    )
    matched_norms = _skill_norms(matched_skills)
    missing_norms = _skill_norms(missing_skills)

    if not missing_skills:
        return _build_strong_match_suggestions(resume_analysis)

    fallback = _build_missing_skill_suggestions(missing_skills)
    has_target_projects = _has_target_projects(resume_analysis)
    has_infra_gap = _has_infra_gap(missing_skills)

    for key in SUGGESTION_KEYS:
        cleaned = []
        seen = set()

        for suggestion in _as_list(parsed_response.get(key)):
            suggestion_norm = normalize_skill(suggestion)
            mentions_missing = any(_suggestion_mentions_skill(suggestion, skill) for skill in missing_skills)
            mentions_matched = any(_suggestion_mentions_skill(suggestion, skill) for skill in matched_skills)

            if _is_rule_leak(suggestion):
                continue

            if _is_matched_observability_suggestion(suggestion, matched_norms):
                continue

            if has_infra_gap and _is_infra_duplicate(suggestion):
                continue

            if _is_project_order_guess(suggestion):
                continue

            if "technical skills section" in suggestion.lower() and not mentions_missing:
                continue

            if mentions_matched and not mentions_missing:
                continue

            if suggestion_norm in matched_norms and suggestion_norm not in missing_norms:
                continue

            if suggestion_norm not in seen:
                cleaned.append(suggestion)
                seen.add(suggestion_norm)

        parsed_response[key] = cleaned[:2]

    if fallback["resume_improvements"]:
        parsed_response["resume_improvements"] = [
            suggestion
            for suggestion in parsed_response["resume_improvements"]
            if not _is_infra_duplicate(suggestion)
        ]
        _append_once(parsed_response["resume_improvements"], fallback["resume_improvements"][0])

    if has_target_projects:
        _append_once(parsed_response["resume_improvements"], METRICS_SUGGESTION)
        _append_once(parsed_response["resume_improvements"], PROJECT_ORDER_SUGGESTION)
        parsed_response["section_order_suggestions"] = [PROJECT_ORDER_SUGGESTION]

    if fallback["skills_to_learn"] and not parsed_response["skills_to_learn"]:
        parsed_response["skills_to_learn"] = fallback["skills_to_learn"][:1]

    parsed_response["resume_improvements"] = parsed_response["resume_improvements"][:3]
    parsed_response["skills_to_learn"] = parsed_response["skills_to_learn"][:1]
    parsed_response["section_order_suggestions"] = parsed_response["section_order_suggestions"][:1]

    return _dedupe_across_sections(parsed_response)


def generate_resume_suggestions(
    resume_analysis: dict,
    jd_analysis: dict,
    matching_analysis: dict,
    evidence_analysis: dict,
) -> dict:
    prompt = f"""
You are a Resume Suggestion Agent.

Generate concise recruiter-style resume recommendations based on:
- Resume Analysis
- JD Analysis
- Matching Analysis
- Evidence Analysis

	Rules:
	- Do not invent fake experience.
	- Do not repeat matched skills as standalone suggestions.
	- Do not suggest adding project-level evidence for matched skills.
	- Suggestions must focus on missing_skills or weak_or_inferred_matches only.
	- If SQL Databases, Vector Databases, Python, Git/GitHub, RAG, LLMs, Agentic AI, or Production-grade AI Applications are matched, do not suggest improving them.
	- Do not generate one suggestion per skill.
	- Suggest moving Retrievium and AetherQuery to the top when both exist because they align with AI platform and GenAI engineering roles.
- Do not suggest strengthening a skill if evidence_analysis already shows strong project-level evidence.
- Group related gaps together.
- Infrastructure gaps like Docker, AWS, Redis, Kubernetes, CI/CD must be grouped into ONE suggestion.
- Project-related suggestions must be grouped by project.
- Return at most 8 total suggestions across all arrays.
- Each suggestion must be one concise sentence.
- Prioritize missing skills and weak evidence over already-strong matches.

	Good suggestions:
	- Emphasize Retrievium's RAG, pgvector, evaluation metrics, and deployment details for AI infrastructure roles.
	- Highlight AetherQuery's SQL analytics, benchmarking, and query optimization work.
	- Build and deploy a production-ready project using Docker, AWS, Redis, Kubernetes, and CI/CD pipelines to close the largest infrastructure skill gaps.
	- Move Retrievium and AetherQuery to the top of the Projects section because they align most closely with AI platform and GenAI engineering roles.
	- Add measurable metrics to Retrievium and AetherQuery, such as latency reduction, retrieval accuracy, query speedup, and benchmark results.

Bad suggestions:
- Python
- FastAPI
- PostgreSQL
	- Mention Git and GitHub usage
	- Add Docker
	- Learn AWS
	- Learn Redis
	- Add concrete cloud deployment details if cloud platforms are still missing
	- Group related gaps together, such as infrastructure gaps like Docker, AWS, Redis, Kubernetes, CI/CD into one suggestion.
	- Prioritize missing skills and weak evidence over already-strong matches.
	- Add project-level evidence for SQL Databases and Vector Databases when those are already matched

Return ONLY valid JSON in this exact structure:

{{
  "strengths_to_highlight": [],
  "projects_to_emphasize": [],
  "resume_improvements": [],
  "skills_to_learn": [],
  "section_order_suggestions": []
}}

Maximum items:
- strengths_to_highlight: 2
- projects_to_emphasize: 2
- resume_improvements: 2
- skills_to_learn: 1
- section_order_suggestions: 1

Resume Analysis:
{json.dumps(resume_analysis, indent=2)}

JD Analysis:
{json.dumps(jd_analysis, indent=2)}

Matching Analysis:
{json.dumps(matching_analysis, indent=2)}

Evidence Analysis:
{json.dumps(evidence_analysis, indent=2)}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        raw_text = response.choices[0].message.content.strip()

        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.replace("```", "").strip()

        parsed_response = json.loads(raw_text)

        expected_keys = {
            "strengths_to_highlight": [],
            "projects_to_emphasize": [],
            "resume_improvements": [],
            "skills_to_learn": [],
            "section_order_suggestions": [],
        }

        for key, default_value in expected_keys.items():
            parsed_response.setdefault(key, default_value)

        return sanitize_resume_suggestions(parsed_response, matching_analysis, resume_analysis)

    except Exception as e:
        return {"error": str(e)}
