# Login System

用户登录认证系统，支持登录/登出、登录信息记录、用户查看自己的登录历史、管理员审计。

## Tech Stack

- **Python 3.11** + **FastAPI 0.115+**
- **SQLAlchemy 2.0** (异步 ORM)
- **SQLite** (开发) → **PostgreSQL** (生产)
- **Argon2id** 密码哈希
- **JWT** httpOnly Cookie 会话管理

## Quickstart

```bash
cd backend
python3.11 -m venv .venv && source .venv/bin/activate
uv sync --extra dev
alembic upgrade head
uv run uvicorn src.app.main:app --reload --port 8000
```

访问:
- API 文档: http://localhost:8000/docs
- 登录页面: http://localhost:8000/login
- 健康检查: http://localhost:8000/health

## Run Tests

```bash
cd backend
.venv/bin/python -m pytest tests/ -v --cov=src/app --cov-report=html
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | 健康检查 |
| POST | `/api/auth/login` | 用户登录 |
| POST | `/api/auth/logout` | 用户登出 |
| POST | `/api/auth/refresh` | 刷新令牌 |
| GET | `/api/auth/me` | 当前用户信息 |
| GET | `/api/auth/login-history` | 用户登录历史 |
| GET | `/api/admin/login-records` | 管理员审计记录 |

## Project Structure

```
backend/
├── src/app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # Pydantic Settings
│   ├── db.py                # Async engine + session factory
│   ├── models/              # SQLAlchemy ORM (user, session, login_record)
│   ├── schemas/             # Pydantic request/response
│   ├── services/            # Business logic (auth, password, login_record)
│   ├── api/                 # Routes (auth, login_record, deps)
│   ├── security/            # JWT, CSRF
│   ├── middleware/          # Error handler, login logger
│   └── utils/               # IP mask utility
├── tests/                   # pytest tests (unit + integration)
├── alembic/                 # Database migrations
└── frontend/templates/      # Jinja2 SSR pages
```
