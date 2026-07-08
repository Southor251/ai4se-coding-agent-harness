# Codex 执行交接文档 · 继续开发计划

> **版本**：v1.1  
> **审查日期**：2026-07-08  
> **目标**：在已经可运行的自实现 harness 基础上，继续推进到“可接入个人 API、可通过 Web/CLI 执行真实任务、可审计、可恢复、可演示”的应用。  
> **适用对象**：Codex / Claude Code / Cursor Agent 等继续接手项目的编码智能体。  
> **执行原则**：先稳定可用核心，再扩展界面与 provider；每个切片 TDD、可回滚、可验证；不为了功能数量牺牲课程核心机制的可解释性和安全边界。

---

## 1. 对 v1.0 计划的批判性审查

v1.0 的大方向是对的：保留自实现 harness 内核，补齐 API 接入、GUI、HITL、trace 和插件扩展。但它存在几个会导致返工的风险：

1. **范围过宽**  
   “自接入任意 API + TDesign React GUI + FastAPI + 插件系统 + 实时 HITL + checkpoint”被放在连续主线中，容易变成多个项目并行推进。课程项目最重要的是证明 harness 机制可运行、可审计、可安全接入真实 API，而不是一次性重做完整 IDE。

2. **“任意 API”表述不够工程化**  
   真实可交付目标应先定义为“OpenAI-compatible chat completion provider 可配置”，再扩展到“少量可测试的 provider adapter”。任意 HTTP API 的请求/响应结构差异很大，若没有 adapter contract、mock 测试和错误语义，容易写成不可维护的 if/else。

3. **GUI 目标过早升级**  
   当前 Streamlit theater 已经能完成任务输入、trace 查看、HITL 审批。直接切换到 TDesign + React + FastAPI 会引入 Node 依赖、前后端契约、打包、跨域和部署问题。更稳妥的方式是先抽出可测试服务层和 API contract，再决定是否上 React。

4. **没有把现有成果作为基线**  
   当前沙箱版本已经通过 `scripts/verify_delivery.py`，覆盖 161 个测试、ruff、CLI smoke、HITL list、secret scan。v1.0 仍把一些已解决内容写成待办，容易让接手 agent 重复劳动。

5. **缺少迁移与同步策略**  
   用户要求在沙箱中开发，但最终需要变成桌面项目可用。计划必须明确：何时从沙箱同步到目标仓库、如何备份、如何避免覆盖用户未提交更改。

6. **验收标准偏“清单式”，缺少用户可试用路径**  
   最终验收不应只看测试通过，还应有一条实际用户路径：配置 API key、运行只读任务、触发写入 HITL、审批继续、查看 trace、导出或复现执行记录。

---

## 2. 当前客观基线

当前沙箱项目已经初步完成一个可用基础版：

- 自实现 agent loop、工具分发、权限治理、ScopeGuard、反馈、HITL 状态机。
- OpenAI-compatible provider 配置：`model`、`base_url`、`temperature`。
- keyring 优先、`.env` fallback 的凭据管理。
- 严格 JSON action protocol，支持 `call_tool`、`take_note`、`done.answer`。
- 默认安全工具：`read_file`、`read_many`、`list_files`、`search_text`、`git_diff`、`write_file`、`replace_once`、`edit_file`、`run_test`。
- 默认 governed runtime 不注册 `run_shell`。
- 持久化 HITL store：`.harness/hitl/requests.json`。
- CLI HITL：`list`、`approve`、`deny`、`approve-and-continue`。
- Streamlit theater：任务输入、trace history、step inspection、HITL approve/deny/approve-and-continue。
- 交付验证脚本：`scripts/verify_delivery.py`。
- 最近验证结果：`161 passed`，ruff 通过，CLI smoke 通过，HITL list smoke 通过，高置信 secret scan 通过。

仍需注意：

- 真实 API 尚未用用户实际 key 做端到端验证。
- 完成成果仍主要在沙箱副本中，未安全同步到最终目标仓库。
- Streamlit 是可用 theater，不是成熟 IDE。
- harness 提供的是应用级治理，不是操作系统级沙箱。

---

## 3. 修订后的总体策略

### 北极星目标

最终交付应是一套可本地运行的个人 coding-agent harness：

1. 用户能配置自己的 API endpoint、model 和 credential。
2. 用户能通过 CLI 或 Web 输入任务。
3. agent 能在受控 workspace 内读文件、搜索、生成 diff、写文件或运行测试。
4. 写操作必须经过 permission/HITL/scope 约束。
5. 每次执行都有 trace，可审计、可复现、可解释。
6. 项目有一键或近一键验证流程，能证明核心功能未被破坏。

### 工程取舍

- **先交付可靠 CLI + Streamlit + provider 配置**，再考虑 React GUI。
- **先支持 OpenAI-compatible provider 的多 endpoint 配置**，再抽象更广义 provider adapter。
- **插件系统先补最小 hooks**，只服务测试、审计和未来扩展，不把它变成新框架。
- **所有真实 API 测试必须可跳过且不提交 key**；核心测试继续使用 mock/fake client。
- **每个阶段独立 commit**，并更新 `PLAN.md`、`AGENT_LOG.md`、`README.md`、`docs/final_status.md` 或本交接文档。

---

## 4. 修订后的执行路线

### 阶段 0：确认源仓库与同步边界

**目标**：避免沙箱成果和桌面目标仓库分叉失控。

任务：

1. 检查沙箱仓库与目标仓库的 `git status`、最近 commit、关键文件差异。
2. 若目标仓库有用户未提交更改，先生成备份或 patch，不直接覆盖。
3. 明确本轮继续开发的源仓库：
   - 默认继续在沙箱开发。
   - 同步到桌面仓库前必须先备份并做 diff 审查。

验收：

```powershell
git status --short
git log --oneline -5
python scripts/verify_delivery.py
```

完成标准：知道哪个目录是当前可信基线，并且不会覆盖用户工作。

---

### 阶段 1：真实 API 接入闭环

**目标**：把“可配置 OpenAI-compatible API”从代码能力推进到用户可按文档完成的实际路径。

任务：

1. 审查 `config/personal-harness.yaml`，确保字段名称和 runtime factory 一致。
2. 补充或修正 credential CLI 文档，明确不要把 key 写入聊天或 Git。
3. 增加 provider smoke helper：
   - 使用 fake client 的自动测试。
   - 使用真实 key 的手动命令，默认跳过。
4. 增加 `agent-harness doctor` 或轻量等价命令，检查：
   - 当前 workspace root。
   - provider 类型、model、base_url 是否存在。
   - credential 是否配置，但不输出明文。
   - 默认工具是否不包含 `run_shell`。
5. 用用户真实 API 前，先运行 mock task，再运行只读真实 task。

验收：

```powershell
python scripts/verify_delivery.py
agent-harness run "say done" --profile config/personal-harness.yaml --trace .harness/runs/latest.jsonl
agent-harness doctor --profile config/personal-harness.yaml
```

完成标准：用户能在不泄露 key 的情况下配置个人 API，并完成一次只读任务。

---

### 阶段 2：HITL 与写入任务实战化

**目标**：验证写入任务不是“测试里能跑”，而是用户实际可审批、可继续、可审计。

任务：

1. 准备一个受控 demo workspace，不直接对项目源码做危险写入。
2. 构造写入任务触发 `write_file` 或 `replace_once`。
3. 确认 permission verdict 为 `ask` 时：
   - request 写入 `.harness/hitl/requests.json`。
   - CLI/Web 均能看到 pending request。
   - approve 后仍执行 `ScopeGuard`。
   - deny 后不执行工具。
   - approve-and-continue 能继续 agent loop。
4. 在 trace 中确认审批、工具结果、halt reason 均可追踪。

验收：

```powershell
agent-harness hitl list --store .harness/hitl/requests.json
agent-harness hitl approve-and-continue <request_id> --config config/personal-harness.yaml --profile config/personal-harness.yaml --store .harness/hitl/requests.json
python scripts/verify_delivery.py
```

完成标准：用户能亲自完成一次“请求写入、审批、继续执行、查看 trace”的闭环。

---

### 阶段 3：Web Theater 加固，而非立刻重写 IDE

**目标**：先把现有 Streamlit theater 打磨成稳定可演示界面。

任务：

1. 固化启动命令或脚本，避免 localhost 连接失败：
   - 使用项目 `.venv` 的 Python。
   - 使用 `--server.address 127.0.0.1`。
   - 使用 `--browser.gatherUsageStats false`。
   - 保持可见 PowerShell 窗口用于保活。
2. 增加 Web 页面上的环境提示：
   - 当前 profile。
   - trace path。
   - pending HITL 数量。
   - 最近 run。
3. Trace 区继续保持可测试服务层，Streamlit 文件只做薄 UI。
4. 为 Web service helper 增加更完整单测，避免 UI 改动破坏核心逻辑。

验收：

```powershell
python -m pytest tests/test_web_services.py -q
python scripts/verify_delivery.py
```

人工验收：

1. 打开 `http://127.0.0.1:8501`。
2. 运行 `say done`。
3. 查看 trace history。
4. 查看 HITL pending 列表。

完成标准：Web theater 是稳定演示入口，不再依赖临场排错。

---

### 阶段 4：后端 API 契约，再决定 React/TDesign

**目标**：如果需要对标 Codex/OpenCode，先建立后端 contract，再实现前端。

任务：

1. 新建 `src/agent_harness/server/`，提供 FastAPI app。
2. REST API 先覆盖最小闭环：
   - `POST /api/runs`
   - `GET /api/runs`
   - `GET /api/runs/{run_id}/trace`
   - `GET /api/hitl`
   - `POST /api/hitl/{id}/approve`
   - `POST /api/hitl/{id}/deny`
   - `POST /api/hitl/{id}/approve-and-continue`
   - `GET /api/workspace/tree`
   - `GET /api/workspace/file`
3. 所有 endpoint 只调用 service 层，不复制 harness 逻辑。
4. 用 FastAPI `TestClient` 完成 contract tests。
5. 只有当 contract 稳定后，再初始化 React/TDesign。

验收：

```powershell
python -m pytest tests/test_server_api.py -q
python scripts/verify_delivery.py
```

完成标准：前端技术栈可替换，核心业务 contract 已稳定。

---

### 阶段 5：React/TDesign GUI（有余力时执行）

**目标**：构建更接近 Codex/OpenCode 的三栏 UI，但不重写 harness。

最小页面：

1. 左侧 workspace 文件树，只读浏览优先。
2. 中间任务/聊天面板，显示 run 状态和 LLM 文本。
3. 右侧 trace / file / diff 查看。
4. HITL 审批弹窗或侧栏。

技术边界：

- 前端不直接读写文件系统。
- 前端不接触 API key 明文。
- 所有写入仍走后端 permission/HITL/scope。
- 不在第一版实现复杂编辑器保存；先展示 diff 和 trace。

验收：

```powershell
cd frontend
npm install
npm run build
```

人工验收：

1. 前端能连接后端。
2. 能运行 `say done`。
3. 能显示 trace。
4. 能显示 pending HITL 并审批。

完成标准：GUI 是 harness 的清晰入口，而不是另一个未验证 agent。

---

### 阶段 6：可恢复性与最终交付

**目标**：让用户后续把它改成个人专属 harness 时，有稳定基础。

任务：

1. 增加 checkpoint 或至少写前 diff/snapshot 机制。
2. 明确 `run_shell` 的启用方式和风险，默认继续禁用。
3. 完成 personal setup 文档：
   - 配 API。
   - 配 workspace。
   - 运行 CLI。
   - 启动 Web。
   - 审批 HITL。
   - 查看 trace。
4. 完成最终验证记录。
5. 安全同步沙箱成果到目标仓库。

验收：

```powershell
python scripts/verify_delivery.py
git status --short
```

最终用户验收路径：

1. 配置 profile。
2. 写入 credential。
3. 运行只读任务。
4. 运行写入任务并触发 HITL。
5. 审批继续。
6. 查看 trace。
7. 确认没有真实 key 或 `.env` 进入 Git。

---

## 5. 暂缓或降级的内容

以下内容不是第一优先级，除非主线已经稳定：

- 真正“任意 HTTP API”的无约束接入。
- 多 agent 协作。
- 自动大范围 shell 执行。
- 完整 IDE 级代码编辑器。
- WebSocket/SSE 实时事件。第一版可用轮询。
- 多项目工作区管理。第一版用 profile + workspace root 即可。

这些内容可以作为后续增强，但不能阻塞“个人 API + 任务执行 + HITL + trace”的核心闭环。

---

## 6. 每个切片的强制动作

每完成一个切片必须执行：

1. 先写或更新测试，再实现。
2. 运行目标测试。
3. 运行完整验证：

```powershell
python scripts/verify_delivery.py
```

4. 更新：
   - `PLAN.md`
   - `AGENT_LOG.md`
   - `README.md` 或相关 docs
   - 外部项目记录
5. 检查 secret/TODO scan。
6. 单独 commit，commit message 说明功能切片。

---

## 7. 安全红线

1. 不使用 LangChain `AgentExecutor`、AutoGen、CrewAI、LlamaIndex agent 等现成 agent 框架替代自实现内核。
2. 不把权限、scope、HITL、feedback 只写成提示词。
3. 不提交真实 API key、`.env`、个人凭据文件。
4. 默认不注册 `run_shell`。
5. approve 只绕过 permission ask，不绕过 scope。
6. Web UI 不直接操作文件系统，不显示 credential 明文。
7. 同步到桌面目标仓库前必须备份或 diff 审查，不能覆盖用户未提交更改。

---

## 8. 推荐的下一步

下一步不应立刻启动 React/TDesign。推荐顺序是：

1. 审查目标仓库与沙箱仓库差异，确认同步策略。
2. 将本计划与当前最终状态文档同步到目标仓库。
3. 补一个 `doctor` 或等价环境检查命令。
4. 做真实 API 只读 smoke。
5. 做 HITL 写入闭环 smoke。
6. 根据用户试用反馈决定是继续强化 Streamlit，还是启动 FastAPI + React。

这样能用最少返工把项目从“初步可用”推进到“用户可以持续使用和扩展”。
