"""LangGraph Vision Agent - main graph definition.

Dual-model architecture:
  - vision_vlm (e.g. Gemini): handles all image understanding
  - text_llm (e.g. SeaLION): generates localized health advice from recognition results

Flow:
  START → image_intake → scene_classifier
        → (conditional) food_analyzer | medication_reader | report_digitizer | rejection_handler
        → health_advisor (SeaLION text analysis)
        → output_formatter → END
"""

from typing import Optional

from langgraph.graph import END, START, StateGraph

from src.vision_agent.llm.base import BaseVLM
from src.vision_agent.llm.mock import MockVLM
from src.vision_agent.llm.retry import RetryVLM
from src.vision_agent.nodes.food_analyzer import make_food_analyzer
from src.vision_agent.nodes.health_advisor import make_health_advisor
from src.vision_agent.nodes.image_intake import image_intake
from src.vision_agent.nodes.medication_reader import make_medication_reader
from src.vision_agent.nodes.output_formatter import output_formatter
from src.vision_agent.nodes.rejection_handler import rejection_handler
from src.vision_agent.nodes.report_digitizer import make_report_digitizer
from src.vision_agent.nodes.scene_classifier import make_scene_classifier
from src.vision_agent.state import VisionAgentState


def _route_by_scene(state: VisionAgentState) -> str:
    """Conditional edge: route to the correct analyzer node."""
    if state.get("error"):
        return "output_formatter"  # Short-circuit on error

    scene = state.get("scene_type", "UNKNOWN")
    routes = {
        "FOOD": "food_analyzer",
        "MEDICATION": "medication_reader",
        "REPORT": "report_digitizer",
    }
    return routes.get(scene, "rejection_handler")


def build_graph(
    vlm: BaseVLM | None = None,
    text_llm: Optional[BaseVLM] = None,
    max_retries: int = 3,
    retry_delay_s: float = 1.0,
) -> StateGraph:
    """Build and compile the Vision Agent LangGraph.

    Args:
        vlm: Vision VLM for image understanding (e.g. Gemini). Defaults to MockVLM.
        text_llm: Text LLM for health advice (e.g. SeaLION). Optional — if None,
                  the health_advisor node is a no-op passthrough.
        max_retries: Number of retry attempts on VLM failure.
        retry_delay_s: Initial delay between retries in seconds.

    Returns:
        Compiled LangGraph ready to invoke.
    """
    if vlm is None:
        vlm = MockVLM()

    # Wrap with retry logic (skip for MockVLM - it never fails)
    if not isinstance(vlm, MockVLM):
        vlm = RetryVLM(vlm, max_retries=max_retries, delay_s=retry_delay_s)

    if text_llm is not None and not isinstance(text_llm, MockVLM):
        text_llm = RetryVLM(text_llm, max_retries=max_retries, delay_s=retry_delay_s)

    # Bind VLM to factory-created nodes
    scene_classifier = make_scene_classifier(vlm)
    food_analyzer = make_food_analyzer(vlm)
    medication_reader = make_medication_reader(vlm)
    report_digitizer = make_report_digitizer(vlm)
    health_advisor = make_health_advisor(text_llm)

    graph = StateGraph(VisionAgentState)

    # Register nodes
    graph.add_node("image_intake", image_intake)
    graph.add_node("scene_classifier", scene_classifier)
    graph.add_node("food_analyzer", food_analyzer)
    graph.add_node("medication_reader", medication_reader)
    graph.add_node("report_digitizer", report_digitizer)
    graph.add_node("rejection_handler", rejection_handler)
    graph.add_node("health_advisor", health_advisor)
    graph.add_node("output_formatter", output_formatter)

    # Linear edges
    graph.add_edge(START, "image_intake")
    graph.add_edge("image_intake", "scene_classifier")

    # Conditional branching after classification
    graph.add_conditional_edges(
        "scene_classifier",
        _route_by_scene,
        {
            "food_analyzer": "food_analyzer",
            "medication_reader": "medication_reader",
            "report_digitizer": "report_digitizer",
            "rejection_handler": "rejection_handler",
            "output_formatter": "output_formatter",
        },
    )

    # All analyzer paths converge at health_advisor, then output_formatter
    graph.add_edge("food_analyzer", "health_advisor")
    graph.add_edge("medication_reader", "health_advisor")
    graph.add_edge("report_digitizer", "health_advisor")
    graph.add_edge("rejection_handler", "health_advisor")
    graph.add_edge("health_advisor", "output_formatter")
    graph.add_edge("output_formatter", END)

    return graph.compile()
