---
description: "测试任务清单模板"
---

# 测试任务: [FEATURE/测试对象名称]

**输入**：来自 `/specs/[###-feature-name]/` 的设计文档  
**前置条件**：`plan.md`（必需）、`spec.md`（必需，用于测试场景）

**测试**：以下示例包含测试任务。

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
- 以下路径假设为单项目——根据 `plan.md` 结构进行调整

<!-- 
  ============================================================================
  IMPORTANT: 以下任务仅为 示例，仅用于说明格式。
  
  /speckit-test.tasks 命令 MUST 将其替换为基于以下内容的实际任务：
  - 测试场景，来自 spec.md（及其优先级 P0, P1, P2…）
  - 测试策略与需求，来自 plan.md
  - 技术决策，来自 research.md
  
  任务 MUST 按四阶段生命周期组织，以便每个场景可以：
  - 环境准备（串行）
  - 用例编写（串行）
  - 自动化代码编写（串行）
  - 测试执行（并行）
  
  在生成的 tasks.md 中，DO NOT 保留这些示例任务。
  ============================================================================
-->

## Phase 1: 测试环境准备（串行，阻塞后续所有阶段）

**目的**：测试基础设施初始化与环境搭建，为所有场景的后续阶段提供基础

**⚠️ CRITICAL**：在此 Phase 完成之前，任何测试用例编写和测试执行任务不得开始

- [ ] T001 [ENV] Initialize testing framework with required dependencies
- [ ] T002 [ENV] Setup Docker-based test environment in `docker-compose.yml`
- [ ] T003 [P] [ENV] Deploy mock services for Nova in `tests/fixtures/mocks/`
- [ ] T004 [ENV] Load baseline test data and configure fixtures
- [ ] T005 [ENV] Verify log, audit, and CI/CD pipeline gates

**Checkpoint**：基础设施就绪——Phase 2 测试用例编写可以开始

---

## Phase 2: 测试用例编写（串行，按场景顺序）

### Phase 2.1: SC-01 用例编写

**目标**：[简述该场景的测试目的，如"验证单台 ECS 实例规格变更的功能正确性"]

- [ ] T006 [CASE-SC-01] 编写 SC-01 手工测试步骤在 `docs/test-scenarios/sc-01.md`
- [ ] T007 [CASE-SC-01] 定义 SC-01 预期输出和验证点在 `docs/test-scenarios/sc-01.md`

**Checkpoint**：SC-01 用例编写完成

### Phase 2.2: SC-02 用例编写

**目标**：[简述该场景的测试目的，如"验证批量 ECS 实例规格变更的并发处理"]

- [ ] T008 [CASE-SC-02] 编写 SC-02 手工测试步骤在 `docs/test-scenarios/sc-02.md`
- [ ] T009 [CASE-SC-02] 定义 SC-02 预期输出和验证点在 `docs/test-scenarios/sc-02.md`

**Checkpoint**：所有测试用例编写完成——Phase 3 测试自动化代码编写可以开始

---

## Phase 3: 测试自动化代码编写（串行，按场景顺序）

### Phase 3.1: SC-01 自动化代码

- [ ] T010 [P] [AUTO-SC-01] 编写主流程自动化测试在 `tests/integration/test_sc01_main.py`
- [ ] T011 [P] [AUTO-SC-01] 编写异常分支自动化测试在 `tests/integration/test_sc01_exception.py`

### Phase 3.2: SC-02 自动化代码

- [ ] T012 [P] [AUTO-SC-02] 编写主流程自动化测试在 `tests/integration/test_sc02_main.py`
- [ ] T013 [P] [AUTO-SC-02] 编写并发测试在 `tests/integration/test_sc02_concurrent.py`

**Checkpoint**：所有自动化代码编写完成——Phase 4 测试执行可以开始

---

## Phase 4: 测试执行（并行，所有自动化用例同时执行）

**目的**：执行全部自动化测试用例，收集结果，验证功能是否符合规格

**⚠️ ALL `[P]` EXECUTE IN PARALLEL**

- [ ] T014 [P] [EVT-SC-01] Execute `test_sc01_main.py` and record results
- [ ] T015 [P] [EVT-SC-01] Execute `test_sc01_exception.py` and record results
- [ ] T016 [P] [EVT-SC-02] Execute `test_sc02_main.py` and record results
- [ ] T017 [P] [EVT-SC-02] Execute `test_sc02_concurrent.py` and record results
- [ ] T018 [EVT-SC-01] 执行回归验证，输出测试总结报告在 `tests/reports/summary.md`

**Checkpoint**：所有测试用例执行完成

---

[根据需要添加更多测试场景 Phase 2.x / Phase 3.x，遵循相同模式]

---

## 依赖与执行顺序

### Phase 执行模式

```
Phase 1: ENV ──────────────────────────────────→ 完成（串行）
                                  ↓
Phase 2: CASE-SC-01 → CASE-SC-02 → CASE-SC-03 → 全部完成（串行）
                                  ↓
Phase 3: AUTO-SC-01 → AUTO-SC-02 → AUTO-SC-03 → 全部完成（串行）
                                  ↓
Phase 4: EVT-SC-01 [P]            ←── 全部并行执行（并行）
         EVT-SC-02 [P]
         EVT-SC-03 [P]
```

### 阶段间依赖

- **Phase 1（测试环境准备）**: 无依赖——可立即开始
- **Phase 2（测试用例编写）**: 依赖 Phase 1 完成——**BLOCKS** 所有场景的自动化代码编写
- **Phase 3（测试自动化代码编写）**: 依赖 Phase 2 全部完成——**BLOCKS** 测试执行
- **Phase 4（测试执行）**: 所有自动化用例可**同时并行执行**

### Phase 4 内并行规则

- 每个 `[EVT-*]` 任务标记 `[P]`，表示可与其他 `[P]` 任务同时执行
- 如果任何并行任务失败，继续执行其余任务，完成后统一报告
- 失败用例必须产出测试事件报告（Test Incident Report）

---

## 并行示例：Phase 4 测试执行

```bash
# 同时启动所有自动化测试用例:
Task: "Execute tests/integration/test_sc01_main.py"
Task: "Execute tests/integration/test_sc01_exception.py"
Task: "Execute tests/integration/test_sc02_main.py"
Task: "Execute tests/integration/test_sc02_concurrent.py"

# 每个用例独立执行，结果汇总至 reports/summary.md
```

---

## 执行策略

### MVP First（仅执行 P0 场景）

1. 完成 Phase 1: 测试环境准备
2. 完成 Phase 2: P0 场景的测试用例编写
3. 完成 Phase 3: P0 场景的自动化代码编写
4. 执行 Phase 4: P0 场景的测试执行
5. **STOP and VALIDATE**：独立验证 P0 场景结果
6. 若通过，输出阶段性报告

### 增量覆盖

1. Phase 1 环境准备 → 基础设施就绪
2. P0 场景执行通过 → 输出阶段性报告（MVP！）
3. 继续 P1 场景的用例编写、自动化、执行
4. 继续 P2 场景的用例编写、自动化、执行
5. 每个场景增加验证范围且不破坏已验证的场景

### 并行团队策略

多人协作时：

1. 团队共同完成 Phase 1: 测试环境准备
2. Phase 2~3 按场景顺序串行编写
3. Phase 4 内所有自动化用例同时并行执行

---

## Notes

- `[P]` 任务 = 不同文件、无依赖关系，可并行执行
- 阶段标签（`[ENV]`, `[CASE-SC-*]`, `[AUTO-SC-*]`, `[EVT-SC-*]`）将任务映射至具体阶段和测试场景以实现可追溯性
- Phase 1~3 为串行依赖，Phase 4 为并行执行
- 执行前确认前置条件与测试数据就绪
- 每个任务或逻辑组执行后记录结果
- 避免：模糊任务、文件冲突、破坏执行顺序的跨阶段依赖
