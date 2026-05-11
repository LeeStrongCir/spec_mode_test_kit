---
description: "LECS主机管理测试任务清单"
---

# 测试任务: LECS主机管理

**输入**：来自 `/specs/001-lecs-host-management/` 的设计文档
**前置条件**：`plan.md`（必需）、`spec.md`（必需，用于测试场景）

**组织**：测试分为四个阶段：阶段1：测试用例编写 → 阶段2：测试自动化代码编写 → 阶段3：测试环境准备 → 阶段4：测试执行。阶段间**严格串行**，但阶段1、2、4**内部任务可并行** `[P]`。

## 格式: `[ID] [P?] [LABEL] Description`

- **[P]**: 可并行执行（不同文件、无依赖关系，阶段内部可同时执行）
- **[LABEL]**: 阶段标签前缀
  - `[CASE-SC-01]`, `[CASE-SC-02]` — 阶段 1 测试用例编写（按场景）
  - `[AUTO-SC-01]`, `[AUTO-SC-02]` — 阶段 2 测试自动化代码编写（按场景）
  - `[ENV]` — 阶段 3 测试环境准备
  - `[EVT-SC-01]`, `[EVT-SC-02]` — 阶段 4 测试执行（按场景）
- 描述中必须包含准确的文件路径

## 路径约定

- **测试用例**：`tests/cases/001-lecs-host-management/`
- **集成测试**：`tests/integration/001-lecs-host-management/`
- **E2E 测试**：`tests/e2e/001-lecs-host-management/`
- **Fixtures**：`tests/fixtures/` 和 `tests/e2e/001-lecs-host-management/fixtures/`

---

## 阶段 1: 测试用例编写（内部可并行 `[P]`）

**说明**：不同场景的测试用例编写可并行执行，但需等待本阶段全部完成后，阶段2才能开始

### 阶段 1.1: SC-01 搜索导航用例编写（P1）

**目标**：验证用户通过控制台搜索栏搜索"LECS"/"云服务器"并跳转至列表页的完整导航路径

- [X] T001 [P] [CASE-SC-01] 在 `tests/cases/001-lecs-host-management/sc-01-search-navigation.md` 中编写搜索关键词匹配与高亮显示（TC-001）的手工测试步骤，包含前置条件、操作步骤、预期结果
- [X] T002 [P] [CASE-SC-01] 在 `tests/cases/001-lecs-host-management/sc-01-search-navigation.md` 中编写搜索"云服"关键词（TC-002）的手工测试步骤
- [X] T003 [P] [CASE-SC-01] 在 `tests/cases/001-lecs-host-management/sc-01-search-navigation.md` 中编写点击搜索结果跳转至列表页（TC-003）的手工测试步骤，验证 URL 变为 `/console/lecs-hosts/list`

### 阶段 1.2: SC-02 列表与操作矩阵用例编写（P1）

**目标**：验证主机列表页的分页展示、状态标签渲染、各状态操作按钮启用/禁用逻辑及 API 列表查询接口

- [X] T004 [P] [CASE-SC-02] 在 `tests/cases/001-lecs-host-management/sc-02-list-operation-matrix.md` 中编写列表页基本展示（TC-010）和状态标签彩色渲染（TC-011）的手工测试步骤
- [X] T005 [P] [CASE-SC-02] 在 `tests/cases/001-lecs-host-management/sc-02-list-operation-matrix.md` 中编写"正常"状态（TC-012）、"已关机"状态（TC-013）、"创建失败"状态（TC-014）、"删除中"状态（TC-015）的操作矩阵手工测试步骤，明确每个状态的按钮启用/禁用预期
- [X] T006 [P] [CASE-SC-02] 在 `tests/cases/001-lecs-host-management/sc-02-list-operation-matrix.md` 中编写软删除主机不可见性（TC-016）和 GET /api/v1/lecs-hosts 列表查询接口（TC-API-010）的手工测试步骤，包含分页参数、状态过滤、401/403 错误验证

### 阶段 1.3: SC-03 创建主机用例编写（P1）

**目标**：验证创建主机完整流程，包括六大配置板块、表单校验、费用估算、确认对话框、异步状态流转及配额上限拦截

- [X] T007 [P] [CASE-SC-03] 在 `tests/cases/001-lecs-host-management/sc-03-create-host.md` 中编写进入创建表单（TC-020）、计费模式默认值（TC-021）、主机名格式校验（TC-022）、访问凭据复杂度校验（TC-023）的手工测试步骤，包含边界值（4/10字符、4/16字符、8/32字符）
- [X] T008 [P] [CASE-SC-03] 在 `tests/cases/001-lecs-host-management/sc-03-create-host.md` 中编写实例规格选择（TC-024）、操作系统镜像默认值（TC-025）、IP配置手工/DHCP模式（TC-026）、购买时长选项（TC-027）的手工测试步骤
- [X] T009 [P] [CASE-SC-03] 在 `tests/cases/001-lecs-host-management/sc-03-create-host.md` 中编写费用估算实时计算（TC-028）、确认对话框（TC-029）、创建后异步状态流转（TC-030）的手工测试步骤，包含轮询行为验证
- [X] T010 [P] [CASE-SC-03] 在 `tests/cases/001-lecs-host-management/sc-03-create-host.md` 中编写 POST /api/v1/lecs-hosts 创建接口（TC-API-020）和配额上限拦截（EC-001）的手工测试步骤

### 阶段 1.4: SC-04 生命周期控用例编写（P1）

**目标**：验证主机关机/启动完整状态流转、过渡态防重复操作及对应 API 接口

- [X] T011 [P] [CASE-SC-04] 在 `tests/cases/001-lecs-host-management/sc-04-lifecycle-control.md` 中编写关机操作完整状态流转（TC-040）和启动操作完整状态流转（TC-041）的手工测试步骤，包含每步的按钮置灰/恢复预期和等待约10秒的状态变化
- [X] T012 [P] [CASE-SC-04] 在 `tests/cases/001-lecs-host-management/sc-04-lifecycle-control.md` 中编写"创建失败"状态主机启动（TC-042）、过渡态防重复操作（TC-043）、POST /api/v1/lecs-hosts/{id}/stop（TC-API-040）和 POST /api/v1/lecs-hosts/{id}/start（TC-API-041）的手工测试步骤

### 阶段 1.5: SC-05 安全删除用例编写（P1）

**目标**：验证运行态主机删除拦截、已关机/创建失败主机删除流程、软删除数据库行为及 DELETE API 接口

- [X] T013 [P] [CASE-SC-05] 在 `tests/cases/001-lecs-host-management/sc-05-safe-delete.md` 中编写运行态主机删除拦截（TC-050）和已关机主机删除流程（TC-051）的手工测试步骤，包含二次确认、状态变为"删除中"、3-5 秒后消失、配额计数减 1
- [X] T014 [P] [CASE-SC-05] 在 `tests/cases/001-lecs-host-management/sc-05-safe-delete.md` 中编写创建失败主机删除（TC-052）、DELETE /api/v1/lecs-hosts/{id} 接口（TC-API-050）和软删除数据库记录保留（EC-005）的手工测试步骤

### 阶段 1.6: SC-06 API管理与边缘场景用例编写（P2）

**目标**：验证 API 权限隔离、统一响应格式、参数校验、并发操作防护、审计日志记录

- [X] T015 [P] [CASE-SC-06] 在 `tests/cases/001-lecs-host-management/sc-06-api-management.md` 中编写 API 列表查询普通用户权限隔离（TC-060）、管理员权限（TC-061）、无认证拒绝（TC-062）、统一响应格式（TC-API-060）和参数校验（TC-API-061）的手工测试步骤
- [X] T016 [P] [CASE-SC-06] 在 `tests/cases/001-lecs-host-management/sc-06-api-management.md` 中编写并发操作冲突防护（EC-003）、表单提交前未填写校验（EC-004）、角色权限越权（EC-006）和审计日志记录（EC-007）的手工测试步骤

**检查点**：所有测试用例编写完成——阶段 2 测试自动化代码编写可以开始

---

## 阶段 2: 测试自动化代码编写（内部可并行 `[P]`）

**说明**：不同场景的自动化代码编写可并行执行，但需等待阶段1全部完成后才能开始，且本阶段全部完成后阶段3才能开始

### 阶段 2.1: SC-01 搜索导航自动化（P1）

- [X] T017 [P] [AUTO-SC-01] 在 `tests/e2e/001-lecs-host-management/test_sc01_search_navigation.spec.ts` 中编写 Playwright E2E 测试：输入"LECS"/"云服"关键词验证搜索高亮、点击结果验证 URL 跳转至 `/console/lecs-hosts/list`，使用 `data-testid` 定位元素

### 阶段 2.2: SC-02 列表与操作矩阵自动化（P1）

- [X] T018 [P] [AUTO-SC-02] 在 `tests/e2e/001-lecs-host-management/test_sc02_list_operation_matrix.spec.ts` 中编写 Playwright E2E 测试：列表页分页展示、状态标签颜色验证、各状态（normal/stopped/failed/deleting）按钮启用/禁用矩阵验证
- [X] T019 [P] [AUTO-SC-02] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_list.py` 中编写 pytest 集成测试：GET /api/v1/lecs-hosts 分页参数、status 过滤、角色权限隔离（普通用户仅见自身主机、管理员查看全部）、401/403 错误响应

### 阶段 2.3: SC-03 创建主机自动化（P1）

- [X] T020 [P] [AUTO-SC-03] 在 `tests/e2e/001-lecs-host-management/test_sc03_create_host.spec.ts` 中编写 Playwright E2E 测试：进入创建表单、六大配置板块填写、确认对话框验证、提交后状态流转（创建中→正常）、费用实时计算验证
- [X] T021 [P] [AUTO-SC-03] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_create.py` 中编写 pytest 集成测试：POST /api/v1/lecs-hosts 参数校验（主机名 4-10 字符、凭据 4-16/8-32 字符）、配额检查（100台上限）、异步任务触发、400/403 错误响应
- [X] T022 [P] [AUTO-SC-03] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_validation.py` 中编写 pytest 集成测试：主机名格式边界值分析（`_invalid`、`ab`、`abcdefghijklmn`、`valid01`）、凭据复杂度校验、IP 格式验证（`999.999.999.999` vs `192.168.1.100`）、掩码范围 8-24
- [X] T023 [P] [AUTO-SC-03] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_pricing.py` 中编写 pytest 集成测试：包年/包月费用计算（100元/月×3月=300元）、按需计费（按月费÷30=元/天）、费用实时更新

### 阶段 2.4: SC-04 生命周期控制自动化（P1）

- [X] T024 [P] [AUTO-SC-04] 在 `tests/e2e/001-lecs-host-management/test_sc04_lifecycle_control.spec.ts` 中编写 Playwright E2E 测试：完整关机流程（normal→shutting_down→stopped，约10秒）、完整启动流程（stopped→starting→normal，约10秒）、按钮实时禁用/启用，使用 `expect.poll()` 轮询断言避免硬编码 sleep
- [X] T025 [P] [AUTO-SC-04] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_stop.py` 中编写 pytest 集成测试：POST /api/v1/lecs-hosts/{id}/stop 状态机校验（仅 normal→shutting_down）、异步流转、并发拒绝（shutting_down 状态再发 stop 返回 403）
- [X] T026 [P] [AUTO-SC-04] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_start.py` 中编写 pytest 集成测试：POST /api/v1/lecs-hosts/{id}/start 状态机校验（stopped/failed→starting）、异步流转、并发拒绝

### 阶段 2.5: SC-05 安全删除自动化（P1）

- [X] T027 [P] [AUTO-SC-05] 在 `tests/e2e/001-lecs-host-management/test_sc05_safe_delete.spec.ts` 中编写 Playwright E2E 测试：已关机主机删除二次确认、状态变为"删除中"、等待 3-5 秒后从列表消失、配额计数减 1 验证
- [X] T028 [P] [AUTO-SC-05] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_delete.py` 中编写 pytest 集成测试：DELETE /api/v1/lecs-hosts/{id} 状态机校验（仅 stopped/failed 允许）、软删除逻辑（`deleted_at` 字段设置）、配额减 1、运行态主机拦截返回 403

### 阶段 2.6: SC-06 API管理、认证、异步与审计自动化（P2）

- [X] T029 [P] [AUTO-SC-06] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_auth.py` 中编写 pytest 集成测试：JWT Cookie 认证、Service Token 认证、401 未授权拦截、403 越权拒绝（用户 B 操作用户 A 主机 EC-006）、认证/授权链路（中间件→Auth→Route）
- [X] T030 [P] [AUTO-SC-06] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_async.py` 中编写 pytest 集成测试：异步状态轮询（3s 间隔）、创建超时 60s 降级（EC-002，使用 `freezegun` 冻结时间）、终态停止轮询、mock 异步任务执行器
- [X] T031 [P] [AUTO-SC-06] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_audit.py` 中编写 pytest 集成测试：审计日志记录（EC-007）验证创建/删除/启动/关机操作包含操作人身份、时间戳、IP 地址、操作详情

### 阶段 2.7: 共享基础设施自动化

- [X] T032 [P] [AUTO-SC-ALL] 在 `tests/integration/001-lecs-host-management/conftest.py` 中编写集成测试 fixtures：`db_engine`（独立内存 SQLite）、`db_session`（事务回滚）、`test_user`/`admin_user`（Factory Boy）、`authenticated_client`/`admin_client`（JWT Cookie）、`lecs_host_factory`（预置 normal/stopped/failed/creating/deleting 状态）
- [X] T033 [P] [AUTO-SC-ALL] 在 `tests/e2e/001-lecs-host-management/fixtures/lecs-hosts-fixtures.ts` 中编写 Playwright E2E fixtures：`authenticatedPage`（预登录状态）、`populatedListPage`（预置各状态主机列表）
- [X] T034 [P] [AUTO-SC-ALL] 在 `tests/fixtures/factories/user_factory.py` 中编写 UserFactory，在 `tests/fixtures/factories/lecs_host_factory.py` 中编写 LecsHostFactory
- [X] T035 [P] [AUTO-SC-ALL] 在 `tests/fixtures/mocks/billing_service_mock.py` 中编写计费系统 Mock，在 `tests/fixtures/mocks/task_queue_mock.py` 中编写异步任务队列 Mock
- [X] T036 [P] [AUTO-SC-ALL] 在 `tests/conftest.py` 中编写全局 pytest 配置；在 `tests/e2e/001-lecs-host-management/fixtures/data/lecs-host-states.json` 中编写 E2E 测试状态数据；在 `tests/e2e/001-lecs-host-management/fixtures/seed-e2e-data.py` 中编写 E2E 种子数据脚本

**检查点**：所有自动化代码编写完成——阶段 3 测试环境准备可以开始

---

## 阶段 3: 测试环境准备（串行，阻塞后续所有阶段）

**目的**：测试基础设施初始化与环境搭建，为测试执行阶段提供基础

**⚠️ 关键**：在此阶段完成之前，任何测试执行任务不得开始

- [X] T037 [ENV] 初始化 Python 测试依赖：在 `requirements-test.txt` 或 `pyproject.toml` 中添加 pytest、pytest-mock、freezegun、pytest-xdist、factory-boy、SQLAlchemy，执行 `pip install -r requirements-test.txt` 安装
- [X] T038 [ENV] 初始化 Node.js E2E 测试依赖：在 `tests/e2e/` 目录下初始化 TypeScript 项目，安装 `@playwright/test`、TypeScript，配置 `playwright.config.ts`（浏览器 Chromium、超时、重试策略），执行 `npx playwright install chromium` 安装浏览器
- [X] T039 [ENV] 配置 pytest 环境：创建/更新 `pytest.ini` 或 `pyproject.toml` 中的 pytest 配置段，设置测试标记（integration/e2e）、并行执行参数（`-n auto`）、覆盖率配置、`PYTHONPATH` 指向仓库根目录
- [X] T040 [ENV] 配置测试环境变量：创建 `.env.test` 文件，设置 `DATABASE_URL=sqlite:///`、`TESTING=true`、`SECRET_KEY=test-secret-key-do-not-use-in-production`、`MOCK_EXTERNAL_SERVICES=true`、`AUTH_JWT_SECRET=test-jwt-secret`、`AUTH_JWT_COOKIE_NAME=session`、`CELERY_TASK_ALWAYS_EAGER=false`
- [X] T041 [ENV] 执行 E2E 种子数据脚本 `tests/e2e/001-lecs-host-management/fixtures/seed-e2e-data.py` 加载基线测试数据（测试用户账号、预置各状态主机记录），验证数据注入成功

**检查点**：基础设施就绪——阶段 4 测试执行可以开始

---

## 阶段 4: 测试执行（内部可并行 `[P]`）

**目的**：执行全部自动化测试用例，收集结果，验证功能是否符合规格

**说明**：本阶段所有任务均可并行执行，但需等待阶段1、2、3全部完成后才能开始

**⚠️ 所有任务均标记 `[P]`，可同时执行**

### 集成测试执行组

- [X] T042 [P] [EVT-SC-02] 执行集成测试 `tests/integration/001-lecs-host-management/test_lecs_hosts_list.py`，验证列表查询 API 契约、分页、状态过滤、角色权限隔离，记录结果至 `tests/reports/integration-test-results.md`
- [X] T043 [P] [EVT-SC-03] 执行集成测试 `tests/integration/001-lecs-host-management/test_lecs_hosts_create.py`，验证创建 API 参数校验、配额检查、异步任务触发，记录结果
- [X] T044 [P] [EVT-SC-03] 执行集成测试 `tests/integration/001-lecs-host-management/test_lecs_hosts_validation.py`，验证主机名/凭据/IP 格式边界值分析，记录结果
- [X] T045 [P] [EVT-SC-03] 执行集成测试 `tests/integration/001-lecs-host-management/test_lecs_hosts_pricing.py`，验证费用计算逻辑（包年/包月、按需计费），记录结果
- [X] T046 [P] [EVT-SC-04] 执行集成测试 `tests/integration/001-lecs-host-management/test_lecs_hosts_stop.py`，验证关机状态机、异步流转、并发拒绝，记录结果
- [X] T047 [P] [EVT-SC-04] 执行集成测试 `tests/integration/001-lecs-host-management/test_lecs_hosts_start.py`，验证启动状态机、异步流转、并发拒绝，记录结果
- [X] T048 [P] [EVT-SC-05] 执行集成测试 `tests/integration/001-lecs-host-management/test_lecs_hosts_delete.py`，验证删除状态机、软删除逻辑、配额减 1、运行态拦截，记录结果
- [X] T049 [P] [EVT-SC-06] 执行集成测试 `tests/integration/001-lecs-host-management/test_lecs_hosts_auth.py`，验证 JWT/Service Token 认证、401/403 拦截、越权拒绝，记录结果
- [X] T050 [P] [EVT-SC-06] 执行集成测试 `tests/integration/001-lecs-host-management/test_lecs_hosts_async.py`，验证异步状态轮询、60s 超时降级、终态停止轮询，记录结果
- [X] T051 [P] [EVT-SC-06] 执行集成测试 `tests/integration/001-lecs-host-management/test_lecs_hosts_audit.py`，验证审计日志记录（身份、时间、IP），记录结果

### E2E 测试执行组

- [X] T052 [P] [EVT-SC-01] 执行 E2E 测试 `tests/e2e/001-lecs-host-management/test_sc01_search_navigation.spec.ts`，验证搜索关键词高亮和跳转列表页，记录结果至 `tests/reports/e2e-test-results.md`
- [X] T053 [P] [EVT-SC-02] 执行 E2E 测试 `tests/e2e/001-lecs-host-management/test_sc02_list_operation_matrix.spec.ts`，验证列表页状态矩阵和按钮启用/禁用，记录结果
- [X] T054 [P] [EVT-SC-03] 执行 E2E 测试 `tests/e2e/001-lecs-host-management/test_sc03_create_host.spec.ts`，验证创建主机完整流程，记录结果
- [X] T055 [P] [EVT-SC-04] 执行 E2E 测试 `tests/e2e/001-lecs-host-management/test_sc04_lifecycle_control.spec.ts`，验证关机→启动生命周期，记录结果
- [X] T056 [P] [EVT-SC-05] 执行 E2E 测试 `tests/e2e/001-lecs-host-management/test_sc05_safe_delete.spec.ts`，验证安全删除流程，记录结果

### 回归验证与报告

- [X] T057 [P] [EVT-ALL] 汇总所有集成测试和 E2E 测试结果，生成测试总结报告在 `tests/reports/summary.md`，包含通过率、失败用例详情、Test Incident Report（针对失败用例）
- [X] T058 [P] [EVT-ALL] 执行回归验证：确认所有 P1 场景（SC-01~SC-05）核心路径通过，无阻塞性缺陷，输出 MVP 通过/不通过结论

**检查点**：所有测试用例执行完成

---

## 并行示例：阶段 4 测试执行

```bash
# 集成测试并行执行（使用 pytest-xdist）:
pytest tests/integration/001-lecs-host-management/ -n auto -v --tb=short

# E2E 测试并行执行（使用 Playwright 多 worker）:
npx playwright test tests/e2e/001-lecs-host-management/ --workers=5

# 或每个用例独立启动:
Task: "Execute test_lecs_hosts_list.py"
Task: "Execute test_lecs_hosts_create.py"
Task: "Execute test_lecs_hosts_stop.py"
Task: "Execute test_lecs_hosts_start.py"
Task: "Execute test_lecs_hosts_delete.py"
Task: "Execute test_lecs_hosts_auth.py"
Task: "Execute test_lecs_hosts_async.py"
Task: "Execute test_lecs_hosts_audit.py"
Task: "Execute test_lecs_hosts_validation.py"
Task: "Execute test_lecs_hosts_pricing.py"
Task: "Execute test_sc01_search_navigation.spec.ts"
Task: "Execute test_sc02_list_operation_matrix.spec.ts"
Task: "Execute test_sc03_create_host.spec.ts"
Task: "Execute test_sc04_lifecycle_control.spec.ts"
Task: "Execute test_sc05_safe_delete.spec.ts"

# 每个用例独立执行，结果汇总至 tests/reports/summary.md
```

---

## 执行策略

### MVP First（仅执行 P1 场景 SC-01~SC-05）

1. 完成 阶段 1: P1 场景（SC-01~SC-05）的测试用例编写（T001~T014，内部可并行）
2. 完成 阶段 2: P1 场景的自动化代码编写（T017~T031，内部可并行）
3. 完成 阶段 3: 测试环境准备（T037~T041，严格串行）
4. 执行 阶段 4: P1 场景的测试执行（T042~T056 中 P1 对应项，内部可行）
5. **停止并验证**：独立验证 P1 场景结果（T057~T058）
6. 若通过，输出阶段性报告

### 增量覆盖

1. 阶段 3 环境准备 → 基础设施就绪
2. P1 场景（SC-01~SC-05）执行通过 → 输出阶段性报告（MVP！）
3. 继续 P2 场景（SC-06 API管理）的自动化执行（T029~T031 相关部分 + T049~T051）
4. 每个场景增加验证范围且不破坏已验证的场景

### 并行团队策略

多人协作时：

1. 阶段 1~2: 不同成员可并行负责不同场景的用例编写和自动化代码编写
   - 成员 A：SC-01、SC-02
   - 成员 B：SC-03
   - 成员 C：SC-04、SC-05
   - 成员 D：SC-06、共享基础设施
2. 阶段 3: 测试环境准备（阻塞后续阶段）
3. 阶段 4: 所有自动化用例同时并行执行
4. **阶段间保持严格串行依赖**：阶段1完成→阶段2开始→阶段3完成→阶段4开始

---

## 依赖关系图

```
阶段 1: [P] CASE-SC-01 (T001-T003) ─┐
       [P] CASE-SC-02 (T004-T006) ──┤
       [P] CASE-SC-03 (T007-T010) ──┤
       [P] CASE-SC-04 (T011-T012) ──┼──→ 全部完成
       [P] CASE-SC-05 (T013-T014) ──┤
       [P] CASE-SC-06 (T015-T016) ─┘
                                     ↓
阶段 2: [P] AUTO-SC-01 (T017) ──────┐
       [P] AUTO-SC-02 (T018-T019) ──┤
       [P] AUTO-SC-03 (T020-T023) ──┤
       [P] AUTO-SC-04 (T024-T026) ──┤
       [P] AUTO-SC-05 (T027-T028) ──┼──→ 全部完成
       [P] AUTO-SC-06 (T029-T031) ──┤
       [P] AUTO-ALL  (T032-T036) ──┘
                                     ↓
阶段 3: ENV (T037) ──▶ ENV (T038) ──▶ ENV (T039) ──▶ ENV (T040) ──▶ ENV (T041) ──→ 完成（严格串行）
                                     ↓
阶段 4: [P] EVT-SC-01 (T042) ───────┐
       [P] EVT-SC-02 (T043-T045) ───┤
       [P] EVT-SC-03 (T046-T048) ───┤
       [P] EVT-SC-04 (T049-T051) ───┤
       [P] EVT-SC-05 (T052-T056) ───┼──→ 全部完成
       [P] EVT-ALL   (T057-T058) ──┘
```

---

## 备注

- `[P]` 任务 = 不同文件、无依赖关系，阶段内部可并行执行
- 阶段标签（`[ENV]`, `[CASE-SC-*]`, `[AUTO-SC-*]`, `[EVT-SC-*]`）将任务映射至具体阶段和测试场景以实现可追溯性
- **阶段间严格串行**：阶段1：测试用例编写 → 阶段2：测试自动化代码编写 → 阶段3：测试环境准备 → 阶段4：测试执行
- **阶段内可并行**：阶段1（按场景）、阶段2（按场景）、阶段4（按用例）— 内部标记 `[P]` 的任务可同时执行
- **阶段3严格串行**：环境准备阶段内所有任务按顺序执行，无并行
- 执行前确认前置条件与测试数据就绪
- 每个任务或逻辑组执行后记录结果至 `tests/reports/` 目录
- 避免：模糊任务、文件冲突、破坏执行顺序的跨阶段依赖
