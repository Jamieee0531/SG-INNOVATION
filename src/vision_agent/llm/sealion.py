"""SEA-LION VLM implementation (placeholder - to be completed when API details provided).

Implements the BaseVLM interface using AI Singapore's SEA-LION API.
"""

import os

import httpx

from src.vision_agent.llm.base import BaseVLM, VLMError


class SeaLionVLM(BaseVLM):
    """SEA-LION API client. Reads credentials from environment variables."""

    def __init__(self) -> None:
        self._api_key = os.environ.get("SEALION_API_KEY", "")
        self._api_url = os.environ.get("SEALION_API_URL", "")
        if not self._api_key or not self._api_url:
            raise VLMError(
                "SEALION_API_KEY and SEALION_API_URL must be set in environment."
            )

    @property
    def model_name(self) -> str:
        return "sea-lion-vlm"

    def call(self, prompt: str, image_base64: str) -> str:
        """Call SEA-LION VLM API.

        NOTE: Exact request/response format TBD once API docs are provided.
        This is a placeholder structure following common VLM API patterns.
        """
        try:
            response = httpx.post(
                self._api_url,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sea-lion-vlm",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    },
                                },
                            ],
                        }
                    ],
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            # TODO: Adjust to actual SEA-LION response structure
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            raise VLMError(f"SEA-LION API error {e.response.status_code}: {e.response.text}") from e
        except httpx.RequestError as e:
            raise VLMError(f"SEA-LION network error: {e}") from e
