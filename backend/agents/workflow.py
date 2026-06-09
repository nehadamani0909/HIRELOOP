import json
from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph, END

from agents.resume_agent import extract_resume_information
from agents.jd_agent import extract_jd_information
from agents.matching_agent import match_resume_to_jd, normalize_skill as _canonical_normalize_skill
from agents.evidence_agent import generate_evidence
from agents.resume_suggestion_agent import generate_resume_suggestions
from utils import extract_skills, get_company_info


class HireLoopState(TypedDict):
    resume_text: str
    job_description: str
    company_name: str

    resume_analysis: Dict[str, Any]
    jd_analysis: Dict[str, Any]
    company_info: Dict[str, Any]
    matching_analysis: Dict[str, Any]
    evidence_analysis: Dict[str, Any]
    suggestion_analysis: Dict[str, Any]


def _as_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    return [str(item).strip() for item in value if str(item).strip()]


PRETTY_SKILL_LABELS = {
    "dsa": "Data Structures and Algorithms",
    "docker": "Docker",
    "aws": "AWS",
    "redis": "Redis",
    "kubernetes": "Kubernetes",
    "ci/cd": "CI/CD Pipelines",
    "ci_cd": "CI/CD Pipelines",
    "observability": "Monitoring & Observability",
    "vector databases": "Vector Databases",
    "vector_databases": "Vector Databases",
    "backend apis": "Backend APIs",
    "backend_frameworks": "Backend Frameworks",
    "sql databases": "SQL Databases",
    "sql_databases": "SQL Databases",
    "performance optimization": "Performance Optimization",
    "performance_optimization": "Performance Optimization",
    "production-grade ai applications": "Production-grade AI Applications",
    "prod_ai": "Production-grade AI Applications",
    "python": "Python",
    "java": "Java",
    "go": "Go",
    "cpp": "C++",
    "programming_languages": "Programming Languages",
    "fastapi": "FastAPI",
    "rest api": "REST APIs",
    "rest_apis": "REST APIs",
    "postgresql": "PostgreSQL",
    "sql": "SQL",
    "git": "Git",
    "github": "GitHub",
    "git_github": "Git/GitHub",
    "langchain": "LangChain",
    "langgraph": "LangGraph",
    "llm": "Large Language Models (LLMs)",
    "llm_apps": "LLM Applications",
    "rag": "Retrieval-Augmented Generation (RAG)",
    "agentic_ai": "Agentic AI Systems",
    "backend_development": "Backend Development",
    "distributed_systems": "Distributed Systems",
    "cloud": "Cloud Platforms",
    "prompt_engineering": "Prompt Engineering",
}


def _normalize_skill(skill: str) -> str:
    s = skill.lower().strip()
    s = s.replace("(", "")
    s = s.replace(")", "")
    s = s.replace("-", " ")
    s = s.replace("/", " ")
    s = s.replace(",", " ")
    s = s.replace("&", " and ")
    s = " ".join(s.split())

    aliases = {
        "data structures and algorithms": "dsa",
        "data structures & algorithms": "dsa",
        "data structures": "dsa",
        "algorithms": "dsa",
        "dsa": "dsa",
        "python programming": "python",
        "python programming skills": "python",
        "go": "go",
        "golang": "go",
        "c++": "cpp",
        "cpp": "cpp",
        "c plus plus": "cpp",
        "strong programming skills in python java go or c++": "programming_languages",
        "python java go or c++": "programming_languages",
        "fastapi or similar backend frameworks": "backend_frameworks",
        "fastapi or backend frameworks": "backend_frameworks",
        "fastapi or similar frameworks": "backend_frameworks",
        "backend frameworks": "backend_frameworks",
        "backend framework": "backend_frameworks",
        "rest apis": "rest_apis",
        "rest api": "rest_apis",
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
        "backend services": "backend_development",
        "high scale backend services": "backend_development",
        "high-scale backend services": "backend_development",
        "distributed systems": "distributed_systems",
        "rest apis and distributed systems": "distributed_systems",
        "fastapi": "fastapi",
        "large language models": "llm_apps",
        "large language models llms": "llm_apps",
        "large language model applications": "llm_apps",
        "large language model llm applications": "llm_apps",
        "llms": "llm_apps",
        "llm": "llm",
        "llm applications": "llm_apps",
        "prompt engineering": "prompt_engineering",
        "retrieval-augmented generation": "rag",
        "retrieval augmented generation": "rag",
        "retrieval augmented generation rag": "rag",
        "retrieval augmented generation rag systems": "rag",
        "retrieval system": "rag",
        "retrieval systems": "rag",
        "retrieval": "rag",
        "rag systems": "rag",
        "rag": "rag",
        "vector database": "vector_databases",
        "vector databases": "vector_databases",
        "vector databases and embeddings": "vector_databases",
        "embeddings and vector databases": "vector_databases",
        "pgvector": "vector_databases",
        "supabase pgvector": "vector_databases",
        "semantic search": "vector_databases",
        "semantic search and embeddings": "vector_databases",
        "embeddings": "vector_databases",
        "hybrid retrieval": "rag",
        "aws cloud services": "aws",
        "aws azure or gcp": "cloud",
        "aws, azure, or gcp": "cloud",
        "aws gcp azure": "cloud",
        "aws, gcp, azure": "cloud",
        "cloud platforms aws gcp azure": "cloud",
        "cloud platforms aws, gcp, azure": "cloud",
        "cloud platforms": "cloud",
        "amazon web services": "aws",
        "aws": "aws",
        "ci/cd pipelines": "ci_cd",
        "ci/cd": "ci_cd",
        "ci cd pipelines": "ci_cd",
        "ci cd": "ci_cd",
        "ci-cd": "ci_cd",
        "containerization": "docker",
        "containers": "docker",
        "docker": "docker",
        "monitoring systems": "observability",
        "monitoring and observability systems": "observability",
        "monitoring and observability": "observability",
        "evaluation frameworks": "observability",
        "evaluation and monitoring systems": "observability",
        "evaluation and monitoring": "observability",
        "monitoring evaluation and observability systems": "observability",
        "monitoring evaluation and observability": "observability",
        "observability systems": "observability",
        "monitoring observability": "observability",
        "observability": "observability",
        "monitoring": "observability",
        "latency": "observability",
        "retrieval latency": "observability",
        "precision@5": "observability",
        "recall@5": "observability",
        "mean reciprocal rank": "observability",
        "mrr": "observability",
        "evaluation framework": "observability",
        "metrics": "observability",
        "sql databases": "sql_databases",
        "sql database": "sql_databases",
        "database system": "sql_databases",
        "database systems": "sql_databases",
        "database": "sql_databases",
        "postgresql and sql": "sql_databases",
        "sql and postgresql": "sql_databases",
        "postgresql sql": "sql_databases",
        "relational databases": "sql_databases",
        "postgresql": "sql_databases",
        "sql": "sql_databases",
        "backend api": "backend apis",
        "backend apis": "backend apis",
        "git": "git_github",
        "github": "git_github",
        "git github": "git_github",
        "git and github": "git_github",
        "github and git": "git_github",
        "version control": "git_github",
        "git version control": "git_github",
        "production grade ai applications": "prod_ai",
        "production ai systems": "prod_ai",
        "production ai applications": "prod_ai",
        "production grade systems": "prod_ai",
        "production-grade systems": "prod_ai",
        "production systems": "prod_ai",
        "production ready systems": "prod_ai",
        "experience building production grade systems": "prod_ai",
        "experience building production-grade systems": "prod_ai",
        "deploying production ai applications": "prod_ai",
        "deployed ai applications": "prod_ai",
        "production deployment": "prod_ai",
        "production deployment experience": "prod_ai",
        "deployment experience": "prod_ai",
        "deployed production systems": "prod_ai",
        "cloud deployment": "prod_ai",
        "cloud deployment experience": "prod_ai",
        "production rag platform": "prod_ai",
        "deployed rag platform": "prod_ai",
        "retrievium": "prod_ai",
        "production grade": "prod_ai",
        "deployed": "prod_ai",
        "deployment": "prod_ai",
        "railway": "prod_ai",
        "render": "prod_ai",
        "vercel": "prod_ai",
        "langgraph": "agentic_ai",
        "agentic ai": "agentic_ai",
        "agentic ai systems": "agentic_ai",
        "agentic systems": "agentic_ai",
        "multi agent systems": "agentic_ai",
        "multi agent": "agentic_ai",
        "performance optimization": "performance_optimization",
        "performance optimization and scalability": "performance_optimization",
        "scalability": "performance_optimization",
        "database optimization": "performance_optimization",
    }

    return aliases.get(s, _canonical_normalize_skill(s))


def _pretty_skill(skill: str) -> str:
    normalized = _normalize_skill(skill)
    return PRETTY_SKILL_LABELS.get(normalized, skill)


def _normalized_set(skills: list[str]) -> set[str]:
    return {_normalize_skill(skill) for skill in skills if skill}


def _covered_skill_norms(norms: set[str]) -> set[str]:
    covered = set()

    if norms & {"python", "java", "go", "cpp", "programming_languages"}:
        covered.update({"python", "java", "go", "cpp", "programming_languages"})

    if norms & {"fastapi", "rest_apis", "backend apis", "backend_frameworks", "backend_development"}:
        covered.update({"fastapi", "rest_apis", "backend apis", "backend_frameworks", "backend_development"})

    if norms & {"sql_databases"}:
        covered.add("sql_databases")

    if norms & {"prod_ai"}:
        covered.update({"prod_ai"})

    if norms & {"observability"}:
        covered.update({"observability"})

    if norms & {"performance_optimization"}:
        covered.update({"performance_optimization"})

    if norms & {"rag", "llm_apps", "agentic_ai", "prompt_engineering"}:
        covered.update({"prompt_engineering"})

    return covered


def _project_evidence_keys(skill: str) -> set[str]:
    normalized = _normalize_skill(skill)
    related = {
        "express.js": {"express", "express.js", "node.js", "node"},
        "git": {"git", "github"},
        "javascript": {
            "javascript",
            "typescript",
            "react",
            "react.js",
            "next.js",
            "node.js",
            "express",
            "express.js",
        },
        "node.js": {"node.js", "node", "express", "express.js"},
        "railway/render": {"railway", "render", "deployment", "deployed"},
        "vercel": {"vercel", "deployment", "deployed"},
    }

    return {normalized, *related.get(normalized, set()), *related.get(skill.lower().strip(), set())}


def _project_terms(resume_analysis: Dict[str, Any]) -> list[str]:
    terms: list[str] = []

    for project in resume_analysis.get("projects", []):
        if not isinstance(project, dict):
            continue

        terms.extend(_as_list(project.get("technologies")))
        terms.extend(_as_list(project.get("inferred_skills")))

        for key in ("name", "description"):
            value = project.get(key)
            if isinstance(value, str):
                terms.extend(extract_skills(value))

    return terms


def _project_names_for_skill(resume_analysis: Dict[str, Any], skill: str) -> list[str]:
    normalized_skill = _normalize_skill(skill)
    project_names: list[str] = []

    for project in resume_analysis.get("projects", []):
        if not isinstance(project, dict):
            continue

        project_terms: list[str] = []
        project_terms.extend(_as_list(project.get("technologies")))
        project_terms.extend(_as_list(project.get("inferred_skills")))

        for key in ("name", "description"):
            value = project.get(key)
            if isinstance(value, str):
                project_terms.extend(extract_skills(value))

        project_norm = _normalized_set(project_terms)
        if project_norm & _project_evidence_keys(skill):
            name = str(project.get("name") or "").strip()
            if name:
                project_names.append(name)

    return sorted(set(project_names))


def _format_project_evidence(project_names: list[str]) -> str:
    if len(project_names) == 1:
        return f"Used in the {project_names[0]} project."

    if len(project_names) == 2:
        return f"Used in the {project_names[0]} and {project_names[1]} projects."

    return (
        f"Used across {', '.join(project_names[:-1])}, "
        f"and {project_names[-1]} projects."
    )


def _has_generic_evidence(evidence: Any) -> bool:
    if not isinstance(evidence, str):
        return True

    lowered = evidence.lower()
    generic_markers = (
        "listed in technical skills",
        "skills section",
        "project-level evidence is limited",
        "listed or inferred from resume skills/projects",
    )

    return any(marker in lowered for marker in generic_markers)


def _resume_skills(state: HireLoopState) -> list[str]:
    resume_analysis = state.get("resume_analysis", {})
    skills = [
        *_as_list(resume_analysis.get("skills")),
        *_project_terms(resume_analysis),
        *extract_skills(state.get("resume_text", "")),
    ]

    return sorted({skill.lower() for skill in skills if skill})


def _jd_skills(state: HireLoopState) -> list[str]:
    jd_analysis = state.get("jd_analysis", {})
    skills = [
        *_as_list(jd_analysis.get("required_skills")),
        *_as_list(jd_analysis.get("preferred_skills")),
        *extract_skills(state.get("job_description", "")),
    ]

    return sorted({skill.lower() for skill in skills if skill})


def _match_record_values(value: Any) -> list[str]:
    record = value if isinstance(value, dict) else {}
    values: list[str] = []

    for item in record.values():
        if isinstance(item, str):
            values.append(item)
        elif isinstance(item, list):
            values.extend(_as_list(item))

    return values


def _semantic_evidence_keys(value: Any) -> list[str]:
    record = value if isinstance(value, dict) else {}
    return [str(key).strip() for key in record if str(key).strip()]


def _resume_capability_norms(state: HireLoopState) -> set[str]:
    resume_analysis = state.get("resume_analysis", {})
    text = f"{state.get('resume_text', '')} {json.dumps(resume_analysis)}".lower()

    rules = {
        "backend_development": ["backend", "fastapi", "rest api", "api development"],
        "rest_apis": ["rest api", "restful api", "api design", "api development", "fastapi"],
        "sql_databases": ["postgresql", "mysql", "sql", "duckdb", "database"],
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
        "rag": [
            "retrievium",
            "rag",
            "retrieval",
            "retrieval system",
            "retrieval systems",
            "hybrid retrieval",
            "retrieval augmented generation",
            "retrieval-augmented generation",
            "semantic search",
            "pgvector",
        ],
        "cloud": ["aws", "gcp", "azure", "amazon web services", "google cloud"],
    }

    caps = set()
    for capability, keywords in rules.items():
        if any(keyword in text for keyword in keywords):
            caps.add(capability)

    return caps


def _fallback_matching(state: HireLoopState) -> Dict[str, Any]:
    resume_norm = _normalized_set(_resume_skills(state)) | _resume_capability_norms(state)
    jd_norm = _normalized_set(_jd_skills(state))

    matched_norm = resume_norm & jd_norm
    covered_norm = _covered_skill_norms(matched_norm)
    missing_norm = jd_norm - matched_norm - covered_norm

    matched_skills = sorted({_pretty_skill(skill) for skill in matched_norm})
    missing_skills = sorted({_pretty_skill(skill) for skill in missing_norm})

    total = len(matched_norm) + len(missing_norm)
    match_score = round((len(matched_norm) / total) * 100, 2) if total else 0

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "semantic_matches": {},
        "partial_matches": {},
        "match_score": match_score,
        "reasoning_summary": (
            "The resume shows meaningful alignment with the role through supported "
            "technical skills, while several JD-requested areas still need stronger evidence."
        ),
    }


def _sanitize_matching(
    state: HireLoopState,
    matching_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    resume_norm = _normalized_set(_resume_skills(state)) | _resume_capability_norms(state)
    jd_norm = _normalized_set(_jd_skills(state))
    llm_matched_norm = _normalized_set(_as_list(matching_analysis.get("matched_skills")))
    semantic_matched_norm = _normalized_set(
        [
            *_match_record_values(matching_analysis.get("semantic_matches")),
            *_semantic_evidence_keys(matching_analysis.get("semantic_evidence")),
        ]
    )

    matched_norm = (
        (llm_matched_norm & jd_norm)
        | (semantic_matched_norm & jd_norm)
        | (resume_norm & jd_norm)
    )
    covered_norm = _covered_skill_norms(matched_norm | llm_matched_norm | resume_norm)
    missing_norm = jd_norm - matched_norm - covered_norm

    matched_skills = sorted({_pretty_skill(skill) for skill in matched_norm})
    missing_skills = sorted({_pretty_skill(skill) for skill in missing_norm})

    total = len(matched_norm) + len(missing_norm)
    match_score = round((len(matched_norm) / total) * 100, 2) if total else 0

    matching_analysis["matched_skills"] = matched_skills
    matching_analysis["missing_skills"] = missing_skills
    matching_analysis["match_score"] = match_score

    return matching_analysis


def _summarize_skills(skills: list[str], limit: int = 6) -> str:
    if not skills:
        return "none"

    shown = skills[:limit]
    if len(skills) <= limit:
        return ", ".join(shown)

    return f"{', '.join(shown)} and {len(skills) - limit} more"


def _build_reasoning_summary(matching_analysis: Dict[str, Any]) -> str:
    matched_skills = _as_list(matching_analysis.get("matched_skills"))
    missing_skills = _as_list(matching_analysis.get("missing_skills"))
    score = matching_analysis.get("match_score")

    if isinstance(score, (int, float)):
        score_text = f"{round(score)}%"
    else:
        score_text = "the current"

    matched_text = _summarize_skills(matched_skills)
    missing_text = _summarize_skills(missing_skills, limit=5)

    if missing_skills:
        return (
            f"The resume matches {len(matched_skills)} JD-requested skill areas "
            f"for a {score_text} fit. Strongest evidence includes {matched_text}. "
            f"Remaining gaps include {missing_text}."
        )

    return (
        f"The resume matches {len(matched_skills)} JD-requested skill areas "
        f"for a {score_text} fit. Strongest evidence includes {matched_text}. "
        "No major skill gaps were identified."
    )


def _fallback_evidence(state: HireLoopState) -> Dict[str, Any]:
    resume_analysis = state.get("resume_analysis", {})
    matching_analysis = state.get("matching_analysis", {})
    resume_evidence = (
        resume_analysis.get("evidence")
        if isinstance(resume_analysis.get("evidence"), dict)
        else {}
    )

    skill_evidence = {}
    for skill in _as_list(matching_analysis.get("matched_skills")):
        project_names = _project_names_for_skill(resume_analysis, skill)
        if project_names:
            skill_evidence[skill] = _format_project_evidence(project_names)
            continue

        skill_evidence[skill] = resume_evidence.get(
            skill,
            "Listed in the parsed resume skills/tools section; no project-level usage is visible in the parsed project blocks.",
        )

    return {
        "skill_evidence": skill_evidence,
        "top_strengths": _as_list(matching_analysis.get("matched_skills"))[:5],
        "weak_or_inferred_matches": {},
        "missing_skill_explanations": {
            skill: "Not clearly shown in the resume."
            for skill in _as_list(matching_analysis.get("missing_skills"))
        },
    }


def _sanitize_evidence(
    state: HireLoopState,
    evidence_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    resume_analysis = state.get("resume_analysis", {})
    matching_analysis = state.get("matching_analysis", {})
    raw_skill_evidence = evidence_analysis.get("skill_evidence")
    skill_evidence = raw_skill_evidence if isinstance(raw_skill_evidence, dict) else {}

    skills = [
        *skill_evidence.keys(),
        *_as_list(matching_analysis.get("matched_skills")),
    ]

    repaired_evidence: Dict[str, Any] = {}
    for skill in sorted({str(item).strip() for item in skills if str(item).strip()}):
        current_evidence = skill_evidence.get(skill)
        project_names = _project_names_for_skill(resume_analysis, skill)

        if project_names and _has_generic_evidence(current_evidence):
            repaired_evidence[skill] = _format_project_evidence(project_names)
        elif _has_generic_evidence(current_evidence):
            repaired_evidence[skill] = (
                "Listed in the parsed resume skills/tools section; no project-level "
                "usage is visible in the parsed project blocks."
            )
        elif current_evidence:
            repaired_evidence[skill] = current_evidence
        elif project_names:
            repaired_evidence[skill] = _format_project_evidence(project_names)
        else:
            repaired_evidence[skill] = (
                "Listed in the parsed resume skills/tools section; no project-level "
                "usage is visible in the parsed project blocks."
            )

    evidence_analysis["skill_evidence"] = repaired_evidence
    return evidence_analysis


def resume_node(state: HireLoopState):
    return {
        "resume_analysis": extract_resume_information(state["resume_text"])
    }


def jd_node(state: HireLoopState):
    return {
        "jd_analysis": extract_jd_information(state["job_description"])
    }


def company_node(state: HireLoopState):
    return {
        "company_info": get_company_info(state["company_name"])
    }


def matching_node(state: HireLoopState):
    matching_analysis = match_resume_to_jd(
        state["resume_analysis"],
        state["jd_analysis"]
    )

    if (
        matching_analysis.get("error")
        or (
            not matching_analysis.get("matched_skills")
            and not matching_analysis.get("missing_skills")
        )
    ):
        matching_analysis = _fallback_matching(state)

    matching_analysis = _sanitize_matching(state, matching_analysis)

    print("\nWORKFLOW FINAL MATCHED")
    print(matching_analysis["matched_skills"])

    print("\nWORKFLOW FINAL MISSING")
    print(matching_analysis["missing_skills"])

    print("\nWORKFLOW FINAL SCORE")
    print(matching_analysis["match_score"])

    matching_analysis["reasoning_summary"] = _build_reasoning_summary(matching_analysis)

    return {
        "matching_analysis": matching_analysis
    }


def evidence_node(state: HireLoopState):
    evidence_analysis = generate_evidence(
        state["resume_analysis"],
        state["matching_analysis"]
    )

    if evidence_analysis.get("error") or not evidence_analysis.get("skill_evidence"):
        evidence_analysis = _fallback_evidence(state)

    evidence_analysis = _sanitize_evidence(state, evidence_analysis)

    return {
        "evidence_analysis": evidence_analysis
    }


def suggestion_node(state: HireLoopState):
    return {
        "suggestion_analysis": generate_resume_suggestions(
            resume_analysis=state["resume_analysis"],
            jd_analysis=state["jd_analysis"],
            matching_analysis=state["matching_analysis"],
            evidence_analysis=state["evidence_analysis"]
        )
    }


def build_hireloop_graph():
    graph = StateGraph(HireLoopState)

    graph.add_node("resume_agent", resume_node)
    graph.add_node("jd_agent", jd_node)
    graph.add_node("company_research_agent", company_node)
    graph.add_node("semantic_matching_agent", matching_node)
    graph.add_node("evidence_agent", evidence_node)
    graph.add_node("resume_suggestion_agent", suggestion_node)

    graph.set_entry_point("resume_agent")

    graph.add_edge("resume_agent", "jd_agent")
    graph.add_edge("jd_agent", "company_research_agent")
    graph.add_edge("company_research_agent", "semantic_matching_agent")
    graph.add_edge("semantic_matching_agent", "evidence_agent")
    graph.add_edge("evidence_agent", "resume_suggestion_agent")
    graph.add_edge("resume_suggestion_agent", END)

    return graph.compile()


hireloop_graph = build_hireloop_graph()
