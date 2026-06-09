from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from utils import (
    extract_text_from_pdf,
    extract_skills,
    compare_skills,
    get_company_info
)
from schemas import (
    AnalyzeResponse,
    AIAnalyzeResponse,
    FullAIAnalyzeResponse,
    MatchingAIAnalyzeResponse,
    EvidenceAIAnalyzeResponse,
    SuggestionAIAnalyzeResponse,
    LangGraphAnalyzeResponse
)


app = FastAPI(title="HireLoop Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "HireLoop backend running"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    company_name: str = Form(...)
):

    file_bytes = await resume.read()

    resume_text = extract_text_from_pdf(file_bytes)

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    matched_skills, missing_skills, match_score = compare_skills(
        resume_skills,
        jd_skills
    )

    company_info = get_company_info(company_name)

    return {
        "resume_text": resume_text,
        "job_description": job_description,
        "company_name": company_name,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_score": match_score,
        "company_info": company_info
    }


@app.post("/analyze-ai", response_model=AIAnalyzeResponse)
async def analyze_resume_ai(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    company_name: str = Form(...)
):
    from agents.resume_agent import extract_resume_information

    file_bytes = await resume.read()

    resume_text = extract_text_from_pdf(file_bytes)

    resume_analysis = extract_resume_information(resume_text)

    return {
        "resume_text": resume_text,
        "job_description": job_description,
        "company_name": company_name,
        "resume_analysis": resume_analysis
    }


@app.post("/analyze-full-ai", response_model=FullAIAnalyzeResponse)
async def analyze_full_ai(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    company_name: str = Form(...)
):
    from agents.resume_agent import extract_resume_information
    from agents.jd_agent import extract_jd_information

    file_bytes = await resume.read()
    resume_text = extract_text_from_pdf(file_bytes)

    resume_analysis = extract_resume_information(resume_text)
    jd_analysis = extract_jd_information(job_description)

    return {
        "resume_text": resume_text,
        "job_description": job_description,
        "company_name": company_name,
        "resume_analysis": resume_analysis,
        "jd_analysis": jd_analysis
    }


@app.post("/analyze-match-ai", response_model=MatchingAIAnalyzeResponse)
async def analyze_match_ai(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    company_name: str = Form(...)
):
    from agents.resume_agent import extract_resume_information
    from agents.jd_agent import extract_jd_information
    from agents.matching_agent import match_resume_to_jd

    file_bytes = await resume.read()
    resume_text = extract_text_from_pdf(file_bytes)

    resume_analysis = extract_resume_information(resume_text)
    jd_analysis = extract_jd_information(job_description)

    matching_analysis = match_resume_to_jd(
        resume_analysis=resume_analysis,
        jd_analysis=jd_analysis
    )

    return {
        "resume_text": resume_text,
        "job_description": job_description,
        "company_name": company_name,
        "resume_analysis": resume_analysis,
        "jd_analysis": jd_analysis,
        "matching_analysis": matching_analysis
    }


@app.post("/analyze-evidence-ai", response_model=EvidenceAIAnalyzeResponse)
async def analyze_evidence_ai(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    company_name: str = Form(...)
):
    from agents.resume_agent import extract_resume_information
    from agents.jd_agent import extract_jd_information
    from agents.matching_agent import match_resume_to_jd
    from agents.evidence_agent import generate_evidence

    file_bytes = await resume.read()
    resume_text = extract_text_from_pdf(file_bytes)

    resume_analysis = extract_resume_information(resume_text)
    jd_analysis = extract_jd_information(job_description)

    matching_analysis = match_resume_to_jd(
        resume_analysis=resume_analysis,
        jd_analysis=jd_analysis
    )

    evidence_analysis = generate_evidence(
        resume_analysis=resume_analysis,
        matching_analysis=matching_analysis
    )

    return {
        "resume_text": resume_text,
        "job_description": job_description,
        "company_name": company_name,
        "resume_analysis": resume_analysis,
        "jd_analysis": jd_analysis,
        "matching_analysis": matching_analysis,
        "evidence_analysis": evidence_analysis
    }


@app.post("/analyze-suggestion-ai", response_model=SuggestionAIAnalyzeResponse)
async def analyze_suggestion_ai(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    company_name: str = Form(...)
):
    from agents.resume_agent import extract_resume_information
    from agents.jd_agent import extract_jd_information
    from agents.matching_agent import match_resume_to_jd
    from agents.evidence_agent import generate_evidence
    from agents.resume_suggestion_agent import generate_resume_suggestions

    file_bytes = await resume.read()
    resume_text = extract_text_from_pdf(file_bytes)

    resume_analysis = extract_resume_information(resume_text)
    jd_analysis = extract_jd_information(job_description)

    matching_analysis = match_resume_to_jd(
        resume_analysis=resume_analysis,
        jd_analysis=jd_analysis
    )

    evidence_analysis = generate_evidence(
        resume_analysis=resume_analysis,
        matching_analysis=matching_analysis
    )

    suggestion_analysis = generate_resume_suggestions(
        resume_analysis=resume_analysis,
        jd_analysis=jd_analysis,
        matching_analysis=matching_analysis,
        evidence_analysis=evidence_analysis
    )

    return {
        "resume_text": resume_text,
        "job_description": job_description,
        "company_name": company_name,
        "resume_analysis": resume_analysis,
        "jd_analysis": jd_analysis,
        "matching_analysis": matching_analysis,
        "evidence_analysis": evidence_analysis,
        "suggestion_analysis": suggestion_analysis
    }


@app.post("/analyze-langgraph", response_model=LangGraphAnalyzeResponse)
async def analyze_langgraph(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    company_name: str = Form(...)
):
    from agents.workflow import hireloop_graph

    file_bytes = await resume.read()
    resume_text = extract_text_from_pdf(file_bytes)

    result = hireloop_graph.invoke({
        "resume_text": resume_text,
        "job_description": job_description,
        "company_name": company_name,
        "resume_analysis": {},
        "jd_analysis": {},
        "company_info": {},
        "matching_analysis": {},
        "evidence_analysis": {},
        "suggestion_analysis": {}
    })

    return result
