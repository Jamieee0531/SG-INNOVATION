"""Tests for configuration module."""

import os
import pytest

from src.vision_agent.config import Settings, VLMProvider, get_settings


class TestSettings:
    def test_defaults_to_mock_provider(self):
        s = Settings()
        assert s.vlm_provider == VLMProvider.MOCK

    def test_log_level_default(self):
        s = Settings()
        assert s.log_level == "INFO"

    def test_max_image_size_default(self):
        s = Settings()
        assert s.max_image_size_mb == 10.0

    def test_retry_defaults(self):
        s = Settings()
        assert s.vlm_max_retries == 3
        assert s.vlm_retry_delay_s == 1.0

    def test_sealion_validation_raises_without_key(self):
        s = Settings(vlm_provider=VLMProvider.SEALION, sealion_api_key="", sealion_api_url="")
        with pytest.raises(ValueError, match="SEALION_API_KEY"):
            s.validate_sealion_config()

    def test_sealion_validation_raises_without_url(self):
        s = Settings(vlm_provider=VLMProvider.SEALION, sealion_api_key="key123", sealion_api_url="")
        with pytest.raises(ValueError, match="SEALION_API_URL"):
            s.validate_sealion_config()

    def test_sealion_validation_passes_with_both(self):
        s = Settings(
            vlm_provider=VLMProvider.SEALION,
            sealion_api_key="key123",
            sealion_api_url="https://api.example.com",
        )
        s.validate_sealion_config()  # should not raise

    def test_mock_provider_skips_sealion_validation(self):
        s = Settings(vlm_provider=VLMProvider.MOCK)
        s.validate_sealion_config()  # no-op, should not raise

    def test_get_settings_returns_settings_instance(self):
        s = get_settings()
        assert isinstance(s, Settings)

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("VLM_MAX_RETRIES", "5")
        s = Settings()
        assert s.log_level == "DEBUG"
        assert s.vlm_max_retries == 5
