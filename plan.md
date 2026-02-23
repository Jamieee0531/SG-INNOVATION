# 🏥 Project: AI-Powered Chronic Disease Management & Community Platform

## 1. 项目背景与目标 (Project Overview)

**背景 (Context):**
新加坡正面临人口老龄化与慢病高发的挑战（如 2型糖尿病）。现有的医疗资源紧张，且患者在院外的依从性（Medication Adherence）、生活方式管理（Lifestyle Management）较差。

**核心用户画像 (Persona):**
*   **Mr. Tan (60s)**: 患有多种慢病，容易忘记复诊和吃药。
*   **Caregivers**: 需要协助照护的家人/护工。

**核心价值 (Value Proposition):**
打造一个结合 **"病友社区 (Community)"** + **"AI 智能体 (Agentic AI)"** 的平台。不仅提供医疗支持，更通过游戏化社交（偷能量、积分兑换）提升患者的参与度。

---

## 2. 系统设计蓝图 (System Architecture)

### 核心假设 (Assumptions)
*   **硬件支持**: 依赖 Sensor + Apple Watch。
*   **数据流**: 可获取连续性的血糖记录 (Readings)、心率、GPS 位置信息。

### 业务逻辑 (Business Logic)
1.  **社交与激励**:
    *   个人/家庭群组共享健康数据。
    *   **游戏化**: 每日步数 + 三餐打卡 + 每日一题 -> 获取积分。
    *   **交互**: 好友间"偷能量"，积分兑换现实奖励。
2.  **任务系统**:
    *   **初始任务**: 设置 Preference（复诊时间、注射单位、每三月提醒更新）。
    *   **日常任务**: 由任务 Agent 自动调度。

### 智能体架构 (Agent Framework)
*   **群组层**:
    *   👨‍⚕️ **医学专家 Agent**: 提供专业级别的护理建议。
*   **个人层**:
    *   🧠 **中央大脑 (Router)**: 负责分诊用户输入（语音/文字/图片）。
    *   💞 **护理 Agent**: 提供心理情绪陪伴，处理主动问询。
    *   📋 **任务发布 Agent**: 根据过往行为调度任务（如打卡点）。
    *   ⚠️ **预警 Agent**: 结合【过往记录 + 实时数据 + **饮食/图片上传** + 聊天记录】进行预测性预警。

---

## 3. 我的职责 (My Role)

> [!IMPORTANT]
> **负责模块**: **多模态 Agent —— 图片输入与处理 (Multimodal Vision Agent)**
> **核心目标**: 让系统具备"视觉"，将非结构化的图片转化为可计算的结构化数据。

在此阶段，**暂不考虑与其他 Agent 的接口对接**，核心在于实现图片内容的准确识别与结构化输出。

### 核心场景 (Key Scenarios)

1.  **🥗 饮食打卡分析 (Dietary Analysis)**
    *   **输入**: 用户上传的一日三餐照片（如海南鸡饭、Kopi C）。
    *   **输出**: 识别食物成分、估算份量、计算卡路里/碳水/GI值。
2.  **💊 药物/处方核查 (Medication Verification)**
    *   **输入**: 药盒、处方单、胰岛素笔刻度。
    *   **输出**: 提取药名、剂量、频次、当前注射刻度（用于校准 Preference）。
3.  **📄 医疗报告数字化 (Report Digitization)**
    *   **输入**: 纸质化验单、检查报告。
    *   **输出**: 提取关键指标数据（如 HbA1c, 血糖值），用于存入系统记录。

---

## 4. 行动计划 (Action Plan)

### ✅ Phase 1: 技术选型与环境搭建 — 已完成

- [x] 确定框架：**LangGraph** (状态图编排) + **Python 3.10**
- [x] 确定 VLM 策略：**Gemini 2.5 Flash**（临时 VLM）→ **FoodAI + SEA-LION VL**（目标方案）
- [x] 搭建本地 Python venv 环境，安装全部依赖
- [x] 初始化 git 仓库，建立项目目录结构

### ✅ Phase 2: Prompt Engineering (核心) — 已完成

- [x] **场景分类 Prompt** (`prompts/classifier.py`)：FOOD / MEDICATION / REPORT / UNKNOWN 四分类
- [x] **食物分析 Prompt** (`prompts/food.py`)：含 50+ 新加坡本地菜名、HPB 营养数据上下文
- [x] **药物识别 Prompt** (`prompts/medication.py`)：含 SG 常见慢病药物、HSA 标签规范、BD/OD/TDS/PRN 频次解析
- [x] **报告数字化 Prompt** (`prompts/report.py`)：含 MOH/HPB 参考值范围、新加坡主要医院格式
- [x] 所有 Prompt 约束输出为严格 JSON 格式

### ✅ Phase 3: 功能实现 — 已完成

- [x] **LangGraph 状态图** (`graph.py`)：完整 START→intake→classify→analyze→format→END 流程
- [x] **7 个节点** (`nodes/`)：image_intake, scene_classifier, food/medication/report analyzer, rejection_handler, output_formatter
- [x] **Pydantic v2 输出校验** (`schemas/outputs.py`)：FoodOutput, MedicationOutput, ReportOutput, UnknownOutput
- [x] **VLM 抽象接口** (`llm/base.py`)：模型可替换，SEA-LION 只是一个实现
- [x] **MockVLM** (`llm/mock.py`)：4 食物 / 4 药物 / 3 报告场景，含真实新加坡数据
- [x] **RetryVLM** (`llm/retry.py`)：指数退避重试包装器
- [x] **VisionAgent API** (`agent.py`)：`agent.analyze(image_path)` → 类型化 AnalysisResult
- [x] **CLI 入口** (`__main__.py`)：`python -m src.vision_agent image.jpg [--json] [--provider]`
- [x] **配置管理** (`config.py`)：pydantic-settings，从 `.env` 读取
- [x] **异常处理**：模糊图片/非目标图片 → UNKNOWN，错误统一走 output_formatter

### 🔄 Phase 4: 测试与真实 API 接入 — 进行中

- [x] **Mock 测试**: 156 个测试用例，99%+ 覆盖率，全部通过
- [x] **参数化测试**: 所有场景的每个 Mock 变体均通过 schema 验证
- [x] **Gemini VLM 接入**: `llm/gemini.py` — Gemini 2.5 Flash 作为临时 VLM（已验证可用）
- [x] **SEA-LION 文本接入**: `llm/sealion.py` — Gemma-SEA-LION-v4-27B-IT 文本模型（已验证可用）
- [ ] **真实图片测试**: 收集 20 张图片，用 Gemini 跑端到端测试
- [ ] **Prompt 优化**: 根据 Gemini 真实输出迭代 prompt
- [ ] **准确率评估**: 识别 10-20 张典型图片（含模糊、复杂食物、手写单据）

---

## 5. VLM 策略与演进路线

### 当前状态

> **SEA-LION API 已拿到，但仅提供文本模型（无 VL 视觉模型）。FoodAI 试用版已申请，等待审批。**

**当前方案（已跑通）：**
```
三个场景统一使用 Gemini 2.5 Flash（临时 VLM）
  图片 → Gemini Vision（识别+分析）→ 结构化 JSON 输出
```

**目标方案（FoodAI + SEA-LION 审批通过后切换）：**
```
食物场景：
  图片 → FoodAI API（"眼睛"：SG 食物识别，756类，100+本地菜）
       → SEA-LION 27B Text（"大脑"：本土化饮食建议，懂 Singlish）

药物/报告场景：
  图片 → SEA-LION VL（等 API 开放）或继续用 Gemini
       → SEA-LION 27B Text（分析建议）
```

**核心逻辑**：FoodAI 做"眼睛"（精准识别新加坡本地食物），SeaLION 做"大脑"（本土化理解与建议）。

### 模型可用性

| Provider | Model | Status | 用途 |
|----------|-------|--------|------|
| `mock` | MockVLM | ✅ 可用 | 开发/测试，无 API 调用 |
| `gemini` | Gemini 2.5 Flash | ✅ 可用 | **当前临时 VLM**（Vision + 文本） |
| `sealion` | Gemma-SEA-LION-v4-27B-IT | ✅ 可用 | 纯文本分析/建议 |
| `foodai` | FoodAI v5.0 (SMU/HPB) | ⏳ 已申请 | SG 食物专精识别（等审批，约 5 工作日） |
| `sealion-vl` | Qwen-SEA-LION-v4-8B-VL | ❌ API 未开放 | 目标 VLM（需等 AI Singapore 开放 VL 模型 API） |

### 切换计划

**Step 1（现在）**：用 Gemini 2.5 Flash 跑通所有场景，收集测试图片，优化 Prompt

**Step 2（FoodAI 审批通过后）**：
- 新建 `llm/foodai.py`，实现 FoodAI API 客户端
- 食物场景切换为：FoodAI 识别 → SeaLION 文本分析
- 药物/报告场景继续用 Gemini

**Step 3（SEA-LION VL API 开放后）**：
- 药物/报告场景切换为 SEA-LION VL
- 全面去除 Gemini 依赖，完全使用新加坡本土 AI 生态

### 下一步行动（顺序执行）

**Step 1: 真实图片测试集**
- 收集 20 张图片放入 `test_images/`：
  - 🥗 食物：5 张新加坡小贩食物（海南鸡饭、椰浆饭、炒粿条、罗惹、肉骨茶）
  - 💊 药物：5 张（处方单、胰岛素笔、药盒）
  - 📄 报告：5 张（血液检查、综合体检报告、血糖记录）
  - ❓ 非目标：5 张（自拍、风景、随机物品）用于测试拒识

**Step 2: Prompt 优化迭代**
- 用 `make run-gemini IMG=xxx.jpg` 逐张测试
- 根据真实输出，针对性调整 prompt
- 重点关注：模糊图、手写处方、复杂背景食物

**Step 3: 定义对外接口（配合团队）**
- 与其他模块成员确认 JSON 输出格式是否符合他们的需求
- 如需要，在 `schemas/outputs.py` 中调整字段

---

## 6. 技术参考

### 当前目录结构

```
SG_INNOVATION/
├── README.md              # 项目说明 + 操作指南
├── CLAUDE.md              # AI 开发规范
├── plan.md                # 本文件
├── Makefile               # make test / make run-gemini / etc.
├── requirements.txt       # 依赖清单
├── .env.example           # 环境变量模板（复制为 .env 填入真实 key）
├── src/vision_agent/
│   ├── agent.py           # ← 对外接口：VisionAgent.analyze()
│   ├── graph.py           # LangGraph 状态图
│   ├── state.py           # 共享状态定义
│   ├── config.py          # 配置（读 .env）
│   ├── llm/               # VLM 接口层（base/gemini/sealion/mock/retry）
│   ├── nodes/             # 7 个处理节点
│   ├── prompts/           # 4 个 SG 优化 Prompt
│   └── schemas/           # Pydantic 输出模型
└── tests/                 # 156 个测试，99%+ 覆盖率
```

### 快速命令

```bash
source .venv/bin/activate                                       # 激活虚拟环境
make test                                                       # 跑所有测试
make coverage                                                   # 测试 + 覆盖率报告
make run IMG=xxx.jpg                                            # 用 Mock 分析图片
make run-gemini IMG=xxx.jpg                                     # 用 Gemini 真实 VLM 分析
python -m src.vision_agent xxx.jpg --provider gemini --json     # CLI + JSON 输出
```

> [!TIP]
> **判断成功的标准**: 给一张新加坡鸡饭照片，输出 `{"scene_type": "FOOD", "items": [{"name": "Hainanese Chicken Rice", ...}], "total_calories_kcal": 480}` — 数据能直接喂给预警 Agent 做血糖预测。

---

## 7. 优化路线图 (Optimization Roadmap)

> 基于调研，以下是已发现的可整合外部资源和优化方向。

### ✅ Phase 4A：接入真实 VLM — 已完成

**目标**：用真实 VLM 替代 MockVLM，端到端跑通

**结果**：
- SEA-LION API 已拿到，但**仅提供文本模型**（无 VL 视觉模型）
- 改用 **Gemini 2.5 Flash** 作为临时 VLM，三个场景均可用
- SEA-LION 27B 文本模型已对接，可做文本分析/建议
- `llm/gemini.py`、`llm/sealion.py` 均已实现并验证

> [!NOTE]
> AI Singapore 已发布视觉语言版本：`Qwen-SEA-LION-v4-4B-VL` 和 `Qwen-SEA-LION-v4-8B-VL`
> 但目前 API 未开放 VL 模型。等 API 开放后可切换。

---

### 🔄 Phase 4A+：接入 FoodAI（食物场景升级）— 等待审批

**目标**：食物场景从 Gemini 切换为 FoodAI（SG 本土专精） + SeaLION（文本建议）

**状态**：FoodAI v5.0 Trial 版已申请（2026-02-23），等待审批（约 5 工作日）

**切换后架构**：
```
当前：图片 → Gemini（通用 VLM 识别+分析）→ FoodOutput
升级：图片 → FoodAI（精准 SG 食物识别）→ SeaLION 27B（本土化分析建议）→ FoodOutput
```

**步骤**：
1. ⏳ 等待 FoodAI 审批通过，获取 API key
2. 新建 `llm/foodai.py`，实现 FoodAI API 客户端
3. 修改 `food_analyzer` 节点，串联 FoodAI → SeaLION
4. 对比 Gemini vs FoodAI 在 SG 本地菜上的识别准确率

**涉及文件**：新建 `llm/foodai.py`、`nodes/food_analyzer.py`、`config.py`

---

### Phase 4B：接入营养数据 MCP（提升食物精度）

**目标**：VLM 负责"看"（识别菜名），MCP 负责"查"（精确营养值）

```
当前：图片 → VLM → VLM 估算卡路里 → FoodOutput
优化：图片 → VLM（识别菜名+份量）→ MCP Tool（查精确营养）→ FoodOutput
```

**可用 Nutrition MCP Server**：

| MCP Server | 数据库 | 免费? | 特点 |
|---|---|---|---|
| `deadletterq/mcp-opennutrition` | 30 万+ 食物 | 免费开源 | 100% 本地运行，无隐私问题 |
| `MCP-Forge/nutritionix-mcp-server` | 190 万食物 | 需 API key | 自然语言查询，最成熟 |
| `domdomegg/openfoodfacts-mcp` | 400 万+ 产品 | 完全免费 | 含 Nutri-Score、NOVA 等级 |
| `neonwatty/food-tracker-mcp` | USDA 7000+ | 免费开源 | 轻量本地运行 |

**步骤**：
1. 选择并安装一个 Nutrition MCP Server（推荐 `mcp-opennutrition`）
2. 在 `food_analyzer` 节点中新增 Tool 调用：VLM 识别菜名 → MCP 查营养值
3. 更新 `FoodOutput` schema，新增 `data_source` 字段（`"vlm_estimate"` / `"database"`）
4. MCP 无结果时 fallback 到 VLM 原始估算

**涉及文件**：`nodes/food_analyzer.py`、`schemas/outputs.py`、`prompts/food.py`

---

### Phase 4C：接入 RxNorm API（药物验证，免费）

**目标**：VLM 从药盒图提取文字后，用 RxNorm 验证和标准化药名

```
当前：图片 → VLM → 直接输出药名/剂量
优化：图片 → VLM（提取药名文字）→ RxNorm API（标准化验证）→ MedicationOutput
```

**RxNorm API**（美国国家医学图书馆）：
- 完全免费，无需授权，20 次/秒
- 查询：`https://rxnav.nlm.nih.gov/REST/drugs?name=Metformin`
- 返回标准化药名、剂量、剂型、RxCUI 编码

**步骤**：
1. 新建 `tools/rxnorm.py`，封装 RxNorm REST API
2. 在 `medication_reader` 节点中调用 RxNorm 验证
3. 更新 `MedicationOutput` schema，新增 `rxnorm_cui`、`verified` 字段

**涉及文件**：新建 `tools/rxnorm.py`、`nodes/medication_reader.py`、`schemas/outputs.py`

---

### Phase 5：进阶优化（长期方向 / 演示展望）

#### 5A. NUS FoodSG-233 — 备选 SG 食物数据集

- **NUS Food.lg / FoodSG-233**：233 种新加坡本地菜，209,861 张图片
  - 联系：[foodlg.comp.nus.edu.sg](https://foodlg.comp.nus.edu.sg/)
  - 注：FoodAI (SMU/HPB) 已提升至 Phase 4A+，作为主要食物识别方案

#### 5B. AWS Textract + Comprehend Medical — 报告数字化增强

- Textract 提取化验单表格 → Comprehend Medical 识别医学实体
- AWS 有完整参考实现：`aws-samples/amazon-textract-and-comprehend-medical-document-processing`

#### 5C. HPB FOCOS 本地营养数据库 — RAG

- 爬取/申请 HPB FOCOS 数据（[focos.hpb.gov.sg](https://focos.hpb.gov.sg/eservices/ENCF/)）
- 构建本地向量数据库，对新加坡本地菜实现 100% 精确营养匹配

#### 5D. 医疗 MCP Server

| MCP Server | 提供什么 |
|---|---|
| `Cicatriiz/healthcare-mcp-public` | FDA 药物、PubMed、RxNorm、ICD-10、临床试验 |
| `JamesANZ/medical-mcp` | FDA + WHO + PubMed + RxNorm |

---

### 优先级排序

| 阶段 | 内容 | 优先级 | 状态 | 依赖 |
|---|---|---|---|---|
| 4A | 真实 VLM 接入 (Gemini + SeaLION) | 🔴 最高 | ✅ 已完成 | — |
| 4A+ | FoodAI 接入（食物场景升级） | 🔴 最高 | ⏳ 等审批 | FoodAI API key |
| 4B | 营养 MCP 接入 | 🟡 高 | 待开始 | 可与 4A+ 并行 |
| 4C | RxNorm 药物验证 | 🟡 高 | 待开始 | 可与 4B 并行 |
| 5A | NUS FoodSG 备选数据集 | 🟢 中 | 待定 | API 授权 |
| 5B | AWS 报告提取 | 🟢 中 | 待定 | AWS 账号 |
| 5C | HPB FOCOS RAG | 🟢 低 | 待定 | 数据获取 |

### 验证方式

- **4A**：`make run-gemini IMG=test_images/chicken_rice.jpg` 输出合理 JSON ✅
- **4A+**：FoodAI 识别准确率 > Gemini（SG 本地菜）
- **4B**：食物输出包含 `"data_source": "database"`，营养值与 HPB 一致
- **4C**：药物输出包含 `"verified": true` 和 `rxnorm_cui`
- 所有阶段：`make test` 全部通过，覆盖率保持 95%+
