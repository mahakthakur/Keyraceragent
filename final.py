import os
from typing import List
from PyPDF2 import PdfReader
from pydantic import BaseModel, Field


from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic import hub
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationChain
from langchain_community.tools.tavily_search import TavilySearchResults



class ResumeAnalysis(BaseModel):
    candidate_name: str = Field(description="The full name of the candidate")
    professional_summary: str = Field(description="A 2-sentence summary of their profile")
    technical_skills: List[str] = Field(description="List of hard skills identified")
    soft_skills: List[str] = Field(description="List of soft skills identified")
    experience_score: int = Field(description="Score from 1-100")
    key_achievements: List[str] = Field(description="Top 3 quantifiable achievements")
    current_gaps: List[str] = Field(description="Skills missing for target role")
    improvement_tips: List[str] = Field(description="Actionable advice for the resume")

# --- PHASE 2: AGENT CLASSES ---

class KeyRacerAnalyzer:
    def __init__(self, api_key: str):
        self.llm = ChatGroq(
            api_key=api_key, 
            model_name="llama-3.1-8b-instant", 
            temperature=0.1
        )
        self.parser = PydanticOutputParser(pydantic_object=ResumeAnalysis)

    def analyze(self, pdf_path: str, role: str):
        reader = PdfReader(pdf_path)
        # Added check for empty pages
        text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        
        template = """
        Analyze this resume for the role of {job_title} based on 2026 standards.
        {format_instructions}
        Content: {content}
        """
        prompt = PromptTemplate(
            template=template,
            input_variables=["content", "job_title"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        chain = prompt | self.llm | self.parser
        return chain.invoke({"content": text, "job_title": role})

class RoadmapAgent:
    def __init__(self, groq_key: str, tavily_key: str):
        os.environ["TAVILY_API_KEY"] = tavily_key
        self.llm = ChatGroq(
            api_key=groq_key, 
            model_name="llama-3.1-8b-instant", 
            temperature=0, 
          
        )
        # Consistent use of TavilySearchResults
        self.tools = [TavilySearchResults(max_results=5)]
        self.prompt = hub.pull("hwchase17/react")
        
        agent = create_react_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            verbose=True, 
            handle_parsing_errors=True,
            max_iterations=8
        )

    def run(self, analysis: ResumeAnalysis, role: str):
        query = f"""
        Objective: Create a 6-month roadmap for {analysis.candidate_name} to become a {role}.
        Gaps: {', '.join(analysis.current_gaps)}.
        Current Skills: {', '.join(analysis.technical_skills)}.
        
        Requirements:
        1. Search for 2026 tools for these gaps.
        2. Monthly breakdown table with: Goal, Project, and Documentation Links.
        """
        return self.executor.invoke({"input": query})["output"]

class CareerSuccessAgent:
    def __init__(self, groq_key: str, tavily_key: str):
        os.environ["TAVILY_API_KEY"] = tavily_key
        # Llama 4 Maverick is highly efficient for structured search-to-table tasks
        self.llm = ChatGroq(
            api_key=groq_key, 
            model_name="meta-llama/llama-4-maverick-17b-128e-instruct", 
            temperature=0.0
        )
        self.tools = [TavilySearchResults(max_results=5)]
        self.prompt = hub.pull("hwchase17/react")
        
        agent = create_react_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            verbose=True, 
            handle_parsing_errors=True
        )

    def find_jobs(self, role: str, skills: List[str]):
        query = (
            f"Search for 5 active 2026 job postings for {role} requiring {', '.join(skills[:3])}. "
            "Return a Markdown table with: Company, Location, Requirements, and Application Link."
        )
        # Consistent invoke pattern
        response = self.executor.invoke({"input": query})
        return response["output"]

class InterviewChatAgent:
    def __init__(self, api_key: str, role: str, report: ResumeAnalysis):
        self.llm = ChatGroq(
            api_key=api_key, 
            model_name="openai/gpt-oss-120b", 
            temperature=0.7
        )
        self.memory = ConversationBufferMemory()
        self.memory.chat_memory.add_ai_message(
            f"Hello {report.candidate_name}. I'm the lead interviewer for the {role} position. Ready?"
        )
        
        template = f"""You are a Senior Technical Interviewer.
        Candidate Summary: {report.professional_summary}
        Target Role: {role}
        
        {{history}}
        Candidate: {{input}}
        Interviewer:"""
        
        prompt = PromptTemplate(input_variables=["history", "input"], template=template)
        self.chain = ConversationChain(llm=self.llm, memory=self.memory, prompt=prompt)

    def chat(self, user_input: str):
        return self.chain.predict(input=user_input)