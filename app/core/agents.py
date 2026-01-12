import os
import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

# Helpers
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    return AsyncOpenAI(api_key=api_key)

class Agent:
    def __init__(self, name: str, system_prompt: str, model: str = "gpt-3.5-turbo"):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.history = [{"role": "system", "content": system_prompt}]
        self._client = None

    @property
    def client(self):
        if not self._client:
            self._client = get_openai_client()
        return self._client

    async def chat(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self.history
            )
            content = response.choices[0].message.content
            self.history.append({"role": "assistant", "content": content})
            return content
        except Exception as e:
            return f"Error encountered by {self.name}: {e}"

class PlannerAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Planner",
            system_prompt="You are a research planner. Given a topic, break it down into 3-5 distinct sub-topics or sections for a report. Return ONLY the list of sections, one per line, without bullets or numbering."
        )

class ResearcherAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Researcher",
            system_prompt="You are a researcher. You will be given a topic and search results. Summarize the information relevant to the topic. Be concise and factual."
        )
        self.ddgs = DDGS()

    async def research(self, query: str) -> str:
        print(f"[{self.name}] Searching for: {query}")
        try:
            results = self.ddgs.text(query, max_results=3)
            search_context = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
            return await self.chat(f"Topic: {query}\n\nSearch Results:\n{search_context}\n\nSummarize these findings.")
        except Exception as e:
            return f"Search failed: {e}. I'll use my internal knowledge."


class WriterAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Writer",
            system_prompt="You are a technical writer. Write a comprehensive section for a report based on the provided research notes. The style should be professional and informative."
        )

class ReviewerAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Reviewer",
            system_prompt="You are an editor. Review the provided draft for clarity, flow, and consistent tone. Provide a polished version of the text. Return ONLY the polished text."
        )

class Orchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.writer = WriterAgent()
        self.reviewer = ReviewerAgent()

    async def generate_report(self, topic: str) -> Dict[str, Any]:
        print(f"[Orchestrator] Starting report on: {topic}")
        
        # 1. Plan
        plan_text = await self.planner.chat(topic)
        sections = [s.strip() for s in plan_text.split('\n') if s.strip()]
        print(f"[Orchestrator] Plan: {sections}")

        final_sections = []

        # 2. Execute per section
        for section in sections:
            print(f"[Orchestrator] Processing section: {section}")
            
            # Research
            research_notes = await self.researcher.research(f"{topic}: {section}")
            
            # Write
            draft = await self.writer.chat(f"Section: {section}\nNotes: {research_notes}")
            
            # Review
            polished = await self.reviewer.chat(f"Draft:\n{draft}")
            
            final_sections.append({
                "title": section,
                "content": polished
            })

        return {
            "topic": topic,
            "sections": final_sections
        }
