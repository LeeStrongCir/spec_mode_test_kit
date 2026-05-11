# 快速开始：LECS 主机管理

**Date**: 2026-05-09
**Feature**: 007-lecs-hosts

## 前置条件

- Docker + Docker Compose（Linux / Windows WSL2 均适用）
- 代码仓：`https://github.com/LeeStrongCir/spec_mode_leecloud.git`
- 项目目录：`spec_mode_leecloud`
- sudo密码：`Hcso@123`

## 部署步骤

### 1. 克隆代码仓

```bash
# 务必克隆到 WSL 原生文件系统（/mnt/c/ 路径构建极慢）
cd ~
git clone https://github.com/LeeStrongCir/spec_mode_leecloud.git
cd spec_mode_leecloud

ls
# 确认看到 Dockerfile 和 docker-compose.yml
```

### 2. 配置环境变量

```bash
cat backend/.env.example    # 查看示例配置
cp backend/.env.example backend/.env
nano backend/.env           # 编辑关键配置
```

必须确认的环境变量：

```env
DATABASE_URL=sqlite+aiosqlite:///data/dev.db    # 开发用 SQLite，生产换 PostgreSQL
SECRET_KEY=<随机字符串>                         # 运行下方命令生成
CSRF_SECRET_KEY=<另一个随机字符串>
APP_ENV=test
```

> **生成随机密钥：**
> ```bash
> python3 -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### 3. 构建并启动

```bash
docker compose up -d --build
```

预期输出：
```
 ✔ [internal] load build definition
 ✔ [stage-0] installing dependencies
 ✔ Container spec_mode_leecloud-app-1  Started
```

### 4. 运行数据库迁移

`docker-compose.yml` 的 `CMD` 只负责启动 uvicorn，不会自动执行 alembic 迁移，需要手动运行：

```bash
# 方式一：一次性命令（推荐）
docker compose run --rm app uv run alembic upgrade head

# 方式二：进入容器手动操作
docker compose exec app bash
uv run alembic upgrade head
exit
```

### 5. 验证服务

```bash
# 检查容器状态
docker compose ps
# 应看到 STATUS=Up

# 查看实时日志
docker compose logs -f app

# curl 健康检查
curl http://localhost:8000/health
# 预期: HTTP 200

# 浏览器验证
# http://localhost:8000/health   ← 健康检查
# http://localhost:8000/docs     ← Swagger API 文档
# http://localhost:8000/login    ← 登录页面
```

## 日常运维速查

| 操作 | 命令 |
|------|------|
| 启动服务 | `docker compose up -d` |
| 停止服务 | `docker compose down` |
| 重启服务 | `docker compose restart` |
| 重新构建镜像 | `docker compose up -d --build` |
| 进入容器调试 | `docker compose exec app bash` |
| 更新代码后重启 | `git pull && docker compose up -d --build` |
| 清理无用镜像 | `docker compose down --rmi local` |
| 重置数据库（含数据卷） | `docker compose down -v` |

## 验证清单

完成部署后，请逐一验证：

- [ ] `docker compose ps` 显示容器状态为 `Up`
- [ ] `docker compose logs` 无启动报错（如端口冲突、环境变量缺失）
- [ ] `curl http://localhost:8000/health` 返回 HTTP 200
- [ ] `docker compose run --rm app uv run alembic upgrade head` 迁移成功
- [ ] 浏览器访问 `http://localhost:8000/docs` 能看到 Swagger API 文档
- [ ] `lecs_hosts` 表已存在于数据库中
- [ ] LECS 主机管理页面功能正常
