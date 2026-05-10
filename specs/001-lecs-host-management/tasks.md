---
description: "测试任务清单：LECS主机管理"
---

# 测试任务: LECS主机管理

**输入**：来自 `/specs/001-lecs-host-management/` 的设计文档  
**前置条件**：`plan.md`（必需）、`spec.md`（必需，用于测试场景）

**测试**：以下任务基于 LECS 主机管理功能的全量功能测试需求。

**组织**：任务按"测试用例编写 → 测试自动化代码编写 → 测试环境准备 → 测试执行"四阶段分组。前三阶段**串行**，第四阶段内每个自动化用例**可并行 `[P]`**。

## 格式: `[ID] [P?] [LABEL] Description`

- **[P]**: 可并行执行（不同文件、无依赖关系）
- **[LABEL]**: 阶段标签前缀
  - `[ENV]` — 阶段 3 测试环境准备
  - `[CASE-SC-01]`, `[CASE-SC-02]` — 阶段 1 测试用例编写（按场景）
  - `[AUTO-SC-01]`, `[AUTO-SC-02]` — 阶段 2 测试自动化代码编写（按场景）
  - `[EVT-SC-01]`, `[EVT-SC-02]` — 阶段 4 测试执行（按场景）
- 描述中必须包含准确的文件路径

## 路径约定

- **测试代码与资产**：`tests/` 在仓库根目录下，`fixtures/` 在 `tests/` 目录下
- 测试用例文档：`tests/cases/001-lecs-host-management/`
- 集成测试：`tests/integration/001-lecs-host-management/`
- E2E 测试：`tests/e2e/001-lecs-host-management/`

---

## 阶段 1: 测试用例编写（串行，按场景顺序）

### 阶段 1.1: SC-01 搜索导航用例编写

**目标**：验证用户从控制台搜索"LECS"/"云服务器"并跳转至列表页的导航路径

- [ ] T001 [CASE-SC-01] 在 `tests/cases/001-lecs-host-management/sc-01-search-navigation.md` 中为 TC-001（搜索"LECS"关键词匹配与高亮）编写手工测试步骤：前置条件（已登录控制台）、操作步骤（输入"LECS"→观察下拉结果）、预期结果（"LECS主机"出现且关键词高亮）
- [ ] T002 [CASE-SC-01] 在 `tests/cases/001-lecs-host-management/sc-01-search-navigation.md` 中为 TC-002（搜索"云服"关键词）编写手工测试步骤：前置条件、操作步骤（输入"云服"→观察结果）、预期结果（"LECS主机"出现且"云服"高亮）
- [ ] T003 [CASE-SC-01] 在 `tests/cases/001-lecs-host-management/sc-01-search-navigation.md` 中为 TC-003（点击搜索结果跳转）编写手工测试步骤：前置条件、操作步骤（点击"LECS主机"条目→观察页面加载）、预期结果（URL 跳转至 `/console/lecs-hosts/list`，列表页正常加载）

**检查点**：SC-01 用例编写完成，优先级均为 P1

### 阶段 1.2: SC-02 列表操作矩阵用例编写

**目标**：验证主机列表页的分页展示、状态标签渲染、各状态行操作按钮启用/禁用逻辑

- [ ] T004 [CASE-SC-02] 在 `tests/cases/001-lecs-host-management/sc-02-list-operation-matrix.md` 中为 TC-010（列表页基本展示）编写手工测试步骤：验证分页表格、表格列（主机名/ID、计费模式、状态、私有IP、操作列）、页面标题栏（仅"创建LECS主机"按钮）、每行操作按钮（关机/启动/删除）
- [ ] T005 [CASE-SC-02] 在 `tests/cases/001-lecs-host-management/sc-02-list-operation-matrix.md` 中为 TC-011（状态标签彩色渲染）编写手工测试步骤：验证各状态颜色映射（正常-绿色、已关机-灰色、创建中-蓝色、创建失败-红色、删除中-黄色）
- [ ] T006 [CASE-SC-02] 在 `tests/cases/001-lecs-host-management/sc-02-list-operation-matrix.md` 中为 TC-012~TC-016（各状态操作矩阵）编写手工测试步骤：
  - TC-012: "正常"状态→关机可点击，启动/删除置灰
  - TC-013: "已关机"状态→启动/删除可点击，关机置灰
  - TC-014: "创建失败"状态→仅删除可点击，关机/启动置灰
  - TC-015: "删除中"状态→全部按钮置灰
  - TC-016: 软删除后主机不再出现在列表中
- [ ] T007 [CASE-SC-02] 在 `tests/cases/001-lecs-host-management/sc-02-list-operation-matrix.md` 中为 TC-API-010（GET /api/v1/lecs-hosts 列表查询接口）编写手工测试步骤：验证分页参数（page/page_size）、status 过滤、响应格式（列表数组+分页元数据）、错误返回（401/403）

**检查点**：SC-02 用例编写完成，优先级均为 P1

### 阶段 1.3: SC-03 创建主机用例编写

**目标**：验证主机创建表单的六大配置板块完整流程（基础配置、实例规格、操作系统、IP配置、购买时长、费用估算）

- [ ] T008 [CASE-SC-03] 在 `tests/cases/001-lecs-host-management/sc-03-create-host.md` 中为 TC-020（进入创建表单页）编写手工测试步骤：点击"创建LECS主机"→验证跳转至 `/console/lecs-hosts/create`→验证六大配置板块显示
- [ ] T009 [CASE-SC-03] 在 `tests/cases/001-lecs-host-management/sc-03-create-host.md` 中为 TC-021~TC-024（基础配置与规格选择）编写手工测试步骤：
  - TC-021: 计费模式默认"包年/包月"，可切换"按需计费"
  - TC-022: 主机名校验（`_invalid`、`ab`、`abcdefghijklmn` 拒绝，`valid01` 通过）
  - TC-023: 访问凭据校验（用户名4-16字符、密码8-32字符边界值）
  - TC-024: 实例规格选择（经济型4个规格、高性能型4个规格、未选择提交错误）
- [ ] T010 [CASE-SC-03] 在 `tests/cases/001-lecs-host-management/sc-03-create-host.md` 中为 TC-025~TC-027（操作系统、IP配置、购买时长）编写手工测试步骤：
  - TC-025: 镜像默认"Huawei Euler OS"，可选 Ubuntu/Windows（P2）
  - TC-026: IP分配方式（手工配置→IP格式校验+掩码8-24下拉；DHCP→隐藏输入）（P2）
  - TC-027: 购买时长选项（1-9个月、1年、2年）（P2）
- [ ] T011 [CASE-SC-03] 在 `tests/cases/001-lecs-host-management/sc-03-create-host.md` 中为 TC-028~TC-030（费用估算、确认对话框、异步状态流转）编写手工测试步骤：
  - TC-028: 费用实时计算（包年/包月100×3=300元、按需÷30元/天、规格修改实时更新）
  - TC-029: 确认对话框（展示配置摘要、取消保留表单、确定提交后重定向）
  - TC-030: 创建后状态流转（创建中→等待30秒→正常/创建失败、3秒轮询、终态停止轮询）
- [ ] T012 [CASE-SC-03] 在 `tests/cases/001-lecs-host-management/sc-03-create-host.md` 中为 TC-API-020（POST /api/v1/lecs-hosts 创建接口）编写手工测试步骤：验证请求体字段、响应格式、错误返回（400参数不合法、403配额超限、401无认证）

**检查点**：SC-03 用例编写完成，含 P1 和 P2 优先级

### 阶段 1.4: SC-04 生命周期控制用例编写

**目标**：验证主机关机/启动生命周期控制的完整状态流转与防重复操作

- [ ] T013 [CASE-SC-04] 在 `tests/cases/001-lecs-host-management/sc-04-lifecycle-control.md` 中为 TC-040（关机操作完整状态流转）编写手工测试步骤：点击关机→按钮置灰→状态"关机中"→全部按钮置灰→等待10秒→状态"已关机"→启动按钮恢复
- [ ] T014 [CASE-SC-04] 在 `tests/cases/001-lecs-host-management/sc-04-lifecycle-control.md` 中为 TC-041（启动操作完整状态流转）编写手工测试步骤：点击启动→按钮置灰→状态"启动中"→全部按钮置灰→等待10秒→状态"正常"→关机按钮恢复
- [ ] T015 [CASE-SC-04] 在 `tests/cases/001-lecs-host-management/sc-04-lifecycle-control.md` 中为 TC-042（"创建失败"状态启动）编写手工测试步骤：点击启动→状态"启动中"→等待10秒→状态"正常"→关机按钮恢复
- [ ] T016 [CASE-SC-04] 在 `tests/cases/001-lecs-host-management/sc-04-lifecycle-control.md` 中为 TC-043（过渡态防重复操作）编写手工测试步骤：验证"关机中"状态按钮保持置灰、尝试点击被后端拒绝
- [ ] T017 [CASE-SC-04] 在 `tests/cases/001-lecs-host-management/sc-04-lifecycle-control.md` 中为 TC-API-040（POST /api/v1/lecs-hosts/{id}/stop）和 TC-API-041（POST /api/v1/lecs-hosts/{id}/start）编写手工测试步骤：验证请求路径参数、响应接受状态、错误返回（状态不匹配403、无认证401）

**检查点**：SC-04 用例编写完成，优先级均为 P1

### 阶段 1.5: SC-05 安全删除用例编写

**目标**：验证主机安全删除流程（二次确认、软删除、配额计数减少、运行态拦截）

- [ ] T018 [CASE-SC-05] 在 `tests/cases/001-lecs-host-management/sc-05-safe-delete.md` 中为 TC-050（运行态主机删除拦截）编写手工测试步骤：验证"正常"状态删除按钮置灰/点击拦截、"创建中"/"关机中"状态删除按钮置灰
- [ ] T019 [CASE-SC-05] 在 `tests/cases/001-lecs-host-management/sc-05-safe-delete.md` 中为 TC-051（已关机主机删除流程）编写手工测试步骤：点击删除→二次确认对话框→取消验证→确认删除→状态"删除中"→等待3-5秒→从列表消失→配额计数减1
- [ ] T020 [CASE-SC-05] 在 `tests/cases/001-lecs-host-management/sc-05-safe-delete.md` 中为 TC-052（创建失败主机删除）编写手工测试步骤：点击删除→确认→状态"删除中"→从列表消失→配额计数减1
- [ ] T021 [CASE-SC-05] 在 `tests/cases/001-lecs-host-management/sc-05-safe-delete.md` 中为 TC-API-050（DELETE /api/v1/lecs-hosts/{id}）编写手工测试步骤：验证请求路径参数、软删除响应、错误返回（状态不允许403、无认证401）

**检查点**：SC-05 用例编写完成，优先级均为 P1

### 阶段 1.6: SC-06 API 管理与边缘场景用例编写

**目标**：验证 API 权限隔离、边缘场景（配额上限、创建超时、并发冲突、软删除数据库行为、审计日志）

- [ ] T022 [CASE-SC-06] 在 `tests/cases/001-lecs-host-management/sc-06-api-management.md` 中为 TC-060~TC-062（API 权限管理）编写手工测试步骤：
  - TC-060: 普通用户仅返回自身主机，越权过滤返回403（P2）
  - TC-061: 管理员返回全部主机列表+分页元数据（P2）
  - TC-062: 无认证返回401（P2）
- [ ] T023 [CASE-SC-06] 在 `tests/cases/001-lecs-host-management/sc-06-api-management.md` 中为 TC-API-060（API 统一响应格式）和 TC-API-061（API 参数校验）编写手工测试步骤：验证成功/失败响应格式一致性、缺失字段/格式错误返回400
- [ ] T024 [CASE-SC-06] 在 `tests/cases/001-lecs-host-management/sc-06-api-management.md` 中为 EC-001（配额上限100台拦截）编写手工测试步骤：预置100台活跃主机→尝试创建第101台→验证提示"主机数量达到上限"
- [ ] T025 [CASE-SC-06] 在 `tests/cases/001-lecs-host-management/sc-06-api-management.md` 中为 EC-002（创建超时降级）编写手工测试步骤：模拟后台创建超60秒→状态降级为"创建失败"→前端停止轮询
- [ ] T026 [CASE-SC-06] 在 `tests/cases/001-lecs-host-management/sc-06-api-management.md` 中为 EC-003（并发操作冲突防护）编写手工测试步骤："关机中"状态按钮置灰→直接API发送启动→后端拒绝
- [ ] T027 [CASE-SC-06] 在 `tests/cases/001-lecs-host-management/sc-06-api-management.md` 中为 EC-004（表单提交前未填写校验）编写手工测试步骤：实例规格未选择→提交拦截；IP格式非法→格式错误提示
- [ ] T028 [CASE-SC-06] 在 `tests/cases/001-lecs-host-management/sc-06-api-management.md` 中为 EC-005（软删除数据库保留）编写手工测试步骤：删除主机→直接查询数据库验证记录存在+deleted_at有值→验证配额统计排除
- [ ] T029 [CASE-SC-06] 在 `tests/cases/001-lecs-host-management/sc-06-api-management.md` 中为 EC-006（角色权限越权）编写手工测试步骤：用户B调用用户A主机的stop/delete→均返回403
- [ ] T030 [CASE-SC-06] 在 `tests/cases/001-lecs-host-management/sc-06-api-management.md` 中为 EC-007（审计日志记录）编写手工测试步骤：执行创建/删除/启动/关机→查询审计日志→验证包含操作人身份、时间戳、IP地址、操作详情

**检查点**：所有测试用例编写完成——阶段 2 测试自动化代码编写可以开始

---

## 阶段 2: 测试自动化代码编写（串行，按场景顺序）

### 阶段 2.1: SC-01 搜索导航自动化代码

**依赖**：T001-T003 完成

- [ ] T031 [P] [AUTO-SC-01] 在 `tests/e2e/001-lecs-host-management/test_sc01_search_navigation.spec.ts` 中编写 E2E 自动化测试：使用 Playwright，验证搜索"LECS"和"云服"关键词高亮显示、点击结果跳转至 `/console/lecs-hosts/list`，使用 `data-testid` 定位元素，`expect.poll()` 处理异步导航

### 阶段 2.2: SC-02 列表操作矩阵自动化代码

**依赖**：T004-T007 完成

- [ ] T032 [P] [AUTO-SC-02] 在 `tests/e2e/001-lecs-host-management/test_sc02_list_operation_matrix.spec.ts` 中编写 E2E 自动化测试：预置各状态主机列表，验证分页表格列展示、状态标签颜色（通过 class/color 属性）、各状态行操作按钮 disabled 属性
- [ ] T033 [P] [AUTO-SC-02] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_list.py` 中编写集成测试：使用 pytest，验证 GET /api/v1/lecs-hosts 接口的分页参数、status 过滤、响应格式（列表数组+分页元数据）、角色权限隔离（普通用户 vs 管理员）、401/403 错误返回
- [ ] T034 [P] [AUTO-SC-02] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_auth.py` 中编写认证集成测试：验证 JWT Cookie 认证中间件、Service Token 认证、无认证401拦截、越权访问403拒绝

### 阶段 2.3: SC-03 创建主机自动化代码

**依赖**：T008-T012 完成

- [ ] T035 [P] [AUTO-SC-03] 在 `tests/e2e/001-lecs-host-management/test_sc03_create_host.spec.ts` 中编写 E2E 自动化测试：完整创建流程（列表页→创建按钮→填写六大配置板块→确认对话框展示摘要→提交→验证状态流转"创建中"→"正常"），验证费用实时计算更新，使用 `expect.poll()` 等待异步状态
- [ ] T036 [P] [AUTO-SC-03] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_create.py` 中编写集成测试：验证 POST /api/v1/lecs-hosts 接口的参数校验（主机名格式、凭据复杂度、实例规格必填）、配额检查（100台上限）、异步任务触发、响应格式、错误返回（400/403/401）
- [ ] T037 [P] [AUTO-SC-03] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_validation.py` 中编写集成测试：应用边界值分析+等价类划分，验证主机名（4-10字符）、用户名（4-16字符）、密码（8-32字符）、IP格式（IPv4合法/非法）、掩码（8-24）的字段级校验与错误提示格式
- [ ] T038 [P] [AUTO-SC-03] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_pricing.py` 中编写费用计算集成测试：验证包年/包月计算（单价×时长）、按需计费计算（月费÷30）、费用随规格修改实时更新

### 阶段 2.4: SC-04 生命周期控制自动化代码

**依赖**：T013-T017 完成

- [ ] T039 [P] [AUTO-SC-04] 在 `tests/e2e/001-lecs-host-management/test_sc04_lifecycle_control.spec.ts` 中编写 E2E 自动化测试：完整关机→启动生命周期（normal→shutting_down→stopped→starting→normal），验证按钮实时 disabled/enabled 切换、状态标签更新、等待策略使用 `expect.poll()` 而非硬编码 sleep
- [ ] T040 [P] [AUTO-SC-04] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_stop.py` 中编写关机集成测试：验证 POST /api/v1/lecs-hosts/{id}/stop 的状态机逻辑（仅 normal→shutting_down）、异步状态流转、并发拒绝（非 normal 状态返回403）、无认证401
- [ ] T041 [P] [AUTO-SC-04] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_start.py` 中编写启动集成测试：验证 POST /api/v1/lecs-hosts/{id}/start 的状态机逻辑（stopped/failed→starting）、异步状态流转、并发拒绝、无认证401

### 阶段 2.5: SC-05 安全删除自动化代码

**依赖**：T018-T021 完成

- [ ] T042 [P] [AUTO-SC-05] 在 `tests/e2e/001-lecs-host-management/test_sc05_safe_delete.spec.ts` 中编写 E2E 自动化测试：已关机主机删除流程（点击删除→二次确认对话框→确认→状态"删除中"→等待3-5秒→从列表消失），验证运行态主机删除拦截（删除按钮置灰或点击拦截）
- [ ] T043 [P] [AUTO-SC-05] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_delete.py` 中编写删除集成测试：验证 DELETE /api/v1/lecs-hosts/{id} 的状态机逻辑（仅 stopped/failed 允许）、软删除逻辑（deleted_at 设置）、配额计数减1、状态不允许返回403及提示信息

### 阶段 2.6: SC-06 API 管理与边缘场景自动化代码

**依赖**：T022-T030 完成

- [ ] T044 [P] [AUTO-SC-06] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_async.py` 中编写异步任务生命周期集成测试：验证状态轮询（3秒间隔）、创建超时60秒降级（使用 `freezegun` 冻结时间控制）、终态（正常/创建失败）停止轮询
- [ ] T045 [P] [AUTO-SC-06] 在 `tests/integration/001-lecs-host-management/test_lecs_hosts_audit.py` 中编写审计日志集成测试：验证创建/删除/启动/关机操作均被记录，日志包含操作人身份、时间戳、IP地址、操作详情
- [ ] T046 [P] [AUTO-SC-06] 在 `tests/fixtures/factories/user_factory.py` 中编写 UserFactory 数据工厂：支持 role 参数（user/admin），配合 Factory Boy 模式快速创建隔离用户实例
- [ ] T047 [P] [AUTO-SC-06] 在 `tests/fixtures/factories/lecs_host_factory.py` 中编写 LecsHostFactory 数据工厂：支持 status 参数（normal/stopped/failed/creating/deleting）、user_id 关联，配合 Factory Boy 模式快速创建预设状态主机

**检查点**：所有自动化代码编写完成——阶段 3 测试环境准备可以开始

---

## 阶段 3: 测试环境准备（串行，阻塞后续所有阶段）

**目的**：测试基础设施初始化与环境搭建，为所有场景的后续阶段提供基础

**⚠️ 关键**：在此阶段完成之前，任何测试执行任务不得开始

- [ ] T048 [ENV] 在 `pytest.ini` 或 `pyproject.toml` 中配置 pytest 运行参数：测试路径（tests/integration/001-lecs-host-management/）、标记（markers: integration, e2e）、并行配置（pytest-xdist）、覆盖率配置
- [ ] T049 [ENV] 在 `playwright.config.ts` 中配置 Playwright 运行参数：浏览器（Chromium）、超时设置、重试策略、测试路径（tests/e2e/001-lecs-host-management/）、`data-testid` 选择器策略
- [ ] T050 [ENV] 在 `tests/conftest.py` 中编写全局 pytest fixtures：db_engine（SQLite 内存库）、db_session（事务回滚会话）、test_user/admin_user（UserFactory 创建）、authenticated_client/admin_client（JWT Cookie 客户端）
- [ ] T051 [ENV] 在 `tests/integration/001-lecs-host-management/conftest.py` 中编写集成测试级 fixtures：lecs_host_factory（预设状态主机工厂）、认证客户端 fixture、异步任务 mock fixture（使用 `unittest.mock`/`pytest-mock`）
- [ ] T052 [ENV] 在 `tests/e2e/001-lecs-host-management/fixtures/lecs-hosts-fixtures.ts` 中编写 Playwright E2E fixtures：authenticatedPage（预登录状态页面）、populatedListPage（预置各状态主机的列表页）
- [ ] T053 [P] [ENV] 在 `tests/fixtures/mocks/billing_service_mock.py` 中编写计费系统 Mock：定义 mock 响应契约（单价查询、费用计算），避免真实网络请求
- [ ] T054 [P] [ENV] 在 `tests/fixtures/mocks/task_queue_mock.py` 中编写异步任务队列 Mock：模拟 Celery/RQ 任务执行器，支持确定性时间控制（配合 `freezegun`）
- [ ] T055 [ENV] 在 `.env.test` 中配置测试环境变量：DATABASE_URL=sqlite:///、TESTING=true、SECRET_KEY=test-secret-key-do-not-use-in-production、MOCK_EXTERNAL_SERVICES=true、AUTH_JWT_SECRET=test-jwt-secret、AUTH_JWT_COOKIE_NAME=session
- [ ] T056 [ENV] 执行 `pip install pytest pytest-mock pytest-xdict freezegun factory-boy` 和 `npm install @playwright/test` 安装测试依赖，执行 `npx playwright install chromium` 安装浏览器

**检查点**：基础设施就绪——阶段 4 测试执行可以开始

---

## 阶段 4: 测试执行（并行，所有自动化用例同时执行）

**目的**：执行全部自动化测试用例，收集结果，验证功能是否符合规格

**⚠️ 所有 `[P]` 任务并行执行**

### E2E 测试执行

- [ ] T057 [P] [EVT-SC-01] 执行 `tests/e2e/001-lecs-host-management/test_sc01_search_navigation.spec.ts` 并记录结果至 `tests/reports/sc01-result.md`：验证搜索导航至列表页，URL 正确跳转
- [ ] T058 [P] [EVT-SC-02] 执行 `tests/e2e/001-lecs-host-management/test_sc02_list_operation_matrix.spec.ts` 并记录结果至 `tests/reports/sc02-result.md`：验证列表页状态矩阵 100% 匹配
- [ ] T059 [P] [EVT-SC-03] 执行 `tests/e2e/001-lecs-host-management/test_sc03_create_host.spec.ts` 并记录结果至 `tests/reports/sc03-result.md`：验证创建主机完整流程与费用计算
- [ ] T060 [P] [EVT-SC-04] 执行 `tests/e2e/001-lecs-host-management/test_sc04_lifecycle_control.spec.ts` 并记录结果至 `tests/reports/sc04-result.md`：验证关机→启动状态流转
- [ ] T061 [P] [EVT-SC-05] 执行 `tests/e2e/001-lecs-host-management/test_sc05_safe_delete.spec.ts` 并记录结果至 `tests/reports/sc05-result.md`：验证安全删除流程

### 集成测试执行

- [ ] T062 [P] [EVT-SC-02] 执行 `pytest tests/integration/001-lecs-host-management/test_lecs_hosts_list.py` 并记录结果至 `tests/reports/integration-list-result.md`：验证列表查询 API 契约
- [ ] T063 [P] [EVT-SC-02] 执行 `pytest tests/integration/001-lecs-host-management/test_lecs_hosts_auth.py` 并记录结果至 `tests/reports/integration-auth-result.md`：验证认证/授权链路
- [ ] T064 [P] [EVT-SC-03] 执行 `pytest tests/integration/001-lecs-host-management/test_lecs_hosts_create.py` 并记录结果至 `tests/reports/integration-create-result.md`：验证创建主机 API 契约与参数校验
- [ ] T065 [P] [EVT-SC-03] 执行 `pytest tests/integration/001-lecs-host-management/test_lecs_hosts_validation.py` 并记录结果至 `tests/reports/integration-validation-result.md`：验证表单字段边界值分析
- [ ] T066 [P] [EVT-SC-03] 执行 `pytest tests/integration/001-lecs-host-management/test_lecs_hosts_pricing.py` 并记录结果至 `tests/reports/integration-pricing-result.md`：验证费用计算逻辑
- [ ] T067 [P] [EVT-SC-04] 执行 `pytest tests/integration/001-lecs-host-management/test_lecs_hosts_stop.py` 并记录结果至 `tests/reports/integration-stop-result.md`：验证关机状态机逻辑
- [ ] T068 [P] [EVT-SC-04] 执行 `pytest tests/integration/001-lecs-host-management/test_lecs_hosts_start.py` 并记录结果至 `tests/reports/integration-start-result.md`：验证启动状态机逻辑
- [ ] T069 [P] [EVT-SC-05] 执行 `pytest tests/integration/001-lecs-host-management/test_lecs_hosts_delete.py` 并记录结果至 `tests/reports/integration-delete-result.md`：验证删除状态机与软删除逻辑
- [ ] T070 [P] [EVT-SC-06] 执行 `pytest tests/integration/001-lecs-host-management/test_lecs_hosts_async.py` 并记录结果至 `tests/reports/integration-async-result.md`：验证异步任务生命周期
- [ ] T071 [P] [EVT-SC-06] 执行 `pytest tests/integration/001-lecs-host-management/test_lecs_hosts_audit.py` 并记录结果至 `tests/reports/integration-audit-result.md`：验证审计日志记录

### 回归验证与总结

- [ ] T072 [EVT-SC-01] 执行回归验证：汇总所有 E2E 测试和集成测试执行结果，输出测试总结报告至 `tests/reports/summary.md`，包含：通过/失败用例统计、失败用例的 Test Incident Report（含失败步骤、预期结果、实际结果、环境信息）、覆盖率统计（FR 编号覆盖情况）
- [ ] T073 [EVT-SC-01] 验证每个场景的独立验证标准：
  - SC-01: 输入关键词 → 点击结果 → 验证 URL 变为 `/console/lecs-hosts/list`
  - SC-02: 预置各状态主机 → 验证按钮启用/禁用矩阵 100% 匹配
  - SC-03: 填写表单 → 确认 → 提交 → 验证状态流转"创建中"→"正常"，费用计算正确
  - SC-04: 完整状态流转 normal→shutting_down→stopped→starting→normal，按钮实时切换
  - SC-05: 已关机主机 → 删除确认 → 验证从列表消失 + 配额计数减 1
  - SC-06: 直接调用各 API 端点 → 验证请求/响应/错误处理符合契约

**检查点**：所有测试用例执行完成

---

## 并行示例：阶段 4 测试执行

```bash
# 并行启动所有 E2E 测试（使用 Playwright test runner 的 --workers 参数）:
npx playwright test tests/e2e/001-lecs-host-management/ --workers=5

# 并行启动所有集成测试（使用 pytest-xdist）:
pytest tests/integration/001-lecs-host-management/ -n auto --dist=loadfile

# 单个用例独立执行示例:
Task: "Execute tests/e2e/001-lecs-host-management/test_sc01_search_navigation.spec.ts"
Task: "Execute tests/e2e/001-lecs-host-management/test_sc02_list_operation_matrix.spec.ts"
Task: "Execute tests/e2e/001-lecs-host-management/test_sc03_create_host.spec.ts"
Task: "Execute tests/e2e/001-lecs-host-management/test_sc04_lifecycle_control.spec.ts"
Task: "Execute tests/e2e/001-lecs-host-management/test_sc05_safe_delete.spec.ts"
Task: "Execute pytest tests/integration/001-lecs-host-management/test_lecs_hosts_list.py"
Task: "Execute pytest tests/integration/001-lecs-host-management/test_lecs_hosts_auth.py"
Task: "Execute pytest tests/integration/001-lecs-host-management/test_lecs_hosts_create.py"
Task: "Execute pytest tests/integration/001-lecs-host-management/test_lecs_hosts_validation.py"
Task: "Execute pytest tests/integration/001-lecs-host-management/test_lecs_hosts_pricing.py"
Task: "Execute pytest tests/integration/001-lecs-host-management/test_lecs_hosts_stop.py"
Task: "Execute pytest tests/integration/001-lecs-host-management/test_lecs_hosts_start.py"
Task: "Execute pytest tests/integration/001-lecs-host-management/test_lecs_hosts_delete.py"
Task: "Execute pytest tests/integration/001-lecs-host-management/test_lecs_hosts_async.py"
Task: "Execute pytest tests/integration/001-lecs-host-management/test_lecs_hosts_audit.py"

# 所有用例独立执行，结果汇总至 tests/reports/summary.md
```

---

## 依赖关系图

```
阶段 1: CASE-SC-01 ── CASE-SC-02 ── CASE-SC-03 ── CASE-SC-04 ── CASE-SC-05 ── CASE-SC-06 → 全部完成
                                    ↓
阶段 2: AUTO-SC-01 ── AUTO-SC-02 ── AUTO-SC-03 ── AUTO-SC-04 ── AUTO-SC-05 ── AUTO-SC-06 → 全部完成
                                    ↓
阶段 3: ENV ───────────────────────────────────────────────────────────────────────────→ 完成
                                    ↓
阶段 4: EVT-SC-01 [P]  ←─── 5 个 E2E 测试并行
        EVT-SC-02 [P]  ←─── 2 个集成测试并行
        EVT-SC-03 [P]  ←─── 3 个集成测试并行
        EVT-SC-04 [P]  ←─── 2 个集成测试并行
        EVT-SC-05 [P]  ←─── 1 个集成测试并行
        EVT-SC-06 [P]  ←─── 2 个集成测试并行
        ──────────────────────────────────────→ 回归验证 + 测试总结报告
```

---

## 执行策略

### MVP First（仅执行 P0/P1 场景）

1. 完成 阶段 1: SC-01~SC-05（P1 场景）的测试用例编写（T001-T021）
2. 完成 阶段 2: SC-01~SC-05（P1 场景）的自动化代码编写（T031-T043）
3. 完成 阶段 3: 测试环境准备（T048-T056）
4. 执行 阶段 4: SC-01~SC-05（P1 场景）的测试执行（T057-T061, T062-T069, T072-T073）
5. **停止并验证**：独立验证 P1 场景结果（所有用户故事 1-5 通过）
6. 若通过，输出阶段性 MVP 报告

### 增量覆盖

1. 阶段 3 环境准备 → 基础设施就绪
2. P1 场景（SC-01~SC-05）执行通过 → 输出阶段性报告（MVP！）
3. 继续 SC-06（P2 场景）的用例编写（T022-T030）、自动化代码（T044-T047）、执行（T070-T071）
4. 每个场景增加验证范围且不破坏已验证的场景

### 并行团队策略

多人协作时：

1. 团队共同完成 阶段 1 按场景顺序串行编写（T001-T030）
2. 阶段 2 按场景顺序串行编写自动化代码（T031-T047）
3. 阶段 3: 测试环境准备（T048-T056）
4. 阶段 4 内所有自动化用例同时并行执行（T057-T073）

---

## Notes

- `[P]` 任务 = 不同文件、无依赖关系，可并行执行
- 阶段标签（`[ENV]`, `[CASE-SC-*]`, `[AUTO-SC-*]`, `[EVT-SC-*]`）将任务映射至具体阶段和测试场景以实现可追溯性
- 阶段 1~3 为串行依赖，阶段 4 为并行执行
- 执行前确认前置条件与测试数据就绪
- 每个任务或逻辑组执行后记录结果
- 避免：模糊任务、文件冲突、破坏执行顺序的跨阶段依赖
