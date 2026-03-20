#!/usr/bin/env python3
"""
"上下文总会满, 要有办法腾地方" -- 三层压缩策略, 换来无限会话。

问题
上下文窗口是有限的。读一个 1000 行的文件就吃掉 ~4000 token; 读 30 个文件、跑 20 条命令, 轻松突破 100k token。不压缩, 智能体根本没法在大项目里干活。
s06_context_compact.py - Compact
Three-layer compression pipeline so the agent can work forever:
    Every turn:
    +------------------+
    | Tool call result |
    +------------------+
            |
            v
    [Layer 1: micro_compact]        (silent, every turn)
      Replace tool_result content older than last 3
      with "[Previous: used {tool_name}]"
            |
            v
    [Check: tokens > 50000?]
       |               |
       no              yes
       |               |
       v               v
    continue    [Layer 2: auto_compact]
                  Save full transcript to .transcripts/
                  Ask LLM to summarize conversation.
                  Replace all messages with [summary].
                        |
                        v
                [Layer 3: compact tool]
                  Model calls compact -> immediate summarization.
                  Same as auto, triggered manually.
Key insight: "The agent can forget strategically and keep working forever."
"""
import json
import os
import subprocess
import time
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
SYSTEM = f"You are a coding agent at {WORKDIR}. Use tools to solve tasks."
THRESHOLD = 50000
TRANSCRIPT_DIR = WORKDIR / ".transcripts"
KEEP_RECENT = 3
def estimate_tokens(messages: list) -> int:
    """Rough token count: ~4 chars per token."""
    return len(str(messages)) // 4
# -- Layer 1: micro_compact - replace old tool results with placeholders --
def micro_compact(messages: list) -> list:
    # Collect indices for all tool messages (OpenAI format: role="tool")
    tool_indices = []
    for msg_idx, msg in enumerate(messages):
        if msg.get("role") == "tool":
            tool_indices.append(msg_idx)
    if len(tool_indices) <= KEEP_RECENT:
        return messages
    # Find tool_name for each result by matching tool_call_id in prior assistant messages
    tool_name_map = {}
    for msg in messages:
        if msg.get("role") == "assistant":
            tool_calls = msg.get("tool_calls", [])
            for tc in tool_calls:
                if isinstance(tc, dict):
                    tool_name_map[tc.get("id")] = tc.get("function", {}).get("name", "unknown")
    # Clear old results (keep last KEEP_RECENT)
    to_clear = tool_indices[:-KEEP_RECENT]
    for idx in to_clear:
        msg = messages[idx]
        content = msg.get("content", "")
        if isinstance(content, str) and len(content) > 100:
            tool_id = msg.get("tool_call_id", "")
            tool_name = tool_name_map.get(tool_id, "unknown")
            msg["content"] = f"[Previous: used {tool_name}]"
    return messages
# -- Layer 2: auto_compact - save transcript, summarize, replace messages --
def auto_compact(messages: list) -> list:
    # Save full transcript to disk
    TRANSCRIPT_DIR.mkdir(exist_ok=True)
    transcript_path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
    with open(transcript_path, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg, default=str) + "\n")
    print(f"[transcript saved: {transcript_path}]")
    # Ask LLM to summarize
    conversation_text = json.dumps(messages, default=str)[:80000]
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content":
            "Summarize this conversation for continuity. Include: "
            "1) What was accomplished, 2) Current state, 3) Key decisions made. "
            "Be concise but preserve critical details.\n\n" + conversation_text}],
        max_tokens=2000,
    )
    summary = response.choices[0].message.content
    # Replace all messages with compressed summary
    return [
        {"role": "user", "content": f"[Conversation compressed. Transcript: {transcript_path}]\n\n{summary}"},
        {"role": "assistant", "content": "Understood. I have the context from the summary. Continuing."},
    ]
# -- Tool implementations --
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
    "bash":       lambda **kw: run_bash(kw["command"]),
    "read_file":  lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file":  lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
    "compact":    lambda **kw: "Manual compression requested.",
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
    {"type": "function", "function": {"name": "compact", "description": "Trigger manual conversation compression.",
     "parameters": {"type": "object", "properties": {"focus": {"type": "string", "description": "What to preserve in the summary"}}}}},
]
def agent_loop(messages: list):
    while True:
        # Layer 1: micro_compact before each LLM call
        micro_compact(messages)
        # Layer 2: auto_compact if token estimate exceeds threshold
        if estimate_tokens(messages) > THRESHOLD:
            print("[auto_compact triggered]")
            messages[:] = auto_compact(messages)
        response = client.chat.completions.create(
            model=MODEL, messages=[{"role": "system", "content": SYSTEM}] + messages,
            tools=TOOLS, max_tokens=8000,
        )
        choice = response.choices[0]
        assistant_msg = choice.message
        if assistant_msg.content is not None:
            print(f"\033[32m{assistant_msg.content}\033[0m")
        messages.append({"role": "assistant", "content": assistant_msg.content, "tool_calls": assistant_msg.tool_calls})
        if not assistant_msg.tool_calls:
            return
        results = []
        manual_compact = False
        for tool_call in assistant_msg.tool_calls:
            if tool_call.function.name == "compact":
                manual_compact = True
                output = "Compressing..."
            else:
                handler = TOOL_HANDLERS.get(tool_call.function.name)
                try:
                    args = json.loads(tool_call.function.arguments)
                    output = handler(**args) if handler else f"Unknown tool: {tool_call.function.name}"
                except Exception as e:
                    output = f"Error: {e}"
            print(f"> {tool_call.function.name}: {str(output)[:200]}")
            results.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(output)})
        messages.extend(results)
        # Layer 3: manual compact triggered by the compact tool
        if manual_compact:
            print("[manual compact]")
            messages[:] = auto_compact(messages)
if __name__ == "__main__":
    history = []
    while True:
        try:
            query = input("\033[36ms06 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        agent_loop(history)
        
