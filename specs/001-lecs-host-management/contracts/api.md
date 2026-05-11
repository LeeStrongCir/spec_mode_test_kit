# API 合同：LECS 主机服务

**Base Path**: `/api/v1/lecs-hosts`
**Auth**: JWT Cookie (`access_token`) — 所有端点均需认证。
**CSRF**: POST/DELETE 操作受保护。
**Rate Limit**: 每用户每分钟 20 个请求。

---

## GET /api/v1/lecs-hosts

**Description**: 分页列出用户的主机列表（已过滤：`deleted_at IS NULL`）。

**查询参数**：
| 参数名 | 类型 | 是否必填 | 默认值 | 描述 |
|-------|------|----------|---------|-------------|
| `page` | int | 否 | 1 | 页码（从 1 开始） |
| `page_size` | int | 否 | 20 | 每页条数（最大 100） |

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "hostname": "web-server-01",
        "billing_mode": "subscription",
        "instance_type": "economy",
        "spec_id": "eco-2c4g",
        "vcpu": 2,
        "ram_gb": 4,
        "system_disk_gb": 40,
        "os_image": "huawei_euler",
        "ip_mode": "dhcp",
        "ip_address": "10.0.0.15",
        "status": "normal",
        "error_msg": null,
        "created_at": "2026-05-09T08:00:00Z",
        "updated_at": "2026-05-09T08:02:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1
  }
}
```

**授权**： 
- 普通用户：仅查看自己的主机（`WHERE user_id = current_user.id`）
- 管理员用户：查看所有主机

**错误**：
| 状态码 | 响应体 | 触发条件 |
|--------|------|-----------|
| 401 | `{"status":"error","error_code":"MISSING_TOKEN","message":"未登录"}` | 无有效的 access_token cookie |

---

## POST /api/v1/lecs-hosts

**Description**: 创建新的 LECS 主机（异步）。立即返回 `creating` 状态。

**请求体**：
```json
{
  "hostname": "web-server-01",
  "billing_mode": "subscription",
  "instance_type": "economy",
  "spec_id": "eco-2c4g",
  "os_image": "huawei_euler",
  "ip_mode": "dhcp",
  "ip_address": null,
  "ip_mask": null,
  "username": "root_admin",
  "password": "MyStr0ng!Pass",
  "duration": 6
}
```

| 参数名 | 类型 | 是否必填 | 验证规则 |
|-------|------|----------|-----------|
| `hostname` | string | 是 | `^[\w]{4,10}$`，不能以 `_` 开头，每个用户唯一 |
| `billing_mode` | string | 是 | `"subscription"` 或 `"on_demand"` |
| `instance_type` | string | 是 | `"economy"` 或 `"high_performance"` |
| `spec_id` | string | 是 | 根据 instance_type 必须有效 |
| `os_image` | string | 是 | `"huawei_euler"`、`"ubuntu"`、`"windows"` |
| `ip_mode` | string | 是 | `"dhcp"` 或 `"manual"` |
| `ip_address` | string | 条件性 | 当 `ip_mode="manual"` 时必填，有效的 IPv4 地址 |
| `ip_mask` | int | 条件性 | 当 `ip_mode="manual"` 时必填，范围 8–24 |
| `username` | string | 是 | `^[a-zA-Z0-9_@.+-]{4,16}$` |
| `password` | string | 是 | `^[a-zA-Z0-9_@#$%^&+=!-]{8,32}$` |
| `duration` | int | 是 | 1–9、12 或 24 |

**Response (201 Created)**:
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "hostname": "web-server-01",
    "status": "creating",
    "message": "任务已提交"
  }
}
```

**错误**：
| 状态码 | 响应体 | 触发条件 |
|--------|------|-----------|
| 400 | `{"status":"error","message":"主机名已存在"}` | 用户已使用该主机名 |
| 403 | `{"status":"error","error_code":"QUOTA_EXCEEDED","message":"主机数量达到上限"}` | 用户拥有 100 个或更多未删除的主机 |
| 422 | `{"detail": [...]}` | 任意字段验证错误 |
| 500 | `{"status":"error","message":"服务内部错误"}` | 创建任务时发生服务器错误 |

---

## POST /api/v1/lecs-hosts/{id}/shutdown

**Description**: 关闭运行中的主机（异步）。耗时约 10 秒。

**路径参数**：`id` (UUID)

**前置条件**：主机状态必须为 `normal`。

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "shutting_down",
    "message": "关机指令已下发"
  }
}
```

**错误**：
| 状态码 | 响应体 | 触发条件 |
|--------|------|-----------|
| 404 | `{"status":"error","message":"主机不存在"}` | 主机不存在或不属于该用户 |
| 409 | `{"status":"error","error_code":"INVALID_STATE","message":"仅可对运行中的主机执行关机操作"}` | 主机不处于 `normal` 状态 |

---

## POST /api/v1/lecs-hosts/{id}/start

**Description**: 启动已关机或失败的主机（异步）。耗时约 10 秒。

**路径参数**：`id` (UUID)

**前置条件**：主机状态必须为 `stopped` 或 `failed`。

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "starting",
    "message": "启动指令已下发"
  }
}
```

**错误**：
| 状态码 | 响应体 | 触发条件 |
|--------|------|-----------|
| 404 | `{"status":"error","message":"主机不存在"}` | 主机不存在或不属于该用户 |
| 409 | `{"status":"error","error_code":"INVALID_STATE","message":"仅可对已关机或创建失败的主机执行启动操作"}` | 主机不处于 `stopped` 或 `failed` 状态 |

---

## DELETE /api/v1/lecs-hosts/{id}

**Description**: 软删除主机（异步）。仅允许对 `stopped` 或 `failed` 状态的主机执行。耗时约 5 秒。

**路径参数**：`id` (UUID)

**前置条件**：主机状态必须为 `stopped` 或 `failed`。

**Response (202 Accepted)**:
```json
{
  "status": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "deleting",
    "message": "删除中，请等待处理完成"
  }
}
```

**错误**：
| 状态码 | 响应体 | 触发条件 |
|--------|------|-----------|
| 404 | `{"status":"error","message":"主机不存在"}` | 主机不存在或不属于该用户 |
| 403 | `{"status":"error","error_code":"NOT_STOPPED","message":"仅支持对已关机或创建失败的主机执行删除"}` | 主机处于 `normal`、`creating` 或过渡状态 |

---

## GET /api/v1/lecs-hosts/pricing

**Description**: 返回当前实例规格价格数据。

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "economy": [
      {"spec_id": "eco-2c2g", "name": "通用计算机", "vcpu": 2, "ram_gb": 2, "system_disk_gb": 40, "monthly_price": 100},
      {"spec_id": "eco-2c4g", "name": "通用计算机", "vcpu": 2, "ram_gb": 4, "system_disk_gb": 40, "monthly_price": 140},
      {"spec_id": "eco-2c8g", "name": "通用计算机", "vcpu": 2, "ram_gb": 8, "system_disk_gb": 40, "monthly_price": 180},
      {"spec_id": "eco-4c8g", "name": "通用计算机", "vcpu": 4, "ram_gb": 8, "system_disk_gb": 40, "monthly_price": 240}
    ],
    "high_performance": [
      {"spec_id": "perf-2c4g", "name": "通用增强计算机", "vcpu": 2, "ram_gb": 4, "system_disk_gb": 40, "monthly_price": 160},
      {"spec_id": "perf-2c8g", "name": "通用增强计算机", "vcpu": 2, "ram_gb": 8, "system_disk_gb": 40, "monthly_price": 200},
      {"spec_id": "perf-4c8g", "name": "通用增强计算机", "vcpu": 4, "ram_gb": 8, "system_disk_gb": 40, "monthly_price": 260},
      {"spec_id": "perf-8c16g", "name": "通用增强计算机", "vcpu": 8, "ram_gb": 16, "system_disk_gb": 40, "monthly_price": 500}
    ]
  }
}
```

---

## 通用错误响应格式

所有错误响应遵循以下结构：

```json
{
  "status": "error",
  "error_code": "VALIDATION_ERROR",
  "message": "Human-readable error description"
}
```

| error_code | 含义 |
|------------|---------|
| `MISSING_TOKEN` | 无有效的认证令牌 |
| `QUOTA_EXCEEDED` | 用户已达到 100 台主机上限 |
| `INVALID_STATE` | 生命周期操作不允许在当前主机状态下执行 |
| `NOT_STOPPED` | 尝试删除未关机或失败的主机 |
| `VALIDATION_ERROR` | 请求体验证失败 |
| `HOST_NOT_FOUND` | 当前用户不存在该主机 ID |
