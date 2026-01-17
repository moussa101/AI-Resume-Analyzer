"""
AI Resume Analyzer - ML Service
FastAPI application for resume parsing and analysis
With Adversarial Defense (SRS v1.1)
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os

# Security imports
try:
    from security.scanner import ResumeSecurityScanner, wrap_for_llm
except ImportError:
    # Fallback for when security module not yet available
    ResumeSecurityScanner = None
    wrap_for_llm = lambda x: x

app = FastAPI(
    title="AI Resume Analyzer - ML Service",
    description="ML service for resume parsing, NER extraction, and semantic similarity scoring with adversarial defense",
    version="1.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class AnalyzeRequest(BaseModel):
    file_path: str
    job_description: str


class SecurityInfo(BaseModel):
    is_safe: bool
    flags: List[str] = []
    invisible_text_detected: bool = False
    homoglyphs_detected: bool = False
    metadata_mismatch: bool = False


class AnalyzeResponse(BaseModel):
    score: float
    suspicious: bool = False  # NFR-SEC-04: Flag high scores
    suspicious_reason: Optional[str] = None
    security: Optional[SecurityInfo] = None
    skills_found: List[str]
    missing_keywords: List[str]
    contact_info: Optional[dict] = None
    education: Optional[List[dict]] = None
    experience: Optional[List[dict]] = None
    feedback: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    version: str


class SecurityScanResponse(BaseModel):
    is_safe: bool
    security_flags: List[str]
    details: Dict[str, Any]


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", version="1.1.0")


# Security scan endpoint
@app.post("/security-scan", response_model=SecurityScanResponse)
async def security_scan(file_path: str):
    """
    FR-SEC-01 to FR-SEC-05: Security scan for adversarial attacks
    """
    if ResumeSecurityScanner is None:
        raise HTTPException(status_code=500, detail="Security scanner not available")
    
    scanner = ResumeSecurityScanner()
    result = scanner.scan_pdf(file_path)
    
    return SecurityScanResponse(
        is_safe=result.get("is_safe", False),
        security_flags=result.get("security_flags", []),
        details=result
    )


# Main analysis endpoint
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(request: AnalyzeRequest):
    """
    Analyze a resume against a job description.
    Includes adversarial defense checks (SRS v1.1)
    """
    
    # Run security scan if available
    security_info = None
    if ResumeSecurityScanner is not None and os.path.exists(request.file_path):
        scanner = ResumeSecurityScanner()
        scan_result = scanner.scan_pdf(request.file_path)
        security_info = SecurityInfo(
            is_safe=scan_result.get("is_safe", True),
            flags=scan_result.get("security_flags", []),
            invisible_text_detected=scan_result.get("invisible_text_detected", False),
            homoglyphs_detected=scan_result.get("homoglyphs_detected", False),
            metadata_mismatch=scan_result.get("metadata_mismatch", False),
        )
    
    # Placeholder score - will be replaced with actual ML logic
    score = 75.5
    
    # NFR-SEC-04: Anomaly Detection - flag suspiciously high scores
    suspicious = False
    suspicious_reason = None
    if score >= 95.0:
        suspicious = True
        suspicious_reason = "Score >= 95% indicates possible JD copy-paste. Manual review required."
    
    return AnalyzeResponse(
        score=score,
        suspicious=suspicious,
        suspicious_reason=suspicious_reason,
        security=security_info,
        skills_found=["Python", "JavaScript", "React", "SQL"],
        missing_keywords=["Docker", "Kubernetes", "AWS"],
        contact_info={
            "name": "Extracted Name",
            "email": "email@example.com",
            "phone": "+1234567890"
        },
        education=[
            {
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "institution": "University Name",
                "year": "2020"
            }
        ],
        experience=[
            {
                "title": "Software Engineer",
                "company": "Tech Company",
                "duration": "2 years",
                "description": "Developed web applications"
            }
        ],
        feedback={
            "summary": "Good resume with room for improvement",
            "suggestions": [
                "Add more quantifiable achievements",
                "Include Docker and cloud experience",
                "Use more action verbs"
            ]
        }
    )


# Text extraction endpoint
@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """
    Extract text from an uploaded resume file.
    Supports PDF, DOCX, and TXT formats.
    """
    
    allowed_extensions = ['.pdf', '.docx', '.txt']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Placeholder - actual implementation will extract text
    return {
        "filename": file.filename,
        "text": "Extracted text will appear here",
        "status": "success"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

