"""Node: image_intake - receive image path(s), validate, encode to base64."""

import base64
import os
from pathlib import Path

from src.vision_agent.state import VisionAgentState

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".avif"}
MAX_FILE_SIZE_MB = 10
MAX_IMAGES = 5


def _validate_and_encode(image_path: str) -> tuple[str | None, str | None]:
    """Validate a single image file and encode to base64.

    Returns:
        (base64_string, None) on success, or (None, error_message) on failure.
    """
    if not image_path:
        return None, "No image path provided."

    path = Path(image_path)

    if not path.exists():
        return None, f"Image file not found: {image_path}"

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return None, (
            f"Unsupported file type '{path.suffix}'. "
            f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    file_size_mb = os.path.getsize(path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return None, f"File too large ({file_size_mb:.1f}MB). Max: {MAX_FILE_SIZE_MB}MB."

    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return encoded, None


def image_intake(state: VisionAgentState) -> dict:
    """Validate image file(s) and encode to base64.

    Returns:
        State update with images_base64 set, or error if validation fails.
    """
    image_paths: list[str] = state.get("image_paths", [])

    if not image_paths:
        return {"error": "No image path provided."}

    if len(image_paths) > MAX_IMAGES:
        return {"error": f"Too many images ({len(image_paths)}). Max: {MAX_IMAGES}."}

    images_base64: list[str] = []
    for img_path in image_paths:
        encoded, err = _validate_and_encode(img_path)
        if err is not None:
            return {"error": err}
        images_base64.append(encoded)

    return {"images_base64": images_base64, "error": None}
