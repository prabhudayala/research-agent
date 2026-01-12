import asyncio
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.agents import Orchestrator, Agent

async def test_orchestration():
    print("Test: Initializing Orchestrator with Mocks...")
    
    # Mocking the Agent.chat method to avoid API calls
    async def mock_chat(self, user_input):
        print(f"  [MockAgent:{self.name}] Input: {user_input[:50]}...")
        if self.name == "Planner":
            return "Introduction\nMain Body\nConclusion"
        elif self.name == "Researcher":
            return "Research data linked to " + user_input
        elif self.name == "Writer":
            return "Draft content for " + user_input
        elif self.name == "Reviewer":
            return "Polished content for " + user_input
        return "Generic response"
    
    # Patching the method dynamically
    original_chat = Agent.chat
    Agent.chat = mock_chat

    try:
        orch = Orchestrator()
        topic = "Test Topic"
        print(f"Test: Running generation for '{topic}'...")
        
        report = await orch.generate_report(topic)
        
        print("\nTest Result:")
        print(f"  Topic: {report['topic']}")
        print(f"  Sections Generated: {len(report['sections'])}")
        for sec in report['sections']:
            print(f"  - {sec['title']}: {sec['content'][:30]}...")
            
        assert report['topic'] == topic
        assert len(report['sections']) == 3
        print("\nSUCCESS: Orchestration logic verified!")
        
    except Exception as e:
        print(f"\nFAILURE: {e}")
    finally:
        Agent.chat = original_chat

if __name__ == "__main__":
    asyncio.run(test_orchestration())
