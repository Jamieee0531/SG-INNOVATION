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
- [x] 确定 VLM：**SEA-LION API**（主办方提供，开发阶段用 MockVLM 替代）
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

### 🔄 Phase 4: 测试与验证 — 进行中

- [x] **Mock 测试**: 155 个测试用例，99.3% 覆盖率，全部通过
- [x] **参数化测试**: 所有场景的每个 Mock 变体均通过 schema 验证
- [ ] **真实图片测试** ← 等待 SEA-LION API（见 Phase 5）
- [ ] **准确率评估**: 识别 10-20 张典型图片（含模糊、复杂食物、手写单据）

---

## 5. 🚧 下一步行动 (Next Steps)

> **当前唯一阻塞点：SEA-LION API 访问凭据**

### 拿到 API 后，立刻做（顺序执行）：

**Step 1: 接入 SEA-LION（预计 30 分钟）**
```bash
# 填写 .env 文件
SEALION_API_KEY=<主办方提供的 key>
SEALION_API_URL=<主办方提供的 endpoint>
```
- 确认 `llm/sealion.py` 中的请求格式与官方文档一致（字段名、认证方式）
- 运行：`python -m src.vision_agent test_images/xxx.jpg --provider sealion`

**Step 2: 真实图片测试集（预计 1-2 天）**
- 收集 20 张图片放入 `test_images/`：
  - 🥗 食物：5 张新加坡小贩食物（海南鸡饭、椰浆饭、炒粿条、罗惹、肉骨茶）
  - 💊 药物：5 张（多克隆卡、处方单、胰岛素笔、药盒）
  - 📄 报告：5 张（血液检查、综合体检报告、血糖记录）
  - ❓ 非目标：5 张（自拍、风景、随机物品）用于测试拒识

**Step 3: Prompt 优化迭代（预计 2-3 天）**
- 根据真实输出，针对性调整 prompt
- 重点关注：模糊图、手写处方、复杂背景食物

**Step 4: 定义对外接口（配合团队）**
- 与其他模块成员确认 JSON 输出格式是否符合他们的需求
- 如需要，在 `schemas/outputs.py` 中调整字段

---

## 6. 技术参考

### 当前目录结构

```
SG_INNOVATION/
├── CLAUDE.md              # AI 开发规范
├── plan.md                # 本文件
├── Makefile               # make test / make coverage / make run IMG=xxx
├── requirements.txt       # 依赖清单
├── .env.example           # 环境变量模板（复制为 .env 填入真实 key）
├── src/vision_agent/
│   ├── agent.py           # ← 对外接口：VisionAgent.analyze()
│   ├── graph.py           # LangGraph 状态图
│   ├── state.py           # 共享状态定义
│   ├── config.py          # 配置（读 .env）
│   ├── llm/               # VLM 接口层（base/mock/retry/sealion）
│   ├── nodes/             # 7 个处理节点
│   ├── prompts/           # 4 个 SG 优化 Prompt
│   └── schemas/           # Pydantic 输出模型
└── tests/                 # 155 个测试，99.3% 覆盖率
```

### 快速命令

```bash
source .venv/bin/activate   # 激活虚拟环境
make test                   # 跑所有测试
make coverage               # 测试 + 覆盖率报告
make run IMG=xxx.jpg        # 用 Mock 分析图片
python -m src.vision_agent xxx.jpg --provider sealion --json  # 真实 API
```

### Git 提交记录（11 commits）
```
087a72c feat: Makefile + image_intake 100% coverage
13fa3ea feat: expand MockVLM - 4 SG food / 4 med / 3 report scenarios
b1ad05f feat: VisionAgent high-level API wrapper
ce56244 refactor: conftest.py shared fixtures
f527153 test: edge case tests + coverage config
79615fc feat: Singapore-specific prompt optimization
3a3d0e5 feat: RetryVLM + logging config
3202d13 feat: config module + CLI entry point
944b5b7 test: comprehensive node tests (89% → 99%)
b5c0675 feat: core Vision Agent implementation
121c964 chore: project initialization
```

> [!TIP]
> **判断成功的标准**: 给一张新加坡鸡饭照片，输出 `{"scene_type": "FOOD", "items": [{"name": "Hainanese Chicken Rice", ...}], "total_calories_kcal": 480}` — 数据能直接喂给预警 Agent 做血糖预测。
