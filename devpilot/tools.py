import json
import subprocess
from pathlib import Path

MAX_OUTPUT_CHARS = 6000

def _truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return text[:MAX_OUTPUT_CHARS] + f"\n...[truncated, {len(text)} chars total]"

class Toolbox:
    def __init__(self, repo_root: str):
        self.root = Path(repo_root).resolve()

    def _safe(self, rel: str) -> Path:
        p = (self.root / rel).resolve()
        if not p.is_relative_to(self.root):      # block ../ escapes
            raise ValueError("path escapes repo root")
        return p

    def read_file(self, path: str, start_line: int = 1, end_line: int = 200):
        lines = self._safe(path).read_text(errors="replace").splitlines()
        chunk = lines[start_line - 1:end_line]
        numbered = [f"{i}: {l}" for i, l in enumerate(chunk, start_line)]
        return _truncate("\n".join(numbered))

    def list_dir(self, path: str = "."):
        p = self._safe(path)
        entries = sorted(x.name + ("/" if x.is_dir() else "") for x in p.iterdir())
        return _truncate("\n".join(entries))

    def grep_repo(self, pattern: str, glob: str = "*.java"):
        out = subprocess.run(
            ["grep", "-rnE", "--include", glob, pattern, str(self.root)],
            capture_output=True, text=True, timeout=20,
        ).stdout
        out = out.replace(str(self.root) + "/", "")
        return _truncate(out or "no matches")

    def call(self, name: str, args: dict) -> str:
        try:
            return str(getattr(self, name)(**args))
        except Exception as e:                    # return errors to the model
            return f"ERROR: {type(e).__name__}: {e}"

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a file with line numbers. Use start_line/end_line for big files.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"},
            "start_line": {"type": "integer"},
            "end_line": {"type": "integer"}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "list_dir",
        "description": "List entries in a directory relative to the repo root.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}}}}},
    {"type": "function", "function": {
        "name": "grep_repo",
        "description": "Regex search across the repo. Returns file:line:match.",
        "parameters": {"type": "object", "properties": {
            "pattern": {"type": "string"},
            "glob": {"type": "string", "description": "file glob, default *.java"}},
            "required": ["pattern"]}}},
]