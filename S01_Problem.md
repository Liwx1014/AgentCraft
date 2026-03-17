只有 bash 时, 所有操作都走 shell。cat 截断不可预测, sed 遇到特殊字符就崩, 每次 bash 调用都是不受约束的安全面。专用工具 (read_file, write_file) 可以在工具层面做路径沙箱。

关键洞察: 加工具不需要改循环

+--------+      +-------+      +------------------+
|  User  | ---> |  LLM  | ---> | Tool Dispatch    |
| prompt |      |       |      | {                |
+--------+      +---+---+      |   bash: run_bash |
                    ^           |   read: run_read |
                    |           |   write: run_wr  |
                    +-----------+   edit: run_edit |
                    tool_result | }                |
                                +------------------+

The dispatch map is a dict: {tool_name: handler_function}.
One lookup replaces any if/elif chain.