# sardana_midterm_exam

# Enhancing Teacher Efficiency Through  Implementation of Language-Vision Model

TThe recruitment of qualified teachers happens in a way that is critical particularly within the school (MATS). However, existing Human Resource (HR) processes often do 
suffer from inefficiencies in that resumes are manually screened plus evaluations are subjective and selection timelines are prolonged. 
These challenges certainly obstruct timely staffing. Candidate assessments' quality as well as consistency are also compromised.

## Prerequisites

Python 3.11.1
Visual Studio Code
Ollama

## Run the following commands
ollama run llava
ollama run llama2
ollama pull llava
ollama pull llama2
ollama run mistral
ollama list 
ollama serve 
pip install PyPDF

## Final Step: Run the Script
python scripts/resume_screener.py

# Criteria for screening resumes 

        1. Required Education (degrees, certifications)
        2. Required Experience (years, type)
        3. Required Skills and Competencies
        4. Preferred Qualifications
        5. Any specific requirements (licenses, endorsements)

# Score Interpretation
•	80-100: 🟢 Strong Hire - Excellent match for position
•	70-79: 🟢 Hire - Good match, recommend interview
•	50-69: 🟡 Consider - Some qualifications missing
•	0-49: 🔴 Not Recommended - Poor match for position






        

