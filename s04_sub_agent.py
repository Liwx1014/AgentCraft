#!/usr/bin/env python3
"""
s04_subagent.py - Subagents
Spawn a child agent with fresh messages=[]. The child works in its own
context, sharing the filesystem, then returns only a summary to the parent.
    Parent agent                     Subagent
    +------------------+             +------------------+
    | messages=[...]   |             | messages=[]      |  <-- fresh
    |                  |  dispatch   |                  |
    | tool: task       | ---------->| while tool_use:   |
    |   prompt="..."   |            |   call tools      |
    |   description="" |            |   append results  |
    |                  |  summary   |                   |
    |   result = "..." | <--------- | return last text  |
    +------------------+             +------------------+
              |
    Parent context stays clean.
    Subagent context is discarded.
Key insight: "Process isolation gives context isolation for free."
"""
import os
import subprocess
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv(override=True)

ARK_API_KEY = os.getenv("ARK_API_KEY", "")
ARK_BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
ARK_MODEL = os.getenv("ARK_MODEL", "doubao-seed-2-0-lite-260215")

if not ARK_API_KEY:
    raise ValueError("请设置 ARK_API_KEY 环境变量或 .env 文件")

client = OpenAI(api_key=ARK_API_KEY, base_url=ARK_BASE_URL)
MODEL = ARK_MODEL
SYSTEM = f"You are a coding agent at {WORKDIR}. Use the task tool to delegate exploration or subtasks."
SUBAGENT_SYSTEM = f"You are a coding subagent at {WORKDIR}. Complete the given task, then summarize your findings."
# -- Tool implementations shared by parent and child --
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
        lines = safe_path(path).read_text().splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more)"]
        return "\n".join(lines)[:50000]
    except Exception as e:
        return f"Error: {e}"
def run_write(path: str, content: str) -> str:
    try:
        fp = safe_path(path)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content)
        return f"Wrote {len(content)} bytes"
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
TOOL_HANDLERS = {
    "bash":       lambda args: run_bash(args["command"]),
    "read_file":  lambda args: run_read(args["path"], args.get("limit")),
    "write_file": lambda args: run_write(args["path"], args["content"]),
    "edit_file":  lambda args: run_edit(args["path"], args["old_text"], args["new_text"]),
}
# Child gets all base tools except task (no recursive spawning)
CHILD_TOOLS = [
    {"type": "function", "function": {"name": "bash", "description": "Run a shell command.",
     "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read file contents.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Write content to file.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "edit_file", "description": "Replace exact text in file.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}}},
]
# -- Subagent: fresh context, filtered tools, summary-only return --
def run_subagent(prompt: str) -> str:
    sub_messages = [{"role": "user", "content": prompt}]  # fresh context
    for _ in range(30):  # safety limit
        response = client.chat.completions.create(
            model=MODEL, messages=[{"role": "system", "content": SUBAGENT_SYSTEM}] + sub_messages,
            tools=CHILD_TOOLS, max_tokens=8000,
        )
        choice = response.choices[0]
        assistant_msg = choice.message
        sub_messages.append({"role": "assistant", "content": assistant_msg.content, "tool_calls": assistant_msg.tool_calls})
        if not assistant_msg.tool_calls:
            break
        results = []
        for tool_call in assistant_msg.tool_calls:
            import json
            args = json.loads(tool_call.function.arguments)
            handler = TOOL_HANDLERS.get(tool_call.function.name)
            output = handler(args) if handler else f"Unknown tool: {tool_call.function.name}"
            results.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(output)[:50000]})
        sub_messages.extend(results)
    # Only the final text returns to the parent -- child context is discarded
    return assistant_msg.content or "(no summary)"
# -- Parent tools: base tools + task dispatcher --
PARENT_TOOLS = CHILD_TOOLS + [
    {"type": "function", "function": {"name": "task", "description": "Spawn a subagent with fresh context. It shares the filesystem but not conversation history.",
     "parameters": {"type": "object", "properties": {"prompt": {"type": "string"}, "description": {"type": "string", "description": "Short description of the task"}}, "required": ["prompt"]}}},
]
def agent_loop(messages: list):
    while True:
        response = client.chat.completions.create(
            model=MODEL, messages=[{"role": "system", "content": SYSTEM}] + messages,
            tools=PARENT_TOOLS, max_tokens=8000,
        )
        choice = response.choices[0]
        assistant_msg = choice.message
        if assistant_msg.content:
            print(f"\033[32m{assistant_msg.content}\033[0m")
        messages.append({"role": "assistant", "content": assistant_msg.content, "tool_calls": assistant_msg.tool_calls})
        if not assistant_msg.tool_calls:
            return
        results = []
        for tool_call in assistant_msg.tool_calls:
            import json
            args = json.loads(tool_call.function.arguments)
            if tool_call.function.name == "task":
                desc = args.get("description", "subtask")
                print(f"\033[36m> task ({desc}): {args['prompt'][:80]}\033[0m")
                output = run_subagent(args["prompt"])
            else:
                handler = TOOL_HANDLERS.get(tool_call.function.name)
                output = handler(args) if handler else f"Unknown tool: {tool_call.function.name}"
            print(f"\033[33m  {str(output)[:200]}\033[0m")
            results.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(output)})
        messages.extend(results)
if __name__ == "__main__":
    history = []
    while True:
        try:
            query = input("\033[36ms04 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        agent_loop(history)