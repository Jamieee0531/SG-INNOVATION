"""Tests for image_intake node."""

import base64
import os
import tempfile

import pytest
from PIL import Image

from src.vision_agent.nodes.image_intake import image_intake


def _make_test_image(suffix: str = ".jpg") -> str:
    """Create a temporary test image file, return its path."""
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        img.save(f.name)
        return f.name


class TestImageIntake:
    def test_valid_jpeg_returns_base64(self):
        path = _make_test_image(".jpg")
        try:
            state = {"image_path": path, "image_base64": "", "scene_type": "",
                     "confidence": 0.0, "raw_response": "", "structured_output": {}, "error": None}
            result = image_intake(state)
            assert result["error"] is None
            assert len(result["image_base64"]) > 0
            # Verify it's valid base64
            decoded = base64.b64decode(result["image_base64"])
            assert len(decoded) > 0
        finally:
            os.unlink(path)

    def test_valid_png_returns_base64(self):
        path = _make_test_image(".png")
        try:
            state = {"image_path": path, "image_base64": "", "scene_type": "",
                     "confidence": 0.0, "raw_response": "", "structured_output": {}, "error": None}
            result = image_intake(state)
            assert result["error"] is None
        finally:
            os.unlink(path)

    def test_missing_path_returns_error(self):
        state = {"image_path": "", "image_base64": "", "scene_type": "",
                 "confidence": 0.0, "raw_response": "", "structured_output": {}, "error": None}
        result = image_intake(state)
        assert result["error"] is not None
        assert "No image path" in result["error"]

    def test_nonexistent_file_returns_error(self):
        state = {"image_path": "/tmp/definitely_does_not_exist_12345.jpg",
                 "image_base64": "", "scene_type": "", "confidence": 0.0,
                 "raw_response": "", "structured_output": {}, "error": None}
        result = image_intake(state)
        assert result["error"] is not None
        assert "not found" in result["error"]

    def test_unsupported_extension_returns_error(self):
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as f:
            f.write(b"GIF89a")
            path = f.name
        try:
            state = {"image_path": path, "image_base64": "", "scene_type": "",
                     "confidence": 0.0, "raw_response": "", "structured_output": {}, "error": None}
            result = image_intake(state)
            assert result["error"] is not None
            assert "Unsupported" in result["error"]
        finally:
            os.unlink(path)

    def test_file_too_large_returns_error(self):
        """Simulate a file that exceeds the 10MB limit via mock."""
        from unittest.mock import patch
        path = _make_test_image(".jpg")
        try:
            with patch(
                "src.vision_agent.nodes.image_intake.os.path.getsize",
                return_value=11 * 1024 * 1024,  # 11MB
            ):
                state = {"image_path": path, "image_base64": "", "scene_type": "",
                         "confidence": 0.0, "raw_response": "", "structured_output": {}, "error": None}
                result = image_intake(state)
                assert result["error"] is not None
                assert "too large" in result["error"]
        finally:
            os.unlink(path)

    def test_webp_extension_supported(self):
        """WebP images should be accepted."""
        img = Image.new("RGB", (100, 100), color=(0, 255, 0))
        with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as f:
            img.save(f.name, format="WEBP")
            path = f.name
        try:
            state = {"image_path": path, "image_base64": "", "scene_type": "",
                     "confidence": 0.0, "raw_response": "", "structured_output": {}, "error": None}
            result = image_intake(state)
            assert result["error"] is None
            assert len(result["image_base64"]) > 0
        finally:
            os.unlink(path)

    def test_jpeg_extension_supported(self):
        """Both .jpg and .jpeg extensions should be accepted."""
        path = _make_test_image(".jpeg")
        try:
            state = {"image_path": path, "image_base64": "", "scene_type": "",
                     "confidence": 0.0, "raw_response": "", "structured_output": {}, "error": None}
            result = image_intake(state)
            assert result["error"] is None
        finally:
            os.unlink(path)
