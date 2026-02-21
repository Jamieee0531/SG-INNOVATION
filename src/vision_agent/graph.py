"""LangGraph Vision Agent - main graph definition.

Flow:
  START → image_intake → scene_classifier
        → (conditional) food_analyzer | medication_reader | report_digitizer | rejection_handler
        → output_formatter → END
"""

from langgraph.graph import END, START, StateGraph

from src.vision_agent.llm.base import BaseVLM
from src.vision_agent.llm.mock import MockVLM
from src.vision_agent.nodes.food_analyzer import make_food_analyzer
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


def build_graph(vlm: BaseVLM | None = None) -> StateGraph:
    """Build and compile the Vision Agent LangGraph.

    Args:
        vlm: VLM implementation to use. Defaults to MockVLM for development.

    Returns:
        Compiled LangGraph ready to invoke.
    """
    if vlm is None:
        vlm = MockVLM()

    # Bind VLM to factory-created nodes
    scene_classifier = make_scene_classifier(vlm)
    food_analyzer = make_food_analyzer(vlm)
    medication_reader = make_medication_reader(vlm)
    report_digitizer = make_report_digitizer(vlm)

    graph = StateGraph(VisionAgentState)

    # Register nodes
    graph.add_node("image_intake", image_intake)
    graph.add_node("scene_classifier", scene_classifier)
    graph.add_node("food_analyzer", food_analyzer)
    graph.add_node("medication_reader", medication_reader)
    graph.add_node("report_digitizer", report_digitizer)
    graph.add_node("rejection_handler", rejection_handler)
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

    # All analyzer paths converge at output_formatter
    graph.add_edge("food_analyzer", "output_formatter")
    graph.add_edge("medication_reader", "output_formatter")
    graph.add_edge("report_digitizer", "output_formatter")
    graph.add_edge("rejection_handler", "output_formatter")
    graph.add_edge("output_formatter", END)

    return graph.compile()
