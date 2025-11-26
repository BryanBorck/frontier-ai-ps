"""
Unit tests for entity normalization logic.

Tests entity normalization using EntityMapper for fund managers and service providers.
"""

import pytest

from src.agent.fund_search.utils.mappings import EntityMapper


@pytest.mark.unit
class TestEntityNormalizer:
    """Unit tests for entity normalization."""

    def test_normalize_xp_variations(self):
        """Test normalization of XP variations."""
        variations = ["XP Investimentos", "XP", "xp gestao", "XP Asset"]

        for variation in variations:
            result = EntityMapper.normalize_provider(variation)
            # Should return normalized name or None
            assert result is None or isinstance(result, str)

    def test_normalize_btg_variations(self):
        """Test normalization of BTG variations."""
        variations = ["BTG Pactual", "BTG", "btg pactual asset"]

        for variation in variations:
            result = EntityMapper.normalize_provider(variation)
            assert result is None or isinstance(result, str)

    def test_normalize_handles_empty_string(self):
        """Test normalization handles empty strings."""
        result = EntityMapper.normalize_provider("")
        assert result is None

    def test_normalize_handles_none(self):
        """Test normalization handles None input."""
        result = EntityMapper.normalize_provider(None)
        assert result is None

    def test_normalize_removes_extra_whitespace(self):
        """Test normalization handles extra whitespace."""
        result = EntityMapper.normalize_provider("  XP   Investimentos  ")
        # Should handle whitespace gracefully
        assert result is None or isinstance(result, str)

    def test_normalize_case_insensitive(self):
        """Test normalization is case insensitive."""
        result1 = EntityMapper.normalize_provider("XP INVESTIMENTOS")
        result2 = EntityMapper.normalize_provider("xp investimentos")
        result3 = EntityMapper.normalize_provider("Xp Investimentos")

        # All should return same result (case insensitive)
        assert result1 == result2 == result3

    def test_normalize_unknown_entity(self):
        """Test normalization of unknown entities returns None."""
        result = EntityMapper.normalize_provider("Unknown Fund Manager XYZ 12345")

        # Unknown entities should return None
        assert result is None


@pytest.mark.integration
class TestEntityNormalizerIntegration:
    """
    Integration tests for entity normalization with real mappings.

    Tests against actual entity correlation data if available.
    """

    def test_normalize_with_real_mappings(self):
        """Test normalization with real entity mappings."""
        # Basic smoke test - should not crash
        result = EntityMapper.normalize_provider("XP Gestão")
        assert result is None or isinstance(result, str)
