# Task Plan: Vision Agent 下一阶段优化

## Goal
清理架构 + 增强 schema + 提升健壮性，使 Vision Agent 成为一个干净的图片处理模块，可嵌入主 chatbot。

## Current Phase
Phase 1

## Phases

---

### Phase 1: 移除 health_advisor 节点（架构清理）
> 对齐新产品定位：Vision Agent 不负责生成文字建议

- [ ] 从 `graph.py` 删除 health_advisor 节点及相关 import
- [ ] 从 `graph.py` 更新边连接（各 analyzer → output_formatter，跳过 health_advisor）
- [ ] 评估 `state.py` 的 `advice` 字段是否保留或删除
- [ ] 更新相关测试（pipeline 全流程测试）
- **复杂度**: 低
- **影响文件**: `graph.py`, `state.py`(可能), `agent.py`(可能), `tests/`
- **Status:** complete ✅

---

### Phase 2: P0 — 补剂多成分 Schema
> 当前 MedicationOutput 只有单一 drug_name + dosage，无法表达补剂的多成分结构

- [ ] `schemas/outputs.py`：新增 `Ingredient` 模型（name + amount 字段）
- [ ] `schemas/outputs.py`：`MedicationOutput` 加 `ingredients: Optional[List[Ingredient]]`
- [ ] `prompts/medication.py`：更新 prompt，引导 VLM 为补剂输出完整成分列表
- [ ] `llm/mock.py`：新增补剂场景 mock 数据（含 ingredients）
- [ ] `tests/`：新增补剂多成分测试，确保旧处方药测试仍通过
- **复杂度**: 中
- **影响文件**: `schemas/outputs.py`, `prompts/medication.py`, `llm/mock.py`, `tests/`
- **向后兼容**: `drug_name` / `dosage` 保留，`ingredients` 为 Optional
- **Status:** complete ✅

---

### Phase 3: P1a — 多图部分失败恢复
> 当前 image_intake 任一图失败即整体报错，3张图传入1张坏了全部失败

- [ ] `nodes/image_intake.py`：改为 partial success 逻辑（收集成功的图，跳过失败的）
- [ ] 在返回 state 中记录跳过信息：`skipped_images: [{"index": 1, "reason": "..."}]`
- [ ] 至少1张成功才继续，全部失败才报错
- [ ] 更新 `tests/test_nodes/`（原有失败测试的语义发生变化）
- **复杂度**: 中
- **影响文件**: `nodes/image_intake.py`, `tests/test_nodes/`
- **Status:** complete ✅

---

### Phase 4: P1b — 置信度校准（策略待定）
> Gemini 总是返回 0.98+，confidence 字段对下游没有实际区分度

- [ ] 收集更多真实图片测试数据（先跑 Gemini，观察真实输出）
- [ ] 根据结果选择校准策略（候选：null 字段计数 / top-2 候选对比 / 启发式规则）
- [ ] 实现选定策略
- [ ] 验证 confidence 分布有区分度
- **复杂度**: 未知（依赖真实测试数据）
- **影响文件**: `prompts/`（4个）或 `nodes/output_formatter.py`（取决于策略）
- **Status:** complete ✅ (null 字段计数法，最大 25% 惩罚，后续可根据真实数据调整)

---

---

### Phase 5: 文档迁移（plan.md → 三文件体系）
> 筛选 plan.md 中仍有价值的内容，按格式要求分别写入对应文件，完成后删除 plan.md

原则：**不是照搬，是筛选后整合**。只迁移有用的、新的信息，内容需符合各文件的定位与格式。

- [ ] 筛选 plan.md 中仍有参考价值的内容（跳过已过时、已体现在代码里的部分）
- [ ] 有用的历史记录（完成了什么、踩过什么坑）→ `progress.md`（session log 格式）
- [ ] 长期路线图、下游协作约定（Section 8）、未解决的技术问题 → `findings.md`（research/decisions 格式）
- [ ] 业务背景如有新内容 → `CLAUDE.md`（保持简短）
- [x] 筛选 plan.md 中仍有参考价值的内容
- [x] 长期路线图、下游协作约定 → `findings.md`
- [x] 历史完成记录 → `progress.md`
- [x] 业务背景 → `CLAUDE.md`（一行简短说明）
- [x] 确认无遗漏后删除 `plan.md`
- **复杂度**: 低（纯文档整理）
- **Status:** complete ✅（plan.md 暂保留，等 Jamie 确认删除）

---

## 执行顺序说明

```
Phase 1（移除 health_advisor）← 独立，最快，先做
    ↓
Phase 2（补剂 schema）        ← 独立，优先级最高，第二做
    ↓
Phase 3（多图恢复）           ← 独立，第三做
    ↓
Phase 4（置信度校准）         ← 依赖真实测试数据，最后做
    ↓
Phase 5（文档迁移）           ← 随时可做，不依赖代码
```

Phase 1-3 互相独立，顺序可调整。Phase 4 需要先跑真实图片才能定策略。Phase 5 随时可穿插进行。

---

## Key Questions
1. `state.py` 的 `advice` 字段：Phase 1 时删掉还是保留备用？
2. Phase 4 校准策略：优先用哪种方案？（等真实测试后再定）

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Phase 1 先做 | 架构清理，影响小，快速对齐新产品定位 |
| ingredients 设为 Optional | 向后兼容，处方药不受影响 |
| Phase 4 最后做 | 依赖数据，策略未定 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| — | — | — |

## Notes
- 每个 Phase 完成后跑 `make test` 确保覆盖率不低于 95%
- 动代码前必须经过 human-in-the-loop 确认
