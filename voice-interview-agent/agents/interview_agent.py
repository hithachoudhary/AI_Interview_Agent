from typing import List 
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationChain
from langchain_core.prompts import MessagesPlaceholder

# Creates a conversation-based interview agent with short-term memory
class InterviewAgent:
    def __init__(self, role: str):
        self.role = role
        self.memory = ConversationBufferMemory(k=3, memory_key="history", return_messages=True)
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        
        system_prompt = (
            "You are a professional and objective human interviewer for a **{role}** position. "
            "Your goal is to conduct a realistic mock interview. "
            "You must only ask one question or provide one follow-up per turn. "
            "If the user's answer is vague or lacks detail, ask a highly contextual follow-up. "
            "If the user goes off-topic, gently steer the conversation back. "
            "Maintain a formal and encouraging tone. Do not provide feedback until the user says 'STOP' or 'END INTERVIEW'."
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt.format(role=role)),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])
        
        self.chain = ConversationChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory
        )

    #Initializing the conversation by asking the first question
    def start_interview(self, initial_question: str) -> str:
        self.memory.save_context({"input": "SETUP"}, {"output": initial_question})
        return initial_question

    def get_response(self, user_input: str) -> str:
        response = self.chain.invoke({"input": user_input})
        return response['response']

    #This will return all the interview turns for evaluation
    def get_full_history(self) -> List[dict]:
        history = []
        for msg in self.memory.buffer_as_messages:
            if msg.content != "SETUP":
                role = "AI" if msg.type == "ai" else "User"
                history.append({"role": role, "content": msg.content})
        return history
