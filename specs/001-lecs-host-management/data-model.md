# 数据模型：LECS 主机

**日期**: 2026-05-09
**功能**: 007-lecs-hosts

## 实体

### LECSHost

代表云服务器的虚拟计算实例。

| 字段 | 类型 | 约束 | 描述 |
|-------|------|-------------|-------------|
| `id` | UUID | PK, 自动生成 | 唯一主机标识符 |
| `user_id` | UUID | FK → users.id, INDEX, NOT NULL | 主机所有者 |
| `hostname` | String(64) | NOT NULL | 用户自定义主机名 |
| `billing_mode` | String(16) | NOT NULL | `"subscription"` 或 `"on_demand"` |
| `instance_type` | String(32) | NOT NULL | `"economy"` 或 `"high_performance"` |
| `spec_id` | String(32) | NOT NULL | 具体规格标识符（例如 `"eco-2c2g"`） |
| `vcpu` | Integer | NOT NULL | CPU 核心数 |
| `ram_gb` | Integer | NOT NULL | 内存大小（GiB） |
| `system_disk_gb` | Integer | NOT NULL | 系统盘大小（GB） |
| `os_image` | String(32) | NOT NULL | `"huawei_euler"`、`"ubuntu"`、`"windows"` |
| `ip_mode` | String(16) | NOT NULL | `"dhcp"` 或 `"manual"` |
| `ip_address` | String(45) | 可空 | 手动配置的 IP；DHCP 模式为 NULL |
| `ip_mask` | Integer | 可空 | 子网掩码（8–24）；DHCP 模式为 NULL |
| `status` | Enum | NOT NULL, 默认=`creating` | 见下方状态机 |
| `error_msg` | Text | 可空 | 失败时的错误详情 |
| `duration` | Integer | NOT NULL | 购买时长（月）（1–9、12、24） |
| `unit_price` | Float | NOT NULL | 每月价格（CNY） |
| `cost_info` | JSON | 可空 | 快照：`{billing_mode, unit_price, duration, total, currency}` |
| `username` | String(64) | NOT NULL | 访问凭证用户名 |
| `password_hash` | String(255) | NOT NULL | 哈希后的访问凭证密码 |
| `deleted_at` | DateTime | 可空, INDEX | 软删除时间戳（NULL = 活跃） |
| `created_at` | DateTime | NOT NULL, 自动设置 | 创建时间戳 |
| `updated_at` | DateTime | NOT NULL, 自动设置 | 最后更新时间戳 |

**索引**：
- `ix_lecs_hosts_user_id` — 用于用户范围查询
- `ix_lecs_hosts_deleted_at` — 用于软删除过滤（`WHERE deleted_at IS NULL`）
- 复合索引：`(user_id, deleted_at)` — 用于配额计数

### InstanceSpec（常量参考数据）

非数据库模型——在代码中定义为常量。将 spec_id 映射到 vCPU、RAM、磁盘和价格。

| spec_id | instance_type | name | vcpu | ram_gb | disk_gb | monthly_price |
|---------|--------------|------|------|--------|---------|---------------|
| `eco-2c2g` | economy | 通用计算机 | 2 | 2 | 40 | 100 |
| `eco-2c4g` | economy | 通用计算机 | 2 | 4 | 40 | 140 |
| `eco-2c8g` | economy | 通用计算机 | 2 | 8 | 40 | 180 |
| `eco-4c8g` | economy | 通用计算机 | 4 | 8 | 40 | 240 |
| `perf-2c4g` | high_performance | 通用增强计算机 | 2 | 4 | 40 | 160 |
| `perf-2c8g` | high_performance | 通用增强计算机 | 2 | 8 | 40 | 200 |
| `perf-4c8g` | high_performance | 通用增强计算机 | 4 | 8 | 40 | 260 |
| `perf-8c16g` | high_performance | 通用增强计算机 | 8 | 16 | 40 | 500 |

### HostStatus 枚举

```python
class HostStatus(str, enum.Enum):
    creating = "creating"
    normal = "normal"
    failed = "failed"
    shutting_down = "shutting_down"
    stopped = "stopped"
    starting = "starting"
    deleting = "deleting"
    deleted = "deleted"
```

## 状态转换规则

| 源状态 | 操作 | 目标状态 | 锁定期间 | 持续时间 |
|-----------|-----------|----------|--------------|----------|
| `creating` | (异步) | `normal` / `failed` | 是 | ~30s（超时 60s） |
| `normal` | `shutdown` | `shutting_down` | 是 | ~10s |
| `shutting_down` | (异步) | `stopped` | 是 | ~10s |
| `stopped` | `start` | `starting` | 是 | ~10s |
| `starting` | (异步) | `normal` | 是 | ~10s |
| `failed` | `start` | `starting` | 是 | ~10s |
| `failed` | `delete` | `deleting` | 是 | ~5s |
| `stopped` | `delete` | `deleting` | 是 | ~5s |
| `deleting` | (异步) | `deleted` | 是 | ~5s |
| `deleted` | (无) | — | N/A | 永久 |

**规则**：
- 未列在上述表格中的转换将被 `409 Conflict` 拒绝。
- 处于过渡状态（`creating`、`shutting_down`、`starting`、`deleting`）时，所有生命周期操作均被拒绝。
- `delete` 仅允许从 `stopped` 或 `failed` 状态执行——从 `normal` 状态尝试删除将返回 `403 Forbidden`。
- 软删除的主机（`deleted_at IS NOT NULL`）不会出现在列表查询中，但保留数据库记录。

## 配额规则

- 每用户最多 **100 台主机**。
- 计数方式：`SELECT COUNT(*) FROM lecs_hosts WHERE user_id = ? AND deleted_at IS NULL`
- 包含除 `deleted` 之外的所有状态（即 `creating`、`normal`、`failed`、`shutting_down`、`stopped`、`starting`、`deleting`）。

## 验证规则

| 规则 | 字段 | 验证逻辑 | 错误信息 |
|------|-------|-----------|---------------|
| VR-001 | hostname | `^[\w]{4,10}$`，不可以 `_` 开头 | "主机名仅支持英文、数字、下划线，长度4-10字符，不可以下划线开头" |
| VR-002 | username | `^[a-zA-Z0-9_@.+-]{4,16}$` | "用户名长度4-16字符" |
| VR-002 | password | `^[a-zA-Z0-9_@#$%^&+=!-]{8,32}$` | "密码长度8-32字符" |
| VR-003 | duration | `int` 取值 {1–9, 12, 24} | "请选择有效的购买时长" |
| VR-007 | spec_id | 必须是 INSTANCE_SPECS 中的有效 spec_id | "请选择有效的实例规格" |
| VR-004 | billing_mode | `"subscription"` 或 `"on_demand"` | "请选择有效的计费模式" |
| VR-009 | ip_address | 有效的 IPv4 格式（当 ip_mode=manual 时） | "请输入有效的IP地址" |
| VR-009 | ip_mask | 整数 8–24（当 ip_mode=manual 时） | "请选择有效的掩码值" |
| VR-005 | 主机名唯一性 | 每用户唯一 | "主机名已存在" |

## 关系

- **LECSHost** → **User**：通过 `user_id` 外键建立多对一关系。用户表**未**实现 `ON DELETE CASCADE`——在删除用户之前必须显式删除主机。
