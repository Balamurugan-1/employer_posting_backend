import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

async def analyze_jobs_with_gemini(user_query: str, jobs_list: list) -> str:
    """
    Sends the user's skills/query and a list of job data to Gemini
    to find the best matches.
    """
    model = genai.GenerativeModel("gemini-2.5-flash") 

    
    prompt = f"""
    You are a helpful Career Advisor AI.
    
    USER PROFILE/QUERY: "{user_query}"
    
    AVAILABLE JOBS (JSON format):
    {jobs_list}
    
    INSTRUCTIONS:
    1. Analyze the user's query against the available jobs.
    2. Select the top 3 best matches.
    3. For each match, explain briefly WHY it fits the user (e.g., "Matches your Python skill").
    4. If no jobs match well, suggest what the user should learn.
    5. Return the response in clean Markdown format.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Service Error: {str(e)}"
    

async def generate_job_description(title: str, company: str, location: str) -> str:
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    Write a professional, engaging Job Description for a {title} role at {company} located in {location}.
    
    Structure:
    1. Brief Role Overview (2-3 sentences)
    2. Key Responsibilities (Bullet points)
    3. Required Skills (Bullet points)
    4. Why Join Us (Short paragraph)
    
    Tone: Professional but exciting.
    Format: Plain text (no markdown symbols like ** or ##, just clean text).
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Could not generate description: {str(e)}"