"""
main.py
项目入口 —— 命令行测试界面
"""
from typing import Optional

from graph.builder import app
from state.chat_state import ChatState
from utils.memory import get_user_profile, add_to_history


def create_initial_state(
    user_input: str,
    user_id: str = "user_001",
    input_mode: str = "text",
    chat_mode: str = "personal",
    audio_path: Optional[str] = None,
    history: list = None,
    conversation_stage: Optional[str] = None,
    collected_info: dict = None,
    recent_emotions: list = None,
    persistent_alert: Optional[dict] = None,
    policy_instruction: Optional[str] = None,
    image_paths: list = None,
) -> ChatState:
    return ChatState(
        user_input=user_input,
        input_mode=input_mode,
        audio_path=audio_path,
        chat_mode=chat_mode,
        user_id=user_id,
        transcribed_text=None,
        emotion_label="neutral",
        emotion_confidence=0.0,
        intent=None,
        all_intents=None,
        policy_instruction=policy_instruction,
        recent_emotions=recent_emotions or [],
        persistent_alert=persistent_alert,
        history=history or [],
        user_profile=get_user_profile(user_id),
        conversation_stage=conversation_stage,
        collected_info=collected_info or {},
        response=None,
        emotion_log=None,
        task_trigger=None,
        alert_trigger=None,
        image_paths=image_paths,
        vision_result=None,
    )


def run_cli():
    print("=" * 55)
    print("  Health Companion — 对话测试")
    print("  输入 'quit' 退出 | 'reset' 清空历史 | 'voice 路径' 语音 | 'image 路径 [文字]' 图片")
    print("=" * 55)

    user_id            = "user_001"
    history            = []
    conversation_stage = None
    collected_info     = {}
    recent_emotions    = []

    profile = get_user_profile(user_id)
    print(f"\n  当前用户：{profile['name']} | 病症：{', '.join(profile['conditions'])}\n")

    while True:
        user_input = input("你：").strip()

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("再见！")
            break
        if user_input.lower() == "reset":
            history            = []
            conversation_stage = None
            collected_info     = {}
            recent_emotions    = []
            print("[系统] 对话历史已清空\n")
            continue

        # 图片模式：输入 "image 图片路径" 或 "image 图片路径 附带文字"
        if user_input.lower().startswith("image "):
            parts = user_input[6:].strip().split(" ", 1)
            img_path = parts[0]
            text = parts[1] if len(parts) > 1 else ""
            print(f"[图片模式] 正在识别：{img_path}")
            state = create_initial_state(
                user_input=text,
                image_paths=[img_path],
                user_id=user_id,
                history=history,
                conversation_stage=conversation_stage,
                collected_info=collected_info,
                recent_emotions=recent_emotions,
            )

        # 语音模式：输入 "voice 音频文件路径"
        elif user_input.lower().startswith("voice "):
            audio_path = user_input[6:].strip()
            print(f"[语音模式] 处理音频：{audio_path}")
            state = create_initial_state(
                user_input="",
                input_mode="voice",
                audio_path=audio_path,
                user_id=user_id,
                history=history,
                conversation_stage=conversation_stage,
                collected_info=collected_info,
                recent_emotions=recent_emotions,
                persistent_alert=None,
                policy_instruction=None,
            )
        else:
            state = create_initial_state(
                user_input=user_input,
                user_id=user_id,
                history=history,
                conversation_stage=conversation_stage,
                collected_info=collected_info,
                recent_emotions=recent_emotions,
                persistent_alert=None,
                policy_instruction=None,
            )

        result   = app.invoke(state)
        response = result["response"]

        # Print vision recognition results if any
        if result.get("vision_result"):
            for vr in result["vision_result"]:
                scene = vr.get("scene_type", "?")
                conf = vr.get("confidence", 0.0)
                print(f"  [Vision] 识别结果：{scene}（置信度 {conf:.0%}）")

        intent  = result.get("intent", "?")
        emotion = result.get("emotion_label", "neutral")
        stage   = result.get("conversation_stage") or "idle"
        policy  = result.get("policy_instruction", "")[:25]
        print(f"\n助手 [{intent} | {emotion} | 阶段:{stage} | 策略:{policy}]：{response}\n")

        # 打印触发信号
        if result.get("persistent_alert"):
            print("  👨‍👩‍👧 → 持续负面情绪预警：建议联系家属/医生")
        if result.get("emotion_log"):
            print("  📊 → 集成数据库：情绪记录已写入")
        if result.get("task_trigger"):
            print("  📋 → Chayi 任务模块：task_trigger 已发出")
        if result.get("alert_trigger"):
            print("  🚨 → Julia 预警模块：alert_trigger 已发出")
        print()

        # 跨轮状态持久化
        history            = add_to_history(history, "user", user_input)
        history            = add_to_history(history, "assistant", response)
        conversation_stage = result.get("conversation_stage")
        collected_info     = result.get("collected_info") or {}
        recent_emotions    = result.get("recent_emotions") or []


if __name__ == "__main__":
    run_cli()
