# LECS 项目 data-testid 清单

> 本清单按页面/模块组织，记录所有使用 `data-testid` 的页面元素。
>
> **宪章要求**：所有可交互组件的 `data-testid` 覆盖率必须达到 100%。

## 页面：ECS 主机列表

**文件**: `backend/frontend/templates/lecs_host_list.html`

| data-testid | 元素类型 | 说明 |
|-------------|---------|------|
| `lecs-host-create-button` | `<a>` 按钮 | 创建 ECS 主机入口 |
| `lecs-host-data-table` | `<table>` | 主机数据表格 |

## 页面：创建 ECS 主机

**文件**: `backend/frontend/templates/lecs_host_create.html`

| data-testid | 元素类型 | 说明 |
|-------------|---------|------|
| `lecs-billing-mode` | `<div>` | 计费方式选择组 |
| `lecs-hostname-input` | `<input>` | 主机名输入框 |
| `lecs-username-input` | `<input>` | 用户名输入框 |
| `lecs-password-input` | `<input>` | 密码输入框 |
| `lecs-instance-type-tabs` | `<div>` | 实例规格 Tab 切换 |
| `lecs-os-image-selector` | `<select>` | 操作系统镜像下拉选择 |
| `lecs-ip-mode-tabs` | `<div>` | IP 分配模式 Tab 切换 |
| `lecs-ip-address-input` | `<input>` | IP 地址输入框 |
| `lecs-ip-mask-selector` | `<select>` | 子网掩码下拉选择 |
| `lecs-duration-selector` | `<div>` | 购买时长选择组 |
| `lecs-config-price` | `<span>` | 配置价格显示 |
| `lecs-buy-submit-button` | `<button>` | 立即购买提交按钮 |
| `lecs-confirm-dialog` | `<div>` | 确认对话框遮罩层 |
| `lecs-confirm-cancel-btn` | `<button>` | 确认对话框 - 取消按钮 |
| `lecs-confirm-ok-btn` | `<button>` | 确认对话框 - 确定按钮 |

## 页面：ECS 主机列表（JS 动态渲染）

**文件**: `backend/frontend/static/js/lecs-hosts.js`

| data-testid | 元素类型 | 说明 |
|-------------|---------|------|
| `lecs-host-status-{id}` | `<span>` | 主机状态标签（动态拼接 id） |
| `lecs-host-action-shutdown` | `<button>` | 关机操作按钮 |
| `lecs-host-action-start` | `<button>` | 启动操作按钮 |
| `lecs-host-action-delete` | `<button>` | 删除操作按钮 |
| `lecs-instance-card-{spec_id}` | `<div>` | 实例规格卡片（动态拼接 spec_id） |

## 统计

- **文件覆盖**: 2 个模板文件 + 1 个 JS 文件
- **data-testid 总数**: 20 个（含动态拼接 id 的模式 5 个）
- **可交互元素**: 17 个
- **展示性元素**: 3 个
