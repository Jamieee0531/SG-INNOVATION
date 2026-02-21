"""Tests for VisionAgentState."""

from src.vision_agent.state import VisionAgentState


class TestVisionAgentState:
    def test_state_is_typeddict(self):
        state: VisionAgentState = {
            "image_path": "/tmp/test.jpg",
            "image_base64": "",
            "scene_type": "FOOD",
            "confidence": 0.9,
            "raw_response": "",
            "structured_output": {},
            "error": None,
        }
        assert state["scene_type"] == "FOOD"
        assert state["error"] is None

    def test_state_allows_partial_construction(self):
        # LangGraph nodes return partial state updates
        partial: dict = {"scene_type": "MEDICATION", "confidence": 0.85}
        assert partial["scene_type"] == "MEDICATION"
