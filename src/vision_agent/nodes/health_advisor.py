"""Node: health_advisor — generates localized health advice using text LLM (SeaLION).

This is the "brain" node. It takes the structured recognition output from the
vision VLM (Gemini) and passes it to SeaLION for SG-specific health advice.

Flow: vision VLM recognizes image → this node sends text to SeaLION → advice returned.
"""

import json
import logging
from typing import Optional

from src.vision_agent.llm.base import BaseVLM, VLMError
from src.vision_agent.prompts.advisor import (
    FOOD_ADVICE_PROMPT,
    MEDICATION_ADVICE_PROMPT,
    REPORT_ADVICE_PROMPT,
)
from src.vision_agent.state import VisionAgentState

logger = logging.getLogger(__name__)

_SCENE_PROMPTS = {
    "FOOD": FOOD_ADVICE_PROMPT,
    "MEDICATION": MEDICATION_ADVICE_PROMPT,
    "REPORT": REPORT_ADVICE_PROMPT,
}


def make_health_advisor(text_llm: Optional[BaseVLM] = None):
    """Factory: returns a health_advisor node bound to the given text LLM.

    Args:
        text_llm: Text LLM for generating advice (e.g., SeaLION).
                  If None, the node is a no-op passthrough.
    """

    def health_advisor(state: VisionAgentState) -> dict:
        # Skip if there's an error or no text LLM configured
        if state.get("error") or text_llm is None:
            return {"advice": ""}

        scene_type = state.get("scene_type", "UNKNOWN")
        prompt_template = _SCENE_PROMPTS.get(scene_type)

        # No advice for UNKNOWN scenes
        if prompt_template is None:
            return {"advice": ""}

        structured_output = state.get("structured_output", {})
        recognition_json = json.dumps(structured_output, indent=2, ensure_ascii=False)
        prompt = prompt_template.format(recognition_json=recognition_json)

        try:
            # text_llm.call() — image_base64 is empty since this is text-only
            raw_advice = text_llm.call(prompt, "")
            # Try to parse as JSON to validate, but store raw string
            advice_data = json.loads(raw_advice)
            advice_json = json.dumps(advice_data, ensure_ascii=False)
            logger.info("Health advice generated for %s scene", scene_type)
            return {"advice": advice_json}
        except json.JSONDecodeError:
            # SeaLION returned non-JSON — store raw text as-is
            logger.warning("Health advisor returned non-JSON, storing raw text")
            return {"advice": raw_advice}
        except VLMError as e:
            logger.warning("Health advisor failed: %s — continuing without advice", e)
            return {"advice": ""}

    return health_advisor
