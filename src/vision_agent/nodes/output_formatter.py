"""Node: output_formatter - final validation and formatting of structured output."""

import logging

from src.vision_agent.state import VisionAgentState

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = {"scene_type", "confidence"}


def output_formatter(state: VisionAgentState) -> dict:
    """Validate structured_output has required fields and add metadata."""
    if state.get("error"):
        # Return error envelope so callers always get consistent structure
        return {
            "structured_output": {
                "scene_type": "ERROR",
                "error": state["error"],
                "confidence": 0.0,
            }
        }

    output = state.get("structured_output", {})
    missing = REQUIRED_FIELDS - set(output.keys())
    if missing:
        logger.error("structured_output missing required fields: %s", missing)
        return {
            "structured_output": {
                "scene_type": "ERROR",
                "error": f"Output missing required fields: {missing}",
                "confidence": 0.0,
            }
        }

    return {"structured_output": output}
