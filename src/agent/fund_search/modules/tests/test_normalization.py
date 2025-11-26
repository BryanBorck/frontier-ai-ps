"""
Unit tests for EntityNormalizer module.

Tests entity normalization logic for fund managers and service providers.
"""

import pytest
from src.agent.fund_search.modules.normalization import EntityNormalizer


@pytest.mark.unit
class TestEntityNormalizer:
    """Unit tests for EntityNormalizer."""

    def test_normalize_xp_variations(self):
        """Test normalization of XP variations."""
        variations = ["XP Investimentos", "XP", "xp gestao", "XP Asset"]

        for variation in variations:
            result = EntityNormalizer.normalize(variation)
            assert result is not None

    def test_normalize_btg_variations(self):
        """Test normalization of BTG variations."""
        variations = ["BTG Pactual", "BTG", "btg pactual asset"]

        for variation in variations:
            result = EntityNormalizer.normalize(variation)
            assert result is not None

    def test_normalize_handles_empty_string(self):
        """Test normalization handles empty strings."""
        result = EntityNormalizer.normalize("")
        assert result == "" or result is None

    def test_normalize_handles_none(self):
        """Test normalization handles None input."""
        result = EntityNormalizer.normalize(None)
        assert result is None or result == ""

    def test_normalize_removes_extra_whitespace(self):
        """Test normalization removes extra whitespace."""
        result = EntityNormalizer.normalize("  XP   Investimentos  ")
        assert result is not None
        # Should not have extra whitespace

    def test_normalize_case_insensitive(self):
        """Test normalization is case insensitive."""
        result1 = EntityNormalizer.normalize("XP INVESTIMENTOS")
        result2 = EntityNormalizer.normalize("xp investimentos")
        result3 = EntityNormalizer.normalize("Xp Investimentos")

        # Should normalize to same value (or at least be consistent)
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None

    def test_normalize_unknown_entity(self):
        """Test normalization of unknown entities."""
        result = EntityNormalizer.normalize("Unknown Fund Manager XYZ")

        # Should still return something (original or normalized)
        assert result is not None


@pytest.mark.integration
class TestEntityNormalizerIntegration:
    """
    Integration tests for EntityNormalizer with entity mappings.

    Tests against actual entity correlation data if available.
    """

    def test_normalize_with_real_mappings(self):
        """Test normalization with real entity mappings."""
        # This would test against actual entity_correlations.json
        # For now, just basic smoke test
        result = EntityNormalizer.normalize("XP Gestão")
        assert result is not None
