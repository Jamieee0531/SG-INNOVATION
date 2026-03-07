"""
专家Agent，用Llama推理模型
State-driven: confidence-based skip/confirm/ask for each field
接收 policy 指令 + vision_result 自动填充已知信息
"""
from datetime import datetime
from enum import Enum
from typing import Optional, Tuple
import copy
import re

from state.chat_state import ChatState
from utils.llm_factory import call_sealion_with_history, format_history_for_sealion


class FieldStatus(str, Enum):
    EMPTY = "empty"          # No value, or confidence < 0.5 -> ask
    UNCERTAIN = "uncertain"  # Has value, confidence 0.5~0.8 -> confirm
    CONFIRMED = "confirmed"  # Has value, confidence >= 0.8 or user-provided -> skip


# Confidence thresholds
CONFIDENCE_LOW = 0.5
CONFIDENCE_HIGH = 0.8

# Fields in collection priority order
REQUIRED_FIELDS = ["glucose", "diet", "medication"]


def classify_field(value: Optional[str], confidence: Optional[float]) -> FieldStatus:
    """Classify a field's status based on value and confidence.

    confidence=None means user-provided (always confirmed).
    """
    if value is None:
        return FieldStatus.EMPTY
    if confidence is None:
        # User directly answered -> always confirmed
        return FieldStatus.CONFIRMED
    if confidence < CONFIDENCE_LOW:
        return FieldStatus.EMPTY
    if confidence < CONFIDENCE_HIGH:
        return FieldStatus.UNCERTAIN
    return FieldStatus.CONFIRMED


def determine_next_question(collected: dict) -> Tuple[Optional[str], Optional[FieldStatus]]:
    """Find the next field needing attention.

    Priority: uncertain fields (need confirmation) first, then empty fields.
    Returns (field_name, status) or (None, None) if all confirmed.
    """
    # First pass: uncertain fields need user confirmation
    for field in REQUIRED_FIELDS:
        entry = collected.get(field)
        if entry is None:
            continue
        value = entry.get("value") if isinstance(entry, dict) else entry
        conf = entry.get("confidence") if isinstance(entry, dict) else None
        if classify_field(value, conf) == FieldStatus.UNCERTAIN:
            return field, FieldStatus.UNCERTAIN

    # Second pass: empty fields need to be asked
    for field in REQUIRED_FIELDS:
        entry = collected.get(field)
        if entry is None:
            return field, FieldStatus.EMPTY
        value = entry.get("value") if isinstance(entry, dict) else entry
        conf = entry.get("confidence") if isinstance(entry, dict) else None
        if classify_field(value, conf) == FieldStatus.EMPTY:
            return field, FieldStatus.EMPTY

    return None, None


def _get_field_value(entry) -> str:
    """Extract human-readable value from a collected field entry."""
    if entry is None:
        return "未知"
    if isinstance(entry, dict):
        return entry.get("value", "未知")
    return str(entry)


def _prefill_from_vision(collected: dict, vision_result: list) -> dict:
    """Pre-fill collected_info from Vision Agent results (immutable pattern)."""
    if not vision_result:
        return collected

    updated = copy.deepcopy(collected)

    for result in vision_result:
        scene = result.get("scene_type", "")
        confidence = result.get("confidence", 0.0)

        if scene == "FOOD" and updated.get("diet") is None:
            items = result.get("items", [])
            if items:
                food_names = ", ".join(
                    item.get("name", "") for item in items if item.get("name")
                )
                total_cal = result.get("total_calories_kcal", "")
                value = f"{food_names}（约{total_cal}大卡）" if total_cal else food_names
                updated["diet"] = {
                    "value": value,
                    "confidence": confidence,
                    "source": "vision",
                }

        elif scene == "MEDICATION" and updated.get("medication") is None:
            drug = result.get("drug_name", "")
            dosage = result.get("dosage", "")
            value = f"{drug} {dosage}".strip()
            if value:
                updated["medication"] = {
                    "value": value,
                    "confidence": confidence,
                    "source": "vision",
                }

    return updated


def _store_user_answer(user_input: str, stage: str, collected: dict) -> dict:
    """Store user's text answer as a confirmed entry."""
    stage_to_field = {
        "asking_glucose":        "glucose",
        "asking_diet":           "diet",
        "asking_medication":     "medication",
        "confirming_diet":       "diet",
        "confirming_medication": "medication",
    }
    field = stage_to_field.get(stage)
    if not field:
        return collected

    updated = copy.deepcopy(collected)
    updated[field] = {"value": user_input, "confidence": None, "source": "user"}
    return updated


def _build_stage_prompt(field: Optional[str], status: Optional[FieldStatus],
                         collected: dict, name: str) -> Tuple[str, str]:
    """Build (stage_instruction, next_stage) for the current step."""
    if field is None:
        # All confirmed -> summarize
        instruction = (
            f"信息已齐全，给出综合建议：\n"
            f"- 血糖：{_get_field_value(collected.get('glucose'))}\n"
            f"- 饮食：{_get_field_value(collected.get('diet'))}\n"
            f"- 用药：{_get_field_value(collected.get('medication'))}\n"
            "结合新加坡本地饮食文化给出具体建议。末尾加免责声明。"
        )
        return instruction, "idle"

    if field == "glucose" and status == FieldStatus.EMPTY:
        return (
            f"先用一句话表示关心，然后只问：{name}，您的血糖大概测到多少呢？不要给任何建议。",
            "asking_glucose",
        )

    if field == "diet" and status == FieldStatus.EMPTY:
        return "先回应一句，然后只问：今天吃了什么？不要给任何建议。", "asking_diet"

    if field == "diet" and status == FieldStatus.UNCERTAIN:
        val = _get_field_value(collected.get("diet"))
        return (
            f"向用户确认：看起来您吃的是{val}，对吗？不要给建议，等用户确认。",
            "confirming_diet",
        )

    if field == "medication" and status == FieldStatus.EMPTY:
        return (
            "先回应饮食情况（一句话），然后只问：今天的药有按时服用吗？不要给任何建议。",
            "asking_medication",
        )

    if field == "medication" and status == FieldStatus.UNCERTAIN:
        val = _get_field_value(collected.get("medication"))
        return (
            f"向用户确认：看起来您在服用{val}，对吗？不要给建议，等用户确认。",
            "confirming_medication",
        )

    # Fallback
    return "正常进行追问和建议。", "idle"


def _check_alert(collected: dict, user_id: str) -> Optional[dict]:
    """Check if glucose value is out of safe range and return alert_trigger."""
    glucose_entry = collected.get("glucose")
    if glucose_entry is None:
        return None
    glucose_val = _get_field_value(glucose_entry)
    numbers = re.findall(r'\d+\.?\d*', glucose_val)
    if not numbers:
        return None
    glucose_num = float(numbers[0])
    if glucose_num > 7.0 or glucose_num < 3.9:
        severity = "elevated" if glucose_num > 7.0 else "low"
        print(f"[Expert] Alert trigger: glucose {glucose_num} ({severity})")
        return {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "glucose_value": glucose_num,
            "severity": severity,
        }
    return None


def expert_agent_node(state: ChatState) -> dict:
    profile       = state.get("user_profile", {})
    name          = profile.get("name", "患者")
    language      = profile.get("language", "Chinese")
    conditions    = profile.get("conditions", ["Type 2 Diabetes"])
    medications   = profile.get("medications", [])
    all_intents   = state.get("all_intents", ["medical"])
    current_stage = state.get("conversation_stage") or "idle"

    # Step 1: Start with current collected_info
    collected = dict(state.get("collected_info") or {})

    # Step 2: Pre-fill from Vision Agent results (immutable)
    vision_result = state.get("vision_result") or []
    collected = _prefill_from_vision(collected, vision_result)

    # Step 3: If user answered a question, store their answer as confirmed
    if current_stage != "idle" and state.get("user_input", "").strip():
        collected = _store_user_answer(state.get("user_input", ""), current_stage, collected)

    # Step 4: Determine next action
    next_field, next_status = determine_next_question(collected)
    stage_instruction, next_stage = _build_stage_prompt(
        next_field, next_status, collected, name
    )

    # Step 5: Alert check (only when all fields just got confirmed)
    alert_trigger = None
    if next_field is None:
        alert_trigger = _check_alert(collected, state["user_id"])

    # Step 6: Emotional prefix from policy
    emotional_prefix = ""
    if "emotional" in all_intents or state.get("emotion_label") in ["anxious", "sad", "angry"]:
        emotional_prefix = "先用一句话安抚用户情绪，再进行追问或给建议。\n"

    # Step 7: Task trigger
    task_suffix = ""
    task_trigger = None
    if "task" in all_intents:
        task_suffix = "\n最后提醒用户：打卡任务已转给任务系统处理。"
        task_trigger = {
            "user_id": state["user_id"],
            "timestamp": datetime.now().isoformat(),
            "request": state.get("user_input", ""),
            "type": "task_request",
        }

    policy_instruction = state.get("policy_instruction", "正常进行追问和建议。")

    system_prompt = (
        f"你是专业的慢性病管理医疗顾问，专注于新加坡患者。\n"
        f"患者：{name} | 病症：{', '.join(conditions)} | "
        f"用药：{', '.join(medications) if medications else '未记录'}\n"
        f"请用{language}回复。\n\n"
        f"【当前策略指令】\n{policy_instruction}\n\n"
        f"{emotional_prefix}{stage_instruction}\n\n"
        f"通用规则：\n"
        "- \u201c打卡\u201d指健康任务打卡，不是自我伤害\n"
        f"- 结合新加坡本地饮食文化\n"
        f"- 回复150字以内{task_suffix}"
    )

    history = format_history_for_sealion(state.get("history", []))
    history.append({"role": "user", "content": state.get("user_input", "")})
    response = call_sealion_with_history(system_prompt, history, reasoning=True)

    if "</think>" in response:
        response = response.split("</think>")[-1].strip()

    print(f"[Expert] Stage: {current_stage} -> {next_stage} | Next field: {next_field}")
    return {
        "response":           response,
        "conversation_stage": next_stage,
        "collected_info":     collected,
        "task_trigger":       task_trigger,
        "alert_trigger":      alert_trigger,
    }
