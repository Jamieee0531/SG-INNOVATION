"""
陪伴Agent，用Qwen对话模型
接收policy指令决定回复风格
内置心理危机关键词检测
"""
from datetime import datetime
from state.chat_state import ChatState
from utils.llm_factory import call_sealion_with_history, format_history_for_sealion

CRISIS_KEYWORDS = [
    "活着没意思", "不想活", "去死", "伤害自己", "结束生命",
    "no point living", "want to die", "hurt myself", "end my life"
]


def companion_agent_node(state: ChatState) -> dict:
    profile            = state.get("user_profile", {})
    name               = profile.get("name", "您")
    language           = profile.get("language", "Chinese")
    user_input         = state["user_input"]
    emotion_label      = state.get("emotion_label", "neutral")
    policy_instruction = state.get("policy_instruction", "温和自然地回复。")

    # 心理危机检测
    is_crisis = any(kw in user_input for kw in CRISIS_KEYWORDS)
    if is_crisis:
        response = (
            f"{name}，您刚才说的话让我很担心。"
            "您的生命很重要，您不需要一个人扛着这些。"
            "请拨打新加坡心理援助热线：1-767（24小时）或 IMH：6389 2222。"
            "我在这里陪您——能告诉我，是什么让您有这样的感受吗？"
        ) if language != "English" else (
            f"I'm really concerned about what you said. You matter and you're not alone. "
            "Please call Samaritans of Singapore: 1-767 (24hr) or IMH: 6389 2222."
        )
        print(f"[陪伴Agent] ⚠️ 心理危机检测触发")
        return {
            "response": response,
            "emotion_log": {
                "user_id": state["user_id"], "timestamp": datetime.now().isoformat(),
                "input": user_input, "emotion_label": "crisis", "is_crisis": True,
            },
            "alert_trigger": {
                "user_id": state["user_id"], "timestamp": datetime.now().isoformat(),
                "alert_input": user_input, "severity": "心理危机",
            },
        }

    system_prompt = f"""你是温暖、有耐心的健康陪伴助手，陪伴新加坡的慢性病患者。
患者姓名：{name}，请用{language}回复。

【当前策略指令】（必须严格执行，违反则无效）
{policy_instruction}

通用原则：
- 回复60字以内，越短越好
- 不提供具体医疗建议
- 不一定每次都要问问题，有时候只是陪着就够了
- 像朋友一样说话，不要像顾问"""

    history  = format_history_for_sealion(state.get("history", []))
    history.append({"role": "user", "content": user_input})
    response = call_sealion_with_history(system_prompt, history)

    emotion_log = {
        "user_id": state["user_id"], "timestamp": datetime.now().isoformat(),
        "input": user_input, "emotion_label": emotion_label,
        "agent_response": response, "is_crisis": False,
    }

    print(f"[陪伴Agent] 回复完成 | 情绪：{emotion_label} | 策略：{policy_instruction[:20]}...")
    return {"response": response, "emotion_log": emotion_log}
