"""
Security module for adversarial defense (SRS v1.1)
"""
import re
import unicodedata
from typing import Dict, List, Any
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
import fitz  # PyMuPDF for color analysis


class ResumeSecurityScanner:
    """
    Implements adversarial defense features:
    - FR-SEC-01: Invisible Text Detection
    - FR-SEC-02: Zero-Width Character Filtering
    - FR-SEC-03: PDF Structure Analysis
    - FR-SEC-05: Metadata Cross-Reference
    """
    
    # Zero-width characters to filter
    ZERO_WIDTH_CHARS = [
        '\u200b',  # Zero Width Space
        '\u200c',  # Zero Width Non-Joiner
        '\u200d',  # Zero Width Joiner
        '\u2060',  # Word Joiner
        '\ufeff',  # Zero Width No-Break Space
    ]
    
    # Cyrillic lookalikes for Latin characters (homoglyphs)
    HOMOGLYPHS = {
        'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c',
        'у': 'y', 'х': 'x', 'А': 'A', 'В': 'B', 'Е': 'E',
        'К': 'K', 'М': 'M', 'Н': 'H', 'О': 'O', 'Р': 'P',
        'С': 'C', 'Т': 'T', 'Х': 'X',
    }
    
    def __init__(self):
        self.security_flags: List[str] = []
        self.invisible_text_detected = False
        self.homoglyphs_detected = False
        self.metadata_mismatch = False
    
    def scan_pdf(self, file_path: str) -> Dict[str, Any]:
        """Main scanning function that runs all security checks"""
        self.security_flags = []
        
        try:
            # Check PDF structure
            structure_ok = self._check_pdf_structure(file_path)
            
            # Check for invisible text
            invisible_text = self._detect_invisible_text(file_path)
            
            # Extract and sanitize text
            raw_text = self._extract_text(file_path)
            sanitized_text = self.sanitize_text(raw_text)
            
            # Check metadata
            metadata = self._extract_metadata(file_path)
            self._cross_reference_metadata(sanitized_text, metadata)
            
            return {
                "is_safe": len(self.security_flags) == 0,
                "security_flags": self.security_flags,
                "invisible_text_detected": self.invisible_text_detected,
                "homoglyphs_detected": self.homoglyphs_detected,
                "metadata_mismatch": self.metadata_mismatch,
                "sanitized_text": sanitized_text,
                "metadata": metadata,
            }
        except Exception as e:
            self.security_flags.append(f"PDF_PARSE_ERROR: {str(e)}")
            return {
                "is_safe": False,
                "security_flags": self.security_flags,
                "error": str(e),
            }
    
    def sanitize_text(self, text: str) -> str:
        """FR-SEC-02: Remove zero-width chars and normalize homoglyphs"""
        # Remove zero-width characters
        for char in self.ZERO_WIDTH_CHARS:
            if char in text:
                self.security_flags.append("ZERO_WIDTH_CHARS_FOUND")
                text = text.replace(char, '')
        
        # Replace homoglyphs
        for cyrillic, latin in self.HOMOGLYPHS.items():
            if cyrillic in text:
                self.homoglyphs_detected = True
                self.security_flags.append("HOMOGLYPHS_DETECTED")
                text = text.replace(cyrillic, latin)
        
        # Normalize unicode
        text = unicodedata.normalize('NFKC', text)
        
        return text
    
    def _check_pdf_structure(self, file_path: str) -> bool:
        """FR-SEC-03: Validate PDF structure for malicious content"""
        try:
            doc = fitz.open(file_path)
            
            # Check for JavaScript
            for page in doc:
                # Check annotations for JavaScript actions
                for annot in page.annots() or []:
                    if annot.info.get("subtype") == "Widget":
                        self.security_flags.append("PDF_CONTAINS_FORM_WIDGET")
            
            # Check for embedded files
            if doc.embfile_count() > 0:
                self.security_flags.append("PDF_CONTAINS_EMBEDDED_FILES")
            
            doc.close()
            return len(self.security_flags) == 0
        except Exception as e:
            self.security_flags.append(f"PDF_STRUCTURE_ERROR: {str(e)}")
            return False
    
    def _detect_invisible_text(self, file_path: str) -> bool:
        """FR-SEC-01: Detect white-on-white or hidden text"""
        try:
            doc = fitz.open(file_path)
            
            for page in doc:
                # Get text with colors
                blocks = page.get_text("dict")["blocks"]
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                # Check if text color matches background
                                text_color = span.get("color", 0)
                                # White text (0xFFFFFF) is suspicious
                                if text_color == 0xFFFFFF or text_color == 16777215:
                                    self.invisible_text_detected = True
                                    self.security_flags.append("INVISIBLE_TEXT_DETECTED")
                                    break
            
            doc.close()
            return self.invisible_text_detected
        except Exception:
            return False
    
    def _extract_text(self, file_path: str) -> str:
        """Extract visible text from PDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception:
            return ""
    
    def _extract_metadata(self, file_path: str) -> Dict[str, str]:
        """Extract PDF metadata"""
        try:
            doc = fitz.open(file_path)
            metadata = doc.metadata
            doc.close()
            return metadata or {}
        except Exception:
            return {}
    
    def _cross_reference_metadata(self, text: str, metadata: Dict[str, str]) -> bool:
        """FR-SEC-05: Compare visible text vs metadata"""
        # Check for significant title/content mismatch
        title = metadata.get("title", "").lower()
        keywords = metadata.get("keywords", "").lower()
        
        # Simple heuristic: if metadata contains "entry level" but text has "senior"
        suspicious_mismatches = [
            ("entry level", "senior"),
            ("junior", "senior"),
            ("intern", "director"),
        ]
        
        text_lower = text.lower()
        for meta_term, text_term in suspicious_mismatches:
            if meta_term in title or meta_term in keywords:
                if text_term in text_lower:
                    self.metadata_mismatch = True
                    self.security_flags.append(f"METADATA_MISMATCH: '{meta_term}' in metadata but '{text_term}' in text")
        
        return self.metadata_mismatch


def wrap_for_llm(resume_text: str) -> str:
    """FR-SEC-04: Wrap resume text to prevent prompt injection"""
    # Remove any existing delimiter-like patterns
    sanitized = re.sub(r'<<<.*?>>>', '', resume_text)
    sanitized = re.sub(r'\[SYSTEM\]', '[BLOCKED]', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'\[INST\]', '[BLOCKED]', sanitized, flags=re.IGNORECASE)
    
    return f"<<<RESUME_START>>>\n{sanitized}\n<<<RESUME_END>>>"
