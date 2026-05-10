# 测试计划: LECS主机管理

> **版本**: `001-lecs-host-management`
> **创建日期**: 2026-05-11
> **输入**: 功能测试规格文件 `/specs/001-lecs-host-management/spec.md`

> **说明**：本模板由 `/speckit-test.plan` 命令填充。测试计划是连接"测试规格说明"与"测试任务分解"的桥梁，定义测试策略、环境、范围和风险。

## 摘要

本测试计划覆盖 LECS主机（云服务器）管理功能的全量功能测试。测试范围包括：控制台搜索导航、主机列表查看与操作矩阵、主机创建（含六大配置板块与费用估算）、主机生命周期控制（关机/启动状态流转）、安全删除（软删除与配额管理）、RESTful API 接口（列表/创建/关机/启动/删除）、基于角色的访问控制、配额上限拦截、异步操作轮询机制与超时降级、表单字段校验。

测试策略采用两层架构：**集成测试**（API 契约验证 + 状态机逻辑 + 数据库行为）+ **端到端测试**（核心用户旅程的浏览器自动化）。所有测试遵循 Lee云平台测试宪章的双向可追溯性与 ISO 29119 测试技术要求。

## 技术上下文

**测试框架**: pytest（Python 后端集成测试）+ Playwright（TypeScript 端到端测试）
**测试数据库**: SQLite 内存数据库（集成测试）+ PostgreSQL test container（端到端测试）
**浏览器自动化**: Playwright（Chromium），优先使用 `data-testid` 定位元素
**Mock 策略**: `unittest.mock` / `pytest-mock` 用于外部服务（计费系统、异步任务队列、邮件服务）；真实数据库与真实认证中间件

## 宪章门禁

*门禁：必须在测试实现前通过。测试设计后需重新检查。*

| 宪章原则 | 检查项 | 状态 |
|----------|--------|------|
| **规格优先，测试贯穿** | 每个功能需求 (FR-001~FR-028) 均有对应测试用例 | ✅ PASS |
| **可追溯性（不可协商）** | 每个测试用例可追溯到 FR/TC/EC 编号 | ✅ PASS |
| **用户故事 → 端到端测试** | 所有 P1 用户故事 (1-5) 均有对应 E2E 测试场景 | ✅ PASS |
| **架构设计 → 集成测试** | API 接口契约 (5 个端点) 均有对应集成测试 | ✅ PASS |
| **ISO 29119 - 接口视图** | 接口契约测试覆盖所有 API 端点 | ✅ PASS |
| **ISO 29119 - 数据设计视图** | 边界值分析 + 等价类划分应用于所有输入字段 | ✅ PASS |
| **ISO 29119 - 依赖视图** | 故障注入 + 负向测试覆盖外部依赖失败场景 | ✅ PASS |
| **负向测试强制要求** | 每个正向测试至少有 1 个负向对应 | ✅ PASS |

## 测试策略总览

### 测试层次

本功能包含以下测试层次：

| 层级 | 职责 | 覆盖指引 | 失败定位 |
|------|------|----------|----------|
| **集成测试** | 组件协作 + API 契约（Route → Service → DB） | 覆盖 28 个功能需求 + 7 个边缘场景 + 5 个 API 端点 | 定位到组件交互边界 |
| **端到端测试** | 完整用户流程端到端验证 | 覆盖 5 个 P1 用户故事的核心路径 | 定位到用户操作级别 |

### 分层边界规则

- **集成测试**：使用真实数据库（SQLite 内存库），**不** mock 框架层（FastAPI/Flask、SQLAlchemy），但**可** mock 外部服务（计费系统、异步任务队列、邮件服务）。
- **端到端测试**：真实浏览器 + 完整应用栈，仅 mock 不可控的外部依赖。**不复测**集成测试已覆盖的 API 契约和边界条件。

## 各层测试详细计划

### 集成测试

**目标**：LECS 主机的 API 契约、状态机逻辑、数据库行为、配额管理、角色权限、费用计算

| 集成点 | 测试文件 | 验证范围 |
|--------|----------|----------|
| API 列表查询（GET /api/v1/lecs-hosts） | `tests/integration/test_lecs_hosts_list.py` | 分页、状态过滤、角色权限隔离、响应格式 |
| API 创建主机（POST /api/v1/lecs-hosts） | `tests/integration/test_lecs_hosts_create.py` | 参数校验、配额检查、异步任务触发、响应格式 |
| API 关机（POST /api/v1/lecs-hosts/{id}/stop） | `tests/integration/test_lecs_hosts_stop.py` | 状态机校验（仅 normal→shutting_down）、异步流转、并发拒绝 |
| API 启动（POST /api/v1/lecs-hosts/{id}/start） | `tests/integration/test_lecs_hosts_start.py` | 状态机校验（stopped/failed→starting）、异步流转、并发拒绝 |
| API 删除（DELETE /api/v1/lecs-hosts/{id}） | `tests/integration/test_lecs_hosts_delete.py` | 状态机校验（仅 stopped/allowed）、软删除逻辑、配额减 1 |
| 认证/授权链路（中间件 → Auth → Route） | `tests/integration/test_lecs_hosts_auth.py` | JWT Cookie 认证、Service Token 认证、401/403 拦截、越权拒绝 |
| 费用计算逻辑 | `tests/integration/test_lecs_hosts_pricing.py` | 包年/包月计算、按需计费计算、费用实时更新 |
| 表单校验逻辑（主机名/凭据/IP） | `tests/integration/test_lecs_hosts_validation.py` | 边界值分析、等价类划分、错误提示格式 |
| 异步任务生命周期 | `tests/integration/test_lecs_hosts_async.py` | 状态轮询（3s 间隔）、创建超时 60s 降级、终态停止轮询 |
| 审计日志 | `tests/integration/test_lecs_hosts_audit.py` | 操作记录（创建/删除/启动/关机）包含身份、时间、IP |

#### Mock 策略

| 依赖类型 | 处理方式 | 理由 |
|----------|----------|------|
| 外部 API/服务（计费系统、镜像服务） | `unittest.mock` / `pytest-mock` | 避免网络不确定性，仅测本功能逻辑 |
| 密码哈希 | 直接调用真实 argon2/bcrypt | 确定性算法，无外部依赖，不应 mock |
| JWT 签发/验证 | 固定 test secret 签发真实 JWT | 签发逻辑不在被测范围内，使用可控密钥 |
| 异步任务队列（Celery/RQ） | mock 任务执行器，模拟异步状态流转 | 任务调度不在被测范围内，需确定性的状态转换 |
| 时间 | `freezegun` 冻结时间 | 创建超时 60s、轮询间隔 3s 需要确定性时间控制 |

#### 测试数据隔离

- **Fixture 作用域**: 每个测试使用独立的内存 SQLite 数据库，通过 `pytest.fixture(scope="function")` 保证
- **数据工厂**: 使用 Factory Boy 模式创建测试数据（LecsHostFactory、UserFactory）
- **事务回滚**: 每个测试在事务中执行，测试完成后自动回滚
- **预置状态**: 每个测试通过 fixture 预置特定状态的主机记录（normal/stopped/failed/creating/deleting）

### 端到端测试

**目标**：验证用户从控制台搜索到主机全生命周期管理的完整操作路径

| 场景 | 测试文件 | 路径 | 预期结果 |
|------|----------|------|----------|
| 搜索导航至列表页 | `tests/e2e/test_sc01_search_navigation.spec.ts` | 登录 → 搜索"LECS" → 点击结果 → 跳转列表页 | URL 变为 `/console/lecs-hosts/list`，页面加载成功 |
| 列表页状态矩阵验证 | `tests/e2e/test_sc02_list_operation_matrix.spec.ts` | 登录 → 访问列表页 → 验证各状态行按钮启用/禁用 | 状态机矩阵 100% 匹配 |
| 创建主机完整流程 | `tests/e2e/test_sc03_create_host.spec.ts` | 列表页 → 创建按钮 → 填写表单 → 确认对话框 → 提交 → 列表页状态流转 | 新主机创建中→正常，费用计算正确 |
| 关机→启动生命周期 | `tests/e2e/test_sc04_lifecycle_control.spec.ts` | 选择正常主机 → 关机 → 等待已关机 → 启动 → 等待正常 | 状态流转正确，按钮实时禁用/启用 |
| 安全删除流程 | `tests/e2e/test_sc05_safe_delete.spec.ts` | 选择已关机主机 → 删除确认 → 等待消失 | 主机从列表消失，配额计数减 1 |

#### Playwright 策略

- **页面交互**: 优先使用 `data-testid` 定位元素；表单元素使用 `getByLabel`/`getByRole`
- **状态验证**: 验证 URL 变化、页面文本内容、按钮 disabled 属性、状态标签颜色（class 或 color 属性）
- **等待策略**: 使用 Playwright 自动等待（`expect(locator).toBeVisible()`）；异步状态转换使用轮询等待（`expect.poll()` 或重试断言），避免硬编码 sleep
- **视觉回归**: v1 不包含截图对比，仅进行功能断言

#### 端到端测试范围约束

- 端到端测试 **不复测** 集成测试已验证的接口契约和边界条件（如字段长度校验、IP 格式验证）
- 端到端测试 仅覆盖「用户操作 → 系统响应」的完整路径
- 每条 端到端测试 用例对应 spec.md 中的一个 P1 用户故事或关键验收场景

## 测试基础设施

### Fixture 设计

```python
# tests/integration/conftest.py - 集成测试 fixtures

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

@pytest.fixture
def db_engine():
    """每个测试独立的内存 SQLite 引擎"""
    engine = create_engine("sqlite:///")
    yield engine
    engine.dispose()

@pytest.fixture
def db_session(db_engine):
    """每个测试独立的事务回滚会话"""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def test_user(db_session):
    """使用 factory 创建标准用户"""
    user = UserFactory(role="user")
    db_session.add(user)
    db_session.commit()
    yield user

@pytest.fixture
def admin_user(db_session):
    """创建管理员用户"""
    user = UserFactory(role="admin")
    db_session.add(user)
    db_session.commit()
    yield user

@pytest.fixture
def authenticated_client(test_client, test_user):
    """创建已认证状态的测试客户端（携带 JWT Cookie）"""
    token = create_test_jwt(test_user.id)
    test_client.cookies.set("session", token)
    yield test_client

@pytest.fixture
def admin_client(test_client, admin_user):
    """创建管理员认证客户端"""
    token = create_test_jwt(admin_user.id)
    test_client.cookies.set("session", token)
    yield test_client

@pytest.fixture
def lecs_host_factory(db_session, test_user):
    """LECS 主机数据工厂"""
    def _create(status="normal", **kwargs):
        host = LecsHostFactory(
            user_id=test_user.id,
            status=status,
            **kwargs
        )
        db_session.add(host)
        db_session.commit()
        return host
    return _create
```

```typescript
// tests/e2e/fixtures/lecs-hosts-fixtures.ts - E2E 测试 fixtures

import { test as base, expect } from '@playwright/test';

export const test = base.extend({
  // 预置已登录状态的页面
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/auth/login');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('TestPass123!');
    await page.getByRole('button', { name: 'Login' }).click();
    await expect(page).toHaveURL(/\/console/);
    await use(page);
  },

  // 预置了各状态主机的列表页
  populatedListPage: async ({ authenticatedPage }, use) => {
    await authenticatedPage.goto('/console/lecs-hosts/list');
    await expect(authenticatedPage.getByTestId('host-list-table')).toBeVisible();
    await use(authenticatedPage);
  },
});
```

### 并行执行策略

- 集成测试使用 `pytest-xdist` 并行执行（独立 SQLite 内存库，无共享状态）
- E2E 测试串行执行（避免浏览器实例冲突和异步状态相互干扰）

## 项目结构

### 文档结构（本特性）

```text
specs/001-lecs-host-management/
├── plan.md              # 本文件（由 /speckit-test.plan 命令输出）
├── research.md          # 阶段 0 输出（技术调研）
├── spec.md              # 测试规格说明
├── tasks.md             # 测试执行任务分解（由 /speckit-test.tasks 命令生成）
└── checklists/
    └── requirements.md  # 规格质量检查清单
```

### 测试工件结构（仓库根目录）

```text
tests/
├── cases/                          # 测试用例（Markdown 规格格式）
│   ├── sc-01-search-navigation.md
│   ├── sc-02-list-operation-matrix.md
│   ├── sc-03-create-host.md
│   ├── sc-04-lifecycle-control.md
│   ├── sc-05-safe-delete.md
│   └── sc-06-api-management.md
│
├── integration/                    # 集成测试（pytest）
│   ├── conftest.py
│   ├── test_lecs_hosts_list.py
│   ├── test_lecs_hosts_create.py
│   ├── test_lecs_hosts_stop.py
│   ├── test_lecs_hosts_start.py
│   ├── test_lecs_hosts_delete.py
│   ├── test_lecs_hosts_auth.py
│   ├── test_lecs_hosts_pricing.py
│   ├── test_lecs_hosts_validation.py
│   ├── test_lecs_hosts_async.py
│   └── test_lecs_hosts_audit.py
│
├── e2e/                            # Playwright 端到端测试
│   ├── lecs-hosts/
│   │   ├── test_sc01_search_navigation.spec.ts
│   │   ├── test_sc02_list_operation_matrix.spec.ts
│   │   ├── test_sc03_create_host.spec.ts
│   │   ├── test_sc04_lifecycle_control.spec.ts
│   │   └── test_sc05_safe_delete.spec.ts
│   └── fixtures/
│       ├── lecs-hosts-fixtures.ts
│       └── data/
│           └── lecs-host-states.json
│
├── fixtures/                       # 可复用的测试基础设施
│   ├── factories/
│   │   ├── user_factory.py
│   │   └── lecs_host_factory.py
│   └── mocks/
│       ├── billing_service_mock.py
│       └── task_queue_mock.py
│
└── conftest.py                     # 全局 pytest 配置
```

## 测试环境

### 环境要求

| 组件 | 要求 | 备注 |
|------|------|------|
| **运行时** | Python 3.11+（后端）、Node 18+（前端） | 与生产环境保持一致 |
| **数据库** | SQLite 内存库（集成测试） | 每个测试独立实例 |
| **浏览器** | Chromium（Playwright 自动管理） | E2E 测试需要 |
| **依赖服务** | 无（外部服务全部 mock） | 集成测试不需要真实 Celery/Redis |

### 环境变量配置

```bash
# .env.test - 测试环境专用配置（集成测试 + E2E 共用）
DATABASE_URL=sqlite:///
TESTING=true
SECRET_KEY=test-secret-key-do-not-use-in-production
MOCK_EXTERNAL_SERVICES=true
AUTH_JWT_SECRET=test-jwt-secret
AUTH_JWT_COOKIE_NAME=session
CELERY_TASK_ALWAYS_EAGER=false  # 集成测试中需要异步行为
```

### 测试配置文件

| 文件 | 用途 |
|------|------|
| `tests/conftest.py` | 全局 pytest fixture（DB、用户、工厂） |
| `tests/integration/conftest.py` | 集成测试级 fixture（认证客户端、主机工厂） |
| `tests/e2e/fixtures/lecs-hosts-fixtures.ts` | Playwright E2E fixture（已登录页面、预置数据页面） |
| `pytest.ini` / `pyproject.toml` | pytest 配置（标记、并行、覆盖率） |
| `playwright.config.ts` | Playwright 配置（浏览器、超时、重试） |

### 测试数据准备

| 数据类型 | 来源 | 刷新频率 | 清理策略 |
|----------|------|----------|----------|
| 基准测试数据 | Factory Boy（LecsHostFactory、UserFactory） | 每次测试运行前 | 事务回滚自动清理 |
| 用户测试数据 | UserFactory（role=user/admin） | 按需创建 | 测试结束后自动删除 |
| 外部服务 Mock 数据 | `tests/fixtures/mocks/` 中定义 | 手动更新 | 版本控制管理 |
| E2E 测试账号 | 预置种子脚本 `tests/e2e/fixtures/seed-e2e-data.py` | E2E 运行前 | E2E 结束后清理 |

### 环境隔离策略

- **数据库隔离**: 每个集成测试使用独立的内存 SQLite 实例（`sqlite:///:memory:`）
- **网络隔离**: Mock 所有外部服务调用（计费系统、镜像服务、任务队列），避免真实网络请求
- **状态隔离**: 测试间不共享状态；每个测试从干净的空数据库开始
- **E2E 隔离**: E2E 测试使用独立的测试用户账号，互不干扰

## 测试可追溯性

### FR → Test 映射

| Spec 中的 FR | 测试层级 | 测试文件 | 对应 TC/EC |
|--------------|----------|----------|------------|
| FR-001 | 端到端测试 | `test_sc01_search_navigation.spec.ts` | TC-001, TC-002, TC-003 |
| FR-002 | 集成测试 + 端到端 | `test_lecs_hosts_list.py`, `test_sc02_list_operation_matrix.spec.ts` | TC-010, TC-011 |
| FR-003 | 集成测试 + 端到端 | `test_sc02_list_operation_matrix.spec.ts`, `test_lecs_hosts_stop.py`, `test_lecs_hosts_start.py`, `test_lecs_hosts_delete.py` | TC-012~TC-016 |
| FR-004 | 集成测试 + 端到端 | `test_lecs_hosts_create.py`, `test_sc03_create_host.spec.ts` | TC-020 |
| FR-005 | 集成测试 | `test_lecs_hosts_validation.py` | TC-022 |
| FR-006 | 集成测试 | `test_lecs_hosts_validation.py` | TC-023 |
| FR-007 | 集成测试 | `test_lecs_hosts_pricing.py` | TC-028 |
| FR-008 | 端到端测试 | `test_sc03_create_host.spec.ts` | TC-029 |
| FR-009 | 集成测试 + 端到端 | `test_lecs_hosts_create.py`, `test_sc03_create_host.spec.ts` | EC-001 |
| FR-010 | 集成测试 + 端到端 | `test_lecs_hosts_stop.py`, `test_sc04_lifecycle_control.spec.ts` | TC-040, TC-043 |
| FR-011 | 集成测试 + 端到端 | `test_lecs_hosts_start.py`, `test_sc04_lifecycle_control.spec.ts` | TC-041, TC-042 |
| FR-012 | 集成测试 + 端到端 | `test_lecs_hosts_delete.py`, `test_sc05_safe_delete.spec.ts` | TC-050 |
| FR-013 | 集成测试 + 端到端 | `test_lecs_hosts_delete.py`, `test_sc05_safe_delete.spec.ts` | TC-051, TC-052 |
| FR-014 | 集成测试 | `test_lecs_hosts_delete.py` | EC-005 |
| FR-015 | 集成测试 + 端到端 | `test_lecs_hosts_async.py`, `test_sc03_create_host.spec.ts` | TC-030 |
| FR-016 | 集成测试 | `test_lecs_hosts_async.py` | EC-002 |
| FR-017 | 集成测试 + 端到端 | `test_lecs_hosts_auth.py`, `test_sc02_list_operation_matrix.spec.ts` | TC-060, TC-061, EC-006 |
| FR-018 | 集成测试 | `test_lecs_hosts_audit.py` | EC-007 |
| FR-019 | 集成测试 | `test_lecs_hosts_auth.py` | TC-062 |
| FR-020 | 集成测试 | `test_lecs_hosts_auth.py` | （安全测试范围） |
| FR-021 | 集成测试 | `test_lecs_hosts_list.py` | TC-API-010 |
| FR-022 | 集成测试 | `test_lecs_hosts_create.py` | TC-API-020 |
| FR-023 | 集成测试 | `test_lecs_hosts_stop.py` | TC-API-040 |
| FR-024 | 集成测试 | `test_lecs_hosts_start.py` | TC-API-041 |
| FR-025 | 集成测试 | `test_lecs_hosts_delete.py` | TC-API-050 |
| FR-026 | 集成测试 | `test_lecs_hosts_auth.py` | TC-API-060, TC-062 |
| FR-027 | 集成测试 | `test_lecs_hosts_validation.py` | TC-API-061 |
| FR-028 | 集成测试 | `test_lecs_hosts_list.py` 等各文件 | TC-API-060 |

### 用户故事 → Test 映射

| 用户故事 | 优先级 | 对应测试 | 独立验证方式 |
|----------|--------|----------|--------------|
| 搜索并跳转至LECS主机列表 | P1 | `test_sc01_search_navigation.spec.ts` | 输入关键词 → 点击结果 → 验证 URL |
| 查看LECS主机列表与操作矩阵 | P1 | `test_sc02_list_operation_matrix.spec.ts` + 集成测试 4 个文件 | 预置各状态主机 → 验证按钮启用/禁用 |
| 创建LECS主机 | P1 | `test_sc03_create_host.spec.ts` + `test_lecs_hosts_create.py` | 填写表单 → 确认 → 提交 → 验证状态流转 |
| 控制主机生命周期 | P1 | `test_sc04_lifecycle_control.spec.ts` + `test_lecs_hosts_stop.py` + `test_lecs_hosts_start.py` | 完整状态流转：normal→shutting_down→stopped→starting→normal |
| 安全删除LECS主机 | P1 | `test_sc05_safe_delete.spec.ts` + `test_lecs_hosts_delete.py` | 已关机主机 → 删除确认 → 验证消失 + 配额减 1 |
| 通过 API 管理 LECS 主机 | P2 | `test_lecs_hosts_*.py`（全部集成测试） | 直接调用 API 端点 → 验证请求/响应/错误 |

## 测试风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 异步操作时序不确定性（状态流转约 10s） | E2E 测试结果不稳定（flaky） | Playwright 使用 `expect.poll()` 轮询断言；集成测试使用 `freezegun` 控制时间，模拟异步完成 |
| 外部服务 Mock 不完整 | 集成测试可能遗漏真实服务行为差异 | Mock 层定义严格的请求/响应契约；定期与真实服务联调验证 |
| 数据库状态泄漏 | 测试间相互影响导致误报 | 每个测试使用独立内存 SQLite + 事务回滚；E2E 使用独立测试账号 |
| 表单校验与前端/后端不一致 | 用户绕过前端校验提交非法数据 | 集成测试直接调用 API 绕过前端，验证后端独立校验逻辑 |
| 角色权限越权场景遗漏 | 安全漏洞未被测试覆盖 | 集成测试中为每个端点显式编写越权测试用例（用户 A 操作用户 B 的主机） |

## 研究决策

### 技术决策记录

**Decision**: 集成测试使用 SQLite 内存数据库，端到端测试使用真实数据库（Docker 内 PostgreSQL）
**Rationale**: 集成测试需要快速执行和确定性行为，SQLite 内存库满足隔离性和速度要求；E2E 测试需要验证真实应用行为，包括数据库特定行为（如软删除的 `deleted_at` 时间戳精度）
**Alternatives considered**: 
- 统一使用 PostgreSQL test container（集成测试执行速度较慢）
- 统一使用 SQLite 内存库（无法验证生产数据库的特定行为）

**Decision**: 异步任务在集成测试中使用 mock 执行器模拟状态流转，而非真实 Celery worker
**Rationale**: Celery 的真实异步行为需要 Redis 和 worker 进程，增加测试基础设施复杂度；mock 执行器可通过 `freezegun` 精确控制时间，测试超时和轮询逻辑
**Alternatives considered**:
- 使用真实 Celery + Redis（基础设施重，CI 环境不稳定）
- 使用 `CELERY_TASK_ALWAYS_EAGER=True` 同步执行（无法测试异步状态流转逻辑）

**Decision**: Playwright E2E 测试使用 `data-testid` 优先定位策略
**Rationale**: `data-testid` 不受 CSS 样式变更和 DOM 结构调整影响，提供最稳定的元素定位
**Alternatives considered**:
- 使用 CSS class/标签选择器（易受样式重构影响）
- 使用 XPath（脆弱，DOM 层级变化即断裂）

## 复杂度追踪

> **仅在宪章门禁存在需要证明的违反项时填写**

| 违反项 | 为什么需要 | 拒绝更简单方案的理由 |
|--------|-----------|---------------------|
| 无 | 本计划完全遵循宪章要求 | 无额外复杂度 |
