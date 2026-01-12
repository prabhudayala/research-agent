# print('Hello world')

from openai import AsyncOpenAI
import os
from dotenv import load_dotenv


load_dotenv()

print(os.getenv("OPENAI_API_KEY"))
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Helloo how are you?"}]
            )
content = response.choices[0].message.content

print(content)