# E2E 测试执行结果 - LECS主机管理

**执行日期**: 2026-05-11
**执行命令**: `npx playwright test --project=chromium`
**结果**: 0 passed / 23 failed

## 失败原因：前端架构不匹配

### 根因

E2E 测试代码基于 **SPA 前端架构** 编写：
- 使用 `[data-testid="username-input"]`、`[data-testid="password-input"]`、`[data-testid="search-bar"]` 等定位元素

但 Docker 容器部署的是 **Jinja2 SSR 模板后端渲染**：
- 使用标准 HTML `<input id="identifier">`、`<form method="POST">`
- 无任何 `data-testid` 属性
- 前端文件位于 `backend/frontend/templates/` + `backend/frontend/static/`

### 实际登录页元素

| E2E 测试选择器（SPA） | SSR 模板实际元素 |
|----------------------|-----------------|
| `[data-testid="username-input"]` | `input[name="identifier"]` / `<label for="identifier">` |
| `[data-testid="password-input"]` | `input[type="password"]` |
| `[data-testid="login-button"]` | `<form method="POST" action="/api/auth/login">` 中的 submit |
| `[data-testid="search-bar"]` | 需确认控制台实际 DOM |
| `[data-testid="search-results"]` | 需确认控制台实际 DOM |

### Chromium 环境状态

- ✅ Chromium 已安装（v1217），Playwright 1.59.1
- ✅ 浏览器可正常启动
- ❌ 测试选择器与前端 DOM 不匹配，非环境问题

## 根因分析：两个不同层面的问题

### 1. 选择器不一致（表层问题）

| 缺失/不匹配的 data-testid | E2E 测试期望值 | 模板实际值/状态 |
|--------------------------|---------------|----------------|
| 登录页用户名输入框 | `[data-testid="username-input"]` | ❌ login.html 中 0 个 testid，仅有 `<input id="identifier">` |
| 登录页密码输入框 | `[data-testid="password-input"]` | ❌ 同上 |
| 登录页登录按钮 | `[data-testid="login-button"]` | ❌ 同上 |
| 控制台搜索栏 | `[data-testid="search-bar"]` | ❌ 未确认是否存在 |
| 搜索结果列表 | `[data-testid="search-results"]` | ❌ 未确认是否存在 |
| 主机列表表格 | `host-list-table` | ⚠️ 存在但名字不同：`lecs-host-data-table` |
| 计费模式 | `billing-mode-select` | ⚠️ 存在但名字不同：`lecs-billing-mode` |

### 2. 架构差异（深层问题）

E2E 测试按 **SPA（单页应用）** 架构编写，预期行为与 SSR 模板实际行为存在本质差异：

| 测试行为 | SPA 预期 | SSR 实际 |
|---------|---------|---------|
| 页面数据加载 | AJAX 请求，动态渲染 DOM | 服务端渲染完整 HTML |
| 导航跳转 | 前端路由变更，URL 变化无整页刷新 | 整页刷新或表单 POST 跳转 |
| 状态轮询 | `expect.poll()` 监听 DOM 实时更新 | 可能需要整页刷新或 WebSocket |
| 搜索建议 | 输入时实时弹出下拉框 | 可能无此 JS 实现 |
| 按钮状态切换 | 动态启用/禁用 (`disabled` 属性实时变化) | 需要刷新页面或 AJAX 响应后再渲染 |

### 改 `data-testid` 能否解决问题？

**结论：必要但不充分。**

- **能跑通的部分**：登录页、列表页静态渲染等 **纯页面展示类测试**，对齐 testid 后大概率通过
- **仍有风险的部分**：搜索栏交互、状态流转轮询、按钮实时启用/禁用等 **交互类测试**，可能因 JS 逻辑缺失或行为差异继续失败

### 实际验证结果

执行 `npx playwright test --project=chromium`：
- **23 / 23 失败**（全部在 `beforeEach` 登录步骤超时，未进入控制台页面）
- 原因：登录页 0 个 `data-testid`，所有测试卡在第一行 `[data-testid="username-input"]`

### 修复建议

1. **Phase 1（低成本验证）**：把 `login.html` 及各模板的 `data-testid` 对齐到 E2E 测试值，重跑看通过率
2. **Phase 2（行为适配）**：针对 Phase 1 中失败的交互类测试，逐个确认 SSR 模板是否实现了对应 JS 逻辑；若无则调整 E2E 测试断言策略（如改为轮询 API 而非轮询 DOM）

## 测试明细

| 文件 | 测试数 | 状态 |
|------|--------|------|
| test_sc01_search_navigation.spec.ts | 3 | 全部超时（找不到 search-bar） |
| test_sc02_list_operation_matrix.spec.ts | 6 | 全部超时（找不到 list-page 元素） |
| test_sc03_create_host.spec.ts | 6 | 全部超时（找不到 create-form） |
| test_sc04_lifecycle_control.spec.ts | 3 | 全部超时（找不到 stop/button） |
| test_sc05_safe_delete.spec.ts | 3 | 全部超时（找不到 delete-dialog） |
