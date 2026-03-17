#!/usr/bin/env python3
"""
s02_tool_use.py - Tools
The agent loop from s01 didn't change. We just added tools to the array
and a dispatch map to route calls.
    +----------+      +-------+      +------------------+
    |   User   | ---> |  LLM  | ---> | Tool Dispatch    |
    |  prompt  |      |       |      | {                |
    +----------+      +---+---+      |   bash: run_bash |
                          ^          |   read: run_read |
                          |          |   write: run_wr  |
                          +----------+   edit: run_edit |
                          tool_result| }                |
                                     +------------------+
Key insight: "The loop didn't change at all. I just added tools."
"""
import os
import subprocess
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv(override=True)
WORKDIR = Path.cwd()
client = OpenAI(
    api_key="2fd38861-c7d5-4316-99aa-dbf73a48d7b2",
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)
MODEL = "doubao-seed-2-0-lite-260215"

SYSTEM = f"You are a coding agent at {WORKDIR}. Use tools to solve tasks. Act, don't explain."

def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path
def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(command, shell=True, cwd=WORKDIR,
                           capture_output=True, text=True, timeout=120)
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
def run_read(path: str, limit: int = None) -> str:
    try:
        text = safe_path(path).read_text()
        lines = text.splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)[:50000]
    except Exception as e:
        return f"Error: {e}"
def run_write(path: str, content: str) -> str:
    try:
        fp = safe_path(path)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content)
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"
def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        fp = safe_path(path)
        content = fp.read_text()
        if old_text not in content:
            return f"Error: Text not found in {path}"
        fp.write_text(content.replace(old_text, new_text, 1))
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"
# -- The dispatch map: {tool_name: handler} --
TOOL_HANDLERS = {
    "bash":       lambda args: run_bash(args["command"]),
    "read_file":  lambda args: run_read(args["path"], args.get("limit")),
    "write_file": lambda args: run_write(args["path"], args["content"]),
    "edit_file":  lambda args: run_edit(args["path"], args["old_text"], args["new_text"]),
}
TOOLS = [
    {"type": "function", "function": {"name": "bash", "description": "Run a shell command.",
     "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read file contents.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Write content to file.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "edit_file", "description": "Replace exact text in file.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}}},
]
def agent_loop(messages: list):
    while True:
        # Get model response
        response = client.chat.completions.create(
            model=MODEL, messages=[{"role": "system", "content": SYSTEM}] + messages,
            tools=TOOLS, max_tokens=8000,
        )

        # Parse model response
        choice = response.choices[0]
        assistant_msg = choice.message
        if assistant_msg.content is not None:
            print(f"[32m{assistant_msg.content}[0m")

        # Append assistant turn
        messages.append({"role": "assistant", "content": assistant_msg.content, "tool_calls": assistant_msg.tool_calls})
        print(f"Messages: {messages}")
        # If the model didn't call a tool, we're done
        if not assistant_msg.tool_calls:
            return

        # Execute each tool call using dispatch map
        results = []
        for tool_call in assistant_msg.tool_calls:
            import json
            args = json.loads(tool_call.function.arguments)
            handler = TOOL_HANDLERS.get(tool_call.function.name)
            if handler:
                output = handler(args)
                print(f"\033[33m> {tool_call.function.name}: {str(output)[:200]}\033[0m")
            else:
                output = f"Unknown tool: {tool_call.function.name}"
                print(f"\033[31m{output}\033[0m")
            results.append({"role": "tool", "tool_call_id": tool_call.id, "content": output})
        # Append tool results
        messages.extend(results)
if __name__ == "__main__":
    history = []
    while True:
        try:
            query = input("\033[36ms02 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        agent_loop(history)
       