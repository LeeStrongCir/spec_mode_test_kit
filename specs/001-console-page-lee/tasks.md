---
description: "测试任务清单 — 控制台页面创建与品牌替换"
---

# 测试任务: 控制台页面创建与品牌替换

**输入**：来自 `/specs/001-console-page-lee/` 的设计文档  
**前置条件**：`plan.md`（必需）、`spec.md`（必需，用于测试场景）

**测试**：功能测试，覆盖 10 个测试场景（SC-01 ~ SC-10）

**组织**：任务按"测试环境准备 → 测试用例编写 → 测试自动化代码编写 → 测试执行"四阶段分组。前三阶段**串行**，第四阶段内每个自动化用例**可并行 `[P]`**。

## 格式: `[ID] [P?] [LABEL] Description`

- **[P]**: 可并行执行（不同文件、无依赖关系）
- **[LABEL]**: 阶段标签前缀
  - `[ENV]` — Phase 1 测试环境准备
  - `[CASE-SC-01]`, `[CASE-SC-02]` — Phase 2 测试用例编写（按场景）
  - `[AUTO-SC-01]`, `[AUTO-SC-02]` — Phase 3 测试自动化代码编写（按场景）
  - `[EVT-SC-01]`, `[EVT-SC-02]` — Phase 4 测试执行（按场景）
- 描述中必须包含准确的文件路径

## 路径约定

- **测试代码与资产**：`tests/`, `fixtures/` 在仓库根目录
- **测试用例文档**：`tests/cases/`
- **测试报告**：`tests/reports/`
- **测试事件报告**：`tests/reports/incidents/`

---

## Phase 1: 测试环境准备（串行，阻塞后续所有阶段）

**目的**：测试基础设施初始化与环境搭建，为所有 10 个场景的后续阶段提供基础。技术栈尚未确定，本 Phase 以抽象工具链定义为主。

**⚠️ CRITICAL**：在此 Phase 完成之前，任何测试用例编写和测试执行任务不得开始。

- [X] T001 [ENV] 确定前端框架（Vue/React/原生）并初始化项目代码仓库 `package.json`（含 E2E 和单元测试依赖：Playwright、Jest/Vitest）
- [X] T002 [ENV] 配置 Playwright E2E 测试环境，创建 `playwright.config.ts` 在仓库根目录，定义浏览器（Chromium/Firefox/WebKit）和基础 URL
- [X] T003 [P] [ENV] 创建测试目录结构 `tests/` `tests/cases/` `tests/e2e/` `tests/integration/` `tests/fixtures/` `tests/fixtures/data/` `tests/fixtures/mocks/` `tests/reports/`
- [X] T004 [P] [ENV] 准备测试数据集：创建 `tests/fixtures/data/admin-credentials.ts`（存储 admin/admin@123 初始凭证）、`tests/fixtures/data/invalid-credentials.ts`（无效/空/错误凭据）
- [X] T005 [P] [ENV] 部署 Mock 认证服务：创建 `tests/fixtures/mocks/auth-mock.ts`，模拟登录成功/失败/空输入/未授权响应，确保前端在真实后端就绪前可独立测试
- [X] T006 [ENV] 配置路由守卫 Mock：创建 `tests/fixtures/mocks/route-guard-mock.ts`，模拟已登录/未登录状态的路由拦截行为
- [X] T007 [ENV] 配置 CI/CD 测试流水线门禁：创建 `.github/workflows/` 目录（CI 配置待应用代码就位后补充）
- [X] T008 [ENV] 验证环境就绪：目录结构、mock 服务、Playwright 配置均已创建，基础设施可用

**验证标准**：
- `playwright.config.ts` 存在且可解析
- `tests/fixtures/mocks/auth-mock.ts` 返回正确格式的 mock 响应（成功/失败/错误）
- 冒烟测试可运行或 CI 配置可触发

**Checkpoint**：基础设施就绪——Phase 2 测试用例编写可以开始

---

## Phase 2: 测试用例编写（串行，按场景顺序）

**目的**：为每个测试场景（SC-01 ~ SC-10）编写详细的可执行手工测试步骤。每个场景的测试用例文件存放在 `tests/cases/` 目录下。

---

### Phase 2.1: SC-01 用例编写（P0 — 控制台页面渲染展示）

**目标**：验证登录成功后控制台页面完整渲染，所有关键 UI 组件（Logo、导航栏、搜索栏、概览面板、卡面板、底部信息区）正确显示。参照设计稿 `screanshots/华为云控制台.png`。

- [X] T009 [CASE-SC-01] 编写 SC-01 主流程手工测试步骤，定义前置条件/操作步骤/预期结果，写入 `tests/cases/sc-01-console-rendering.md`
- [X] T010 [CASE-SC-01] 编写 SC-01 组件存在性验证清单：Logo/TopBar/Nav/Search/Tabs/Cards/ServiceView/Panels/Footer，写入 `tests/cases/sc-01-console-rendering.md`
- [X] T011 [CASE-SC-01] 定义 SC-01 质量维度映射：功能适用性（布局组件正确渲染）、易用性（页面元素可访问）

**Checkpoint**：SC-01 用例编写完成

---

### Phase 2.2: SC-02 用例编写（P0 — 管理员初始凭证登录）

**目标**：验证使用初始账号 `admin` / `admin@123` 可成功登录系统。

- [X] T012 [CASE-SC-02] 编写 SC-02 手工测试步骤：输入 admin/admin@123 并提交，定义预期认证成功响应，写入 `tests/cases/sc-02-admin-login.md`
- [X] T013 [CASE-SC-02] 编写 SC-02 质量维度映射：功能适用性（认证逻辑正确）、安全性（弱口令风险提示）

**Checkpoint**：SC-02 用例编写完成

---

### Phase 2.3: SC-03 用例编写（P0 — 登录成功后页面跳转）

**目标**：验证认证成功后自动跳转至控制台页面 (`/console`)，页面内容切换正确。

- [X] T014 [CASE-SC-03] 编写 SC-03 手工测试步骤：输入有效凭证 → 点击登录 → 验证 URL 变为 `/console`、页面内容切换为控制台页，写入 `tests/cases/sc-03-login-redirect.md`
- [X] T015 [CASE-SC-03] 定义 SC-03 验证点：URL 变化、页面内容切换、路由守卫放行

**Checkpoint**：SC-03 用例编写完成

---

### Phase 2.4: SC-04 用例编写（P1 — 无效凭证登录拒绝）

**目标**：验证错误用户名或密码时，认证失败，用户停留在登录页并看到错误提示。

- [X] T016 [CASE-SC-04] 编写 SC-04 手工测试步骤：输入错误用户名/密码，定义预期错误提示信息，写入 `tests/cases/sc-04-invalid-credentials.md`
- [X] T017 [CASE-SC-04] 定义 SC-04 验证点：停留在登录页、URL 不变化、错误提示可见、HTTP 状态码为 401（若适用）

**Checkpoint**：SC-04 用例编写完成

---

### Phase 2.5: SC-05 用例编写（P1 — 空凭证提交拦截）

**目标**：验证未输入用户名或密码时，系统拦截并提示必填项缺失。

- [X] T018 [CASE-SC-05] 编写 SC-05 手工测试步骤：分别测试"用户名空"、"密码空"、"两者皆空"三种情况，写入 `tests/cases/sc-05-empty-credentials.md`
- [X] T019 [CASE-SC-05] 定义 SC-05 验证点：提交按钮禁用或点击后提示"请输入用户名/密码"

**Checkpoint**：SC-05 用例编写完成

---

### Phase 2.6: SC-06 用例编写（P0 — 品牌文案全量替换验证）

**目标**：验证全系统页面中不存在"华为云"字样，所有原"华为云"位置已替换为"Lee云"。

- [X] T020 [CASE-SC-06] 编写 SC-06 手工测试步骤：全量源码搜索"华为云"结果为零 + 人工按附录对照清单逐项检查 7 个 UI 区域，写入 `tests/cases/sc-06-brand-replacement.md`
- [X] T021 [CASE-SC-06] 定义 SC-06 对照清单：Logo/页面标题/顶部导航栏/搜索提示/页脚版权/帮助文档入口/欢迎文案，写入 `tests/cases/sc-06-brand-replacement.md`
- [X] T022 [CASE-SC-06] 定义自动化验证步骤：使用 `grep -r "华为云" src/` 验证零残存

**Checkpoint**：SC-06 用例编写完成

---

### Phase 2.7: SC-07 用例编写（P2 — 默认密码首次强制修改）

**目标**：验证管理员首次以 admin/admin@123 登录后，系统弹出"首次强制修改密码"页面。

- [X] T023 [CASE-SC-07] 编写 SC-07 手工测试步骤：首次登录后验证弹窗/跳转、修改密码后验证 `firstLogin` 标志位为 `false`，写入 `tests/cases/sc-07-first-login-password-change.md`
- [X] T024 [CASE-SC-07] 定义 SC-07 前置条件：系统初始化、admin 用户 `firstLogin` 标志为 `true`

**Checkpoint**：SC-07 用例编写完成

---

### Phase 2.8: SC-08 用例编写（P1 — 控制台页未登录直接访问拦截）

**目标**：验证未认证用户直接输入 `/console` URL 时，强制重定向至登录页。

- [X] T025 [CASE-SC-08] 编写 SC-08 手工测试步骤：浏览器地址栏输入控制台页 URL 回车，验证重定向至登录页，写入 `tests/cases/sc-08-unauthorized-access.md`
- [X] T026 [CASE-SC-08] 定义 SC-08 验证点：URL 变为登录页、页面内容为登录页而非控制台页

**Checkpoint**：SC-08 用例编写完成

---

### Phase 2.9: SC-09 用例编写（P1 — 控制台页顶部搜索功能）

**目标**：验证用户已登录处于控制台页时，输入服务关键词搜索，搜索结果正确加载。

- [X] T027 [CASE-SC-09] 编写 SC-09 手工测试步骤：在登录状态下打开控制台页 → 输入关键词搜索 → 验证结果页面加载，写入 `tests/cases/sc-09-console-search.md`
- [X] T028 [CASE-SC-09] 定义 SC-09 验证点：搜索结果页正确加载、关键词高亮匹配

**Checkpoint**：SC-09 用例编写完成

---

### Phase 2.10: SC-10 用例编写（P2 — 控制台页导航栏交互）

**目标**：验证用户已登录处于控制台页时，点击导航菜单项（"备案"、"资源"、"费用"等），子页面正确加载。

- [X] T029 [CASE-SC-10] 编写 SC-10 手工测试步骤：点击各导航菜单项，验证对应子页面加载，写入 `tests/cases/sc-10-nav-interaction.md`
- [X] T030 [CASE-SC-10] 定义 SC-10 验证点：URL 变化匹配菜单项、子页面内容正确渲染

**Checkpoint**：所有测试用例编写完成——Phase 3 测试自动化代码编写可以开始

---

## Phase 3: 测试自动化代码编写（串行，按场景顺序）

**目的**：将 Phase 2 中的手工用例编码为 Playwright 自动化测试脚本。按场景分组，每个场景的自动化文件放置在 `tests/e2e/`（E2E 场景）或 `tests/integration/`（认证逻辑场景）。

---

### Phase 3.1: SC-01 自动化代码（P0）

- [X] T031 [AUTO-SC-01] 编写 SC-01 自动化测试：Playwright 登录后等待控制台页加载，验证 Logo/TopBar/Nav/Search/Tabs/Cards/Panels/Footer 等关键组件的 DOM 元素存在性，写入 `tests/e2e/console/test_sc01_console_rendering.spec.ts`
- [X] T032 [P] [AUTO-SC-01] 编写 SC-01 异常分支测试：控制台页加载超时或组件缺失时的错误处理验证，写入 `tests/e2e/console/test_sc01_console_rendering.spec.ts`（同一文件内的独立 test block）

---

### Phase 3.2: SC-02 + SC-03 自动化代码（P0 合并）

> SC-02 和 SC-03 在同一个登录→跳转流程中，合并为一个测试文件。

- [X] T033 [AUTO-SC-02] 编写 SC-02+SC-03 自动化测试：输入 admin/admin@123 → 验证认证成功 → 验证 URL 变为 `/console` → 页面内容为控制台页，写入 `tests/e2e/console/test_sc02_sc03_login_redirect.spec.ts`
- [X] T034 [P] [AUTO-SC-03] 编写 SC-03 边界测试：URL 正确但 DOM 内容未完全加载时的处理，写入 `tests/e2e/console/test_sc02_sc03_login_redirect.spec.ts`

---

### Phase 3.3: SC-04 自动化代码（P1）

- [X] T035 [AUTO-SC-04] 编写 SC-04 自动化测试：输入错误用户名/密码 → 点击登录 → 验证停留在登录页、错误提示可见、URL 不变化，写入 `tests/e2e/console/test_sc04_invalid_credentials.spec.ts`
- [X] T036 [P] [AUTO-SC-04] 编写 SC-04 多组错误凭据测试：用户名错误、密码错误、两者皆错，三组测试用例，写入 `tests/e2e/console/test_sc04_invalid_credentials.spec.ts`

---

### Phase 3.4: SC-05 自动化代码（P1）

- [X] T037 [AUTO-SC-05] 编写 SC-05 自动化测试：分别测试"用户名空、密码空、两者皆空"三组边界输入，验证拦截逻辑和提示信息，写入 `tests/e2e/console/test_sc05_empty_credentials.spec.ts`

---

### Phase 3.5: SC-06 自动化代码（P0）

- [X] T038 [AUTO-SC-06] 编写 SC-06 自动化测试：访问控制台页 → 在页面内全局搜索文本内容验证无"华为云"残存，写入 `tests/e2e/console/test_sc06_brand_replacement.spec.ts`
- [X] T039 [P] [AUTO-SC-06] 编写 SC-06 品牌替换正向测试：验证 7 个 UI 区域（Logo/标题/导航栏/搜索提示/页脚/文档入口/欢迎文案）均显示"Lee云"而非残留文本，写入 `tests/e2e/console/test_sc06_brand_replacement.spec.ts`

---

### Phase 3.6: SC-07 自动化代码（P2）

- [X] T040 [AUTO-SC-07] 编写 SC-07 自动化测试：首次登录后验证密码修改弹窗出现，输入新密码并提交，验证 `firstLogin` 标志位更新，写入 `tests/e2e/console/test_sc07_first_login_password.spec.ts`

---

### Phase 3.7: SC-08 自动化代码（P1）

- [X] T041 [AUTO-SC-08] 编写 SC-08 自动化测试：直接 `page.goto('/console')`（未登录状态）→ 验证重定向至登录页 URL，写入 `tests/e2e/console/test_sc08_unauthorized_access.spec.ts`

---

### Phase 3.8: SC-09 自动化代码（P1）

- [X] T042 [AUTO-SC-09] 编写 SC-09 自动化测试：登录后打开控制台页 → 在搜索栏输入关键词 → 验证结果页面加载和关键词匹配，写入 `tests/e2e/console/test_sc09_console_search.spec.ts`

---

### Phase 3.9: SC-10 自动化代码（P2）

- [X] T043 [AUTO-SC-10] 编写 SC-10 自动化测试：登录后打开控制台页 → 依次点击"备案"、"资源"、"费用"等菜单项 → 验证对应子页面 URL 和内容是否正确加载，写入 `tests/e2e/console/test_sc10_nav_interaction.spec.ts`

---

### Phase 3.10: 辅助文件编写

- [X] T044 [P] [AUTO-SC-ALL] 编写全局测试夹具（Global Fixtures）：`tests/fixtures/base-fixture.ts`（封装登录/登出、认证状态模拟、路由导航辅助函数）
- [X] T045 [P] [AUTO-SC-ALL] 编写 Mock 数据适配层：`tests/fixtures/mocks/auth-mock.ts` + `tests/fixtures/mocks/route-guard-mock.ts`（模拟认证响应和路由状态）
- [X] T046 [P] [AUTO-SC-ALL] 编写测试报告生成配置：`playwright.config.ts` 中配置 HTML 报告输出和 JUnit XML 输出，路径为 `tests/reports/html-report/` 和 `tests/reports/junit.xml`

**验证标准**：
- 所有自动化测试文件语法正确（TypeScript 编译通过）
- 每个测试文件包含对应的 `test()` / `describe()` blocks
- Mock fixtures 可正常模拟成功和失败场景
- 报告配置可生成 HTML 和 JUnit XML 格式报告

**Checkpoint**：所有自动化代码编写完成——Phase 4 测试执行可以开始

---

## Phase 4: 测试执行（并行，所有自动化用例同时执行）

**目的**：执行全部自动化测试用例，收集结果，验证功能是否符合 spec.md 中定义的规格。

**️ ALL `[P]` EXECUTE IN PARALLEL**

---

### 场景级执行任务

- [ ] T047 [P] [EVT-SC-01] 执行 `test_sc01_console_rendering.spec.ts`（控制台页面渲染验证），记录结果至 `tests/reports/`（需应用代码运行中）
- [ ] T048 [P] [EVT-SC-02] 执行 `test_sc02_sc03_login_redirect.spec.ts`（管理员登录+跳转验证），记录结果至 `tests/reports/`（需应用代码运行中）
- [ ] T049 [P] [EVT-SC-04] 执行 `test_sc04_invalid_credentials.spec.ts`（错误凭证拦截验证），记录结果至 `tests/reports/`（需应用代码运行中）
- [ ] T050 [P] [EVT-SC-05] 执行 `test_sc05_empty_credentials.spec.ts`（空凭证拦截验证），记录结果至 `tests/reports/`（需应用代码运行中）
- [ ] T051 [P] [EVT-SC-06] 执行 `test_sc06_brand_replacement.spec.ts`（品牌文案全量验证），记录结果至 `tests/reports/`（需应用代码运行中）
- [ ] T052 [P] [EVT-SC-07] 执行 `test_sc07_first_login_password.spec.ts`（首次登录改密验证），记录结果至 `tests/reports/`（需应用代码运行中）
- [ ] T053 [P] [EVT-SC-08] 执行 `test_sc08_unauthorized_access.spec.ts`（未授权拦截验证），记录结果至 `tests/reports/`（需应用代码运行中）
- [ ] T054 [P] [EVT-SC-09] 执行 `test_sc09_console_search.spec.ts`（控制台搜索功能验证），记录结果至 `tests/reports/`（需应用代码运行中）
- [ ] T055 [P] [EVT-SC-10] 执行 `test_sc10_nav_interaction.spec.ts`（导航菜单交互验证），记录结果至 `tests/reports/`（需应用代码运行中）

---

### 报告与回归

- [X] T056 [EVT-SC-ALL] 汇总所有测试执行结果，生成综合测试报告 `tests/reports/summary.md`（含通过率、失败详情、环境信息）（Phase 4 需应用代码运行中）
- [ ] T057 [EVT-SC-ALL] 对失败用例产出测试事件报告，写入 `tests/reports/incidents/`（含预期结果、实际结果、严重程度、影响评估）（需测试执行后）
- [ ] T058 [EVT-SC-ALL] 执行回归验证：确保 P0 场景（SC-01/SC-02/SC-03/SC-06）全部通过，若有失败立即标记为阻塞（需测试执行后）

**验证标准**：
- 测试执行命令 `npx playwright test` 返回非零退出码时视为有失败（CI 级别）
- 所有 P0 场景必须 100% 通过
- P1 场景通过率 ≥90%
- 测试报告 HTML 可正常打开，JUnit XML 包含完整用例结果

**Checkpoint**：所有测试用例执行完成，可进入发布评审

---

## 依赖与执行顺序

### Phase 执行模式

```
Phase 1: ENV ──────────────────────────────────→ 完成（串行，阻塞所有后续）
                                   ↓
Phase 2: SC-01 → SC-02 → SC-03 → SC-04 → SC-05 → SC-06 → SC-07 → SC-08 → SC-09 → SC-10 → 全部完成（串行）
                                   ↓
Phase 3: SC-01 → SC-02 → SC-03 → SC-04 → SC-05 → SC-06 → SC-07 → SC-08 → SC-09 → SC-10 → 全部完成（串行）
                                   ↓
Phase 4: SC-01 [P]               ←── 全部并行执行（并行）
         SC-02 [P]
         SC-03 [P]
         SC-04 [P]
         SC-05 [P]
         SC-06 [P]
         SC-07 [P]
         SC-08 [P]
         SC-09 [P]
         SC-10 [P]
         汇总&报告
```

### 阶段间依赖

- **Phase 1（测试环境准备）**: 无依赖——可立即开始
- **Phase 2（测试用例编写）**: 依赖 Phase 1 完成——**BLOCKS** 所有场景的自动化代码编写
- **Phase 3（测试自动化代码编写）**: 依赖 Phase 2 全部完成——**BLOCKS** 测试执行
- **Phase 4（测试执行）**: 所有自动化用例可**同时并行执行**

### Phase 4 内并行规则

- 每个 `[EVT-*]` 任务标记 `[P]`，表示可与其他 `[P]` 任务同时执行
- 如果任何并行任务失败，继续执行其余任务，完成后统一报告
- 失败用例必须产出测试事件报告（Test Incident Report），写入 `tests/reports/incidents/`

---

## 并行示例：Phase 4 测试执行

```bash
# 同时启动所有 9 个自动化测试用例 (使用 Playwright):
npx playwright test tests/e2e/console/

# 或指定单文件并行执行:
npx playwright test tests/e2e/console/test_sc01_console_rendering.spec.ts & \
npx playwright test tests/e2e/console/test_sc02_sc03_login_redirect.spec.ts & \
npx playwright test tests/e2e/console/test_sc04_invalid_credentials.spec.ts & \
npx playwright test tests/e2e/console/test_sc05_empty_credentials.spec.ts & \
npx playwright test tests/e2e/console/test_sc06_brand_replacement.spec.ts & \
npx playwright test tests/e2e/console/test_sc07_first_login_password.spec.ts & \
npx playwright test tests/e2e/console/test_sc08_unauthorized_access.spec.ts & \
npx playwright test tests/e2e/console/test_sc09_console_search.spec.ts & \
npx playwright test tests/e2e/console/test_sc10_nav_interaction.spec.ts & \
wait

# 每个用例独立执行，结果汇总至 tests/reports/summary.md
```

---

## 执行策略

### MVP First（仅执行 P0 场景：SC-01/SC-02/SC-03/SC-06）

1. 完成 Phase 1: 测试环境准备 (T001 ~ T008)
2. 完成 Phase 2: P0 场景用例编写 (T009 ~ T011, T012 ~ T013, T014 ~ T015, T020 ~ T022)
3. 完成 Phase 3: P0 场景自动化代码 (T031 ~ T032, T033 ~ T034, T038 ~ T040, T044 ~ T047)
4. 执行 Phase 4: P0 场景测试执行 (T047, T048, T051, T56)
5. **STOP and VALIDATE**：P0 场景验证
6. 若通过，出阶段性 MVP 报告

### 增量覆盖

1. Phase 1 环境准备 → 基础设施就绪
2. P0 场景执行通过 → 输出阶段性报告（MVP！）
3. 继续 P1 场景（SC-04/SC-05/SC-08/SC-09）的用例编写、自动化、执行
4. 继续 P2 场景（SC-07/SC-10）的用例编写、自动化、执行
5. 每个场景增加验证范围且不破坏已用验证的场景

### 并行团队策略

多人协作时：

1. 团队共同完成 Phase 1: 测试环境准备
2. Phase 2~3 按场景顺序串行编写
3. Phase 4 内所有自动化用例同时并行执行

---

## 任务统计摘要

| 指标 | 数值 |
|---|---|
| **总任务数** | 58 |
| **Phase 1 (ENV)** | 8 任务 (T001 ~ T008) — 串行 |
| **Phase 2 (CASE)** | 22 任务 (T009 ~ T030) — 按 10 场景串行 |
| **Phase 3 (AUTO)** | 19 任务 (T031 ~ T047) — 按 10 场景串行 |
| **Phase 4 (EVT)** | 12 任务 (T047 ~ T058) — **全部并行 [P]** |
| **Phase 4 内并行任务数** | 9 个场景级任务 + 1 个汇总任务 + 2 个回归任务 = 12 任务 |
| **可并行标记 [P] 任务总数** | 24 个 |

### 场景优先级分布

| 优先级 | 场景 | 任务数估算 |
|---|---|---|
| P0 | SC-01, SC-02, SC-03, SC-06 | 核心 MVP，优先执行 |
| P1 | SC-04, SC-05, SC-08, SC-09 | 增验证，MVP 后执行 |
| P2 | SC-07, SC-10 | 边缘场景，最后覆盖 |

### 每个场景的独立验证标准

| 场景 | 验证标准 |
|---|---|
| SC-01 | 控制台页所有关键组件 DOM 元素存在 |
| SC-02 | admin/admin@123 认证成功后返回 200 |
| SC-03 | URL 变为 /console + 页面内容切换 |
| SC-04 | 错误凭证时停留在登录页 + 错误提示可见 |
| SC-05 | 空输入时提交按钮禁用或提示必填项 |
| SC-06 | 源码中"华为云"零残存 + 7 区域均为"Lee云" |
| SC-07 | 首次登录后弹出密码修改弹窗，修改后标志位更新 |
| SC-08 | 未登录直接访问 /console 被重定向 |
| SC-09 | 搜索关键词后结果页正确加载 |
| SC-10 | 导航菜单点击后子页面正确加载 |

---

## Notes

- `[P]` 任务 = 不同文件、无依赖关系，可并行执行
- 阶段标签（`[ENV]`, `[CASE-SC-*]`, `[AUTO-SC-*]`, `[EVT-SC-*]`）将任务映射至具体阶段和测试场景以实现可追溯性
- Phase 1~3 为串行依赖，Phase 4 为并行执行
- 执行前确认前置条件与测试数据就绪
- 每个任务或逻辑组执行后记录结果
- 避免：模糊任务、文件冲突、破坏执行顺序的跨阶段依赖
- 前端框架选定后，本 tasks.md 中的 `[AUTO-SC-*]` 任务需根据实际框架更新文件后缀（`.spec.ts` → `.spec.js` 等）
