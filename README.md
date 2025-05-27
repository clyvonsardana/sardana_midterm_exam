# sardana_midterm_exam

# Enhancing Teacher Efficiency Through  Implementation of Language-Vision Model

TThe recruitment of qualified teachers happens in a way that is critical particularly within the school (MATS). However, existing Human Resource (HR) processes often do 
suffer from inefficiencies in that resumes are manually screened plus evaluations are subjective and selection timelines are prolonged. 
These challenges certainly obstruct timely staffing. Candidate assessments' quality as well as consistency are also compromised.

## Prerequisites

1. Python 3.11.1
2. Visual Studio Code
3. Ollama

## Run the following commands
1. ollama run llava
2. ollama run llama2
3. ollama pull llava
4. ollama pull llama2
5. ollama run mistral
6. ollama list 
7. ollama serve 
8. pip install PyPDF
9. install reportlab

## Final Step: Run the Script

python scripts/resume_screener.py

# Criteria for screening resumes 

        1. Required Education (degrees, certifications)
        2. Required Experience (years, type)
        3. Required Skills and Competencies
        4. Preferred Qualifications
        5. Any specific requirements (licenses, endorsements)

# Score Interpretation
1.	80-100: 🟢 Strong Hire - Excellent match for position
2.	70-79: 🟢 Hire - Good match, recommend interview
3.	50-69: 🟡 Consider - Some qualifications missing
4.	0-49: 🔴 Not Recommended - Poor match for position






        

