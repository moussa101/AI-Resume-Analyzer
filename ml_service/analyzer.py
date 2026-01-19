"""
ML Analyzer - Real semantic similarity scoring
Using sentence-transformers for embeddings and cosine similarity
"""

import re
from typing import List, Dict, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Try to import ML libraries
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False

# Common tech skills for extraction
TECH_SKILLS = {
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "ruby", "go", "rust", "php", "swift", "kotlin",
    # Frontend
    "react", "angular", "vue", "svelte", "next.js", "nextjs", "html", "css", "sass", "tailwind", "bootstrap",
    # Backend
    "node.js", "nodejs", "express", "fastapi", "django", "flask", "spring", "nestjs", "rails",
    # Databases
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb", "sqlite",
    # Cloud & DevOps
    "aws", "gcp", "azure", "docker", "kubernetes", "k8s", "terraform", "ci/cd", "jenkins", "github actions",
    # Data & ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
    # Tools
    "git", "jira", "agile", "scrum", "rest api", "graphql", "microservices"
}


class ResumeAnalyzer:
    """Analyzes resume against job description using semantic similarity"""
    
    def __init__(self):
        self.model = None
        if SENTENCE_TRANSFORMER_AVAILABLE:
            try:
                # Use a lightweight model for faster inference
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Failed to load sentence transformer: {e}")
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from PDF/DOCX file"""
        try:
            if file_path.lower().endswith('.pdf'):
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            elif file_path.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return ""
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract tech skills from text"""
        text_lower = text.lower()
        found_skills = []
        for skill in TECH_SKILLS:
            # Check for skill with word boundaries
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill.title())
        return list(set(found_skills))
    
    def calculate_semantic_similarity(self, resume_text: str, job_description: str) -> float:
        """Calculate semantic similarity using sentence embeddings"""
        if self.model is None:
            # Fallback to keyword matching if no model
            return self._keyword_similarity(resume_text, job_description)
        
        try:
            # Get embeddings
            resume_embedding = self.model.encode([resume_text], convert_to_numpy=True)
            jd_embedding = self.model.encode([job_description], convert_to_numpy=True)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(resume_embedding, jd_embedding)[0][0]
            
            # Convert to percentage (0-100)
            score = float(similarity * 100)
            return max(0, min(100, score))  # Clamp between 0-100
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return self._keyword_similarity(resume_text, job_description)
    
    def _keyword_similarity(self, resume_text: str, job_description: str) -> float:
        """Fallback keyword-based similarity"""
        resume_skills = set(self.extract_skills(resume_text))
        jd_skills = set(self.extract_skills(job_description))
        
        if not jd_skills:
            return 50.0  # Default if no skills found in JD
        
        matched = resume_skills.intersection(jd_skills)
        return (len(matched) / len(jd_skills)) * 100
    
    def find_missing_keywords(self, resume_text: str, job_description: str) -> List[str]:
        """Find keywords in JD that are missing from resume"""
        resume_skills = set(self.extract_skills(resume_text))
        jd_skills = set(self.extract_skills(job_description))
        
        missing = jd_skills - resume_skills
        return [skill.title() for skill in missing]
    
    def analyze(self, file_path: str, job_description: str) -> Dict:
        """Main analysis function"""
        # Extract resume text
        resume_text = self.extract_text_from_file(file_path)
        
        if not resume_text:
            resume_text = "Unable to extract text from file"
        
        # Extract skills
        skills_found = self.extract_skills(resume_text)
        
        # Calculate similarity
        score = self.calculate_semantic_similarity(resume_text, job_description)
        
        # Find missing keywords
        missing_keywords = self.find_missing_keywords(resume_text, job_description)
        
        # Generate feedback
        feedback = self._generate_feedback(score, skills_found, missing_keywords)
        
        return {
            "score": round(score, 1),
            "skills_found": skills_found[:10],  # Top 10 skills
            "missing_keywords": missing_keywords[:8],  # Top 8 missing
            "feedback": feedback,
            "resume_text_length": len(resume_text),
        }
    
    def _generate_feedback(self, score: float, skills: List[str], missing: List[str]) -> Dict:
        """Generate actionable feedback"""
        if score >= 80:
            summary = "Excellent match! Your resume aligns well with the job requirements."
        elif score >= 60:
            summary = "Good match with room for improvement. Consider adding missing skills."
        elif score >= 40:
            summary = "Moderate match. You may need to tailor your resume more specifically."
        else:
            summary = "Low match. Consider gaining experience in the required areas."
        
        suggestions = []
        if missing:
            suggestions.append(f"Add experience with: {', '.join(missing[:3])}")
        if len(skills) < 5:
            suggestions.append("List more technical skills explicitly in a skills section")
        suggestions.append("Quantify achievements with numbers and metrics")
        suggestions.append("Use action verbs to describe accomplishments")
        
        return {
            "summary": summary,
            "suggestions": suggestions[:4]
        }


# Singleton instance
_analyzer = None

def get_analyzer() -> ResumeAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = ResumeAnalyzer()
    return _analyzer
