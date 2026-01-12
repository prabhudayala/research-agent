import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.agents import Orchestrator

load_dotenv()

async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY in .env file")
        return

    topic = input("Enter a research topic: ")
    orchestrator = Orchestrator()
    
    print("\n--- Starting Research ---\n")
    report = await orchestrator.generate_report(topic)
    
    print("\n--- Final Report ---\n")
    print(f"Topic: {report['topic']}\n")
    for section in report['sections']:
        print(f"### {section['title']}\n")
        print(f"{section['content']}\n")

if __name__ == "__main__":
    asyncio.run(main())
