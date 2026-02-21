"""VisionAgentState - the shared state flowing through the LangGraph."""

from typing import Optional
from typing_extensions import TypedDict


class VisionAgentState(TypedDict):
    image_path: str          # Input image file path
    image_base64: str        # Base64-encoded image for VLM API
    scene_type: str          # FOOD / MEDICATION / REPORT / UNKNOWN
    confidence: float        # Scene classification confidence (0.0 - 1.0)
    raw_response: str        # Raw text response from VLM
    structured_output: dict  # Parsed, validated structured data
    error: Optional[str]     # Error message if any node fails
