from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import PyPDF2
import io

app = Flask(__name__)

# Configure Gemini Pro with API key directly
API_KEY = "AIzaSyAuLLG_0OIvAjhTHnizecCx3dOfo4fimXI"  # Replace with your actual API key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def analyze_resume(resume_text):
    prompt = f"""
    Analyze this resume and provide job recommendations with real job listings. Format the response as JSON:
    {{
        "top_skills": ["skill1", "skill2", "skill3"],
        "recommended_jobs": [
            {{
                "title": "Job Title",
                "company": "Company Name",
                "location": "City, State or Remote",
                "match_score": "85%",
                "salary_range": "$XX,XXX - $XX,XXX",
                "job_description": "Brief job description",
                "reasons": [
                    "Reason 1",
                    "Reason 2"
                ],
                "required_skills": ["skill1", "skill2"],
                "missing_skills": ["skill1", "skill2"],
                "application_links": {{
                    "linkedin": "https://www.linkedin.com/jobs/search/?keywords=job_title",
                    "indeed": "https://www.indeed.com/jobs?q=job_title",
                    "glassdoor": "https://www.glassdoor.com/Job/search?keyword=job_title",
                    "company_website": "https://careers.company.com"
                }}
            }}
        ],
        "improvement_areas": [
            "Improvement 1",
            "Improvement 2"
        ],
        "job_search_tips": [
            "Tip 1",
            "Tip 2"
        ]
    }}

    Based on the skills and experience in this resume:
    {resume_text}
    
    Provide real, relevant job titles and companies that match the candidate's profile. Generate appropriate application URLs for LinkedIn, Indeed, and Glassdoor based on the job titles. Ensure the job recommendations are specific and actionable.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Find the first { and last } to extract just the JSON part
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        json_str = response_text[start_idx:end_idx]
        
        return json_str
        
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        raise Exception(f"Analysis failed: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Please upload a PDF file'}), 400
    
    try:
        resume_text = extract_text_from_pdf(file)
        if not resume_text.strip():
            return jsonify({'error': 'Could not extract text from PDF. Please ensure it is not scanned.'}), 400
            
        analysis = analyze_resume(resume_text)
        return jsonify({'analysis': analysis})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)