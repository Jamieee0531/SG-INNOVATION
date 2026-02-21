"""Integration tests for the full LangGraph Vision Agent."""

import os
import tempfile

import pytest
from PIL import Image

from src.vision_agent.graph import build_graph
from src.vision_agent.llm.mock import MockVLM


def _make_test_image() -> str:
    img = Image.new("RGB", (100, 100), color=(0, 128, 0))
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        img.save(f.name)
        return f.name


def _base_state(image_path: str) -> dict:
    return {
        "image_path": image_path,
        "image_base64": "",
        "scene_type": "",
        "confidence": 0.0,
        "raw_response": "",
        "structured_output": {},
        "error": None,
    }


class TestGraphFoodPath:
    def test_food_image_returns_structured_output(self):
        path = _make_test_image()
        try:
            graph = build_graph(vlm=MockVLM(forced_scene="FOOD"))
            result = graph.invoke(_base_state(path))
            assert result["error"] is None
            assert result["scene_type"] == "FOOD"
            output = result["structured_output"]
            assert output["scene_type"] == "FOOD"
            assert "items" in output
            assert output["total_calories_kcal"] > 0
        finally:
            os.unlink(path)


class TestGraphMedicationPath:
    def test_medication_image_returns_structured_output(self):
        path = _make_test_image()
        try:
            graph = build_graph(vlm=MockVLM(forced_scene="MEDICATION"))
            result = graph.invoke(_base_state(path))
            assert result["error"] is None
            assert result["scene_type"] == "MEDICATION"
            output = result["structured_output"]
            assert "drug_name" in output
            assert "dosage" in output
        finally:
            os.unlink(path)


class TestGraphReportPath:
    def test_report_image_returns_structured_output(self):
        path = _make_test_image()
        try:
            graph = build_graph(vlm=MockVLM(forced_scene="REPORT"))
            result = graph.invoke(_base_state(path))
            assert result["error"] is None
            assert result["scene_type"] == "REPORT"
            output = result["structured_output"]
            assert "indicators" in output
            assert len(output["indicators"]) > 0
        finally:
            os.unlink(path)


class TestGraphUnknownPath:
    def test_unknown_image_returns_rejection(self):
        path = _make_test_image()
        try:
            graph = build_graph(vlm=MockVLM(forced_scene="UNKNOWN"))
            result = graph.invoke(_base_state(path))
            assert result["scene_type"] == "UNKNOWN"
            output = result["structured_output"]
            assert output["scene_type"] == "UNKNOWN"
            assert "reason" in output
        finally:
            os.unlink(path)


class TestGraphErrorHandling:
    def test_missing_image_path_propagates_error(self):
        graph = build_graph(vlm=MockVLM())
        state = _base_state("")
        result = graph.invoke(state)
        assert result["structured_output"]["scene_type"] == "ERROR"
        assert result["structured_output"]["error"] is not None

    def test_nonexistent_file_propagates_error(self):
        graph = build_graph(vlm=MockVLM())
        state = _base_state("/tmp/no_such_file_xyz.jpg")
        result = graph.invoke(state)
        assert result["structured_output"]["scene_type"] == "ERROR"

    def test_default_vlm_is_mock(self):
        path = _make_test_image()
        try:
            graph = build_graph()  # No VLM passed → defaults to MockVLM
            result = graph.invoke(_base_state(path))
            assert "scene_type" in result
        finally:
            os.unlink(path)
