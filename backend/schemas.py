from pydantic import BaseModel
from typing import List, Dict, Any

class AnalyzeResponse(BaseModel):
    resume_text: str
    job_description: str
    company_name: str
    resume_skills: List[str]
    jd_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    match_score: float
    company_info: Dict[str, Any]

class AIAnalyzeResponse(BaseModel):
    resume_text: str
    job_description: str
    company_name: str
    resume_analysis: Dict[str, Any]

class FullAIAnalyzeResponse(BaseModel):
    resume_text: str
    job_description: str
    company_name: str
    resume_analysis: Dict[str, Any]
    jd_analysis: Dict[str, Any]

class MatchingAIAnalyzeResponse(BaseModel):
    resume_text: str
    job_description: str
    company_name: str
    resume_analysis: Dict[str, Any]
    jd_analysis: Dict[str, Any]
    matching_analysis: Dict[str, Any]

class EvidenceAIAnalyzeResponse(BaseModel):
    resume_text: str
    job_description: str
    company_name: str
    resume_analysis: Dict[str, Any]
    jd_analysis: Dict[str, Any]
    matching_analysis: Dict[str, Any]
    evidence_analysis: Dict[str, Any]

class SuggestionAIAnalyzeResponse(BaseModel):
    resume_text: str
    job_description: str
    company_name: str
    resume_analysis: Dict[str, Any]
    jd_analysis: Dict[str, Any]
    matching_analysis: Dict[str, Any]
    evidence_analysis: Dict[str, Any]
    suggestion_analysis: Dict[str, Any]

class LangGraphAnalyzeResponse(BaseModel):
    resume_text: str
    job_description: str
    company_name: str
    resume_analysis: Dict[str, Any]
    jd_analysis: Dict[str, Any]
    company_info: Dict[str, Any]
    matching_analysis: Dict[str, Any]
    evidence_analysis: Dict[str, Any]
    suggestion_analysis: Dict[str, Any]