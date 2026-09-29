import sys
from .agent import run_agent

if __name__ == "__main__":
    repo, question = sys.argv[1], " ".join(sys.argv[2:])
    print(run_agent(question, repo))