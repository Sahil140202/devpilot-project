import json
import sys
from pathlib import Path
from devpilot.agent import run_agent

def main(repo: str):
    questions = json.loads((Path(__file__).parent / "questions.json").read_text())
    passed, total_tokens, total_secs = 0, 0, 0.0

    results = []

    for i, item in enumerate(questions, 1):
        r = run_agent(item["q"], repo, verbose=False)
        answer = r["answer"].lower()
        ok = all(e.lower() in answer for e in item["expect"])
        if "expect_start" in item:
            ok = ok and answer.lstrip("*# ").startswith(item["expect_start"].lower())
        passed += ok
        total_tokens += r["tokens"]
        total_secs += r["seconds"]
        print(f"{i:>2}. {'PASS' if ok else 'FAIL'}  "
              f"{r['calls']} calls  {r['tokens']} tok  {r['seconds']}s  | {item['q']}")
        results.append({"q": item["q"], "type": item.get("type"), "ok": ok, **r})
        if not ok:
            print(f"      expected: {item['expect']}")

    n = len(questions)
    print(f"\nScore: {passed}/{n} ({100*passed//n}%)  "
          f"avg {total_tokens//n} tok, avg {total_secs/n:.0f}s per question")
    out = Path(__file__).parent / "last_run.json"
    out.write_text(json.dumps(results, indent=2))

if __name__ == "__main__":
    main(sys.argv[1])