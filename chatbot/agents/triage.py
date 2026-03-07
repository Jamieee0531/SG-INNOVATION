"""
agents/triage.py
意图分类 + 情绪识别合并为一次调用
追问链进行中：只检测退出意图，不判断情绪（省token）
"""
import json
import sys as _sys
import os as _os
from typing import Optional
from state.chat_state import ChatState
from utils.llm_factory import call_sealion
from utils.meralion import process_voice_input
from config.settings import ALL_INTENTS, INTENT_CHITCHAT

# Add Vision Agent to path for direct import
# chatbot/ is inside SG_INNOVATION/, so go up two levels to reach SG_INNOVATION root
_VISION_AGENT_PATH = _os.path.abspath(
    _os.path.join(_os.path.dirname(__file__), "..", "..")
)
if _os.path.isdir(_VISION_AGENT_PATH) and _VISION_AGENT_PATH not in _sys.path:
    _sys.path.insert(0, _VISION_AGENT_PATH)


def analyze_image(image_path: str):
    """Call Vision Agent to analyze an image. Returns AnalysisResult."""
    from src.vision_agent.agent import VisionAgent
    agent = VisionAgent()
    return agent.analyze(image_path)


# scene_type → synthetic text (when user sends image with no text)
SCENE_TEXT_MAP = {
    "FOOD":       "我拍了一张食物照片",
    "MEDICATION": "我拍了一张药物照片",
    "REPORT":     "我拍了一张化验单照片",
    "UNKNOWN":    "我发了一张照片",
}

# 退出追问链的关键词
EXIT_CHAIN_KEYWORDS = [
    "不想聊", "不想说", "换个话题", "先不说", "不想谈",
    "不聊了", "算了", "不想", "stop", "never mind", "孤独",
    "难过", "伤心", "不开心", "很烦", "不想回答",
]


def input_node(state: ChatState) -> dict:
    # ── Voice mode ──────────────────────────────────────
    if state["input_mode"] == "voice":
        audio_path = state.get("audio_path", "")
        result = process_voice_input(audio_path)
        return {
            "user_input":         result["transcribed_text"],
            "transcribed_text":   result["transcribed_text"],
            "emotion_label":      result["emotion_label"],
            "emotion_confidence": result["emotion_confidence"],
        }

    # ── Image handling ──────────────────────────────────
    image_paths = state.get("image_paths") or []
    vision_result = []

    if image_paths:
        for path in image_paths:
            try:
                result = analyze_image(path)
                if not result.is_error and result.structured_output:
                    vision_result.append(result.structured_output.model_dump())
                else:
                    vision_result.append({
                        "scene_type": "UNKNOWN",
                        "error": result.error or "识别失败",
                        "confidence": 0.0,
                    })
            except Exception as e:
                vision_result.append({
                    "scene_type": "UNKNOWN",
                    "error": str(e),
                    "confidence": 0.0,
                })

    # ── Synthetic text for image-only input ─────────────
    user_input = state["user_input"]
    if image_paths and not user_input.strip():
        scene = vision_result[0].get("scene_type", "UNKNOWN") if vision_result else "UNKNOWN"
        user_input = SCENE_TEXT_MAP.get(scene, "我发了一张照片")

    updates = {
        "transcribed_text":   user_input,
        "emotion_label":      "neutral",
        "emotion_confidence": 0.0,
    }

    if image_paths:
        updates["user_input"] = user_input
        updates["vision_result"] = vision_result

    return updates


def triage_node(state: ChatState) -> dict:
    current_stage      = state.get("conversation_stage")
    emotion_label      = state.get("emotion_label", "neutral")
    emotion_confidence = state.get("emotion_confidence", 0.0)
    user_input         = state["user_input"]

    # ── 追问链进行中：检测是否需要退出 ──────────────────
    if current_stage and current_stage != "idle":
        should_exit = any(kw in user_input for kw in EXIT_CHAIN_KEYWORDS)

        if should_exit:
            # 退出追问链，重新做完整意图+情绪判断
            print(f"[Triage] 检测到退出追问链关键词，重置阶段")
            # 走下面的完整判断流程，同时通知expert重置stage
            result = _full_triage(state)
            result["conversation_stage"] = "idle"  # 强制重置追问链
            result["collected_info"]     = {}
            return result

        # 没有退出意图：保持路由到expert，情绪不判断省token
        print(f"[Triage] 追问链进行中（阶段:{current_stage}）→ expert_agent")
        return {
            "intent":        "medical",
            "all_intents":   ["medical"],
            "emotion_label": "neutral",
        }

    # ── 正常流程：完整意图+情绪判断 ──────────────────────
    return _full_triage(state)



# ── Keyword pre-classification ────────────────────────────────────────────
# Checked before LLM call. Order matters: alert > medical > emotional > task.
KEYWORD_RULES = [
    ("alert", [
        "头晕", "晕倒", "胸痛", "发抖", "chest pain", "dizzy", "faint",
        r"血糖.*1[5-9]", r"血糖.*[2-9][0-9]", r"血糖.*[0-2]\.\d", "低血糖",
    ]),
    ("medical", [
        "血糖", "glucose", "sugar", "药", "medicine", "metformin",
        "二甲双胍", "饮食", "diet", "吃了什么", "GI", "升糖",
    ]),
    ("emotional", [
        "难过", "伤心", "压力", "焦虑", "害怕", "孤独", "stress",
        "担心", "不开心", "depressed", "anxious",
    ]),
    ("task", ["打卡", "积分", "提醒我", "记录血糖", "remind"]),
]

EMOTION_KEYWORDS = {
    "sad":     ["难过", "伤心", "不开心", "sad", "depressed"],
    "anxious": ["焦虑", "担心", "害怕", "紧张", "anxious", "worried", "压力"],
    "angry":   ["生气", "烦", "angry", "frustrated"],
    "happy":   ["开心", "高兴", "happy", "great"],
}


def keyword_preclassify(user_input: str) -> Optional[str]:
    """Classify intent by keywords. Returns intent string or None (fall back to LLM)."""
    import re
    text = user_input.lower()
    for intent, keywords in KEYWORD_RULES:
        for kw in keywords:
            if re.search(kw, text):
                return intent
    return None


def _simple_emotion_detect(
    user_input: str,
    voice_emotion: str,
    voice_confidence: float,
    input_mode: str,
) -> str:
    """Detect emotion by keywords. Voice emotion overrides if mode=voice and confidence > 0.6."""
    if input_mode == "voice" and voice_confidence > 0.6:
        return voice_emotion
    text = user_input.lower()
    for emotion, keywords in EMOTION_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return emotion
    return "neutral"


def _full_triage(state: ChatState) -> dict:
    """完整的意图+情绪判断：关键词预分类 + LLM兜底"""
    emotion_label      = state.get("emotion_label", "neutral")
    emotion_confidence = state.get("emotion_confidence", 0.0)
    user_input         = state["user_input"]

    # ── Step 1: Try keyword pre-classification ──────────
    keyword_intent = keyword_preclassify(user_input)
    if keyword_intent:
        emotion = _simple_emotion_detect(
            user_input, emotion_label, emotion_confidence,
            state.get("input_mode", "text")
        )
        print(f"[Triage] 关键词命中：{keyword_intent} | 情绪：{emotion}")
        return {
            "intent":        keyword_intent,
            "all_intents":   [keyword_intent],
            "emotion_label": emotion,
        }

    # ── Step 2: Fall back to LLM ────────────────────────

    emotion_hint = ""
    if state["input_mode"] == "voice" and emotion_confidence > 0.6:
        emotion_hint = f"\n用户语音情绪：{emotion_label}（置信度 {emotion_confidence:.0%}）"

    system_prompt = """你是医疗健康助手的分诊系统，服务于新加坡的慢性病患者。
结合【最近对话】和【当前消息】，分析用户意图和情绪，返回JSON：
{"intents": ["标签1","标签2"], "emotion": "情绪标签"}

意图标签（按优先级，可多选）：
- alert      （严重症状：头晕、胸痛、发抖；血糖>15或<3.5）
- medical    （血糖偏高、药物、饮食建议、症状）
- emotional  （情绪倾诉、担心、沮丧、孤独、失望、需要陪伴）
- task       （打卡、积分、提醒、上传照片）
- chitchat   （日常闲聊）

情绪标签（只选一个）：
neutral / happy / sad / anxious / angry / confused

规则：
- 结合上下文：若前几轮是情绪话题，简短回应也归为emotional
- "打卡"指健康任务，"打视频"、"打电话"是通讯行为归emotional
- 只返回JSON，不要任何解释""" + emotion_hint

    history = state.get("history", [])
    recent  = history[-4:] if len(history) >= 4 else history
    context = ""
    if recent:
        context = "【最近对话】\n"
        for h in recent:
            role     = "用户" if h["role"] == "user" else "助手"
            context += f"{role}：{h['content']}\n"
        context += "\n【当前消息】\n"

    raw = call_sealion(system_prompt, context + state["user_input"])

    try:
        clean   = raw.strip().replace("```json","").replace("```","").strip()
        data    = json.loads(clean)
        intents = [i for i in data.get("intents", []) if i in ALL_INTENTS]
        emotion = data.get("emotion", "neutral")
        if emotion not in ["neutral","happy","sad","anxious","angry","confused"]:
            emotion = "neutral"
    except Exception:
        intents = [INTENT_CHITCHAT]
        emotion = "neutral"

    if not intents:
        intents = [INTENT_CHITCHAT]

    if state["input_mode"] == "voice" and emotion_confidence > 0.6:
        emotion = emotion_label

    print(f"[Triage] 意图：{intents} | 情绪：{emotion} | 输入：{state['input_mode']}")
    return {
        "intent":        intents[0],
        "all_intents":   intents,
        "emotion_label": emotion,
    }


def route_by_intent(state: ChatState) -> str:
    route_map = {
        "emotional": "companion_agent",
        "medical":   "expert_agent",
        "task":      "task_forward",
        "alert":     "alert_forward",
        "chitchat":  "chitchat_agent",
    }
    return route_map.get(state.get("intent", "chitchat"), "chitchat_agent")
