<h1 align="center">AgentCraft</h1>

<p align="center">
  <img src="logo.jpeg" alt="AgentCraft Logo" width="300"/>
</p>

<div align="center">

> 从零到一手把手教你构建一个迷你版 Claude Code，包含所有知识点。
> 基于 [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code)

</div>

---

## 背景知识：Agent 本质

### 模型即智能体 (The Model Is The Agent)

在讨论代码之前，我们必须明确一件事：

**智能体是一个模型。不是框架，不是提示链，不是拖拽工作流。**

### 什么是智能体

智能体是一个神经网络——Transformer、RNN、一个被训练出来的函数，经过数十亿次梯度更新，在行动序列数据上学会了感知环境、推理目标、采取行动。AI 领域的 "agent" 一词始终是这个含义。

**人类**就是一个智能体。一个经过数百万年进化训练形成的生物神经网络，通过感官感知世界，通过大脑推理，通过身体行动。

**历史证明**：

| 年份 | 里程碑 | 说明 |
|---------|------------------|------------------------|
| 2013 | DeepMind DQN 玩 Atari | 单个神经网络，仅接收原始像素和游戏分数，学会玩 7 款 Atari 游戏，超越所有先前算法，在 3 款游戏中击败人类专家 |
| 2019 | OpenAI Five 征服 Dota 2 | 5 个神经网络，10 个月内自我对局相当于 45,000 年 Dota 2，击败世界冠军 OG |
| 2019 | AlphaStar 精通星际争霸 II | 击败职业选手 10-1，后来达到欧洲服务器大师级（top 0.15%） |
| 2019 | 腾讯绝艺征服王者荣耀 | 击败 KPL 职业选手，1v1 模式下职业选手 15 局仅胜 1 局 |
| 2024-2025 | LLM 智能体重塑软件工程 |Claude等模型在人类全部代码和推理上训练的大语言模型， 被部署为编程 agent。它们阅读代码库，编写实现，调试故障，团队协作。架构与之前每一个 agent 完全相同：一个训练好的模型，放入一个环境，给予感知和行动的工具。唯一的不同是它们学到的东西的规模和解决任务的通用性。 |

**每一个里程碑都揭示同一个真理：智能体从来不是周围的代码，智能体始终是模型。**

### 什么不是智能体

"智能体"这个词被整个提示管道行业劫持了。

拖拽式工作流构建器、零代码 "AI 智能体" 平台、提示链编排库——它们都共享同一种妄想：用 if-else 分支、节点图和硬编码路由逻辑连接 LLM API 调用就构成了 "构建智能体"。

**提示管道 "智能体" 是不会训练模型的程序员的幻想。**

### 思维转变：从 "开发智能体" 到 "开发 Harness"

当有人说 "我在开发智能体"，他只能意味两件事之一：

**1. 训练模型** - 通过强化学习、微调、RLHF 或其他基于梯度的方法调整权重

**2. 构建 Harness** - 编写为模型提供操作环境的代码

```
Harness = Tools + Knowledge + Observation + Action Interfaces + Permissions

    Tools:          文件 I/O、shell、网络、数据库、浏览器
    Knowledge:      产品文档、领域参考、API 规范、样式指南
    Observation:    git diff、错误日志、浏览器状态、传感器数据
    Action:         CLI 命令、API 调用、UI 交互
    Permissions:    沙箱、审批工作流、信任边界
```

模型决定，Harness 执行。模型推理，Harness 提供上下文。模型比作马的话，Harness就是鞍具。

### Harness 工程师的真正工作

- **实现工具** - 给智能体双手：文件读写、shell 执行、API 调用、浏览器控制、数据库查询
- **管理知识** - 给智能体领域专业知识：按需加载（s05）而非预先塞入
- **管理上下文** - 给智能体干净的内存：子智能体隔离（s04）、上下文压缩（s06）、任务系统（s07）
- **控制权限** - 给智能体边界：沙箱文件访问、破坏性操作审批、信任边界
- **收集任务数据** - 每个行动序列都是训练信号

**你不是在编写智能，你是在构建智能所居住的世界。构建伟大的 Harness，智能体会完成剩下的工作。**

---

## 课程概述

**核心洞察**：所有 AI 编程 Agent 的底层都是同一个循环——用户发消息给模型，模型决定要不要调用工具，调用了就执行，把结果喂回去，继续循环，直到模型觉得任务完成了。

整个 Agent 的最小实现不到 30 行代码。剩下的一切——规划、子任务拆分、上下文压缩、多 Agent 协作、工作目录隔离——都是在这个循环上面一层一层叠加的。

```
User --> messages[] --> LLM --> response
                          |
              stop_reason == "tool_use"?
              /                        \
            yes                         no
            |                           |
        execute tools                return text
        append results
        loop back ----------------> messages[]
```

---

## 课程结构

| 阶段 | 章节 | 主题 | 核心理念 |
|------|------|------|----------|
| **第一阶段：核心循环** | s01 | Agent Loop | "One loop & Bash is all you need" |
| | s02 | Tool Use | "Adding a tool means adding one handler" |
| **第二阶段：规划与知识** | s03 | TodoWrite | "An agent without a plan drifts" |
| | s04 | Subagents | "Break big tasks down; each subtask gets a clean context" |
| | s05 | Skills | "Load knowledge when you need it, not upfront" |
| | s06 | Context Compact | "Context will fill up; you need a way to make room" |
| **第三阶段：持久化** | s07 | Tasks | "Break big goals into small tasks, order them, persist to disk" |
| | s08 | Background Tasks | "Run slow operations in the background; the agent keeps thinking" |
| **第四阶段：多 Agent 协作** | s09 | Agent Teams | "When the task is too big for one, delegate to teammates" |
| | s10 | Team Protocols | "Teammates need shared communication rules" |
| | s11 | Autonomous Agents | "Teammates scan the board and claim tasks themselves" |
| | s12 | Worktree + Task Isolation | "Each works in its own directory, no interference" |
| **整合** | s13 | Full Agent | 所有机制整合的完整参考实现 |

---

## 第一阶段：核心循环

### s01 - The Agent Loop

**文件**: [s01_agent_loop.py](s01_agent_loop.py)  
**Motto**: "One loop & Bash is all you need"

**问题**
一切从哪里开始？最原始的 Agent 循环是什么样的？

**知识点**
- **while True 循环**：核心循环模式，持续调用模型直到停止
- **tool_calls 机制**：模型返回的工具调用请求
- **tool_call_id 配对**：tool_use 和 tool_result 的关联
- **subprocess.run()**：执行外部 shell 命令

**代码架构**
```python
def agent_loop(messages: list):
    while True:
        # 1. 获取模型响应
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS
        )
        
        # 2. 解析响应
        if not assistant_msg.tool_calls:
            return  # 模型停止，循环结束
        
        # 3. 执行工具调用
        for tool_call in assistant_msg.tool_calls:
            output = run_bash(command)
            results.append({"role": "tool", "tool_call_id": tool_call.id, "content": output})
        
        # 4. 将结果喂回模型
        messages.extend(results)
```

**新增文件**: `s01_agent_loop.py` (102 行)

---

### s02 - Tool Use

**文件**: [s02_tools_use.py](s02_tools_use.py)  
**Motto**: "Adding a tool means adding one handler"

**问题**
只有一个 bash 工具太简陋了。如何优雅地添加更多工具？

**知识点**
- **TOOL_HANDLERS 分发映射**：`{tool_name: handler_function}` 模式
- **工具注册表**：新增工具只需添加 handler，无需修改循环
- **safe_path() 安全检查**：防止路径穿越攻击

**关键洞察**：循环本身完全没有改变，我们只是在 TOOLS 数组中添加工具，在 TOOL_HANDLERS 中添加分发规则。

**代码架构**
```python
# 新增 3 个工具处理器
TOOL_HANDLERS = {
    "bash":       lambda args: run_bash(args["command"]),
    "read_file":  lambda args: run_read(args["path"], args.get("limit")),
    "write_file": lambda args: run_write(args["path"], args["content"]),
    "edit_file":  lambda args: run_edit(args["path"], args["old_text"], args["new_text"]),
}

# 工具调用分发
for tool_call in assistant_msg.tool_calls:
    handler = TOOL_HANDLERS.get(tool_call.function.name)
    if handler:
        output = handler(args)
```

**新增文件**: `s02_tools_use.py` (139 行)

---

## 第二阶段：规划与知识

### s03 - TodoWrite

**文件**: [s03_todo_write.py](s03_todo_write.py)  
**Motto**: "An agent without a plan drifts"

**问题**
没有计划的 Agent 会跑偏。如何让 Agent 跟踪自己的进度？

**知识点**
- **TodoManager 类**：结构化状态管理类
- **任务状态机**：pending → in_progress → completed
- **Nag Reminder 机制**：3 轮无更新则注入提醒
- **dict.get() 方法**：安全获取字典值

**代码架构**
```
TodoManager state
[ ] task A
[>] task B <- doing (只能一个 in_progress)
[x] task C
```

**Nag Reminder 机制**
```python
rounds_since_todo = 0 if used_todo else rounds_since_todo + 1
if rounds_since_todo >= 3:
    results.insert(0, {"role": "user", "content": "<reminder>Update your todos.</reminder>"})
```

**新增文件**: `s03_todo_write.py` (183 行)

---

### s04 - Subagents

**文件**: [s04_sub_agent.py](s04_sub_agent.py)  
**Motto**: "Break big tasks down; each subtask gets a clean context"

**问题**
大任务会让对话上下文膨胀。如何让子任务拥有干净的上下文？

**知识点**
- **run_subagent() 函数**：spawn → execute → return summary → destroyed
- **messages=[] 隔离**：子任务拥有独立的对话历史
- **过滤工具**：子任务不能 spawn 子子任务（避免递归）
- **extend vs append**：列表合并的区别

**代码架构**
```
Parent agent                     Subagent
+------------------+             +------------------+
| messages=[...]   |             | messages=[]      |  <-- fresh
|                  |  dispatch   |                  |
| tool: task       | ---------->| while tool_use:   |
|   prompt="..."   |            |   call tools      |
|                  |  summary   |                   |
|   result = "..." | <--------- | return last text  |
+------------------+             +------------------+
          |
Parent context stays clean.
Subagent context is discarded.
```

**新增文件**: `s04_sub_agent.py` (160 行)

---

### s05 - Skills

**文件**: [s05_skills.py](s05_skills.py)  
**Motto**: "Load knowledge when you need it, not upfront"

**问题**
10 个技能，每个 2000 token，全塞进系统提示就是 20,000 token。大部分跟当前任务毫无关系。

**知识点**
- **两层技能注入**：Layer 1 (metadata) + Layer 2 (full body)
- **SkillLoader 类**：扫描 skills/ 目录
- **YAML frontmatter**：解析技能元数据
- **按需加载**：`<skill>` 标签在 tool_result 中注入

**代码架构**
```
skills/
  pdf/
    SKILL.md          <-- frontmatter (name, description) + body
  code-review/
    SKILL.md

System prompt: Layer 1 - 仅元数据 (~100 tokens/skill)

When model calls load_skill("pdf"):
Tool result: Layer 2 - 完整技能体
<skill name="pdf">
  Full PDF processing instructions
  Step 1: ...
  Step 2: ...
</skill>
```

**SKILL.md 格式**
```yaml
---
name: pdf
description: Process PDF files
tags: document, pdf
---
# PDF Processing Skill

Step 1: Read the PDF file using read_file
Step 2: Extract key information
...
```

**新增文件**: `s05_skills.py` (195 行)

---

### s06 - Context Compact

**文件**: [s06_cotext_compact.py](s06_cotext_compact.py)  
**Motto**: "Context will fill up; you need a way to make room"

**问题**
上下文窗口是有限的。读一个 1000 行的文件就吃掉 ~4000 token；读 30 个文件，轻松突破 100k token。

**知识点**
- **三层压缩策略**：micro_compact → auto_compact → manual compact
- **micro_compact**：静默执行，将旧的 tool_result 替换为占位符
- **auto_compact**：超过阈值时，保存转录 + LLM 摘要
- **transcript 持久化**：对话历史保存到 .transcripts/ 目录

**代码架构**
```
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
              Ask LLM to summarize.
              Replace all messages with [summary].
```

**新增文件**: `s06_cotext_compact.py` (222 行)

---

## 第三阶段：持久化

### s07 - Task System

**文件**: [s07_task_system.py](s07_task_system.py)  
**Motto**: "Break big goals into small tasks, order them, persist to disk"

**问题**
s03 的 TodoManager 只是内存中的扁平清单。没有顺序、没有依赖、状态只有做完没做完。而且清单只活在内存里，s06 压缩一跑就没了。

**知识点**
- **TaskManager 类**：基于 JSON 文件的持久化任务管理
- **依赖图**：blockedBy / blocks 双向关联
- **.tasks/ 目录**：每个任务一个 JSON 文件
- **状态传播**：完成任务自动解除依赖阻塞

**代码架构**
```
.tasks/
  task_1.json  {"id":1, "status":"completed", ...}
  task_2.json  {"id":2, "blockedBy":[1], "status":"pending", ...}
  task_3.json  {"id":3, "blockedBy":[2], "blocks":[], ...}

Dependency resolution:
+----------+     +----------+     +----------+
| task 1   | --> | task 2   | --> | task 3   |
| complete |     | blocked  |     | blocked  |
+----------+     +----------+     +----------+
     |                ^
     +--- completing task 1 removes it from task 2's blockedBy
```

**关键洞察**：状态存在于对话之外，所以压缩不会丢失。

**新增文件**: `s07_task_system.py` (220 行)

---

### s08 - Background Tasks

**文件**: [s08_background_task.py](s08_background_task.py)  
**Motto**: "Run slow operations in the background; the agent keeps thinking"

**问题**
有些命令要跑好几分钟：npm install、pytest、docker build。阻塞式循环下模型只能干等。用户说"装依赖，顺便建个配置文件"，智能体却只能一个一个来。

**知识点**
- **BackgroundManager 类**：线程池 + 通知队列
- **threading.Thread**：守护线程并行执行
- **Queue 通知机制**：后台任务完成后注入通知
- **drain_notifications()**：在 LLM 调用前清空通知

**代码架构**
```
Main thread                Background thread
+-----------------+        +-----------------+
| agent loop      |        | task executes   |
| ...             |        | ...             |
| [LLM call] <---+------- | enqueue(result) |
|  ^drain queue   |        +-----------------+
+-----------------+
Timeline:
Agent ----[spawn A]----[spawn B]----[other work]----
             |              |
             v              v
          [A runs]      [B runs]        (parallel)
             |              |
             +-- notification queue --> [results injected]
```

**关键洞察**：Fire and forget——Agent 不阻塞，命令并行跑。

**新增文件**: `s08_background_task.py` (209 行)

---

## 第四阶段：多 Agent 协作

### s09 - Agent Teams

**文件**: [s09_agent_team.py](s09_agent_team.py)  
**Motto**: "When the task is too big for one, delegate to teammates"

**问题**
一个人干不完的活怎么办？需要组队协作。

**知识点**
- **TeammateManager 类**：持久化命名智能体
- **config.json**：团队配置持久化
- **JSONL 收件箱**：`.team/inbox/{name}.jsonl` 消息总线
- **threading.Thread**：每个队友一个独立线程
- **Subagent vs Teammate**：
  - Subagent: spawn → execute → return summary → destroyed
  - Teammate: spawn → work → idle → work → ... → shutdown

**代码架构**
```
.team/
├── config.json          # 团队配置
└── inbox/
    ├── lead.jsonl       # Lead 的收件箱
    ├── alice.jsonl      # Alice 的收件箱
    └── bob.jsonl        # Bob 的收件箱

Message types: message, broadcast, shutdown_request, shutdown_response, plan_approval_response
```

**MessageBus 机制**
```python
def send(self, sender: str, to: str, content: str, msg_type: str = "message"):
    msg = {"type": msg_type, "from": sender, "content": content, "timestamp": time.time()}
    with open(f"{to}.jsonl", "a") as f:
        f.write(json.dumps(msg) + "\n")

def read_inbox(self, name: str) -> list:
    messages = [json.loads(l) for l in inbox_path.read_text().splitlines()]
    inbox_path.write_text("")  # drain
    return messages
```

**新增文件**: `s09_agent_team.py` (365 行)

---

### s10 - Team Protocols

**文件**: [s10_team_protocols.py](s10_team_protocols.py)  
**Motto**: "Teammates need shared communication rules"

**问题**
队友之间需要规范的交互模式。如何优雅地关闭队友？如何审批队友的计划？

**知识点**
- **Shutdown Protocol**：request_id 握手模式
- **Plan Approval Protocol**：计划提交 → 审批 → 反馈
- **状态机**：pending → approved | rejected
- **tracker_lock**：线程安全的请求追踪

**代码架构**
```
Shutdown FSM: pending -> approved | rejected

Lead                              Teammate
+---------------------+          +---------------------+
| shutdown_request     |          |                     |
| {                    | -------> | receives request    |
|   request_id: abc    |          | decides: approve?   |
| }                    |          |                     |
+---------------------+          +---------------------+
                                 |
+---------------------+          +-------v-------------+
| shutdown_response    | <------- | shutdown_response   |
| {                    |          | {                   |
|   request_id: abc    |          |   request_id: abc   |
|   approve: true      |          |   approve: true     |
| }                    |          | }                   |
+---------------------+          +---------------------+
```

**关键洞察**：相同的 request_id 关联模式，两个不同领域的应用。

**新增文件**: `s10_team_protocols.py` (490 行)

---

### s11 - Autonomous Agents

**文件**: [s11_auto_agent.py](s11_auto_agent.py)  
**Motto**: "Teammates scan the board and claim tasks themselves"

**问题**
需要领导一个个分配任务太麻烦了。能不能让队友自己找活干？

**知识点**
- **WORK / IDLE 状态机**：自动切换工作模式
- **任务认领机制**：扫描看板 → 认领无主任务 → 自动继续
- **身份重注入**：压缩后恢复身份上下文
- **轮询机制**：IDLE 时每 5 秒检查一次

**代码架构**
```
Teammate lifecycle:
+-------+
| spawn |
+---+---+
    |
    v
+-------+  tool_use    +-------+
| WORK  | <----------- |  LLM  |
+---+---+              +-------+
    |
    | stop_reason != tool_use
    v
+--------+
| IDLE   | poll every 5s for up to 60s
+---+----+
    |
    +---> check inbox -> message? -> resume WORK
    |
    +---> scan .tasks/ -> unclaimed? -> claim -> resume WORK
    |
    +---> timeout (60s) -> shutdown
```

**身份重注入**
```python
def make_identity_block(name: str, role: str, team_name: str) -> dict:
    return {
        "role": "user",
        "content": f"<identity>You are '{name}', role: {role}, team: {team_name}. Continue your work.</identity>",
    }

# 压缩后上下文为空时，注入身份
if len(messages) <= 3:
    messages.insert(0, make_identity_block(name, role, team_name))
```

**新增文件**: `s11_auto_agent.py` (582 行)

---

### s12 - Worktree + Task Isolation

**文件**: [s12_work_tree.py](s12_work_tree.py)  
**Motto**: "Each works in its own directory, no interference"

**问题**
并行任务如何互不干扰？Git worktree 是什么？

**知识点**
- **Git Worktree**：同一仓库的多个工作目录
- **WorktreeManager 类**：工作树生命周期管理
- **EventBus**：可观测性日志（.worktrees/events.jsonl）
- **keep vs remove**：保留 vs 删除工作树
- **任务-工作树绑定**：task_id ↔ worktree_name

**代码架构**
```
.tasks/task_12.json
{
  "id": 12,
  "subject": "Implement auth refactor",
  "status": "in_progress",
  "worktree": "auth-refactor"
}

.worktrees/index.json
{
  "worktrees": [
    {
      "name": "auth-refactor",
      "path": ".../.worktrees/auth-refactor",
      "branch": "wt/auth-refactor",
      "task_id": 12,
      "status": "active"
    }
  ]
}

关键洞察：任务管理控制平面，工作树管理执行平面。
```

**worktree 操作**
| 操作 | 效果 |
|------|------|
| create | 创建新分支 + 工作目录 |
| run | 在指定工作目录执行命令 |
| keep | 保留目录，标记为 kept |
| remove | 删除目录 + 分支 |

**新增文件**: `s12_work_tree.py` (829 行)

---

## 整合：完整 Agent

### s13 - Full Agent

**文件**: [s13_full_agent.py](s13_full_agent.py)

**核心理念**：整合 s01-s11 所有机制的完整参考实现。s12 单独教学（因为涉及 Git 仓库依赖）。

```
+------------------------------------------------------------------+
|                        FULL AGENT                                 |
|                                                                   |
|  System prompt (s05 skills, task-first + optional todo nag)      |
|                                                                   |
|  Before each LLM call:                                            |
|  +--------------------+  +------------------+  +--------------+  |
|  | Microcompact (s06) |  | Drain bg (s08)   |  | Check inbox  |  |
|  | Auto-compact (s06) |  | notifications    |  | (s09)        |  |
|  +--------------------+  +------------------+  +--------------+  |
|                                                                   |
|  Tool dispatch (s02 pattern):                                     |
|  +--------+----------+----------+---------+-----------+            |
|  | bash   | read     | write    | edit    | TodoWrite |            |
|  | task   | load_sk  | compress | bg_run  | bg_check  |            |
|  | t_crt  | t_get    | t_upd    | t_list  | spawn_tm  |            |
|  | list_tm| send_msg | rd_inbox | bcast   | shutdown  |            |
|  | plan   | idle     | claim    |         |           |            |
|  +--------+----------+----------+---------+-----------+            |
|                                                                   |
|  Subagent (s04):  spawn -> work -> return summary                 |
|  Teammate (s09):  spawn -> work -> idle -> auto-claim (s11)      |
|  Shutdown (s10):  request_id handshake                            |
|  Plan gate (s10): submit -> approve/reject                        |
+------------------------------------------------------------------+

REPL commands: /compact /tasks /team /inbox
```

**新增文件**: `s13_full_agent.py` (749 行)

---

## 快速开始

### 环境配置

```bash
# 克隆项目
git clone https://github.com/shareAI-lab/learn-claude-code
cd AgentCraft

# 安装依赖
pip install -r requirements.txt

# 配置 API Key (已配置火山云)
# API Key: 2fd38861-c7d5-4316-99aa-dbf73a48d7b2
# Base URL: https://ark.cn-beijing.volces.com/api/v3
# Model: doubao-seed-2-0-lite-260215
```

### 运行课程

```bash
# 从第一课开始
python s01_agent_loop.py

# 逐步推进到完整版
python s02_tools_use.py
python s03_todo_write.py
...
python s13_full_agent.py
```

### REPL 命令

| 命令 | 功能 |
|------|------|
| `q` / `exit` | 退出 |
| `/compact` | 手动压缩对话 |
| `/tasks` | 查看任务列表 |
| `/team` | 查看团队状态 |
| `/inbox` | 查看收件箱 |

---

## 知识点汇总

### 核心模式

| 模式 | 文件 | 说明 |
|------|------|------|
| Agent Loop | s01 | while True + tool_calls + 结果喂回 |
| Tool Dispatch | s02 | {name: handler} 分发表 |
| Nag Reminder | s03 | 定期提醒更新状态 |
| Subagent | s04 | fresh messages[] 隔离 |
| Skill Loading | s05 | 两层注入（metadata + body）|
| Compression | s06 | 三层压缩策略 |
| File Tasks | s07 | JSON 持久化 + 依赖图 |
| Background | s08 | threading.Thread + Queue |
| JSONL Inbox | s09 | 异步消息总线 |
| Protocol Handshake | s10 | request_id 关联 |
| Autonomous | s11 | WORK/IDLE 状态机 |
| Worktree | s12 | Git 多工作目录 |

### 关键类

| 类名 | 文件 | 职责 |
|------|------|------|
| TodoManager | s03 | 待办清单管理 |
| SkillLoader | s05 | 技能扫描和加载 |
| TaskManager | s07 | 持久化任务系统 |
| BackgroundManager | s08 | 后台任务执行 |
| MessageBus | s09 | JSONL 收件箱 |
| TeammateManager | s09/10/11 | 团队生命周期 |
| WorktreeManager | s12 | Git worktree 管理 |

### 工具数量

| 文件 | 工具数 | 新增工具 |
|------|--------|----------|
| s01 | 1 | bash |
| s02 | 4 | bash, read_file, write_file, edit_file |
| s03 | 5 | + todo |
| s04 | 5 | (子任务用父工具集) |
| s05 | 6 | + load_skill |
| s06 | 6 | + compress |
| s07 | 10 | + task_create, task_update, task_list, task_get |
| s08 | 12 | + background_run, check_background |
| s09 | 9 | + spawn_teammate, list_teammates, send_message, read_inbox, broadcast |
| s10 | 12 | + shutdown_request, shutdown_response, plan_approval |
| s11 | 14 | + idle, claim_task |
| s12 | 15+ | + worktree_* 系列 |
| s13 | 24 | 完整工具集 |

---

## 学习路径

```
s01 Agent Loop
  │
  ▼
s02 Tool Use
  │
  ▼
s03 TodoWrite ──────────────────┐
  │                             │
  ▼                             │
s04 Subagents ───────┐          │
  │                  │          │
  ▼                  │          │
s05 Skills ──────────┼──────────┤
  │                  │          │
  ▼                  │          ▼
s06 Context ─────────┴──────────┤
Compact                         │
  │                             │
  ▼                             ▼
s07 Task ──────────────────────┐│
  │                            ││
  ▼                            ││
s08 Background ────────────────┼┤
Tasks                          ││
  │                            ││
  ▼                            ││
s09 Agent ─────────────────────┐││
Teams                          │││
  │                            │││
  ▼                            │││
s10 Team ──────────────────────┼┴┘
Protocols                      │
  │                            │
  ▼                            │
s11 Autonomous ────────────────┘
Agents
  │
  ▼
s12 Worktree + Task Isolation
  │
  ▼
s13 Full Agent (整合所有机制)
```

---

## 延伸学习

- [Kode Agent CLI](https://github.com/shareai-lab/kode) - 开源编程助手 CLI
- [Kode Agent SDK](https://github.com/shareai-lab/kode-sdk) - Agent 能力嵌入库

---

*本文档由 AgentCraft 课程自动生成，基于 Learn Claude Code 教学项目。*
