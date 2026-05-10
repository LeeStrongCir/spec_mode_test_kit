# 研究与决策记录: LECS主机管理

> **版本**: `001-lecs-host-management`
> **创建日期**: 2026-05-11
> **目的**: 记录测试计划阶段的技术决策，澄清所有 NEEDS CLARIFICATION 项

## 技术上下文决策

### 决策 1: 测试框架选择

**Decision**: 集成测试使用 pytest（Python），端到端测试使用 Playwright（TypeScript）

**Rationale**: 
- 源规格提及后端基础设施使用 Celery/RQ（Python 生态），表明后端为 Python 框架（FastAPI/Flask）
- pytest 为 Python 生态标准测试框架，支持 fixture、参数化、插件生态（pytest-mock、freezegun、pytest-xdist）
- Playwright 为现代浏览器自动化首选，支持自动等待、多浏览器、TypeScript 类型安全
- 宪章要求"测试框架必须支持并行执行"——pytest-xdist + Playwright 均满足

**Alternatives considered**:
- Jest + Puppeteer（更适合 Node.js 后端，本项目后端为 Python）
- Selenium + pytest（Playwright 的自动等待机制更稳定，减少 flaky 测试）
- Cypress（仅支持 Chromium 系浏览器，Playwright 支持更多浏览器引擎）

### 决策 2: 测试数据库策略

**Decision**: 集成测试使用 SQLite 内存数据库，端到端测试使用 PostgreSQL test container

**Rationale**:
- 集成测试需要快速、确定性的数据库交互；SQLite 内存库零配置、零 I/O
- E2E 测试需要验证真实应用行为（包括软删除 `deleted_at` 时间戳精度、分页查询性能）
- 宪章要求"集成测试中所有外部依赖必须使用 mock/stub"——数据库在集成测试中视为"可控依赖"而非"外部服务"

**Alternatives considered**:
- 统一 PostgreSQL test container（集成测试启动慢，增加 CI 时间）
- 统一 SQLite 内存库（无法验证生产数据库特有的 SQL 方言行为）

### 决策 3: 异步任务 Mock 策略

**Decision**: 集成测试中 mock 异步任务执行器，通过 `freezegun` 精确控制时间

**Rationale**:
- 真实 Celery 需要 Redis broker + worker 进程，增加测试基础设施复杂度
- Mock 执行器可通过确定性时间控制测试超时逻辑（60s 创建超时降）和轮询逻辑（3s 间隔）
- 宪章要求"集成测试中所有外部依赖必须使用 mock/stub"——任务队列明确属于外部服务

**Alternatives considered**:
- 使用真实 Celery + Redis + Docker Compose（基础设施重，CI 环境不稳定）
- 使用 `CELERY_TASK_ALWAYS_EAGER=True`（同步执行，无法测试异步状态流转和轮询逻辑）

### 决策 4: E2E 测试元素定位策略

**Decision**: Playwright 测试优先使用 `data-testid` 属性定位元素

**Rationale**:
- `data-testid` 不受 CSS 类名变更和 DOM 结构调整影响
- 源规格提到"前端页面风格与控制台保持一致"——意味着 UI 可能频繁重构
- 宪章未强制定位策略，但稳定性是 E2E 测试核心要求

**Alternatives considered**:
- CSS 选择器（易受 Tailwind/CSS modules 重构影响）
- XPath（极度脆弱，DOM 层级变化即断裂）
- 文本内容匹配（多语言/国际化场景下不稳定）

### 决策 5: 角色权限测试数据策略

**Decision**: 为每个权限测试场景创建独立的用户 fixture（test_user、admin_user、user_a、user_b）

**Rationale**:
- 宪章要求"测试数据必须隔离（测试之间无共享可变状态）"
- 角色权限测试需要至少 3 种角色（admin、user_a、user_b）验证越权场景
- Factory Boy 模式支持快速创建隔离的用户实例

**Alternatives considered**:
- 使用共享测试账号（违反宪章的数据隔离要求）
- 手动 SQL 插入用户记录（维护成本高，不可读）

### 决策 6: 边界值分析技术

**Decision**: 对所有输入字段应用边界值分析 + 等价类划分（ISO 29119-4 要求）

**Rationale**:
- 宪章明确要求"数据设计视图必须使用边界值分析 + 等价类划分"
- 主机名（4-10 字符）、用户名（4-16 字符）、密码（8-32 字符）、IP 地址（格式校验）、掩码（8-24）均有明确的边界约束
- 每个字段需要测试：下界-1、下界、中间值、上界、上界+1、非法格式

**Alternatives considered**:
- 仅测试合法值和非法值（不满足宪章的 ISO 29119 要求）
- 随机模糊测试（无系统性的边界覆盖）

## 已解析的 NEEDS CLARIFICATION 项

本特性规格无未解决的 NEEDS CLARIFICATION 标记。所有技术细节通过合理假设和行业标准默认值已充分明确：

| 潜在疑问 | 解析结果 | 依据 |
|----------|----------|------|
| 后端语言/框架 | Python（基于 Celery/RQ 提及） | 源规格假设章节 |
| 认证方式 | JWT Cookie | FR-019 明确指定 |
| 数据库类型 | PostgreSQL（生产）/ SQLite（集成测试） | 行业标准和宪章要求 |
| 异步任务基础设施 | Celery/RQ | 源规格假设章节 |
| 前端框架 | 未指定（E2E 测试框架无关） | 测试规格面向行为而非实现 |
