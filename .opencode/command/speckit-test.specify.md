---
description: 根据自然语言测试特性描述，创建或更新测试规格说明。
handoffs: 
  - label: 构建技术计划
    agent: speckit-test.plan
    prompt: Create a plan for the spec. I am building with...
  - label: 澄清规格需求
    agent: speckit-test.clarify
    prompt: Clarify specification requirements
    send: true
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前，你 **MUST** 考虑用户输入（如果不为空）。

## 概要

用户在触发消息中 `/speckit-test.specify` 之后输入的文本 **就是** 特性描述。即使下方 `$ARGUMENTS` 以字面形式出现，你也应始终假设它在此对话中可用。除非用户提供了空命令，否则不要要求用户重复。

给定该特性描述，执行以下操作：

1. **生成简洁的短名称**（2-4 个词）：
   - 分析特性描述并提取最有意义的关键词
   - 创建一个 2-4 词的短名称，捕捉特性的核心
   - 尽可能使用 action-noun 格式（如 "add-user-auth"、"fix-payment-bug"）
   - 保留技术术语和缩写（OAuth2, API, JWT 等）
   - 保持简洁但足够描述性，以便一目了然地理解特性
   - 示例：
     - "我想添加用户认证" → "user-auth"
     - "实现 API 的 OAuth2 集成" → "oauth2-api-integration"
     - "创建数据分析面板" → "analytics-dashboard"
     - "修复支付处理超时 bug" → "fix-payment-timeout"

2. **创建规格特性目录**：

   规格文件默认存放在 `specs/` 目录下，除非用户明确提供了 `SPECIFY_FEATURE_DIRECTORY`。

   **`SPECIFY_FEATURE_DIRECTORY` 的解析顺序**：
   1. 如果用户明确提供了 `SPECIFY_FEATURE_DIRECTORY`（如通过环境变量、参数或配置），直接使用
   2. 否则，在 `specs/` 下自动生成：
      - 检查 `.specify/init-options.json` 中的 `branch_numbering`
      - 如果是 `"timestamp"`：前缀为 `YYYYMMDD-HHMMSS`（当前时间戳）
      - 如果是 `"sequential"` 或不存在：前缀为 `NNN`（扫描 `specs/` 中已有目录后的下一个 3 位数字）
      - 构造目录名：`<prefix>-<short-name>`（如 `003-user-auth` 或 `20260319-143022-user-auth`）
      - 将 `SPECIFY_FEATURE_DIRECTORY` 设置为 `specs/<目录名>`

   **创建目录和规格文件**：
   - `mkdir -p SPECIFY_FEATURE_DIRECTORY`
   - 将 `.specify/templates/spec-template.md` 复制到 `SPECIFY_FEATURE_DIRECTORY/spec.md` 作为起点
   - 将 `SPEC_FILE` 设置为 `SPECIFY_FEATURE_DIRECTORY/spec.md`
   - 将解析的路径持久化到 `.specify/feature.json`：
     ```json
     {
       "feature_directory": "<resolved feature dir>"
     }
     ```
     写入实际解析的目录路径值（如 `specs/003-user-auth`），而不是字面字符串 `SPECIFY_FEATURE_DIRECTORY`。
     这使得下游命令（`/speckit-test.plan`、`/speckit-test.tasks` 等）能够定位特性目录，而无需依赖 git 分支名约定。

   **IMPORTANT**：
   - 每次 `/speckit-test.specify` 调用只能创建一个特性

3. 加载 `.specify/templates/spec-template.md` 以了解必需的章节。

4. 标注测试类型：
    1. 从用户描述中识别本次规格所属的测试类型
    2. 在规格文件头部标注测试类型（功能测试 / 性能测试 / 安全测试 / 兼容性测试 / 回归测试等）
    3. 根据测试类型调整后续内容生成策略

5. 遵循此执行流程：
    1. 从参数解析用户描述
       如果为空：ERROR "No feature description provided"
    2. 从描述中提取关键概念
       识别：actors, actions, data, constraints
    3. 对于不清晰的方面：
       - 根据上下文和行业标准进行有根据的猜测
       - 仅在以下条件满足时标记为 `[NEEDS CLARIFICATION: 具体问题]`：
         - 该选择显著影响特性范围或用户体验
         - 存在多种合理的解释且含义不同
         - 不存在合理的默认值
       - **限制：最多 3 个 `[NEEDS CLARIFICATION]` 标记**
       - 按影响优先级排序澄清：scope > security/privacy > user experience > technical details
    4. 填写 User Scenarios & Testing 部分
       如果没有清晰的用户流程：ERROR "Cannot determine user scenarios"
    5. 生成功能需求
       每个需求必须是可测试的
       对未指定的细节使用合理的默认值（在 Assumptions 部分记录假设）
    6. 定义 Success Criteria
       创建可衡量的、从用户行为视角 + 系统行为视角双轨验证的标准
       包括定量指标（时间、性能、容量）和定性指标（用户满意度、任务完成率、系统正确性）
       用户行为视角：用户能否完成预期的业务目标和操作路径
       系统行为视角：系统在给定输入、状态或并发条件下的可验证行为
       每个标准必须在不涉及实现细节的情况下可验证
    7. 识别 Key Entities（如果涉及数据）
    8. 返回：SUCCESS（规格说明已就绪，可进行 planning）

6. 使用模板结构将规格说明写入 `SPEC_FILE`，用从特性描述（参数）派生的具体细节替换占位符，同时保持章节顺序和标题。

7. **规格质量验证**：编写初始规格说明后，根据质量标准进行验证：

    a. **创建规格质量检查清单**：在 `SPECIFY_FEATURE_DIRECTORY/checklists/requirements.md` 生成检查清单文件，使用检查清单模板结构，包含以下验证项：

      ```markdown
      # Specification Quality Checklist: [FEATURE NAME]
      
      **Purpose**: Validate test specification completeness and quality before proceeding to planning
      **Created**: [DATE]
      **Feature**: [Link to spec.md]
      **Test Type**: [功能测试/性能测试/安全测试/兼容性测试/回归测试]
      
      ## Content Quality
      
      - [ ] 测试类型已明确标注
      - [ ] 聚焦于被测功能的行为验证和结果判定
      - [ ] 面向测试工程师和质量保障人员编写
      - [ ] 所有必填章节已完成
      
      ## Requirement Completeness
      
      - [ ] No [NEEDS CLARIFICATION] markers remain
      - [ ] 需求的测试场景和验收标准可执行且无歧义
      - [ ] 成功标准可衡量（包含用户行为视角 + 系统行为视角）
      - [ ] 所有异常分支和边界情况已识别
      - [ ] 测试范围已明确界定
      - [ ] 前置条件、依赖项和假设已识别
      
      ## Feature Readiness
      
      - [ ] 所有测试场景有明确的预期输出和判定标准
      - [ ] 主流程和异常流程均已定义
      - [ ] 功能满足 Success Criteria 中定义的可衡量结果
      - [ ] 测试规格中不包含具体的实现代码或工具选型
      
      ## Notes
      
      - Items marked incomplete require spec updates before `/speckit-test.clarify` or `/speckit-test.plan`
      ```

   b. **执行验证检查**：逐条审查规格说明是否符合检查清单：
      - 对每一项，判定通过或不通过
      - 记录发现的具体问题（引用相关规格章节）

   c. **处理验证结果**：

      - **如果全部通过**：标记检查清单完成，进入第 7 步

      - **如果有项目不通过（不含 `[NEEDS CLARIFICATION]`）**：
        1. 列出不通过项及具体问题
        2. 更新规格以解决每个问题
        3. 重新运行验证直到全部通过（最多 3 次迭代）
        4. 如果 3 次后仍未通过，在检查清单备注中记录剩余问题并警告用户

      - **如果有 `[NEEDS CLARIFICATION]` 标记遗留**：
        1. 提取规格中所有 `[NEEDS CLARIFICATION: ...]` 标记
        2. **数量检查**：如果超过 3 个标记，仅保留最关键的 3 个（按 scope/security/UX 影响排序），其余做有根据的猜测
        3. 对每个需要澄清的问题（最多 3 个），以下列格式向用户呈现选项：

           ```markdown
           ## Question [N]: [Topic]
           
           **Context**: [Quote relevant spec section]
           
           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]
           
           **Suggested Answers**:
           
           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [第一个建议答案] | [这对特性意味着什么] |
           | B      | [第二个建议答案] | [这对特性意味着什么] |
           | C      | [第三个建议答案] | [这对特性意味着什么] |
           | Custom | 提供你自己的答案 | [说明如何提供自定义输入] |
           
           **Your choice**: _[Wait for user response]_
           ```

        4. **CRITICAL - 表格格式**：确保 markdown 表格正确格式化：
           - 使用一致的间距，管道符对齐
           - 每个单元格内容周围应有空格：`| Content |` 而非 `|Content|`
           - 表头分隔符必须至少包含 3 个破折号：`|--------|`
           - 测试表格是否能在 markdown 预览中正确渲染
        5. 按顺序编号问题（Q1, Q2, Q3 - 最多 3 个）
        6. 在等待回复前一次性呈现所有问题
        7. 等待用户回复所有问题的选择（如 "Q1: A, Q2: Custom - [details], Q3: B"）
        8. 用用户选择或提供的答案替换每个 `[NEEDS CLARIFICATION]` 标记
        9. 所有澄清解决后重新运行验证

   d. **更新检查清单**：每次验证迭代后，更新检查清单文件中的当前通过/失败状态

7. **向用户报告完成情况**：
   - `SPECIFY_FEATURE_DIRECTORY` — 特性目录路径
   - `SPEC_FILE` — 规格文件路径
   - 检查清单结果摘要
   - 下一阶段的就绪状态（`/speckit-test.clarify` 或 `/speckit-test.plan`）

## 快速指南

- 聚焦被测功能的 **WHAT** 行为和 **WHY** 验证。
- 避免涉及 HOW 实现（无 tech stack, APIs, code structure）。
- 面向测试工程师和质量保障人员编写，而非 developers。
- DO NOT 创建嵌入在规格说明中的任何检查清单。这将是单独的命令。

### 章节要求

- **必填章节**：每个特性都必须完成
- **可选章节**：仅在相关时包含
- 当某个章节不适用时，完全删除它（不要留 "N/A"）

### AI 生成指南

从用户提示创建此规格说明时：

1. **做有根据的猜测**：使用上下文、行业标准和常见模式填补空白
2. **记录假设**：在 Assumptions 部分记录合理的默认值
3. **限制澄清数量**：最多 3 个 `[NEEDS CLARIFICATION]` 标记 - 仅用于关键决策：
   - 显著影响特性范围或用户体验
   - 存在多种合理暗示不同的解释
   - 缺乏任何合理默认值
4. **澄清优先级**：scope > security/privacy > user experience > technical details
5. **像测试人员一样思考**：每个模糊需求都应该在 "testable and unambiguous" 检查清单项中失败
6. **常见需要澄清的领域**（仅在不存在合理默认值时）：
   - 特性范围和边界（包含/排除特定用例）
   - 用户类型和权限（如果存在多种冲突解释）
   - 安全/合规要求（当涉及法律/财务重要性时）

**合理默认值示例**（不要询问这些）：

- 数据保留：行业标准的领域实践
- 性能目标：标准 Web/移动应用期望，除非另有说明
- 错误处理：用户友好的消息和适当的回退机制
- 认证方法：标准基于会话或 OAuth2 的 Web 应用
- 集成模式：使用项目适当的模式（REST/GraphQL for web services, function calls for libraries, CLI args for tools 等）

### Success Criteria 指南

Success criteria 必须：

1. **Measurable**：包含具体指标（时间、百分比、计数、速率）
2. **Technology-agnostic**：不提及 frameworks, languages, databases, 或 tools
3. **双轨视角**：从用户行为视角（能否完成业务目标）和系统行为视角（输出是否正确可验证）描述结果
4. **Verifiable**：无需了解实现细节即可测试/验证

**好示例**：

- "用户可在 3 分钟内完成结账"
- "系统支持 10,000 并发用户"
- "95% 的搜索在 1 秒内返回结果"
- "任务完成率提升 40%"
- "批量规格变更后，所有实例状态在 5 分钟内同步"

**坏示例**（面向实现）：

- "API 响应时间低于 200ms"（过于技术化，用 "用户立即看到结果"）
- "数据库可处理 1000 TPS"（实现细节，用面向用户的指标）
- "React 组件高效渲染"（框架特定）
- "Redis 缓存命中率高于 80%"（技术特定）
