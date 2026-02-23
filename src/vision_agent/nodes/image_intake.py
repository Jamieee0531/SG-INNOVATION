"""Node: image_intake - receive image path, validate, encode to base64."""

import base64
import os
from pathlib import Path

from src.vision_agent.state import VisionAgentState

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".avif"}
MAX_FILE_SIZE_MB = 10


def image_intake(state: VisionAgentState) -> dict:
    """Validate image file and encode to base64.

    Returns:
        State update with image_base64 set, or error if validation fails.
    """
    image_path = state.get("image_path", "")

    if not image_path:
        return {"error": "No image path provided."}

    path = Path(image_path)

    if not path.exists():
        return {"error": f"Image file not found: {image_path}"}

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return {
            "error": (
                f"Unsupported file type '{path.suffix}'. "
                f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
            )
        }

    file_size_mb = os.path.getsize(path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return {"error": f"File too large ({file_size_mb:.1f}MB). Max: {MAX_FILE_SIZE_MB}MB."}

    with open(path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    return {"image_base64": image_base64, "error": None}
