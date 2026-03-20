#!/usr/bin/env python3
"""
s01_agent_loop.py - The Agent Loop
The entire secret of an AI coding agent in one pattern:
    while stop_reason == "tool_use":
        response = LLM(messages, tools)
        execute tools
        append results
    +----------+      +-------+      +---------+
    |   User   | ---> |  LLM  | ---> |  Tool   |
    |  prompt  |      |       |      | execute |
    +----------+      +---+---+      +----+----+
                          ^               |
                          |   tool_result |
                          +---------------+
                          (loop continues)
This is the core loop: feed tool results back to the model
until the model decides to stop. Production agents layer
policy, hooks, and lifecycle controls on top.
"""
import os
import subprocess
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
SYSTEM = f"You are a coding agent at {os.getcwd()}. Use bash to solve tasks. Act, don't explain."
TOOLS = [{
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Run a shell command.",
        "parameters": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
}]
def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(command, shell=True, cwd=os.getcwd(),
                           capture_output=True, text=True, timeout=120)
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
# -- The core pattern: a while loop that calls tools until the model stops --
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

        # Execute each tool call, collect results
        results = []
        for tool_call in assistant_msg.tool_calls:
            if tool_call.function.name == "bash":
                import json
                args = json.loads(tool_call.function.arguments)
                command = args.get("command", "")
                print(f"\033[33m$ {command}\033[0m")
                output = run_bash(command)
                print(output[:200])
                results.append({"role": "tool", "tool_call_id": tool_call.id, "content": output})
        # Append tool results
        messages.extend(results)
if __name__ == "__main__":
    history = []
    while True:
        try:
            query = input("\033[36ms01 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        agent_loop(history)
       
