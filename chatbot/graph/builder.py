"""
graph/builder.py
LangGraph 图构建
加入Policy层：triage → policy → 各Agent

流程：
input_node → triage_node → policy_node → [条件路由] → 各Agent → END
"""
from langgraph.graph import StateGraph, END
from state.chat_state import ChatState
from agents.triage import input_node, triage_node, route_by_intent
from agents.policy import policy_node
from agents.companion import companion_agent_node
from agents.expert import expert_agent_node
from agents.task_forward import task_forward_node
from agents.alert_forward import alert_forward_node
from agents.chitchat import chitchat_agent_node


def build_graph():
    graph = StateGraph(ChatState)

    # ── 注册节点 ─────────────────────────────────────────
    graph.add_node("input_node",      input_node)
    graph.add_node("triage_node",     triage_node)
    graph.add_node("policy_node",     policy_node)       # ← 新增
    graph.add_node("companion_agent", companion_agent_node)
    graph.add_node("expert_agent",    expert_agent_node)
    graph.add_node("task_forward",    task_forward_node)
    graph.add_node("alert_forward",   alert_forward_node)
    graph.add_node("chitchat_agent",  chitchat_agent_node)

    # ── 入口 ─────────────────────────────────────────────
    graph.set_entry_point("input_node")

    # ── 固定边 ───────────────────────────────────────────
    graph.add_edge("input_node",  "triage_node")
    graph.add_edge("triage_node", "policy_node")        # ← triage后先过policy

    # ── 条件路由：policy → 各Agent ───────────────────────
    graph.add_conditional_edges(
        "policy_node",
        route_by_intent,
        {
            "companion_agent": "companion_agent",
            "expert_agent":    "expert_agent",
            "task_forward":    "task_forward",
            "alert_forward":   "alert_forward",
            "chitchat_agent":  "chitchat_agent",
        }
    )

    # ── 所有Agent → END ──────────────────────────────────
    for node in ["companion_agent", "expert_agent",
                 "task_forward", "alert_forward", "chitchat_agent"]:
        graph.add_edge(node, END)

    return graph.compile()


app = build_graph()
