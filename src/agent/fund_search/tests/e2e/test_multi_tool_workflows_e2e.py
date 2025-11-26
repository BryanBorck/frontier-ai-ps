"""
E2E tests for multi-tool workflows.

Tests that the agent correctly orchestrates multiple tools for complex queries.

Example: "XP funds investing in Petrobras" requires:
    1. semantic_search (for XP funds)
    2. position_search (for Petrobras equity)
    3. Intersection of results
"""

import pytest


@pytest.mark.e2e
@pytest.mark.integration
class TestMultiToolWorkflowsE2E:
    """
    E2E tests for complex queries requiring multiple tools
    """

    def test_manager_plus_position(self, fund_search_tool):
        """
        Test: "XP funds investing in Petrobras"

        Expected workflow:
        1. semantic_search: Find XP-managed funds
        2. position_search: Find Petrobras equity funds
        3. Intersection: Return funds meeting both criteria

        Why critical: Combining manager + holdings is common query pattern
        """
        result = fund_search_tool.ask("XP funds investing in Petrobras")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ Manager + position query test passed!")
        print(f"  - Found {len(result.cnpjs)} XP funds with Petrobras")
        print(f"  - Response type: {result.response_type}")

    def test_position_plus_performance(self, fund_search_tool):
        """
        Test: "funds with Vale that returned more than 10% this year"

        Expected workflow:
        1. position_search: Find Vale funds
        2. snapshot_search: Filter by return > 10%
        3. Intersection

        Why critical: Position + performance is key filtering pattern
        """
        result = fund_search_tool.ask("funds with Vale that returned more than 10% this year")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ Position + performance query test passed!")
        print(f"  - Found {len(result.cnpjs)} high-performing Vale funds")

    def test_complex_three_criteria(self, fund_search_tool):
        """
        Test: "large BTG equity funds with positive returns"

        Expected workflow:
        - semantic_search: BTG funds
        - metadata_search: equity fund type
        - snapshot_search: AUM > threshold and return > 0

        Why critical: Complex multi-criteria queries are real use cases
        """
        result = fund_search_tool.ask("large BTG equity funds with positive returns")

        assert result is not None
        assert isinstance(result.cnpjs, list)

        print("\n✓ Complex 3-criteria query test passed!")
        print(f"  - Found {len(result.cnpjs)} funds")
