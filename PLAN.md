# PLAN · Coding Agent Harness 实现计划

> 版本：v2.0（垂直切片，范围收缩）
> 日期：2026-07-07
> 策略：先做端到端最短路径（T0→T7），确保每个机制可单测、可回放；T8 插件系统作为扩展；T9 配置/凭据/CLI；T10 分发/文档
> 每个 task 颗粒度 2-5 分钟，可由一个 subagent 在一次会话内完成
> TDD 强制：每个 task 先写失败测试（红），再写最少代码（绿），再重构

---

## 依赖关系图

```
T0 (骨架) ──→ T1 (数据模型+MockLLM) ──→ T2 (主循环) ──→ T3 (5工具)
                                              ├──→ T4 (权限+围栏) ←── T3
                                              ├──→ T5 (反馈+自愈) ←── T3
                                              └──→ T6 (trace+demo) ←── T4, T5
T6 ──→ T7 (Agent Loop Theater)
T2 ──→ T8 (插件系统) ←── T3, T4, T5
T2 ──→ T9 (配置+凭据+CLI)
全部 ──→ T10 (分发+文档)

关键路径：T0 → T1 → T2 → T3 → T4 → T5 → T6 → T7 → T10
```

---

## Task 列表

### 阶段 0：环境与工程初始化

| # | 目标 | 文件 | 实现要点 | 验证步骤（含失败测试） | 依赖 |
|---|------|------|----------|----------------------|------|
| T0.1 | 创建项目骨架 | `pyproject.toml`, `src/agent_harness/__init__.py`, `tests/__init__.py` | 项目结构、依赖声明（openai/keyring/streamlit/pyyaml/pydantic/pytest） | `python -c "import agent_harness"` 不报错 | 无 |
| T0.2 | 配置 Makefile | `Makefile` | `test`/`lint`/`clean`/`web`/`demo` 目标 | `make test` 运行 pytest（空测试通过） | T0.1 |
| T0.3 | 配置 CI | `.gitlab-ci.yml`, `.github/workflows/test.yml` | `unit-test` job，push 自动运行 pytest + ruff | CI 手动触发一次 pass | T0.2 |
| T0.4 | 创建 GitHub 仓库 | 远程仓库 | 公开仓库，初始化 README，首次 push | `git clone` 可拉取 | T0.1 |

### 阶段 1：核心引擎（数据模型 + MockLLM）

| # | 目标 | 文件 | 实现要点 | 验证步骤（含失败测试） | 依赖 |
|---|------|------|----------|----------------------|------|
| **T1.1** | **定义核心数据模型** | `src/agent_harness/models.py` | AgentAction, ToolResult, TraceRecord, Feedback, HITLRequest, PermissionRule, ScopeVerdict | **红**：`tests/test_models.py` 创建各数据类实例 → 断言字段正确（此时类不存在，测试失败） | T0.1 |
| **T1.2** | **实现 LLMInterface 抽象基类** | `src/agent_harness/llm/interface.py` | 抽象基类，定义 `call(context, menu) -> LLMResponse` 接口 | **红**：`tests/test_llm.py` 断言不能实例化抽象类 | T1.1 |
| **T1.3** | **实现 MockLLM** | `src/agent_harness/llm/mock.py` | 接受预设响应队列 `list[LLMResponse]`，每次 call 弹出下一个 | **红**：`tests/test_llm.py` MockLLM 返回第一个响应 → 再 call 返回第二个 | T1.2 |
| T1.4 | 实现 OpenAILLM | `src/agent_harness/llm/openai.py` | 真实 API 调用（同步），重试 3 次 | 手动测试：配置 key → call → 返回响应 | T1.2 |

### 阶段 2：Agent 主循环

| # | 目标 | 文件 | 实现要点 | 验证步骤（含失败测试） | 依赖 |
|---|------|------|----------|----------------------|------|
| **T2.1** | **实现 Harness 数据类** | `src/agent_harness/agent/harness.py` | 持有所有组件（llm, tools, permission, feedback, trace, memory, config） | **红**：`tests/test_loop.py` build Harness → 访问各组件 | T1.3 |
| **T2.2** | **实现 agent_loop 基础循环** | `src/agent_harness/agent/loop.py` | context 装配 → while → LLM call → 解析 → done 则停 | **红**：`tests/test_loop.py` MockLLM=[done] → 1 轮即停，返回 answer | T2.1 |
| **T2.3** | **加 call_tool 分发** | 同上 | action.type=="call_tool" → 调用 tool → 结果回灌 context | **红**：`tests/test_loop.py` MockLLM=[call_tool(read_file), done] → 2 轮，trace 有 2 条 | T2.2 |
| **T2.4** | **加 MAX_STEPS 守卫** | 同上 | steps >= MAX_STEPS → 停机 | **红**：`tests/test_loop.py` MockLLM 无 done → 到 MAX_STEPS 停 | T2.3 |
| T2.5 | 加 take_note 分发 | 同上 | action.type=="take_note" → memory.write | **红**：`tests/test_loop.py` MockLLM=[take_note, done] → note 写入 | T2.4 |

### 阶段 3：工具系统（5 个核心工具）

| # | 目标 | 文件 | 实现要点 | 验证步骤（含失败测试） | 依赖 |
|---|------|------|----------|----------------------|------|
| **T3.1** | **实现 ToolBase + ToolRegistry** | `src/agent_harness/tools/base.py`, `src/agent_harness/tools/registry.py` | ToolBase 抽象基类（name, description, run）+ ToolRegistry（register/list/call） | **红**：`tests/test_tools.py` 注册假工具 → list 含它 → call 返回结果 | T2.3 |
| **T3.2** | **实现 read_file** | `src/agent_harness/tools/builtin/read_file.py` | 读文件内容，返回 ToolResult | **红**：`tests/test_tools.py` 读现有文件 → content 正确；读不存在 → error | T3.1 |
| **T3.3** | **实现 write_file** | `src/agent_harness/tools/builtin/write_file.py` | 写文件，返回 ToolResult(success) | **红**：`tests/test_tools.py` write → 文件存在且内容正确 | T3.1 |
| **T3.4** | **实现 edit_file** | `src/agent_harness/tools/builtin/edit_file.py` | 替换文件中文本，返回 ToolResult(success, diff) | **红**：`tests/test_tools.py` edit → old 被替换为 new | T3.2 |
| **T3.5** | **实现 run_shell** | `src/agent_harness/tools/builtin/run_shell.py` | 执行 shell，返回 stdout/stderr/exit_code | **红**：`tests/test_tools.py` run "echo hello" → stdout 含 hello | T3.1 |
| **T3.6** | **实现 run_test** | `src/agent_harness/tools/builtin/run_test.py` | 运行 pytest，解析 passed/failed | **红**：`tests/test_tools.py` run_test on passing → success；on failing → failure | T3.5 |
| T3.7 | 工具集成到主循环 | `src/agent_harness/agent/loop.py` | 5 工具注册到 ToolRegistry，菜单含它们 | **红**：`tests/test_loop.py` MockLLM 调 read_file → trace 含 tool_result | T3.6 + T2.3 |

### 阶段 4：治理护栏（重点维度）

| # | 目标 | 文件 | 实现要点 | 验证步骤（含失败测试） | 依赖 |
|---|------|------|----------|----------------------|------|
| **T4.1** | **实现 PermissionRule + 规则匹配** | `src/agent_harness/governance/permission.py` | PermissionRule 数据类 + 命令/路径/正则匹配 | **红**：`tests/test_permission.py` rm -rf → deny；ls → allow | T2.3 |
| **T4.2** | **实现 PermissionPolicy 三态引擎** | 同上 | allow/ask/deny，deny 优先级最高，多规则取最严 | **红**：`tests/test_permission.py` 两条规则（allow + deny）→ deny 赢 | T4.1 |
| **T4.3** | **实现 ScopeGuard 路径围栏** | `src/agent_harness/governance/scope.py` | realpath 规范化 → workspace 边界检查 → 敏感路径检查 | **红**：`tests/test_scope.py` `../etc` → outside；`./src` → inside；`.git` → sensitive | T4.1 |
| **T4.4** | **实现 HITL 状态机** | `src/agent_harness/governance/hitl.py` | pending → approved/denied/timed_out + 超时默认 deny | **红**：`tests/test_hitl.py` pending → approve → approved；pending → timeout → timed_out | T4.2 |
| T4.5 | 权限+围栏集成到主循环 | `src/agent_harness/agent/loop.py` | PermissionPolicy.check + ScopeGuard.check 插在 LLM 后、tool 前 | **红**：`tests/test_loop.py` MockLLM 返回 rm -rf → trace 显示 denied | T4.4 + T4.3 + T2.3 |

### 阶段 5：反馈传感器（重点维度）

| # | 目标 | 文件 | 实现要点 | 验证步骤（含失败测试） | 依赖 |
|---|------|------|----------|----------------------|------|
| **T5.1** | **实现 Feedback 分类器** | `src/agent_harness/feedback/classifier.py` | 解析输出文本 → 分类 syntax/assertion/timeout/tool_error/success | **红**：`tests/test_feedback.py` "AssertionError" → assertion；"SyntaxError" → syntax | T2.3 |
| **T5.2** | **实现 FeedbackSensor** | `src/agent_harness/feedback/sensor.py` | 解析 ToolResult → Feedback 对象 → 生成结构化 feedback 文本 | **红**：`tests/test_feedback.py` 失败的 ToolResult → Feedback(category, message) | T5.1 |
| **T5.3** | **实现自愈计数器** | `src/agent_harness/feedback/heal.py` | 记录修正次数，超限（默认 3）设 escalate 标志 | **红**：`tests/test_feedback.py` 3 次失败 → escalate=True | T5.2 |
| T5.4 | 反馈集成到主循环 | `src/agent_harness/agent/loop.py` | changed_code 后 run FeedbackSensor → 结构化 feedback 回灌 context | **红**：`tests/test_loop.py` MockLLM=[call_tool(失败), call_tool(修正), done] → trace 含 feedback，第 2 轮 action 改变 | T5.3 + T2.3 |

### 阶段 6：TraceStore + 机制演示

| # | 目标 | 文件 | 实现要点 | 验证步骤（含失败测试） | 依赖 |
|---|------|------|----------|----------------------|------|
| **T6.1** | **实现 TraceStore JSONL 写入** | `src/agent_harness/trace/store.py` | record(step_data) → 追加一行 JSON 到 .harness/trace/{session}.jsonl | **红**：`tests/test_trace.py` record 3 次 → 文件有 3 行 JSON | T2.3 |
| **T6.2** | **实现 TraceStore flush + 读取** | 同上 | flush() 最终落盘；load(path) → list[TraceRecord] | **红**：`tests/test_trace.py` 写入后 load → 长度正确，字段正确 | T6.1 |
| T6.3 | trace 集成到主循环 | `src/agent_harness/agent/loop.py` | 每轮 TraceStore.record + 退出时 flush | **红**：`tests/test_loop.py` 跑完循环 → trace 文件存在且行数=步数 | T6.2 + T2.3 |
| **T6.4** | **机制演示 1：权限拦截** | `demo/demo_guardrail.py` | MockLLM 返回 rm -rf → PermissionPolicy deny → trace 记录 | **红**：`tests/test_demo.py` 运行 demo → 输出确定性结果（denied） | T4.5 |
| **T6.5** | **机制演示 2：反馈自愈** | `demo/demo_feedback.py` | MockLLM=[改代码(失败), 改代码(修正), done] → feedback 回灌 → action 改变 | **红**：`tests/test_demo.py` 运行 demo → 输出确定性结果（healed） | T5.4 |
| **T6.6** | **机制演示 3：权限+围栏联动** | `demo/demo_scope.py` | MockLLM 返回越界路径写 → ScopeGuard outside → PermissionPolicy deny | **红**：`tests/test_demo.py` 运行 demo → 输出确定性结果（scope denied） | T4.5 |

### 阶段 7：Agent Loop Theater

| # | 目标 | 文件 | 实现要点 | 验证步骤 | 依赖 |
|---|------|------|----------|----------|------|
| T7.1 | 实现 Streamlit 骨架 | `src/agent_harness/web/theater.py` | 读取 .harness/trace/*.jsonl → 下拉选择 session | 手动测试：`streamlit run theater.py` → 可选 session | T6.2 |
| T7.2 | 实现逐步回放 UI | 同上 | step 滑块 + 前进/后退按钮 + 当前步详情 | 手动测试：滑动 step → 显示对应轮详情 | T7.1 |
| T7.3 | 实现金色/蓝色可视化 | 同上 + custom CSS | 金色高亮 llm_text + llm_action；蓝色显示 permission_verdict + tool_result + feedback | 手动测试：金色/蓝色区分清晰 | T7.2 |
| T7.4 | 实现侧栏统计 | 同上 | context_size 曲线 + step 计数 + 停机原因 | 手动测试：侧栏显示正确 | T7.3 |

### 阶段 8：插件系统

| # | 目标 | 文件 | 实现要点 | 验证步骤（含失败测试） | 依赖 |
|---|------|------|----------|----------------------|------|
| **T8.1** | **定义 5 个插件基类** | `src/agent_harness/plugins/base.py` | ToolPlugin, GuardrailPlugin, SensorPlugin, MemoryBackend, UIPanel | **红**：`tests/test_plugins.py` 各基类实例化 → 断言接口方法存在 | T3.1, T4.1, T5.1 |
| **T8.2** | **实现插件注册表** | `src/agent_harness/plugins/registry.py` | PluginRegistry（register/list/get）+ 显式注册（从 YAML 配置加载） | **红**：`tests/test_plugins.py` 注册 ToolPlugin → 其工具出现在 ToolRegistry | T8.1 |
| **T8.3** | **实现 4 个生命周期钩子** | `src/agent_harness/plugins/hooks.py` | HookRegistry（before_action/after_action/on_feedback/on_halt）+ 执行 | **红**：`tests/test_plugins.py` 注册 before_action → 触发；返回 deny → 拦截 | T8.1 |
| T8.4 | 实现 entry_points 发现（可选） | `src/agent_harness/plugins/discovery.py` | importlib.metadata.entry_points 扫描 + 配置开关 | **红**：`tests/test_plugins.py` 注册测试 entry_point → 被加载 | T8.2 |
| T8.5 | 插件集成到主循环 | `src/agent_harness/agent/loop.py` | before_action/after_action 钩子插在 tool 执行前后；on_feedback 在反馈后；on_halt 在停机时 | **红**：`tests/test_loop.py` 注册 hook → trace 显示 hook 触发 | T8.3 + T2.3 |

### 阶段 9：配置 + 凭据 + CLI

| # | 目标 | 文件 | 实现要点 | 验证步骤（含失败测试） | 依赖 |
|---|------|------|----------|----------------------|------|
| T9.1 | 实现配置加载 | `src/agent_harness/config/loader.py`, `config/agent-harness.yaml` | YAML → Pydantic 校验 → 默认值 | **红**：`tests/test_config.py` 加载 YAML → 配置对象字段正确 | T0.1 |
| T9.2 | 实现凭据管理 | `src/agent_harness/credentials/manager.py` | keyring 存储 + .env 回退 + getpass 隐藏输入 | 手动测试：录入 → 查看（不显明文）→ 更新 → 清除 | T0.1 |
| T9.3 | 实现 CLI 主入口 | `src/agent_harness/cli/main.py` | argparse: run / web / credentials {show,update,clear} | 手动测试：各子命令帮助信息正确 | T9.1 |
| T9.4 | 实现 run 命令 | `src/agent_harness/cli/run.py` | 加载配置 → 装配 harness → agent_loop → 输出 | 手动测试：`agent-harness run "test"` → 输出 | T9.3 + T2.3 |
| T9.5 | 实现 credentials 命令 | `src/agent_harness/cli/credentials.py` | show/update/clear 子命令 | 手动测试：show → 不显示明文 | T9.2 |

### 阶段 10：分发 + 文档

| # | 目标 | 文件 | 实现要点 | 验证步骤 | 依赖 |
|---|------|------|----------|----------|------|
| T10.1 | 编写 Dockerfile | `Dockerfile` | python:3.12-slim + pip install + EXPOSE 8501 | `docker build -t agent-harness .` 成功 | T9.3 |
| T10.2 | 编写 README.md | `README.md` | 项目简介、安装、运行、分发命令、目录结构、安全边界说明 | 从零开始按 README 操作一次 | 全部 |
| T10.3 | 编写 AGENT_LOG.md | `AGENT_LOG.md` | 按时间记录关键节点 | 逐条填入 | 全部 |
| T10.4 | 最终安全检查 | 全局 | 确认 .env / history / 配置文件中无真实凭据 | grep 搜索 sk- 模式 | 全部 |
| T10.5 | 更新 PLAN.md | `PLAN.md` | 每完成一个 task 标记完成 + 附 commit hash | 逐条核对 | 全部 |
| T10.6 | 冷启动验证 | 第二阶段 | 用不同 agent 仅凭 SPEC+PLAN 实现 1-2 task | 记录暂停点与 spec 缺陷 | T10.2 |
| T10.7 | 编写 REFLECTION.md | `REFLECTION.md` | 1500-2500 字，本人撰写 | 字数检查 | 全部 |
| T10.8 | 最终 CI/CD 通过 | CI | 最后一次 CI/CD pass | 检查 CI 状态 | 全部 |
| T10.9 | 提交 NJU Git 仓库 | 远程仓库 | 最终提交 | 仓库链接可访问 | 全部 |

---

## 并行策略

### Worktree 分配

| Worktree | 包含 Task | 说明 |
|----------|-----------|------|
| `wt/core` | T0, T1, T2, T3 | 核心引擎，顺序依赖，串行 |
| `wt/governance` | T4 | 治理护栏，依赖 T2 完成后可并行 |
| `wt/feedback` | T5 | 反馈闭环，依赖 T2 完成后可并行 |
| `wt/trace` | T6 | trace + demo，依赖 T4 + T5 |
| `wt/theater` | T7 | Agent Loop Theater，依赖 T6 |
| `wt/plugins` | T8 | 插件系统，依赖 T3 + T4 + T5 |
| `wt/cli` | T9 | 配置/凭据/CLI，依赖 T2 |
| `wt/dist` | T10 | 分发/文档，依赖全部 |

### 关键路径

```
T0 → T1 → T2 → T3 → T4 → T5 → T6 → T7 → T10
                     ↓
                     T8 → T10
                     ↓
                     T9 → T10
```

---

## 测试策略

### 单元测试（每个核心模块）

| 模块 | 测试文件 | 最少用例数 |
|------|----------|:--------:|
| 数据模型 | `tests/test_models.py` | 5 |
| LLM 抽象层 | `tests/test_llm.py` | 3 |
| Agent 主循环 | `tests/test_loop.py` | 5 |
| 工具系统 | `tests/test_tools.py` | 12（5工具×2 + 2注册） |
| 权限引擎 | `tests/test_permission.py` | 5 |
| 路径围栏 | `tests/test_scope.py` | 4 |
| HITL 状态机 | `tests/test_hitl.py` | 4 |
| 反馈传感器 | `tests/test_feedback.py` | 5 |
| TraceStore | `tests/test_trace.py` | 3 |
| 插件系统 | `tests/test_plugins.py` | 5 |
| 配置系统 | `tests/test_config.py` | 3 |
| **合计** | | **≥ 54 个** |

### 机制演示（确定性，mock LLM）

```
demo/
├── demo_guardrail.py    # 权限拦截危险动作（mock LLM，确定性）
├── demo_feedback.py     # 注入失败 → 反馈修正（mock LLM，确定性）
└── demo_scope.py        # 权限+围栏联动（mock LLM，确定性）
```

对应测试：`tests/test_demo.py` 断言三个 demo 输出确定性结果。

### 运行命令

```bash
make test      # 运行所有单元测试
make demo      # 运行机制演示脚本
make lint      # ruff 检查
make web       # 启动 Agent Loop Theater
```

---

## TDD 纪律提醒

1. **每个 task 先写失败测试**（红）：测试文件先于实现文件。
2. **再写最少代码使测试通过**（绿）：不写多余功能。
3. **再重构**：改善代码质量，测试仍通过。
4. **Critical issue 必须修复才能进入下一 task**。
5. **每完成一个 task**：PLAN.md 标记完成 + 附 commit hash + AGENT_LOG.md 记录。
# Recovery Status - 2026-07-07

## Implementation Status - 2026-07-08

- Persistent HITL store is implemented in `agent_harness.hitl.store.HITLStore`.
- CLI HITL commands are implemented: `agent-harness hitl list|approve|deny`.
- HITL approval execution keeps scope enforcement before running stored actions.
- Web task/HITL service helpers are implemented in `agent_harness.web.services`.
- Streamlit theater can run a goal, show run/trace state, and list/approve/deny HITL requests against the same store.
- Tool menus now include argument schemas for OpenAI-compatible structured JSON actions.
- Structured `done` actions now support `answer` for clean final output.
- Fake OpenAI client e2e now verifies read/write/run_test/done.answer through the governed runtime.
- HITL approve can now continue a saved-context run with `agent-harness hitl approve --continue`.
- Default runtime now includes safe read-only browsing tools `list_files` and `search_text`.
- Default runtime now includes `read_many` and read-only `git_diff`.
- Default runtime now includes safer single-match `replace_once`.
- Streamlit HITL controls now support approve-and-continue for saved-context requests.
- Streamlit can now select JSONL run history from `.harness/runs`.
- Delivery verification script and personal setup guide are now available.
- High-confidence secret and marker scan is included in delivery verification.
- `run_shell` remains outside the default governed runtime tool registry.
- Latest verification: `161 passed`, ruff passed, CLI run/list smoke passed.
- Secret and marker scan found only API-key documentation and fake test credential references.

The sandbox recovery pass implemented the deterministic harness kernel described in `docs/superpowers/plans/2026-07-07-harness-recovery-and-kernel-redesign.md`.

Completed:

- Baseline dependency, CI, lint, and test recovery.
- Governance integration for scope, permission, and HITL.
- Feedback classification and loop context injection.
- JSONL trace recording and deterministic mechanism demos.
- Config loader, credential manager, CLI skeleton, plugin interfaces, and trace theater loader.
- Delivery artifacts: `README.md`, `AGENT_LOG.md`, `SPEC_PROCESS.md`, `Dockerfile`, and `REFLECTION.md`.

Latest verification:

- `python -m pytest -q` -> `134 passed`
- `python -m ruff check src/ tests/ demo/` -> `All checks passed!`

Remaining follow-up:

- Implement real API-backed provider execution behind the working CLI runtime.
- Strict structured action protocol is implemented. Next milestone: richer governed tool execution and HITL approval flow for real task work.
- Runtime factory now registers safe default tools under scope and feedback; shell remains excluded by default.
- Runtime factory now loads permission rules and creates HITL requests for ask-mode actions.
- `agent-harness run` now writes JSONL traces by default.
- Trace theater can summarize steps, tool calls, denials, and feedback events.
- Optional project memory writes append-only notes under `.harness/memory/project.md`.
- `agent-harness run` accepts `--profile <path>` for project-specific overlays.
- HITL pending requests can be approved and executed through a small resume API.
- HITL requests persist to JSON and are manageable through `agent-harness hitl list|approve|deny`.
- Build a richer trace replay UI.
- Add personal-harness features after course delivery requirements are locked.

## Completion Gap Closure - 2026-07-08

- Added `agent-harness doctor` to diagnose active config/profile, provider, model, base URL, credential status, default tools, `run_shell` status, permission rules, memory, and max steps without printing secrets.
- Added `agent-harness smoke hitl-write` to create a deterministic pending write request in a controlled workspace, proving the HITL queue can be exercised without a real API.
- Hardened Web startup instructions with explicit Windows Streamlit flags: `--server.address 127.0.0.1`, `--server.headless true`, `--browser.gatherUsageStats false`, and `--global.developmentMode false`.
- Updated personal setup and final status docs with the recommended real API read-only smoke and HITL write-loop smoke.
- GitHub `main` was previously verified synchronized at `68570413c94700c39c61aede809463966781f821`; this slice should be pushed after final verification.
- Latest verification: `python scripts/verify_delivery.py` -> `165 passed`, ruff passed, CLI run/list smoke passed, high-confidence secret scan passed.
