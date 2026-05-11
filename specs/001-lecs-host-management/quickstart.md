# 快速开始：LECS 主机管理

**Date**: 2026-05-09
**Feature**: 007-lecs-hosts

## 前置条件

- Python 3.11+
- 数据库迁移已更新至最新

## 安装设置

### 1. 进入后端目录

```bash
cd backend
```

### 2. 创建虚拟环境

```bash
python -m venv .venv && source .venv/bin/activate
```


### 3. 安装依赖（如果尚未安装）

```bash
uv sync --extra dev
```

### 4. 运行数据库迁移

```bash
uv run alembic upgrade head
```

这将创建 `lecs_hosts` 表，包含迁移中定义的所有列。

### 5. 启动服务器

```bash
uv run uvicorn src.app.main:app --reload --port 8000
```

## 验证清单

完成设置后，请验证以下事项：

- [ ] 服务在 `http://localhost:8000` 成功启动，无报错日志
- [ ] 访问 `http://localhost:8000/health` 返回健康状态（HTTP 200）
- [ ] 数据库迁移已应用，`lecs_hosts` 表存在于数据库中
