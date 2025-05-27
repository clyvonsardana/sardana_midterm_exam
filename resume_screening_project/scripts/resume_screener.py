import ollama
import os
import json
from PyPDF2 import PdfReader
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime

class ResumeScreener:
    def __init__(self):
        """Initialize the resume screening system"""
        self.client = ollama.Client()
        self.job_requirements = ""
        self.results = []
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF files"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"❌ Error reading PDF {pdf_path}: {e}")
            return ""
    
    def load_job_requirements(self, job_policy_path):
        """Load and analyze job requirements from policy document"""
        print(f"📋 Loading job requirements from: {job_policy_path}")
        
        # Extract text from job policy
        job_text = self.extract_text_from_pdf(job_policy_path)
        
        if not job_text:
            print("❌ Could not extract text from job policy document")
            return False
        
        # Ask AI to extract key requirements
        prompt = f"""
        Analyze this job policy document and extract the key hiring criteria:
        
        {job_text}
        
        Please extract and list:
        1. Required Education (degrees, certifications)
        2. Required Experience (years, type)
        3. Required Skills and Competencies
        4. Preferred Qualifications
        5. Any specific requirements (licenses, endorsements)
        
        Format your response as clear bullet points.
        """
        
        try:
            response = self.client.chat(
                model='llava',
                messages=[
                    {'role': 'system', 'content': 'You are an HR assistant who extracts job requirements from policy documents.'},
                    {'role': 'user', 'content': prompt}
                ]
            )
            
            self.job_requirements = response['message']['content']
            print("✅ Job requirements extracted successfully!")
            print(f"\n📝 **Job Requirements:**\n{self.job_requirements}\n")
            return True
            
        except Exception as e:
            print(f"❌ Error analyzing job requirements: {e}")
            return False
    
    def screen_pdf_resume(self, resume_path, candidate_name):
        """Screen a PDF resume"""
        print(f"📄 Screening PDF resume: {candidate_name}")
        
        # Extract text from resume
        resume_text = self.extract_text_from_pdf(resume_path)
        
        if not resume_text:
            return {"name": candidate_name, "score": 0, "recommendation": "Could not read resume", "details": "PDF extraction failed"}
        
        # Create screening prompt
        prompt = f"""
        You are a hiring manager screening teaching candidates.
        
        JOB REQUIREMENTS:
        {self.job_requirements}
        
        CANDIDATE RESUME:
        {resume_text}
        
        
        Please evaluate this candidate and provide:
        1. Overall Score (0-100): How well does this candidate match the job requirements?
        2. Recommendation: (Strong Hire / Hire / Consider / Reject)
        3. Strengths: What qualifications does this candidate have?
        4. Weaknesses: What requirements are they missing?
        5. Additional Notes: Any other relevant observations
        
        Be specific and reference both the job requirements and resume content.
        """
        
        try:
            response = self.client.chat(
                model='llava',
                messages=[
                    {'role': 'system', 'content': 'You are an experienced hiring manager for educational positions.'},
                    {'role': 'user', 'content': prompt}
                ]
            )
            
            evaluation = response['message']['content']
            
            # Extract score (basic parsing)
            score = self.extract_score_from_response(evaluation)
            
            return {
                "name": candidate_name,
                "score": score,
                "evaluation": evaluation,
                "file_type": "PDF"
            }
            
        except Exception as e:
            print(f"❌ Error screening resume: {e}")
            return {"name": candidate_name, "score": 0, "evaluation": f"Error: {e}", "file_type": "PDF"}
    
    def screen_image_resume(self, image_path, candidate_name):
        """Screen an image resume (JPG, PNG)"""
        print(f"🖼️ Screening image resume: {candidate_name}")
        
        try:
            # Read image file
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()
            
            prompt = f"""
            You are a hiring manager screening teaching candidates.
            
            JOB REQUIREMENTS:
            {self.job_requirements}
            
            Please analyze the resume image and evaluate this candidate:
            1. Overall Score (0-100): How well does this candidate match the job requirements?
            2. Recommendation: (Strong Hire / Hire / Consider / Reject)
            3. Strengths: What qualifications does this candidate have?
            4. Weaknesses: What requirements are they missing?
            5. Additional Notes: Any other relevant observations
            
            Be specific about what you can read from the resume image.
            """
            
            response = self.client.chat(
                model='llava',
                messages=[
                    {'role': 'system', 'content': 'You are an experienced hiring manager for educational positions.'},
                    {'role': 'user', 'content': prompt}
                ],
                images=[image_bytes]
            )
            
            evaluation = response['message']['content']
            score = self.extract_score_from_response(evaluation)
            
            return {
                "name": candidate_name,
                "score": score,
                "evaluation": evaluation,
                "file_type": "Image"
            }
            
        except Exception as e:
            print(f"❌ Error screening image resume: {e}")
            return {"name": candidate_name, "score": 0, "evaluation": f"Error: {e}", "file_type": "Image"}
    
    def extract_score_from_response(self, response_text):
        """Extract numerical score from AI response"""
        import re
        # Look for patterns like "Score: 85" or "85/100" or "Overall Score (0-100): 75"
        patterns = [
            r'score[:\s]*(\d+)',
            r'(\d+)\/100',
            r'(\d+)\s*points?',
            r'rating[:\s]*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response_text.lower())
            if match:
                score = int(match.group(1))
                return min(score, 100)  # Cap at 100
        
        # Default scoring based on keywords if no number found
        response_lower = response_text.lower()
        if 'strong hire' in response_lower or 'excellent' in response_lower:
            return 85
        elif 'hire' in response_lower or 'recommend' in response_lower:
            return 70
        elif 'consider' in response_lower:
            return 50
        elif 'reject' in response_lower or 'not qualified' in response_lower:
            return 20
        else:
            return 60  # Default middle score
    
    def process_all_resumes(self, resume_folder, job_policy_path):
        """Process all resumes in the folder"""
        print("🚀 Starting resume screening process...\n")
        
        # Load job requirements first
        if not self.load_job_requirements(job_policy_path):
            print("❌ Cannot proceed without job requirements")
            return
        
        # Get all resume files
        resume_files = []
        supported_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.docx']
        
        for filename in os.listdir(resume_folder):
            file_path = os.path.join(resume_folder, filename)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename.lower())
                if ext in supported_extensions:
                    resume_files.append((file_path, filename))
        
        if not resume_files:
            print(f"❌ No supported resume files found in {resume_folder}")
            print(f"Supported formats: {', '.join(supported_extensions)}")
            return
        
        print(f"📁 Found {len(resume_files)} resume files to process\n")
        
        # Process each resume
        for file_path, filename in resume_files:
            candidate_name = os.path.splitext(filename)[0]
            
            if filename.lower().endswith('.pdf'):
                result = self.screen_pdf_resume(file_path, candidate_name)
            elif filename.lower().endswith('.docx'):
                print(f"⚠️ DOCX files not fully supported yet: {filename}")
                continue
            else:  # Image files
                result = self.screen_image_resume(file_path, candidate_name)
            
            self.results.append(result)
            print(f"✅ Completed: {candidate_name} (Score: {result['score']})\n")
        
        # Generate final report
        self.generate_report()
    
    def generate_report(self):
        """Generate and save the final screening report"""
        if not self.results:
            print("❌ No results to report")
            return
        
        # Sort results by score (highest first)
        sorted_results = sorted(self.results, key=lambda x: x['score'], reverse=True)
        
        # Generate report
        report = f"""
# TEACHER RESUME SCREENING REPORT
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## SUMMARY
- Total Candidates Screened: {len(self.results)}
- Average Score: {sum(r['score'] for r in self.results) / len(self.results):.1f}
- Top Score: {max(r['score'] for r in self.results)}
- Recommended Candidates (Score ≥ 70): {len([r for r in self.results if r['score'] >= 70])}

## JOB REQUIREMENTS
{self.job_requirements}

## CANDIDATE RANKINGS

"""
        
        for i, result in enumerate(sorted_results, 1):
            status = "🟢 RECOMMENDED" if result['score'] >= 70 else "🟡 CONSIDER" if result['score'] >= 50 else "🔴 NOT RECOMMENDED"
            
            report += f"""
### {i}. {result['name']} - Score: {result['score']}/100
**Status:** {status}
**File Type:** {result['file_type']}

**Detailed Evaluation:**
{result['evaluation']}

---
"""
        
        # Save report
        os.makedirs('results', exist_ok=True)
        report_path = f"results/screening_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📊 **SCREENING COMPLETE!**")
        print(f"📁 Report saved to: {report_path}")
        print(f"\n🏆 **TOP 3 CANDIDATES:**")
        
        for i, result in enumerate(sorted_results[:3], 1):
            status_emoji = "🟢" if result['score'] >= 70 else "🟡" if result['score'] >= 50 else "🔴"
            print(f"{i}. {status_emoji} {result['name']} - {result['score']}/100")

def main():
    """Main function to run the resume screener"""
    print("=" * 60)
    print("🎯 TEACHER RESUME SCREENING SYSTEM")
    print("=" * 60)
    
    screener = ResumeScreener()
    
    # Configuration
    RESUME_FOLDER = "resumes"
    JOB_POLICY_FILE = "job_descriptions/teacher_job_policy.pdf"  
    
    # Check if folders exist
    if not os.path.exists(RESUME_FOLDER):
        print(f"❌ Resume folder not found: {RESUME_FOLDER}")
        print("Please create the folder and add resume files")
        return
    
    if not os.path.exists(JOB_POLICY_FILE):
        print(f"❌ Job policy file not found: {JOB_POLICY_FILE}")
        print("Please add your job policy document")
        return
    
    # Process all resumes
    screener.process_all_resumes(RESUME_FOLDER, JOB_POLICY_FILE)

if __name__ == "__main__":
    main()