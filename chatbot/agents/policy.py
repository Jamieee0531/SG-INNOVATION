"""
纯规则表，不调LLM
根据 情绪+意图 → 决策策略，查表生成策略指令字符串
同时统计近5轮情绪触发持续负面预警
"""
from state.chat_state import ChatState


# ============================================================
# 规则表：(主意图, 情绪) → 策略指令
# ============================================================
POLICY_MAP = {
    # Medical + 情绪
    ("medical", "anxious"):  "先用一句话稳定用户情绪，再进行追问。语气要平稳确定，不要催促。",
    ("medical", "sad"):      "先表达关心，再进行追问。不要急于给建议，让用户感到被理解。",
    ("medical", "angry"):    "先认可用户的烦躁感受，再温和地进行追问。不要争辩。",
    ("medical", "neutral"):  "正常进行追问和建议。",
    ("medical", "happy"):    "轻松回应，正常给出建议。",

    # Emotional + 情绪
    ("emotional", "sad"): "用户很难过，只需要陪伴。禁止给任何建议。如果用户刚刚拒绝了某个建议（说'不想'、'不要'），先认可这个拒绝，说一句'好的，没关系'，然后静静陪着他。",
    #("emotional", "sad"):     "用户很难过，只需要陪伴。禁止给任何建议（不要说'可以试试'、'或许可以'、'建议您'）。只说一句感同身受的话，然后沉默式陪伴或问'您想说说吗'。每次最多一个问题，而且不一定要问。",
    ("emotional", "anxious"): "先给予确定感，说一句'没关系，我在这里'之类的话。不要立刻给建议或行动清单。",
    ("emotional", "angry"):   "先完全认可感受，禁止给建议或替代方案。只说一句理解的话，然后问是什么让他这么烦。",
    ("emotional", "happy"):   "轻松互动，分享正面情绪，顺带关心健康状态。",
    ("emotional", "neutral"):  "温和自然，像朋友一样聊天。",

    # Alert + 情绪
    ("alert", "anxious"):    "先用一句话稳定情绪，再给出紧急指引。语气要平稳确定。",
    ("alert", "neutral"):    "直接给出紧急指引，清晰简洁。",
    ("alert", "sad"):        "先安抚，再给出紧急指引。",

    # Task / Chitchat
    ("task",    "neutral"):  "正常处理任务请求。",
    ("chitchat","neutral"):  "轻松自然地聊天。",
    ("chitchat","sad"):      "注意到用户情绪低落，聊天时多一些关心。",
}

# 持续负面情绪阈值
PERSISTENT_NEGATIVE_THRESHOLD = 3
NEGATIVE_EMOTIONS = ["sad", "anxious", "angry"]


def policy_node(state: ChatState) -> dict:
    """
    Policy层：
    1. 根据意图+情绪查规则表，生成策略指令
    2. 检测持续负面情绪，超过阈值触发预警
    """
    intent        = state.get("intent", "chitchat")
    emotion       = state.get("emotion_label", "neutral")
    all_intents   = state.get("all_intents", [intent])
    history       = state.get("history", [])

    # ── 查规则表 ──────────────────────────────────────
    policy_instruction = POLICY_MAP.get(
        (intent, emotion),
        POLICY_MAP.get((intent, "neutral"), "正常回复。")
    )

    # ── 持续负面情绪检测 ──────────────────────────────
    # 统计最近几轮的负面情绪记录
    recent_emotions = state.get("recent_emotions", [])
    if emotion in NEGATIVE_EMOTIONS:
        recent_emotions = (recent_emotions + [emotion])[-5:]  # 保留最近5轮
    else:
        recent_emotions = (recent_emotions + [emotion])[-5:]

    negative_count = sum(1 for e in recent_emotions if e in NEGATIVE_EMOTIONS)

    persistent_alert = None
    if negative_count >= PERSISTENT_NEGATIVE_THRESHOLD:
        persistent_alert = {
            "type":            "persistent_negative_emotion",
            "user_id":         state["user_id"],
            "negative_turns":  negative_count,
            "recent_emotions": recent_emotions,
            "suggestion":      "用户连续出现负面情绪，建议提醒家属或医生关注",
        }
        # 在策略里加入提示
        policy_instruction += f"\n注意：用户已连续{negative_count}轮出现负面情绪，请在回复末尾温和地建议联系家人或医生。"
        print(f"[Policy] ⚠️ 持续负面情绪检测：{negative_count}轮，触发预警")

    print(f"[Policy] 意图：{intent} | 情绪：{emotion} → 策略：{policy_instruction[:30]}...")
    return {
        "policy_instruction": policy_instruction,
        "recent_emotions":    recent_emotions,
        "persistent_alert":   persistent_alert,
    }
