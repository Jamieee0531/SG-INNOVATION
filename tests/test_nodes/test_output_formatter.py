"""Tests for output_formatter and rejection_handler nodes."""

import pytest

from src.vision_agent.nodes.output_formatter import output_formatter
from src.vision_agent.nodes.rejection_handler import rejection_handler


def _state(structured_output=None, error=None, scene_type="FOOD", confidence=0.9):
    return {
        "image_path": "/tmp/test.jpg",
        "image_base64": "b64",
        "scene_type": scene_type,
        "confidence": confidence,
        "raw_response": "",
        "structured_output": structured_output or {},
        "error": error,
    }


class TestOutputFormatter:
    def test_passes_through_valid_output(self):
        state = _state(structured_output={
            "scene_type": "FOOD",
            "confidence": 0.9,
            "items": [],
            "total_calories_kcal": 0.0,
        })
        result = output_formatter(state)
        assert result["structured_output"]["scene_type"] == "FOOD"

    def test_error_state_returns_error_envelope(self):
        state = _state(error="something went wrong")
        result = output_formatter(state)
        out = result["structured_output"]
        assert out["scene_type"] == "ERROR"
        assert "something went wrong" in out["error"]
        assert out["confidence"] == 0.0

    def test_missing_scene_type_returns_error(self):
        state = _state(structured_output={"confidence": 0.9})  # missing scene_type
        result = output_formatter(state)
        out = result["structured_output"]
        assert out["scene_type"] == "ERROR"
        assert "missing required fields" in out["error"]

    def test_missing_confidence_returns_error(self):
        state = _state(structured_output={"scene_type": "FOOD"})  # missing confidence
        result = output_formatter(state)
        out = result["structured_output"]
        assert out["scene_type"] == "ERROR"

    def test_empty_structured_output_returns_error(self):
        state = _state(structured_output={})
        result = output_formatter(state)
        assert result["structured_output"]["scene_type"] == "ERROR"


class TestRejectionHandler:
    def test_returns_unknown_output(self):
        state = _state(scene_type="UNKNOWN", confidence=0.85)
        result = rejection_handler(state)
        out = result["structured_output"]
        assert out["scene_type"] == "UNKNOWN"
        assert "reason" in out
        assert len(out["reason"]) > 0

    def test_error_is_none(self):
        state = _state(scene_type="UNKNOWN")
        result = rejection_handler(state)
        assert result["error"] is None

    def test_confidence_preserved(self):
        state = _state(scene_type="UNKNOWN", confidence=0.73)
        result = rejection_handler(state)
        assert result["structured_output"]["confidence"] == 0.73

    def test_reason_mentions_upload_instruction(self):
        state = _state(scene_type="UNKNOWN")
        result = rejection_handler(state)
        reason = result["structured_output"]["reason"]
        assert "upload" in reason.lower() or "please" in reason.lower()
