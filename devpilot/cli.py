import sys
from .agent import run_agent

if __name__ == "__main__":
    repo, question = sys.argv[1], " ".join(sys.argv[2:])
    r = run_agent(question, repo)
    print(r["answer"])
    print(f"\n[{r['calls']} calls, {r['tokens']} tokens, {r['seconds']}s]")