"""Tests for Pydantic output schemas."""

import pytest
from pydantic import ValidationError

from src.vision_agent.schemas.outputs import (
    FoodItem,
    FoodOutput,
    MedicationOutput,
    NutritionInfo,
    ReportIndicator,
    ReportOutput,
    SceneType,
    UnknownOutput,
)


class TestSceneType:
    def test_valid_values(self):
        assert SceneType.FOOD == "FOOD"
        assert SceneType.MEDICATION == "MEDICATION"
        assert SceneType.REPORT == "REPORT"
        assert SceneType.UNKNOWN == "UNKNOWN"


class TestFoodOutput:
    def test_valid_food_output(self):
        data = {
            "scene_type": "FOOD",
            "items": [
                {
                    "name": "Chicken Rice",
                    "quantity": "1 plate",
                    "nutrition": {
                        "calories_kcal": 450.0,
                        "carbs_g": 60.0,
                        "protein_g": 25.0,
                        "fat_g": 12.0,
                    },
                }
            ],
            "total_calories_kcal": 450.0,
            "meal_type": "lunch",
            "confidence": 0.92,
        }
        output = FoodOutput(**data)
        assert output.scene_type == SceneType.FOOD
        assert len(output.items) == 1
        assert output.items[0].name == "Chicken Rice"
        assert output.total_calories_kcal == 450.0

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            FoodOutput(scene_type="FOOD", total_calories_kcal=400.0, confidence=0.9)

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            FoodOutput(
                scene_type="FOOD",
                items=[],
                total_calories_kcal=0,
                meal_type="lunch",
                confidence=1.5,  # > 1.0
            )

    def test_nutrition_optional_fields(self):
        item = FoodItem(
            name="Kaya Toast",
            quantity="2 slices",
            nutrition=NutritionInfo(calories_kcal=180.0),
        )
        assert item.nutrition.carbs_g is None
        assert item.nutrition.protein_g is None


class TestMedicationOutput:
    def test_valid_medication(self):
        data = {
            "scene_type": "MEDICATION",
            "drug_name": "Metformin",
            "dosage": "500mg",
            "frequency": "twice daily",
            "route": "oral",
            "confidence": 0.88,
        }
        output = MedicationOutput(**data)
        assert output.drug_name == "Metformin"
        assert output.dosage == "500mg"

    def test_optional_fields_default_none(self):
        data = {
            "scene_type": "MEDICATION",
            "drug_name": "Insulin",
            "dosage": "10 units",
            "frequency": "once daily",
            "confidence": 0.75,
        }
        output = MedicationOutput(**data)
        assert output.route is None
        assert output.warnings is None
        assert output.expiry_date is None


class TestReportOutput:
    def test_valid_report(self):
        data = {
            "scene_type": "REPORT",
            "report_type": "blood_test",
            "indicators": [
                {
                    "name": "HbA1c",
                    "value": "7.2",
                    "unit": "%",
                    "reference_range": "4.0-5.6",
                    "is_abnormal": True,
                }
            ],
            "report_date": "2024-01-15",
            "confidence": 0.95,
        }
        output = ReportOutput(**data)
        assert output.report_type == "blood_test"
        assert output.indicators[0].name == "HbA1c"
        assert output.indicators[0].is_abnormal is True

    def test_indicator_abnormal_defaults_false(self):
        indicator = ReportIndicator(name="Glucose", value="5.5", unit="mmol/L")
        assert indicator.is_abnormal is False


class TestUnknownOutput:
    def test_valid_unknown(self):
        output = UnknownOutput(
            scene_type="UNKNOWN",
            reason="Image does not contain food, medication, or medical report",
            confidence=0.85,
        )
        assert output.scene_type == SceneType.UNKNOWN
        assert "food" in output.reason
