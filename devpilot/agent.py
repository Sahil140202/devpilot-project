import json
import time
from .llm import LLMClient
from .tools import Toolbox, TOOL_SCHEMAS

SYSTEM = """You are a senior Java/Spring Boot engineer helping debug and understand a codebase.
Use the tools to inspect the repo before answering. Prefer grep_repo to locate code, then read_file
for the relevant range. Never guess file contents. When done, answer concisely and cite file:line."""

def run_agent(question: str, repo: str, max_steps: int = 12, verbose: bool = True) -> dict:
    llm = LLMClient()
    tools = Toolbox(repo)
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question},
    ]
    t0 = time.time()
    answer = "Stopped: hit max_steps without a final answer."

    for step in range(max_steps):
        msg = llm.chat(messages, tools=TOOL_SCHEMAS)
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            answer = msg.content or ""
            break

        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            if verbose:
                print(f"  -> {tc.function.name}({args})")
            result = tools.call(tc.function.name, args)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    return {
        "answer": answer,
        "calls": llm.calls,
        "tokens": llm.total_tokens,
        "seconds": round(time.time() - t0, 1),
    }