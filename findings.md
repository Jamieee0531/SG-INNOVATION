# Findings & Decisions

*Last updated: 2026-02-25 — Full project scan*

---

## 产品定位（重新明确，2026-02-25）

**Vision Agent 是多模态 chatbot 的图片处理模块，不是独立产品。**

- 用户发送：图片 + 文字（如"这顿饭健康吗？"）
- Vision Agent 负责：识别图片 → 提取结构化 JSON
- 主 LLM（chatbot）负责：理解用户问题 + Vision 输出 → 生成回复
- Vision Agent **不负责**生成文字建议（health_advisor 节点应移除）
- 数据库存储（对话历史 + 图片识别结果）是后续 chatbot 模块的事，**不在本 Vision Agent 范围内**

## Requirements

- P0: 补剂多成分 schema — `MedicationOutput` 支持 `ingredients: list[Ingredient]`
- P1a: 多图部分失败恢复 — 1张图失败不影响整体，输出记录跳过原因
- P1b: 置信度校准 — Gemini 总是返回 0.98+，需要有区分度
- 真实图片测试集 — 收集 20 张，跑端到端 Gemini 测试
- FoodAI 接入 — 等审批（已申请 2026-02-23）
- **[新] 移除 health_advisor 节点** — SeaLION 文本建议不属于 Vision Agent 职责

---

## 架构概览

### LangGraph 完整流程（8个节点）

```
image_intake → scene_classifier
  → food_analyzer | medication_reader | report_digitizer | rejection_handler
  → health_advisor (SeaLION 文本建议)
  → output_formatter → END
```

### 双模型架构

| 模型 | 角色 | 状态 |
|------|------|------|
| Gemini 2.5 Flash | 视觉理解（所有场景） | ✅ 可用 |
| SeaLION 27B Text | 健康建议文本生成 | ✅ 可用 |
| FoodAI v5.0 | SG 本地食物精准识别 | ⏳ 等审批 |

### State 字段（VisionAgentState）

```python
image_paths: list[str]      # 输入图片路径（支持多图）
images_base64: list[str]    # base64 编码
scene_type: str             # FOOD / MEDICATION / REPORT / UNKNOWN
confidence: float           # 分类置信度
raw_response: str           # VLM 原始返回
structured_output: dict     # 解析后结构化数据
advice: str                 # SeaLION 健康建议
error: Optional[str]        # 错误信息
```

---

## 关键文件清单

| 文件 | 作用 |
|------|------|
| `src/vision_agent/schemas/outputs.py` | Pydantic 输出模型（FoodOutput、MedicationOutput 等）|
| `src/vision_agent/state.py` | VisionAgentState TypedDict 定义 |
| `src/vision_agent/graph.py` | LangGraph 图构建 + 路由逻辑 |
| `src/vision_agent/agent.py` | 对外公开 API（VisionAgent + AnalysisResult）|
| `src/vision_agent/nodes/image_intake.py` | 图片校验 + base64 编码 |
| `src/vision_agent/nodes/medication_reader.py` | 药物分析节点 |
| `src/vision_agent/nodes/output_formatter.py` | 最终校验 + 错误包装 |
| `src/vision_agent/prompts/medication.py` | 药物识别 prompt（SG 优化）|
| `src/vision_agent/llm/base.py` | BaseVLM 抽象接口 |

---

## P0 分析：补剂多成分 Schema

### 现状问题

`MedicationOutput` 当前结构：
```python
drug_name: str          # 只支持一个药名
dosage: str             # 只支持一个剂量
frequency: Optional[str]
route: Optional[str]
warnings: Optional[List[str]]
expiry_date: Optional[str]
confidence: float
```

补剂实际有多成分（如 BioFinest Magnesium）：
- Magnesium 400mg
- Vitamin B6 5mg
- Zinc 10mg

**当前 schema 无法表达多成分结构。**

### 需要修改的文件

| 文件 | 改动内容 |
|------|---------|
| `schemas/outputs.py` | 新增 `Ingredient` 模型，`MedicationOutput` 加 `ingredients: Optional[List[Ingredient]]` |
| `prompts/medication.py` | 更新 prompt，引导 VLM 为补剂输出完整成分列表 |
| `llm/mock.py` | 更新 mock 数据，补剂场景包含 `ingredients` |
| `tests/test_schemas/` | 新增补剂多成分测试 |

### 向后兼容性

- `drug_name` / `dosage` 保留（处方药继续使用）
- `ingredients` 设为 `Optional`，处方药填 `None`，补剂填列表

---

## P1a 分析：多图部分失败恢复

### 现状问题

`image_intake.py` 第 60-63 行：
```python
for img_path in image_paths:
    encoded, err = _validate_and_encode(img_path)
    if err is not None:
        return {"error": err}   # 第一张失败 → 整体返回错误
```

3张图传入，第2张损坏 → 整个请求失败，第1、3张白传。

### 修改方案

收集成功的图片，跳过失败的，在 state 或输出中记录跳过原因：
```python
skipped: [{"index": 1, "path": "...", "reason": "file too large"}]
```

### 影响范围

| 文件 | 改动 |
|------|------|
| `nodes/image_intake.py` | 改为 partial success 逻辑 |
| `schemas/outputs.py` | 可选：各 Output 模型加 `skipped_images` 字段 |
| `tests/test_nodes/` | 更新 image_intake 测试（现有失败测试语义改变）|

---

## P1b 分析：置信度校准

### 现状问题

Gemini 返回的 confidence 几乎全是 0.98~1.0，下游无法用这个值做差异化判断。

### 可选方案（待验证）

1. Prompt 里要求 VLM 返回 top-2 候选 + 各自分数，取差值作为区分度
2. 根据 `null` 字段数量动态下调置信度（字段缺失越多，置信度越低）
3. 启发式规则（图片分辨率、response 字符数等）

### 影响范围

- `prompts/` 所有 4 个 prompt 文件（如果改 prompt 方案）
- `nodes/output_formatter.py`（如果做后处理调整）

---

## 长期路线图（来自 plan.md，待实现）

### Phase 4A+：FoodAI 接入（等待审批）
- 食物场景从 Gemini 切换为 FoodAI（SG 本土，756类 100+本地菜）+ SeaLION 文字建议
- 状态：FoodAI v5.0 Trial 已申请（2026-02-23），等待约 5 工作日审批
- 涉及文件：新建 `llm/foodai.py`、修改 `nodes/food_analyzer.py`、`config.py`

### Phase 4B：营养 MCP 接入（提升食物精度）
- VLM 识别菜名 → MCP Tool 查精确营养值（替代 VLM 估算）
- 推荐：`deadletterq/mcp-opennutrition`（30万+食物，本地运行，无隐私问题）
- 涉及文件：`nodes/food_analyzer.py`、`schemas/outputs.py`（加 data_source 字段）

### Phase 4C：RxNorm 药物验证（免费）
- VLM 提取药名 → RxNorm API 标准化验证
- API：`https://rxnav.nlm.nih.gov/REST/drugs?name=Metformin`（完全免费，20次/秒）
- 涉及文件：新建 `tools/rxnorm.py`、`nodes/medication_reader.py`、`schemas/outputs.py`

### Phase 5：进阶方向（长期/演示）
- NUS FoodSG-233 — 233种SG本地菜数据集（209,861张图片）
- AWS Textract + Comprehend Medical — 报告数字化增强
- HPB FOCOS 本地营养数据库 RAG

---

## 下游协作约定（Section 8，来自 plan.md）

### null 字段 = 图片中该信息不存在（不是识别失败）
下游节点应据此触发用户追问：

| 场景 | 缺失字段 | 下游触发示例 |
|------|---------|------------|
| 药物 | frequency | "这个补剂没有标注服用频次，你通常怎么吃？" |
| 药物 | dosage | "照片上看不清剂量，能确认一下是多少 mg 吗？" |
| 食物 | quantity | "这份看起来是鸡饭，你吃了多少？整份还是半份？" |

### confidence 使用约定
| 值 | 建议下游行为 |
|----|------------|
| ≥ 0.8 | 直接使用，无需确认 |
| 0.5~0.8 | 展示结果但请用户确认 |
| < 0.5 | 不自动使用，主动询问 |

### schema 设计原则
- 字段存在即可信（非 null = VLM 实际识别到）
- null = 信息源本身没有（不是错误）
- scene_type 是路由键，下游可直接 switch

---

## 未来方向（暂不实现，记录思路）

### 提取完整度信号（Completeness Signal）

**背景**：下游 chatbot 需要知道"这次识别质量怎样"，以决定是否直接使用结果或追问用户。

**现有机制**：null 字段已经隐式传递了"信息缺失"的信号（null = 图片中不存在该信息）。

**未来可以增强**：
```json
"missing_fields": ["dosage", "frequency"],  ← 明确列出缺失字段
"completeness": 0.4                          ← 汇总完整度分数
```

**何时做**：等 chatbot 模块开始真正消费 Vision 输出时，再根据实际需求设计。

---

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| `ingredients` 设为 Optional | 向后兼容，处方药不受影响 |
| `drug_name` 保留 | 处方药场景继续用，补剂可填主成分名 |
| P1a 用 partial success | 比整体失败更健壮，符合真实使用场景 |

---

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| image_intake 任一图失败即整体报错 | P1a 待修复 |
| Gemini confidence 无区分度 | P1b 方向已定，策略待定 |

---

## Resources

- `plan.md` — 完整路线图（Section 9 优化方向）
- `src/vision_agent/schemas/outputs.py` — 所有 Pydantic 输出模型
- `src/vision_agent/nodes/image_intake.py` — 多图处理入口

---

*Update this file after every 2 view/browser/search operations*
