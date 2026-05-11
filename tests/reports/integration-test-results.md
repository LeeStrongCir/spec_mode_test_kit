# 集成测试执行结果 - LECS主机管理

**执行日期**: 2026-05-11
**执行命令**: `pytest tests/integration/001-lecs-host-management/ -v --tb=short`
**总计**: 150 passed / 66 failed / 116 errors

## 通过的文件
- `test_lecs_hosts_list.py` — 列表分页/状态过滤/角色权限隔离 全部通过
- `test_lecs_hosts_pricing.py` — 包年包月/按需计费计算 全部通过

## 失败/错误的文件
- `test_lecs_hosts_create.py` — hostname/凭证校验测试失败(后端接受 201 而非期望 422)
- `test_lecs_hosts_stop.py` — 全部 9 个测试返回 404 而非期望的 200/403/401
- `test_lecs_hosts_start.py` — 状态码(409 vs 403)和响应体格式不匹配
- `test_lecs_hosts_delete.py` — 返回码差异(202 vs 200)
- `test_lecs_hosts_auth.py` — 跨用户测试返回 404 而非 403，_seed_host 签名不匹配
- `test_lecs_hosts_async.py` — SQLite db 路径问题(7 errors)，已删除状态过滤(1 failed)
- `test_lecs_hosts_audit.py` — 审计日志记录未生效(1 failed)
- `test_lecs_hosts_validation.py` — 116 errors: `app.services.billing` 模块不存在

## 关键发现
1. **stop 路由全 404**: 所有关机操作返回 404，说明路由注册或主机 ID 查询存在问题
2. **billing 模块缺失**: 116 errors 全部来自引用了不存在的 `app.services.billing`
3. **异步测试 db 冲突**: 部分 async 测试使用独立的 SQLite db 引擎但共享了 session
