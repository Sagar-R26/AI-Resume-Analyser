import os
import streamlit as st
from dotenv import load_dotenv
import builtins
if not hasattr(builtins, "xrange"):
    builtins.xrange = range
import google.generativeai as genai
import pdfplumber
import tempfile
import json
import math
import re

class AIResumeAnalyzer:
    def __init__(self):
        load_dotenv()
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
    
    def extract_text_from_pdf(self, pdf_file):
        text = ""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            if hasattr(pdf_file, 'getbuffer'):
                temp_file.write(pdf_file.getbuffer())
            elif hasattr(pdf_file, 'read'):
                temp_file.write(pdf_file.read())
                pdf_file.seek(0)
            else:
                temp_file.write(pdf_file)
            temp_path = temp_file.name
        
        try:
            try:
                with pdfplumber.open(temp_path) as pdf:
                    for page in pdf.pages:
                        try:
                            import warnings
                            with warnings.catch_warnings():
                                warnings.filterwarnings("ignore", message=".*PDFColorSpace.*")
                                warnings.filterwarnings("ignore", message=".*Cannot convert.*")
                                page_text = page.extract_text()
                                if page_text:
                                    text += page_text + "\n"
                        except Exception as e:
                            if "PDFColorSpace" not in str(e) and "Cannot convert" not in str(e):
                                st.warning(f"Error extracting text from page with pdfplumber: {e}")
            except Exception as e:
                st.warning(f"pdfplumber extraction failed: {e}")
            
            if text.strip():
                os.unlink(temp_path)
                return text.strip()
            
            st.info("Trying PyPDF2 extraction method...")
            try:
                import pypdf
                pdf_text = ""
                with open(temp_path, 'rb') as file:
                    pdf_reader = pypdf.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            pdf_text += page_text + "\n"
                
                if pdf_text.strip():
                    os.unlink(temp_path)
                    return pdf_text.strip()
            except Exception as e:
                st.warning(f"PyPDF2 extraction failed: {e}")
            
            st.warning("Standard text extraction methods failed. Your PDF might be image-based or scanned.")
            
            try:
                import pytesseract
                from pdf2image import convert_from_path
                st.info("Attempting OCR for image-based PDF. This may take a moment...")
                poppler_path = None
                if os.name == 'nt':
                    possible_paths = [
                        r'C:\poppler\Library\bin',
                        r'C:\Program Files\poppler\bin',
                        r'C:\Program Files (x86)\poppler\bin',
                        r'C:\poppler\bin'
                    ]
                    for path in possible_paths:
                        if os.path.exists(path):
                            poppler_path = path
                            st.success(f"Found Poppler at: {path}")
                            break
                    if not poppler_path:
                        st.warning("Poppler not found in common locations. Using default path: C:\\poppler\\Library\\bin")
                        poppler_path = r'C:\poppler\Library\bin'
                
                try:
                    if poppler_path and os.name == 'nt':
                        images = convert_from_path(temp_path, poppler_path=poppler_path)
                    else:
                        images = convert_from_path(temp_path)
                    
                    ocr_text = ""
                    for i, image in enumerate(images):
                        st.info(f"Processing page {i+1} with OCR...")
                        page_text = pytesseract.image_to_string(image)
                        ocr_text += page_text + "\n"
                    
                    if ocr_text.strip():
                        os.unlink(temp_path)
                        return ocr_text.strip()
                    else:
                        st.error("OCR extraction yielded no text. Please check if the PDF contains actual text content.")
                except Exception as e:
                    st.error(f"PDF to image conversion failed: {e}")
                    st.info("If you're on Windows, make sure Poppler is installed and in your PATH.")
                    st.info("Download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases/")
            except ImportError as e:
                st.error(f"OCR libraries not available: {e}")
                st.info("Please install the required OCR libraries:")
                st.code("pip install pytesseract pdf2image")
                st.info("For Windows, also download and install:")
                st.info("1. Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki")
                st.info("2. Poppler: https://github.com/oschwartz10612/poppler-windows/releases/")
            except Exception as e:
                st.error(f"OCR processing failed: {e}")
        
        except Exception as e:
            st.error(f"PDF processing failed: {e}")
        
        try:
            os.unlink(temp_path)
        except:
            pass
        
        st.error("All text extraction methods failed. Please try a different PDF or manually extract the text.")
        return ""
    
    def extract_text_from_docx(self, docx_file):
        from docx import Document
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            temp_file.write(docx_file.getbuffer())
            temp_path = temp_file.name
        text = ""
        try:
            doc = Document(temp_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            st.error(f"Error extracting text from DOCX: {e}")
        os.unlink(temp_path)
        return text
    
    def analyze_resume_with_gemini(self, resume_text, job_description=None, job_role=None):
        if not resume_text:
            return {"error": "Resume text is required for analysis."}
        
        if not self.google_api_key:
            return {"error": "Google API key is not configured. Please add it to your .env file."}
        
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            base_prompt = f"""
            You are an expert resume analyst with deep knowledge of industry standards, job requirements, and hiring practices across various fields. Your task is to provide a comprehensive, detailed analysis of the resume provided.
            
            Please structure your response in the following format:
            
            ## Overall Assessment
            [Provide a detailed assessment of the resume's overall quality, effectiveness, and alignment with industry standards. Include specific observations about formatting, content organization, and general impression. Be thorough and specific.]
            
            ## Professional Profile Analysis
            [Analyze the candidate's professional profile, experience trajectory, and career narrative. Discuss how well their story comes across and whether their career progression makes sense for their apparent goals.]
            
            ## Skills Analysis
            - **Current Skills**: [List ALL skills the candidate demonstrates in their resume, categorized by type (technical, soft, domain-specific, etc.). Be comprehensive.]
            - **Skill Proficiency**: [Assess the apparent level of expertise in key skills based on how they're presented in the resume]
            - **Missing Skills**: [List important skills that would improve the resume for their target role. Be specific and explain why each skill matters.]
            
            ## Experience Analysis
            [Provide detailed feedback on how well the candidate has presented their experience. Analyze the use of action verbs, quantifiable achievements, and relevance to their target role. Suggest specific improvements.]
            
            ## Education Analysis
            [Analyze the education section, including relevance of degrees, certifications, and any missing educational elements that would strengthen their profile.]
            
            ## Key Strengths
            [List 5-7 specific strengths of the resume with detailed explanations of why these are effective]
            
            ## Areas for Improvement
            [List 5-7 specific areas where the resume could be improved with detailed, actionable recommendations]
            
            ## ATS Optimization Assessment
            [Analyze how well the resume is optimized for Applicant Tracking Systems. Provide a specific ATS score from 0-100, with 100 being perfectly optimized. Use this format: "ATS Score: XX/100". Then suggest specific keywords and formatting changes to improve ATS performance.]
            
            ## Recommended Courses/Certifications
            [Suggest 5-7 specific courses or certifications that would enhance the candidate's profile, with a brief explanation of why each would be valuable]
            
            ## Resume Score
            [Provide a score from 0-100 based on the overall quality of the resume. Use this format exactly: "Resume Score: XX/100" where XX is the numerical score. Be consistent with your assessment - a resume with significant issues should score below 60, an average resume 60-75, a good resume 75-85, and an excellent resume 85-100.]
            
            Resume:
            {resume_text}
            """
            
            if job_role:
                base_prompt += f"""
                
                The candidate is targeting a role as: {job_role}
                
                ## Role Alignment Analysis
                [Analyze how well the resume aligns with the target role of {job_role}. Provide specific recommendations to better align the resume with this role.]
                """
            
            if job_description:
                base_prompt += f"""
                
                Additionally, compare this resume to the following job description:
                
                Job Description:
                {job_description}
                
                ## Job Match Analysis
                [Provide a detailed analysis of how well the resume matches the job description, with a match percentage and specific areas of alignment and misalignment]
                
                ## Key Job Requirements Not Met
                [List specific requirements from the job description that are not addressed in the resume, with recommendations on how to address each gap]
                """
            
            response = model.generate_content(base_prompt)
            analysis = response.text.strip()
            
            resume_score = self._extract_score_from_text(analysis)
            ats_score = self._extract_ats_score_from_text(analysis)
            
            return {"analysis": analysis, "resume_score": resume_score, "ats_score": ats_score}
        
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    def _extract_score_from_text(self, analysis_text):
        try:
            if "## Resume Score" in analysis_text:
                score_section = analysis_text.split("## Resume Score")[1].strip()
                score_match = re.search(r'Resume Score:\s*(\d{1,3})/100', score_section)
                if score_match:
                    score = int(score_match.group(1))
                    return max(0, min(score, 100))
                score_match = re.search(r'\b(\d{1,3})\b', score_section)
                if score_match:
                    score = int(score_match.group(1))
                    return max(0, min(score, 100))
            score_match = re.search(r'Resume Score:\s*(\d{1,3})/100', analysis_text)
            if score_match:
                score = int(score_match.group(1))
                return max(0, min(score, 100))
            return 0
        except Exception as e:
            print(f"Error extracting score: {str(e)}")
            return 0
            
    def _extract_ats_score_from_text(self, analysis_text):
        try:
            if "## ATS Optimization Assessment" in analysis_text:
                ats_section = analysis_text.split("## ATS Optimization Assessment")[1].split("##")[0].strip()
                score_match = re.search(r'ATS Score:\s*(\d{1,3})/100', ats_section)
                if score_match:
                    score = int(score_match.group(1))
                    return max(0, min(score, 100))
            return 0
        except Exception as e:
            print(f"Error extracting ATS score: {str(e)}")
            return 0
            
    def analyze_resume(self, resume_text, job_role=None, role_info=None, model="Google Gemini"):
        import traceback
        
        try:
            job_description = None
            if role_info:
                job_description = f"""
                Role: {job_role}
                Description: {role_info.get('description', '')}
                Required Skills: {', '.join(role_info.get('required_skills', []))}
                """
            
            if model == "Google Gemini":
                result = self.analyze_resume_with_gemini(resume_text, job_description, job_role)
                model_used = "Google Gemini"
            else:
                result = self.analyze_resume_with_gemini(resume_text, job_description, job_role)
                model_used = "Google Gemini"
            
            analysis_text = result.get("analysis", "")
            
            strengths = []
            if "## Key Strengths" in analysis_text:
                strengths_section = analysis_text.split("## Key Strengths")[1].split("##")[0].strip()
                strengths = [s.strip().replace("- ", "").replace("* ", "").replace("• ", "") 
                            for s in strengths_section.split("\n") 
                            if s.strip() and (s.strip().startswith("-") or s.strip().startswith("*") or s.strip().startswith("•"))]
            
            weaknesses = []
            if "## Areas for Improvement" in analysis_text:
                weaknesses_section = analysis_text.split("## Areas for Improvement")[1].split("##")[0].strip()
                weaknesses = [w.strip().replace("- ", "").replace("* ", "").replace("• ", "") 
                             for w in weaknesses_section.split("\n") 
                             if w.strip() and (w.strip().startswith("-") or w.strip().startswith("*") or w.strip().startswith("•"))]
            
            suggestions = []
            if "## Recommended Courses" in analysis_text:
                suggestions_section = analysis_text.split("## Recommended Courses")[1].split("##")[0].strip()
                suggestions = [s.strip().replace("- ", "").replace("* ", "").replace("• ", "") 
                                for s in suggestions_section.split("\n") 
                                if s.strip() and (s.strip().startswith("-") or s.strip().startswith("*") or s.strip().startswith("•"))]
            
            score = result.get("resume_score", 0)
            if not score:
                score = self._extract_score_from_text(analysis_text)
            
            ats_score = self._extract_ats_score_from_text(analysis_text)
            
            return {
                "score": score, "ats_score": ats_score,
                "strengths": strengths, "weaknesses": weaknesses,
                "suggestions": suggestions, "full_response": analysis_text,
                "model_used": model_used
            }
            
        except Exception as e:
            print(f"Error in analyze_resume: {str(e)}")
            print(traceback.format_exc())
            return {
                "error": f"Analysis failed: {str(e)}", "score": 0, "ats_score": 0,
                "strengths": ["Unable to analyze resume due to an error."],
                "weaknesses": ["Unable to analyze resume due to an error."],
                "suggestions": ["Try again with a different model or check your resume format."],
                "full_response": f"Error: {str(e)}", "model_used": "Error"
            }
