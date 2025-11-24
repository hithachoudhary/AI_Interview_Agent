from langchain_core.tools import tool
import json
import random
import os

#Question data import
file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'questions.json')
try:
    with open(file_path, 'r') as f:
        QUESTION_BANK = json.load(f)
except FileNotFoundError:
    QUESTION_BANK = {}
    print("Warning: questions.json not found. Using fallback questions.")
    
@tool
def get_interview_question(job_role: str) -> str:
    """
    Retrieves a relevant interview question for the specified job role by
    selecting a category (e.g., Behavioral, Technical) and a question.
    """
    role_key = job_role.lower().replace(" ", "_")
    
    if role_key in QUESTION_BANK:
        role_data = QUESTION_BANK[role_key]
        category = random.choice(list(role_data.keys()))
        question = random.choice(role_data[category])
        return f"Let's try a {category} question: {question}"
    else:
        return "Let's start with a general behavioral question: Tell me about yourself and why you applied for this role."
