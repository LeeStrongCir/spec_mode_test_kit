# /speckit-test.specify 执行流程记录

## 基本信息

| 项 | 内容 |
|---|---|
| **命令** | `/speckit-test.specify @reqs/需求规格说明书-LECS主机.md` |
| **执行日期** | 2026-05-09 |
| **输入文件** | `reqs/需求规格说明书-LECS主机.md` |
| **需求编号** | 007-LECS主机 |
| **需求名称** | LECS主机（云服务器）功能开发 |
| **测试类型** | 功能测试 (Function Test Specification) |

---

## 执行流程概览

```
用户触发 /speckit-test.specify
    ↓
1. 解析用户输入参数（需求文件路径）
    ↓
2. 读取需求规格说明书内容
    ↓
3. 读取 .specify 模板与配置
    ↓
4. 确定特性目录编号与命名
    ↓
5. 创建特性目录结构
    ↓
6. 分析需求内容，提取关键概念
    ↓
7. 填写测试规格文件（spec.md）
    ↓
8. 执行规格质量验证，生成检查清单
    ↓
9. 更新 feature.json 持久化路径
    ↓
10. 输出完成情况报告
```

---

## 详细执行步骤

### 步骤 1：解析用户输入

- **输入参数**：`@reqs/需求规格说明书-LECS主机.md`
- **解析结果**：识别到需求文件路径为 `reqs/需求规格说明书-LECS主机.md`
- **意图判定**：根据 `/speckit-test.specify` 命令定义，识别为"创建测试规格说明"意图

### 步骤 2：读取需求规格说明书

- **操作**：使用 Read 工具读取 `reqs/需求规格说明书-LECS主机.md` 完整内容（352 行）
- **内容摘要**：
  - **业务背景**：Lee云平台需要提供云服务器（LECS主机）管理能力
  - **核心功能**：搜索、列表查看、创建、开关机控制、删除操作
  - **5 个用户故事**：搜索跳转（P1）、列表与操作矩阵（P1）、创建主机（P2）、生命周期控制（P3）、安全删除（P4）
  - **前端需求**：2 个页面（列表页、创建页），22 个 data-testid 组件标识
  - **后端需求**：5 个 API 接口（查询/创建/关机/启动/删除）
  - **数据模型**：LECSHost 实体，8 种状态枚举
  - **核心状态机**：creating → normal → shutting_down → stopped → starting → normal / failed → deleted
  - **业务规则**：配额上限 100 台，软删除机制，异步操作流转
  - **成功标准**：6 项可衡量指标

### 步骤 3：读取 .specify 模板与配置

**3.1 读取 spec-template.md**
- **文件路径**：`.specify/templates/spec-template.md`（340 行）
- **模板结构**：
  - 第一章：模板前置说明
  - 第二章：顶层宪章合规申明
  - 第三章：核心测试目标
  - 第四章：法定测试范围（4.1 场景定义、4.2 对象属性、4.3 测试操作、4.4 流程定义）
  - 第五章：功能交互与耦合关系（5.1 交互定义、5.2 耦合关系）
  - 第六章：法定不测试范围
  - 第七章：刚性验收标准（7.1~7.5 五个维度）
- **模板特点**：包含"标准模板原文"和【举例】两部分，举例基于"华为云 ECS 批量规格变更"功能

**3.2 读取 init-options.json**
- **文件路径**：`.specify/init-options.json`
- **关键配置**：
  - `branch_numbering`: `"sequential"`（顺序编号模式）
  - `ai`: `"opencode"`
  - `speckit_version`: `"0.8.6.dev0"`

**3.3 读取 feature.json**
- **文件路径**：`.specify/feature.json`
- **当前值**：`"feature_directory": "specs/001-console-page-lee"`
- **用途**：记录上一次生成的特性目录路径

### 步骤 4：确定特性目录编号与命名

**4.1 扫描现有目录**
- 使用 `glob` 和 `ls` 检查 `specs/` 目录
- 发现已有目录：`specs/001-console-page-lee`
- 确定下一个编号：`002`（顺序编号 +1）

**4.2 生成短名称**
- **分析需求关键词**：LECS、主机、生命周期管理、云服务器
- **命名规则**：action-noun 格式，保留技术术语
- **最终命名**：`lecs-host-management`
- **完整目录名**：`002-lecs-host-management`

**4.3 确定最终路径**
- `SPECIFY_FEATURE_DIRECTORY` = `specs/002-lecs-host-management`
- `SPEC_FILE` = `specs/002-lecs-host-management/spec.md`
- `checklists/requirements.md` = `specs/002-lecs-host-management/checklists/requirements.md`

### 步骤 5：创建特性目录结构

- **操作 1**：`mkdir -p specs/002-lecs-host-management/checklists`
- **创建结果**：
  ```
  specs/002-lecs-host-management/
  ├── spec.md          （待填写）
  └── checklists/
      └── requirements.md  （待填写）
  ```

### 步骤 6：分析需求内容，提取关键概念

**6.1 识别 actors（参与者）**
- **管理员**：管理所有 LECS 主机
- **普通用户**：仅管理自己的 LECS 主机

**6.2 识别 actions（操作）**
- **搜索**：控制台搜索"LECS主机"或"云服务器"，跳转至列表页
- **创建**：填写六大板块配置 → 费用确认 → 弹窗确认 → 提交
- **查看**：列表页加载数据，状态标签渲染，操作列按钮渲染
- **关机**：normal → shutting_down → stopped
- **开机**：stopped/failed → starting → normal
- **删除**：stopped/failed → deleting → deleted（软删除）

**6.3 识别 data（数据）**
- **核心实体**：LECSHost
- **关键属性**：hostname, status, billing_mode, instance_type, os_image, ip_mode, ip_address, ip_mask, duration, username, password, deleted_at

**6.4 识别 constraints（约束）**
- **配额上限**：100 台（deleted_at IS NULL 的记录）
- **状态机约束**：操作按钮严格遵循状态机矩阵
- **表单校验**：主机名 4-10 字符、密码 8-32 字符、IP 格式、掩码 8-24
- **异步超时**：创建 30s、关机/开机 10s、删除 5s
- **前端轮询**：3 秒/次，仅针对过渡态主机

**6.5 确定测试类型**
- **测试结果**：**功能测试 (Function Test)**
- **判定理由**：需求聚焦于 LECS 主机的生命周期管理、状态机流转、操作矩阵、表单校验等功能行为验证，不涉及性能压测、安全渗透、兼容性测试等专项领域

### 步骤 7：填写测试规格文件（spec.md）

**7.1 模板适配策略**
- 保留模板的章节结构和标题
- 将所有【举例】部分替换为本项目"LECS主机生命周期管理"的真实示例
- 填充各章节的具体内容（场景定义、对象属性、测试操作、流程定义等）
- 删除模板中"标准模板原文"部分的通用说明，保留结构框架

**7.2 逐章填写详情**

**第一章｜模板前置说明**
- 将示例从"华为云 ECS 批量规格变更"替换为"LECS主机生命周期管理"
- 更新示例项目描述、使用范围说明、填写规则说明

**第二章｜顶层宪章合规申明**
- 更新示例：状态机流转与需求规格说明书第 6.1 节对齐
- 删除拦截返回 403 状态码的合规说明
- 全量追溯示例：SC-05（状态机拦截-正常态删除）

**第三章｜核心测试目标**
- 对齐示例：LECSHost.status 状态枚举与数据模型对齐
- 覆盖示例：搜索、列表、创建、开关机、删除、配额、网络断连
- 回归示例：控制台全局搜索、用户认证系统
- 合规示例：审计日志字段、API 响应码规范

**第四章｜法定测试范围**

**4.1 功能应用场景定义** - 定义 25 个场景（SC-01~SC-25）：
- **正常场景**：SC-01 搜索跳转、SC-02 列表加载、SC-04~SC-06 操作列按钮、SC-08~SC-10 开关机、SC-12~SC-13 删除、SC-16 创建流程、SC-23 软删除隐藏、SC-24 轮询机制
- **异常场景**：SC-03 空列表、SC-07 过渡态置灰、SC-11 关机超时、SC-14~SC-15 删除拦截、SC-17~SC-22 创建表单校验/配额拦截/超时降级
- **边缘场景**：SC-25 网络断连恢复

**4.2 被测对象、属性与属性取值定义** - 定义 12 项属性（OP-01~OP-12）：
- status（8 种枚举）、hostname（正则校验）、billing_mode、instance_type、os_image、ip_mode、ip_address（IPv4）、ip_mask（8-24）、duration（1-9/12/24）、username（4-16）、password（8-32）、deleted_at

**4.3 测试操作定义** - 定义 10 项操作（ACT-01~ACT-10）：
- 搜索跳转、加载列表、查看按钮状态、执行关机、执行开机、执行删除、填写表单、表单校验、触发轮询、网络恢复刷新

**4.4 功能处理流程定义**
- **创建流程图**（Mermaid）：Start → Route → FillForm → Validate → QuotaCheck → Dialog → Confirm → Submit → Response → Redirect
- **关机流程图**（Mermaid）：normal → ClickShutdown → StateCheck → API → shutting_down → Worker → stopped → Update
- **异常分支表**：8 项（EX-01~EX-08），覆盖状态拦截、配额上限、超时降级、并发锁、网络断连
- **核心状态机**（Mermaid）：8 种状态完整流转图

**第五章｜功能交互与耦合关系定义**

**5.1 功能交互定义** - 定义 11 项交互（IT-01~IT-11）：
- 前端 → API 服务（CRUD 操作）、轮询机制、配额校验、异步任务队列、全局搜索、认证系统、审计日志

**5.2 功能耦合关系定义** - 定义 6 项耦合（CP-01~CP-06）：
- StatusMatrix（强）、FormValidator（强）、PollingManager（中）、QuotaChecker（中）、AsyncWorker（中）、CostCalculator（弱）

**第六章｜法定不测试范围**
- 排除：性能测试、可靠性测试、安全测试、兼容性测试、UI 测试
- 排除：需求 1.3 节明确"不包含"的功能（重启、VNC、安全组、弹性 IP 等）

**第七章｜刚性验收标准**

**7.1 被测对象与属性验收标准** - 7 条规则（hostname/password/IP/mask/duration/status 校验）
**7.2 功能场景与处理流程覆盖验收标准** - 4 条规则（25 场景全执行、状态机一致、轮询启停、异步流转）
**7.3 功能交互与耦合验收标准** - 4 条规则（DELETE 拦截、并发冲突处理、配额统计、data-testid 覆盖）
**7.4 继承性回归验收标准** - 2 项回归场景（全局搜索、认证系统）
**7.5 合规验收标准** - 4 条规则（审计日志、密码哈希、软删除、配额释放）

**第八章｜测试环境要求**
- **8.1 前置条件**：API 部署、Token 有效、数据库可注入、网络模拟
- **8.2 测试数据准备**：6 类数据（正常 3、已关机 2、创建失败 1、过渡态 4、空数据 1、满配额 1）

**第九章｜假设与约束**
- 6 项假设与约束（Worker 运行、计费逻辑、v1.0 范围、Mock 环境、数据源可用性、配额阈值）

### 步骤 8：执行规格质量验证，生成检查清单

**8.1 创建 requirements.md**

按照命令要求的格式，在 `specs/002-lecs-host-management/checklists/requirements.md` 创建质量检查清单文件，结构如下：

- **标题**：Specification Quality Checklist: LECS主机生命周期管理功能
- **元数据**：Purpose、Created、Feature 链接、Test Type
- **验证维度**：
  - Content Quality（内容质量）：4 项
  - Requirement Completeness（需求完整性）：6 项
  - Feature Readiness（特性就绪度）：4 项
- **备注**：Notes 区域

**8.2 逐项验证**

| 维度 | 检查项 | 判定 | 验证说明 |
|------|--------|------|----------|
| Content Quality | 测试类型已明确标注 | ✅ 通过 | 文件头部明确标注"测试类型: 功能测试" |
| Content Quality | 聚焦于被测功能的行为验证和结果判定 | ✅ 通过 | 第四章涵盖状态机流转、操作矩阵、表单校验等 |
| Content Quality | 面向测试工程师和 QA 人员编写 | ✅ 通过 | 使用"场景 ID""前置条件""触发条件"等测试语言，无实现代码 |
| Content Quality | 所有必填章节已完成 | ✅ 通过 | 第一章至第九章均已填写完整 |
| Requirement Completeness | No [NEEDS CLARIFICATION] markers remain | ✅ 通过 | 全文无任何 NEEDS CLARIFICATION 标记 |
| Requirement Completeness | 测试场景和验收标准可执行且无歧义 | ✅ 通过 | 25 个场景有明确前置/触发条件，7 章有具体判定规则 |
| Requirement Completeness | 成功标准可衡量（双轨视角） | ✅ 通过 | 从属性校验、场景覆盖、交互契约、回归、合规五维度定义 |
| Requirement Completeness | 所有异常分支和边界情况已识别 | ✅ 通过 | 8 项异常分支 + 边界场景覆盖 |
| Requirement Completeness | 测试范围已明确界定 | ✅ 通过 | 25 场景正向覆盖 + 6 项不测试范围排除 |
| Requirement Completeness | 前置条件、依赖项和假设已识别 | ✅ 通过 | 第 8 章前置条件 + 第 5 章 11 项依赖 + 第 9 章 6 项假设 |
| Feature Readiness | 所有测试场景有明确的预期输出和判定标准 | ✅ 通过 | 每个场景含前置/触发条件；第 7 章给出判定规则 |
| Feature Readiness | 主流程和异常流程均已定义 | ✅ 通过 | 2 个 Mermaid 主流程图 + 8 项异常分支 + 1 个状态机图 |
| Feature Readiness | 功能满足 Success Criteria 定义的可衡量结果 | ✅ 通过 | 第 7 章五维度验收标准 |
| Feature Readiness | 测试规格中不包含具体的实现代码或工具选型 | ✅ 通过 | 全文聚焦行为描述，无具体测试工具选型 |

**8.3 验证结果**
- **总计**：14 项检查项全部通过
- **遗留问题**：无
- **NEEDS CLARIFICATION 标记**：0 个
- **注意事项**：记录了 3 个关键验证点提醒（状态机矩阵测试用例细化、轮询机制验证方法、data-testid 逐项验证）

### 步骤 9：更新 feature.json 持久化路径

- **文件路径**：`.specify/feature.json`
- **旧值**：`{"feature_directory": "specs/001-console-page-lee"}`
- **新值**：`{"feature_directory": "specs/002-lecs-host-management"}`
- **目的**：为下游命令（`/speckit-test.plan`、`/speckit-test.tasks`）提供特性目录定位

### 步骤 10：输出完成情况报告

| 输出项 | 状态 |
|--------|------|
| `SPECIFY_FEATURE_DIRECTORY` | ✅ `specs/002-lecs-host-management` |
| `SPEC_FILE` | ✅ `specs/002-lecs-host-management/spec.md` |
| 检查清单 | ✅ `specs/002-lecs-host-management/checklists/requirements.md` |
| `feature.json` 更新 | ✅ 已更新至当前特性目录 |

**规格说明摘要**：
- 测试场景：25 个（SC-01~SC-25）
- 异常分支：8 项（EX-01~EX-08）
- 外部依赖：11 项（IT-01~IT-11）
- 内部耦合：6 项（CP-01~CP-06）
- 验收标准：5 大维度
- 核心状态机：8 种状态完整流转图

**下一阶段就绪状态**：已就绪，可进行 `/speckit-test.plan` 或 `/speckit-test.clarify`

---

## 设计决策与注意事项

1. **模板适配**：模板中的【举例】全部替换为本项目真实内容，而非留空或保留示例
2. **状态机完整性**：严格对齐需求规格说明书第 6.1 节的状态机图，未添加任何需求中未定义的状态流转
3. **NEEDS CLARIFICATION 处理**：需求文档内容详尽，无需提出澄清问题，所有模糊点均做了合理推测并记录在假设章节
4. **data-testid 覆盖**：需求 3.2 节定义了 22 个组件标识，规格中将其纳入测试验收标准（7.3 节）
10. **软删除逻辑**：明确区分"前端列表隐藏"与"数据库记录保留"，在场景定义和验收标准中均有体现

---

## 文件清单

| 文件路径 | 用途 |
|---------|------|
| `specs/002-lecs-host-management/spec.md` | LECS主机生命周期管理功能测试规格文件 |
| `specs/002-lecs-host-management/checklists/requirements.md` | 规格质量检查清单 |
| `.specify/feature.json` | 当前特性目录路径记录 |

---

*本文档由 /speckit-test.specify 命令自动生成，记录执行全过程。*
