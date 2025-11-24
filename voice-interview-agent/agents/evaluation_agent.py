from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

#Defining the structured schema for interview feedback
class FeedbackSection(BaseModel):
    area: str = Field(description="The skill area, e.g., 'Communication', 'Technical Knowledge', 'Structure (STAR)'.")
    score_out_of_5: int = Field(description="Score from 1 to 5.")
    summary: str = Field(description="A brief summary of performance in this area.")
    areas_for_improvement: List[str] = Field(description="Specific, actionable steps to improve.")

class InterviewFeedback(BaseModel):
    overall_assessment: str = Field(description="A professional, encouraging summary of the user's overall performance.")
    sections: List[FeedbackSection]

#Core function which will generate the structured interview feedback
def generate_feedback(role: str, conversation_history: List[dict]) -> InterviewFeedback:
    history_str = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation_history])

    feedback_prompt = ChatPromptTemplate.from_messages([
        ("system", 
         """You are an expert Interview Coach. Analyze the mock interview transcript for a {role} role. 
         Generate a structured, objective, and constructive feedback report. 
         Focus on the clarity of answers, depth of technical knowledge, and use of structured methods like STAR. 
         Your output MUST conform strictly to the provided JSON schema."""
        ),
        ("human", 
         f"Mock Interview Transcript for a {role} role:\n\n{history_str}\n\n---Generate the structured feedback report now.---"
        )
    ])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    structured_llm = llm.with_structured_output(InterviewFeedback)
    chain = feedback_prompt | structured_llm
    return chain.invoke({"role": role})
