import os
import time
from openai import OpenAI

MODEL = "Atria-Dawn-Preview"

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://api.atria-asi.ai/v1",
            api_key=os.environ["ATRIA_API_KEY"],
            max_retries=5,
            timeout=120,
        )
        self.total_tokens = 0
        self.calls = 0

    def chat(self, messages, tools=None, max_tokens=8000):
        t0 = time.time()
        resp = self.client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            max_tokens=max_tokens,
        )
        self.calls += 1
        self.total_tokens += resp.usage.total_tokens
        print(f"  [llm call {self.calls}: {time.time()-t0:.1f}s, "
              f"{resp.usage.total_tokens} tok]")
        return resp.choices[0].message