import json
from pathlib import Path
from devpilot.llm import LLMClient

SYSTEM = ("You are answering questions about the Spring PetClinic Java project. "
          "You have NO file access. Answer from your own knowledge, concisely.")

def main():
    questions = json.loads((Path(__file__).parent / "questions.json").read_text())
    llm = LLMClient()
    passed = 0

    for i, item in enumerate(questions, 1):
        msg = llm.chat(
            [{"role": "system", "content": SYSTEM},
             {"role": "user", "content": item["q"]}],
            max_tokens=4000,
        )
        answer = (msg.content or "").lower()
        ok = all(e.lower() in answer for e in item["expect"])
        if "expect_start" in item:
            ok = ok and answer.lstrip("*# ").startswith(item["expect_start"].lower())
        passed += ok
        print(f"{i:>2}. {'PASS' if ok else 'FAIL'}  | {item['q']}")

    n = len(questions)
    print(f"\nNo-tools score: {passed}/{n} ({100*passed//n}%)")

if __name__ == "__main__":
    main()