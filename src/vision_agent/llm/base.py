"""Abstract base class for VLM (Vision Language Model) interface.

Design goal: SEA-LION is just one implementation.
Swap models by swapping implementations, not graph logic.
"""

from abc import ABC, abstractmethod


class BaseVLM(ABC):
    """Abstract VLM interface. All VLM implementations must subclass this."""

    @abstractmethod
    def call(self, prompt: str, image_base64: str) -> str:
        """Send a prompt + image to the VLM and return the raw text response.

        Args:
            prompt: The text prompt / instruction.
            image_base64: Base64-encoded image string.

        Returns:
            Raw text response from the model.

        Raises:
            VLMError: If the API call fails.
        """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Human-readable model identifier."""


class VLMError(Exception):
    """Raised when a VLM API call fails."""
