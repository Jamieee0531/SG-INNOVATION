"""Mock VLM implementation for development and testing.

Returns pre-baked JSON responses without making real API calls.
Controlled via scene_type to simulate each path through the graph.
"""

import json
from typing import Optional

from src.vision_agent.llm.base import BaseVLM


_MOCK_RESPONSES: dict[str, str] = {
    "FOOD": json.dumps({
        "scene_type": "FOOD",
        "items": [
            {
                "name": "Hainanese Chicken Rice",
                "quantity": "1 plate",
                "nutrition": {
                    "calories_kcal": 480.0,
                    "carbs_g": 65.0,
                    "protein_g": 28.0,
                    "fat_g": 12.0,
                },
            },
            {
                "name": "Soup (clear)",
                "quantity": "1 bowl",
                "nutrition": {
                    "calories_kcal": 20.0,
                    "carbs_g": 2.0,
                    "protein_g": 1.0,
                    "fat_g": 0.5,
                },
            },
        ],
        "total_calories_kcal": 500.0,
        "meal_type": "lunch",
        "notes": "Estimated portion sizes. Common Singapore hawker meal.",
        "confidence": 0.91,
    }),
    "MEDICATION": json.dumps({
        "scene_type": "MEDICATION",
        "drug_name": "Metformin Hydrochloride",
        "dosage": "500mg",
        "frequency": "twice daily with meals",
        "route": "oral",
        "warnings": ["Do not crush or chew", "Take with food"],
        "expiry_date": "2025-12",
        "confidence": 0.87,
    }),
    "REPORT": json.dumps({
        "scene_type": "REPORT",
        "report_type": "blood_test",
        "indicators": [
            {
                "name": "HbA1c",
                "value": "7.2",
                "unit": "%",
                "reference_range": "4.0-5.6",
                "is_abnormal": True,
            },
            {
                "name": "Fasting Glucose",
                "value": "6.8",
                "unit": "mmol/L",
                "reference_range": "3.9-6.1",
                "is_abnormal": True,
            },
            {
                "name": "Total Cholesterol",
                "value": "4.5",
                "unit": "mmol/L",
                "reference_range": "< 5.2",
                "is_abnormal": False,
            },
        ],
        "report_date": "2024-01-15",
        "lab_name": "Singapore General Hospital",
        "confidence": 0.95,
    }),
    "UNKNOWN": json.dumps({
        "scene_type": "UNKNOWN",
        "reason": "Image does not contain identifiable food, medication, or medical report.",
        "confidence": 0.82,
    }),
}


class MockVLM(BaseVLM):
    """Deterministic mock VLM for dev/testing. No API calls made."""

    def __init__(self, forced_scene: Optional[str] = None) -> None:
        """
        Args:
            forced_scene: If set, always return this scene's mock response.
                          If None, MockVLM tries to infer from prompt keywords.
        """
        self._forced_scene = forced_scene

    @property
    def model_name(self) -> str:
        return "mock-vlm-v1"

    def call(self, prompt: str, image_base64: str) -> str:  # noqa: ARG002
        scene = self._forced_scene or self._infer_scene(prompt)
        return _MOCK_RESPONSES.get(scene, _MOCK_RESPONSES["UNKNOWN"])

    def _infer_scene(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "food" in prompt_lower or "meal" in prompt_lower or "nutrition" in prompt_lower:
            return "FOOD"
        if "medication" in prompt_lower or "drug" in prompt_lower or "prescription" in prompt_lower:
            return "MEDICATION"
        if "report" in prompt_lower or "lab" in prompt_lower or "blood" in prompt_lower:
            return "REPORT"
        return "UNKNOWN"
