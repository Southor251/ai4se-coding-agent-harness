# AI4SE Coding Agent Harness 项目文档

## 项目概要

构建一个 **Coding Agent Harness**（编码智能体脚手架），核心等式 `Agent = LLM + Harness`。LLM 负责"决策下一步做什么"，Harness 负责将其封装成稳定可靠的工程系统。本项目使用 Superpowers 框架开发，产物本身也是一个可独立运行的 harness 内核。

## 源文件

- 通用要求：`C:\Users\hp\Desktop\AI4SE_Final_Project_通用要求.md`
- A 项目专用：`C:\Users\hp\Downloads\AI4SE_Final_Project_A_Coding_Agent_Harness.md`

---

## 简报：全部要求与注意事项

### 一、项目本质（核心命题）

**当 LLM 能完成大部分编码工作时，工程师的真正价值在哪里。** 项目关注三个核心问题：
1. 能否引导 brainstorming 产出足够清晰的 spec？
2. 能否驾驭 plan + subagent 工作流，让智能体长时间自主推进而不脱轨？
3. 能否对智能体生成的代码做出有意义的评审与修正？

### 二、7 项学习目标

1. 从模糊想法 → 可执行的规约与计划
2. 设计端到端智能体工作流（task 拆分、subagent 派发、并行 worktree）
3. TDD + "先验证再宣称完成"的工程纪律
4. Prompt / Context Engineering 提升输出质量
5. 阅读、评审并修正智能体生成的代码
6. 需求 → 规约 → 计划 → 实现 → 凭据治理 → 分发的完整闭环
7. 对 agentic SE 方法论形成批判性见解

### 三、必须做的工程事项

#### 3.1 凭据 / API Key 安全存储（必做）

**注意事项：**
- Key **绝不硬编码**进源码、**绝不提交**进 Git（含历史）、**绝不写入日志 / 终端 history / 明文配置文件**
- 必须实现至少一种**安全存储**：Windows Credential Manager、加密文件、或带主密码的加密文件
- 环境变量可以作为来源，但必须通过 `.env` 文件加载（非命令行 `export`），且必须说明 `.env` 的明文风险
- 首次运行**必须引导用户安全录入** key（如隐藏输入）
- 必须支持查看 / 更新 / 清除（查看状态时**不得回显明文**）
- SPEC 安全一节中必须明确凭据威胁模型与对策

#### 3.2 分发（必做，三选一或多种）

- **容器镜像**（Docker / OCI）：单条 `docker build` + `docker run` 可启动，推送到公开 registry
- **原生可执行二进制**：单文件可执行，说明平台 / 架构 / 签名 / 系统拦截处理
- **包管理器分发**：npm / PyPI / cargo / Homebrew 等
- README 必须写清：获取方式、运行命令、**key 在目标机器上的安全配置方式**、已知限制

#### 3.3 规模与深度

- 无硬性行数下限，评价重心是**工程深度**
- 至少 **3 个以上职责清晰的功能模块**
- 可**一键运行的测试**
- 凭据与分发必须经得起"一台全新机器上从零运行"的检验
- **不接受纯 demo 或玩具级项目**

#### 3.4 工具链（强制要求）

- **必须使用 Superpowers 框架**（任选 Claude Code / Codex CLI / Cursor / OpenCode / Copilot CLI / Gemini CLI）
- 必须**如实遵循 Superpowers 七步工作流**（brainstorming → writing-plans → using-git-worktrees → subagent-driven-development / executing-plans → test-driven-development → requesting-code-review → finishing-a-development-branch）
- 偏离必须在 `AGENT_LOG.md` 中记录与解释
- **TDD 是硬性要求**：先红 → 再绿 → 再重构。不接受"先写实现再补测试"

#### 3.5 独立完成

个人项目，不允许组队。学生一人承担 PM / 架构师 / reviewer / 最终责任人。

### 四、Coding Agent Harness 专属要求

#### 4.1 你必须实现的 4 类机制

1. **动作 / 工具**：读写文件、执行 shell、运行构建与测试
2. **客观反馈信号**：运行测试 / lint / 类型检查，客观、确定、可回灌
3. **危险动作**：必须暂停并交人工审批（HITL），边界需设定
4. **记忆**：跨会话记忆 + 按需检索（非全量载入）

#### 4.2 实现边界（核心纪律）

**必须自己实现（不得寄生于现成框架）：**
- Agent 主循环：组织上下文 → 调用 LLM → 解析动作 → 分发执行 → 回灌结果 → 停机判断
- 可注入 mock 的 LLM 抽象层（可替换为 mock LLM 运行离线测试，也可接入真实供应商）

**允许使用的零件：**
- LLM 供应商的单次对话补全 API、HTTP 库、向量库、解析库

**严禁使用的：**
- 现成的 agent 编排框架的高层循环（LangChain `AgentExecutor`、AutoGen、CrewAI、LlamaIndex agent、编码智能体 SDK 自带的 agent runner）

**机制必须是代码，不能是提示词：**
- 反馈信号 = 你编写的**校验器 / 传感器**（解析产物 → 客观判定 → 回灌给循环）
- 危险动作拦截 = 你编写的**护栏**（识别危险动作 → 拦截 → 要求人工确认）

**判定标准（用于评分）：**
- 移除真实 LLM 后，每个核心机制仍能用确定性单元测试验证
- 配置文件 / 规则文件 / 技能文件 / 提示词文件**不计入 harness 实现工作量**

#### 4.3 基础完整 + 重点深入

- 六个维度（决策 / 工具 / 记忆 / 治理 / 反馈 / 配置）都要有**可运行的最低实现**
- 选择一个维度**深入实现**作为主要贡献
- 推荐的深入维度：治理（护栏 / 沙箱 / HITL 状态机）、反馈闭环（确定性校验器 + 失败分类 + 多轮自我修正）、扩展（工具分发 / 多 agent 编排）

### 五、工作流程与过程要求

#### 5.1 核心红线

**在 SPEC 与 PLAN 完成并通过冷启动验证之前，禁止编写任何实现代码。**

#### 5.2 完整工作流

1. **规约与计划生成**（brainstorming → writing-plans）
2. **交付物 1: SPEC.md**（10 项标准内容 + "领域与机制设计"额外节）
3. **交付物 2: PLAN.md**（task 颗粒度细、含验证步骤、标出依赖与可并行部分）
4. **交付物 3: SPEC_PROCESS.md**（3 轮关键迭代、对话节选、决策记录、反思）
5. **自我验证：冷启动试运行**
   - 使用**与主开发智能体不同**的 agent
   - **不导入任何先前会话或 memory**
   - 仅提供 SPEC + PLAN
   - 指定它从 PLAN 选 1–2 个 task 自主推进
   - 记录它的暂停点、不一致解读、spec 缺陷

#### 5.3 实现工作流

1. **git worktrees 隔离工作区**：每个独立功能 / 大模块开一个 worktree，对应一个 PR
2. **subagent 驱动开发**：每个 task 派一个新鲜 subagent
3. **TDD 强制**：红–绿–重构，没有先于测试写出的实现
4. **两阶段评审**：先 spec 合规检查 → 再代码质量检查。Critical issue 必须修复
5. **完成分支**：由 `finishing-a-development-branch` 决定 merge / PR / 保留 / 丢弃

### 六、GitHub 仓库要求

- 公开 GitHub 仓库（私有仓需加助教为协作者）
- **完整的 commit 历史与 PR 工作流**：拒绝单次 commit 提交全部代码
- **每个 worktree 对应一个 PR**
- **仓库内不得出现任何真实凭据**（提交前自查 `.env`、history、配置文件）
- commit message / PR 描述中标注由哪个 subagent 完成、人工修改了哪些部分
- **PLAN.md 持续更新**：每完成一个 task 即标记完成并附 commit hash
- 维护 `AGENT_LOG.md`

### 七、测试要求

#### 通用测试要求
- 可一键运行的测试命令（`make test` 或等价）
- 覆盖核心功能
- CI（GitHub Actions）配置：每次 push 自动运行测试
- CI 配置 `.gitlab-ci.yml`，**必须**包含名为 `unit-test` 的 job
- 最后一次 CI/CD 执行**必须**是 pass 状态

#### Harness 专属测试要求
- **核心机制必须用 mock / stub LLM 写确定性单元测试**（不依赖网络与真实 LLM）
- **提交机制演示**，在 mock LLM 下确定性地复现：
  1. 治理护栏拦截一个危险动作
  2. 注入一次失败，反馈闭环使 agent 收到反馈并改变下一步动作
  3. 重点维度的一个确定性行为

### 八、最终交付物清单

1. `SPEC.md`（设计文档，含"领域与机制设计"节）
2. `PLAN.md`（实现计划）
3. `SPEC_PROCESS.md`（过程文档）
4. 完整源代码（含 harness 内核 + mock-LLM 单元测试 + 机制演示）
5. 分发产物与说明（Dockerfile 或二进制构建脚本 / 打包配置）
6. `README.md`（项目简介、安装、运行、分发命令、目录结构、安全边界说明）
7. `AGENT_LOG.md`（过程日志）
8. `.gitlab-ci.yml`（含 `unit-test` job）
9. CI/CD 执行记录（最后一次必须 pass）
10. `REFLECTION.md`（1500–2500 字反思报告，**必须本人撰写**）
11. 线上部署 URL（可访问的 WebUI 接口）

### 九、学术规范

- 手写核心算法时须在文件 / 函数顶部注释说明
- 第三方代码须遵守许可证，在 README 中列出
- 反思报告必须本人撰写，可用 AI 辅助润色但须标注

### 十、推荐资源（必读）

- Superpowers 仓库与文档：https://github.com/obra/superpowers
- Superpowers 发布博文：https://blog.fsck.com/2025/10/09/superpowers/
- Open Design（前端/UI 项目）：https://github.com/nexu-io/open-design
- 所选编码智能体的 Superpowers 安装与使用文档
- OS 钥匙串 / 凭据管理接口文档
- 所选分发形态的打包文档

---

## 开发计划

### 阶段 0：环境与准备工作

| # | 任务 | 预期产出 |
|---|------|----------|
| 0.1 | 确定编码智能体（OpenCode）及 Superpowers 版本 | 确认可用 |
| 0.2 | 创建 GitHub 公开仓库 | 仓库 URL |
| 0.3 | 确定技术栈（建议 Python，便于凭据管理 + 跨平台 + 测试） | 技术选型确认 |
| 0.4 | 确定分发形态（建议 Docker + PyPI 双通道） | 分发方案确认 |

### 阶段 1：Brainstorming → SPEC.md

| # | 任务 | 预期产出 | 涉及技能 |
|---|------|----------|----------|
| 1.1 | 启动 brainstorming 技能，明确问题域与用户故事 | 问题陈述 + 5+ 用户故事 | brainstorming |
| 1.2 | 设计 4 类机制（动作/工具、反馈、危险动作、记忆） | 机制设计文档 | brainstorming |
| 1.3 | 确定重点深入维度（建议：**治理护栏 + 反馈闭环**） | 主要贡献声明 | brainstorming |
| 1.4 | 设计凭据方案（Windows Credential Manager + .env 回退） | 凭据存储设计 | brainstorming |
| 1.5 | 设计分发方案、系统架构、数据模型 | 架构图 + 数据模型 | brainstorming |
| 1.6 | 编写 SPEC.md 终稿（含"领域与机制设计"节） | SPEC.md | writing-plans |
| 1.7 | 编写 SPEC_PROCESS.md | SPEC_PROCESS.md | — |

### 阶段 2：Writing Plans → PLAN.md

| # | 任务 | 预期产出 |
|---|------|----------|
| 2.1 | 触发 writing-plans 技能，分解 task | task 列表 |
| 2.2 | 每个 task 标注：目标、文件路径、实现要点、验证步骤 | 完整 PLAN.md |
| 2.3 | 标出 task 间依赖与可并行部分 | 依赖图 |

### 阶段 3：冷启动验证

| # | 任务 | 预期产出 |
|---|------|----------|
| 3.1 | 用不同 agent（建议 Cursor Agent），仅给 SPEC + PLAN | 冷启动测试 |
| 3.2 | 记录暂停点、不一致解读、spec 缺陷 | 反馈记录 |
| 3.3 | 修订 SPEC / PLAN | SPEC/PLAN v2 |

### 阶段 4：实现（按 worktree 并行）

| # | 任务 | 涉及文件 | 依赖 | 验证 |
|---|------|----------|------|------|
| 4.1 | **LLM 抽象层**：`LLMInterface` 抽象基类 + `MockLLM` + `RealLLM` | `src/llm/` | 无 | 单元测试：mock 返回固定响应 |
| 4.2 | **Agent 主循环**：`AgentLoop(context → call_llm → parse → dispatch → feedback → halt)` | `src/agent/loop.py` | 4.1 | 单元测试：mock LLM 驱动循环 |
| 4.3 | **工具系统**：文件读写工具 + Shell 执行工具 + 工具注册表 | `src/tools/` | 4.2 | 单元测试：工具注册和调度 |
| 4.4 | **治理护栏**：`Guardrail` 危险动作识别 + HITL 拦截状态机 | `src/governance/guardrail.py` | 4.2 | **Mock测试：拦截危险命令** |
| 4.5 | **反馈闭环**：`FeedbackSensor` 测试结果解析 → 分类 → 回灌修正 | `src/feedback/` | 4.2 | **Mock测试：注入失败→行为改变** |
| 4.6 | **记忆系统**：会话级记忆 + 跨会话持久化 + 按需检索 | `src/memory/` | 无 | 单元测试：记忆读写 |
| 4.7 | **配置系统**：声明式 YAML 配置 → agent 行为约束 | `src/config/` | 4.2 | 单元测试：配置加载与校验 |
| 4.8 | **凭据管理**：Windows Credential Manager 集成 + 首次引导 | `src/credentials/` | 无 | 手动测试 + 单元测试 |
| 4.9 | **CLI 入口**：命令行界面（参数解析、子命令） | `src/cli/` | 4.1-4.8 | 集成测试 |

### 阶段 5：测试与 CI

| # | 任务 | 预期产出 |
|---|------|----------|
| 5.1 | 编写 mock-LLM 单元测试（覆盖所有核心机制） | `tests/test_*` |
| 5.2 | 实现 **机制演示脚本**（危险动作拦截 + 反馈修正 + 重点维度展示） | `demo/mechanism_demo.py` |
| 5.3 | 配置 `make test` 一键运行命令 | `Makefile` |
| 5.4 | 配置 `.gitlab-ci.yml`（含 `unit-test` job） | `.gitlab-ci.yml` |
| 5.5 | 配置 GitHub Actions（push 自动测试 + 构建） | `.github/workflows/` |

### 阶段 6：分发与文档

| # | 任务 | 预期产出 |
|---|------|----------|
| 6.1 | Dockerfile（多阶段构建 + 最小镜像） | `Dockerfile` |
| 6.2 | PyPI 打包配置（`pyproject.toml`） | `pyproject.toml` |
| 6.3 | 编写 README.md | README.md |
| 6.4 | 编写 AGENT_LOG.md | AGENT_LOG.md |
| 6.5 | WebUI 部署（可选，满足最终交付物清单第 9 项） | 部署 URL |

### 阶段 7：复盘与提交

| # | 任务 | 预期产出 |
|---|------|----------|
| 7.1 | 更新 PLAN.md（标记完成 + commit hash） | PLAN.md |
| 7.2 | 编写 REFLECTION.md（1500–2500 字，本人撰写） | REFLECTION.md |
| 7.3 | 安全检查：确认 `.env`、history、配置文件中无真实凭据 | 清除验证 |
| 7.4 | 最终 CI/CD 通过 | Pass 状态截图 |
| 7.5 | 提交 NJU Git 仓库 | 最终提交 |

---

## 设计决策记录（Brainstorming 已确认）

> 每条决策包含：编号、决策内容、理由、取舍考量。后续项目遇到相关问题时先查此表。

| # | 决策 | 内容 | 理由 | 取舍 |
|---|------|------|------|------|
| D01 | 项目定位 | 教学演示型为主（B），兼顾个人长期使用 | AI4SE 课程要求展示 harness 内部机制；同时满足"有人使用"的工程检验 | 深度优先于广度，教学清晰度优先于功能完整 |
| D02 | 技术栈 | Python 核心 + Streamlit 前端 | 开发工具 dsv4flash 对 Python 标准库/Streamlit 可靠性最高；Python 是 AI4SE 默认语言，读者门槛最低 | 放弃 FastAPI+HTMX 的架构简洁性，换取 AI 开发稳定性 |
| D03 | 前端框架 | Streamlit（自定义主题 + 少量 CSS） | 纯 Python，API 极简单；dsv4flash 训练数据覆盖充分；一行 `docker run` 可访问 WebUI | 界面可定制性不如 React，但足以做到"大方" |
| D04 | 插件系统 | 架构按 C 级（全量插件框架）预留接口，实际实现 B+ 级（entry_points 发现 + 5 扩展点 + 4 钩子） | 教学演示目标下，插件机制不应稀释核心机制（护栏+反馈）的深度；C 级骨架可展示架构前瞻性 | 插件不是主要贡献，不投入过多精力 |
| D05 | 重点深入维度 | 治理护栏（Guardrail + HITL 状态机）+ 反馈闭环（确定性校验器 + 失败分类 + 多轮自我修正） | 两者天然适合编码实现（非提示词），可用 mock LLM 写确定性单元测试，是 harness 工程深度的最强体现 | 记忆/配置维度只做最低可运行实现 |
| D06 | LLM 供应商 | OpenAI API（兼容性最广），通过 LLM 抽象层支持插件式切换 | 教学演示时使用 mock LLM 离线运行 | 实际调用需 API key，凭据管理必须安全实现 |
| D07 | 分发形态 | Docker（多阶段构建 + 最小镜像）+ PyPI（`pyproject.toml`） | Docker 覆盖"新机器零配置运行"的检验；PyPI 满足开发者安装习惯 | 不选原生二进制（跨平台交叉编译复杂度高，dsv4flash 调试困难） |
| D08 | 冷启动验证 agent | Cursor Agent 或 Claude Code | 与主开发智能体 OpenCode 类型不同，满足"换 agent 测试 spec 清晰度"的要求 | — |

### v2.0 修订决策（2026-07-07，基于 Codex gpt-5.5 审阅报告 + dsv4flash 能力边界）

| # | 决策 | 内容 | 理由 | 取舍 |
|---|------|------|------|------|
| D09 | 范围收缩为垂直切片 | v1 只做端到端最短路径：主循环 + MockLLM + 5 工具 + 权限引擎 + 路径围栏 + 反馈分类 + trace JSONL + Agent Loop Theater + 插件系统 | v1.0 的 14 阶段约 50 task 对 dsv4flash 体量过大，容易做成"每个模块都有文件，核心机制不够硬"；深度优先于广度 | 文件快照、跨会话记忆、PyPI、LSP、双通道 HITL 移到未来工作 |
| D10 | 新增 PermissionPolicy | allow/ask/deny 三态权限引擎，deny 优先级最高 | 参考 OpenCode permissions 与 Codex permissions，有真实工程出处；三态比 v1.0 的两态更贴合真实 agent 权限模型 | — |
| D11 | 新增 ScopeGuard | workspace root + 路径规范化（realpath 解析 `..`、符号链接）+ 敏感路径 deny | 不做真沙箱时，路径围栏是最低可信的治理边界；Codex sandbox 也以 workspace root 为基础 | 不做容器级沙箱隔离 |
| D12 | 新增 TraceStore | JSONL 格式，每行一个 step（决策 + 观察结果），增量落盘 | 参考 OpenCode trace 与 agent-loop.html 可观测性概念卡的双节奏；是 Agent Loop Theater 回放的数据源 | — |
| D13 | 自愈闭环改为确定性可测 | FeedbackSensor 分类失败 → 注入结构化 feedback → MockLLM 选择预设动作；不依赖 LLM 理解力 | A.4-(C) 硬标准：移除真实 LLM 后机制仍可单测；v1.0 描述"agent 自动分析失败"依赖 LLM 智能，不可测 | — |
| D14 | WebUI 改为 Agent Loop Theater | 运行 demo 生成 trace.jsonl → Streamlit 读取回放 → 金色/蓝色手术灯可视化 | 确定性回放，不依赖 session_state，dsv4flash 可靠；直接呼应课件 agent-loop.html 的"逐步展开 agent 一生" | 放弃实时观察（dsv4flash 对 Streamlit session_state 不可靠） |
| D15 | 插件发现改为显式注册为主 | YAML 配置显式注册为主路径，entry_points 为可选增强（带配置开关） | dsv4flash 对 importlib.metadata 覆盖不足；显式注册更可靠 | entry_points 仍保留，作为 pip 安装插件的自动发现 |
| D16 | 分发仅 Docker | v1 只做 Docker 分发，PyPI 移到未来工作 | Docker 覆盖"新机器零配置运行"检验已足够；PyPI 增加打包复杂度 | — |

### 取舍原则备忘

本项目的核心质量指标（按优先级）：
1. **工程深度可验证**：核心机制（权限引擎、路径围栏、反馈传感器）移除 LLM 后仍可用确定性单元测试验证
2. **教学演示清晰**：评审人可从源码 + Agent Loop Theater 直观理解 harness 如何运转
3. **凭据与分发经得起"全新机器从零运行"**：以 Docker 覆盖
4. **个人可扩展**：插件接口保留（显式注册 + entry_points 可选）