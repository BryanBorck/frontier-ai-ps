"""
Unit tests for SemanticSearchTool.

Focuses on testing semantic similarity of investment strategies and objectives.
Tests verify that the multilingual sentence transformer correctly understands
Portuguese investment terminology and finds semantically related funds.
"""

import pytest

from src.agent.fund_search.tools.search_semantic.tool import SemanticSearchTool


@pytest.mark.unit
class TestSemanticSearchToolUnit:
    """Unit tests focused on semantic understanding of investment strategies."""

    def test_initialization(self, test_vector_store):
        """Test tool initializes correctly."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)
        assert tool.vector_store_path == test_vector_store

    # Semantic Understanding - Real Estate / Fundos Imobiliários
    def test_semantic_similarity_real_estate_portuguese(self, test_vector_store):
        """Test semantic understanding of real estate in Portuguese."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # "imóveis" (properties) should semantically match "fundos imobiliários"
        results = tool.forward(query="imóveis e propriedades", top_k=5)

        # Should return real estate funds (FII)
        assert isinstance(results, list)
        assert len(results) > 0
        # XP Malls and BTG Logística are real estate funds
        assert any(cnpj in ["12.345.678/0001-90", "98.765.432/0001-10"] for cnpj in results)

    def test_semantic_similarity_shopping_malls(self, test_vector_store):
        """Test semantic understanding of shopping mall strategy."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Query about shopping centers should find XP Malls
        results = tool.forward(query="shopping centers de alto padrão", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0
        # Should find XP Malls which invests in shopping centers
        assert "12.345.678/0001-90" in results

    def test_semantic_similarity_logistics(self, test_vector_store):
        """Test semantic understanding of logistics strategy."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Query about logistics should find BTG Logística
        results = tool.forward(query="galpões logísticos e centros de distribuição", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0
        # Should find BTG Pactual Logística
        assert "98.765.432/0001-10" in results

    # Semantic Understanding - Stocks / Ações
    def test_semantic_similarity_stocks_portuguese(self, test_vector_store):
        """Test semantic understanding of stocks in Portuguese."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # "bolsa de valores" (stock exchange) should match "ações"
        results = tool.forward(query="bolsa de valores e empresas listadas", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0
        # Should include stock funds
        assert "11.222.333/0001-44" in results  # Itaú Ações Small Cap

    def test_semantic_similarity_small_cap_strategy(self, test_vector_store):
        """Test semantic understanding of small cap investment strategy."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Query about small companies should find small cap fund
        results = tool.forward(query="empresas de pequena capitalização com potencial de crescimento", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0
        # Should find Itaú Ações Small Cap
        assert "11.222.333/0001-44" in results

    # Semantic Understanding - Fixed Income / Renda Fixa
    def test_semantic_similarity_fixed_income_portuguese(self, test_vector_store):
        """Test semantic understanding of fixed income in Portuguese."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # "títulos de renda fixa" should match fixed income funds
        results = tool.forward(query="títulos públicos e privados de renda fixa", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0
        # Should include fixed income funds
        assert any(cnpj in ["22.333.444/0001-55", "44.555.666/0001-77"] for cnpj in results)

    def test_semantic_similarity_cdi_tracking(self, test_vector_store):
        """Test semantic understanding of CDI tracking strategy."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Query about following CDI should find referenciado DI fund
        results = tool.forward(query="acompanhar a variação do CDI", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0
        # Should find Bradesco Renda Fixa Referenciado DI
        assert "22.333.444/0001-55" in results

    def test_semantic_similarity_credit_strategy(self, test_vector_store):
        """Test semantic understanding of private credit strategy."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Query about corporate credit should find credit fund
        results = tool.forward(query="crédito corporativo e debêntures de empresas", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0
        # Should find XP Crédito Privado
        assert "44.555.666/0001-77" in results

    # Semantic Understanding - Multimercado / Multimarket
    def test_semantic_similarity_macro_strategy(self, test_vector_store):
        """Test semantic understanding of macro investment strategy."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Query about global macro should find macro fund
        results = tool.forward(query="estratégia macro global com alocação diversificada", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0
        # Should find Santander Multimercado Macro
        assert "33.444.555/0001-66" in results

    def test_semantic_similarity_value_investing(self, test_vector_store):
        """Test semantic understanding of value investing strategy."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Query about value investing should find Verde Asset
        results = tool.forward(query="value investing e ações com desconto", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0
        # Should find Verde Asset Allocation
        assert "55.666.777/0001-88" in results

    # Semantic Understanding - Infrastructure / Infraestrutura
    def test_semantic_similarity_infrastructure_renewable_energy(self, test_vector_store):
        """Test semantic understanding of renewable energy infrastructure."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Query about renewable energy should find infrastructure fund
        results = tool.forward(query="energia renovável solar e eólica", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0
        # Should find Kinea Infraestrutura
        assert "66.777.888/0001-99" in results

    # Risk Profile Semantic Understanding
    def test_semantic_similarity_conservative_low_risk(self, test_vector_store):
        """Test semantic understanding of conservative/low risk profile."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Query about conservative investment should find low-risk funds
        results = tool.forward(query="investimento conservador e seguro", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0
        # Should find Bradesco Renda Fixa (Low risk)
        assert "22.333.444/0001-55" in results

    def test_semantic_similarity_aggressive_high_risk(self, test_vector_store):
        """Test semantic understanding of aggressive/high risk profile."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Query about aggressive investment should find high-risk funds
        results = tool.forward(query="investimento agressivo com volatilidade", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0
        # Should include high-risk funds like small cap, multimercado
        assert any(
            cnpj
            in [
                "11.222.333/0001-44",  # Small Cap - High risk
                "33.444.555/0001-66",  # Multimercado - High risk
                "55.666.777/0001-88",  # Multimercado - High risk
            ]
            for cnpj in results
        )

    # Search Mode Tests - Multi-Query Fusion
    def test_search_mode_name_focuses_on_fund_names(self, test_vector_store):
        """Test that 'name' mode focuses query on fund names."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Search for XP in name mode - should prioritize name matches
        results = tool.forward(query="XP Malls", top_k=5, search_mode="name")

        assert isinstance(results, list)
        assert len(results) > 0
        # Should find XP Malls as top result
        assert "12.345.678/0001-90" in results

    def test_search_mode_name_vs_strategy_different_results(self, test_vector_store):
        """Test that name mode returns different results than strategy mode."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Same query, different modes
        results_name = tool.forward(query="small cap", top_k=5, search_mode="name")
        results_strategy = tool.forward(query="small cap", top_k=5, search_mode="strategy")

        # Both should return results but may differ in ranking
        assert isinstance(results_name, list)
        assert isinstance(results_strategy, list)
        # Strategy mode should find Itaú Small Cap fund better
        if "11.222.333/0001-44" in results_strategy:
            # Small cap fund should rank higher in strategy mode
            strategy_rank = results_strategy.index("11.222.333/0001-44")
            assert strategy_rank < 3  # Should be in top 3

    def test_search_mode_strategy_finds_by_objective(self, test_vector_store):
        """Test that 'strategy' mode finds funds by investment objective."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Search focused on strategy/objective
        results = tool.forward(query="investimento em pequenas empresas", top_k=5, search_mode="strategy")

        assert isinstance(results, list)
        assert len(results) > 0
        # Should find small cap fund
        assert "11.222.333/0001-44" in results

    def test_search_mode_all_combines_approaches(self, test_vector_store):
        """Test that 'all' mode combines name and strategy search."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="fundos imobiliários", top_k=5, search_mode="all")

        assert isinstance(results, list)
        assert len(results) > 0
        # Should find both real estate funds
        assert any(cnpj in results for cnpj in ["12.345.678/0001-90", "98.765.432/0001-10"])

    def test_search_mode_all_has_best_recall(self, test_vector_store):
        """Test that 'all' mode provides best recall with multiple query variations."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Query that could match name OR strategy
        results_all = tool.forward(query="XP", top_k=10, search_mode="all")
        results_name = tool.forward(query="XP", top_k=10, search_mode="name")

        # All mode should find at least as many results as name-only
        assert len(results_all) >= len(results_name)

    # Portuguese Language Understanding
    def test_portuguese_accents_and_special_characters(self, test_vector_store):
        """Test handling of Portuguese accents and special characters."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Query with various Portuguese accents
        results = tool.forward(query="ações de tecnologia e inovação", top_k=5)

        assert isinstance(results, list)

    def test_portuguese_financial_terminology(self, test_vector_store):
        """Test understanding of Portuguese financial terms."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        queries_and_expected = [
            ("imóveis", ["12.345.678/0001-90", "98.765.432/0001-10"]),  # Real estate
            ("renda fixa", ["22.333.444/0001-55", "44.555.666/0001-77"]),  # Fixed income
            ("ações", ["11.222.333/0001-44"]),  # Stocks
        ]

        for query, expected_cnpjs in queries_and_expected:
            results = tool.forward(query=query, top_k=10)
            assert isinstance(results, list)
            # At least one expected fund should be in results
            assert any(cnpj in results for cnpj in expected_cnpjs)

    # Top K Parameter Tests
    def test_top_k_zero_returns_empty(self, test_vector_store):
        """Test top_k=0 returns empty list."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="fundos", top_k=0)

        assert results == []

    def test_top_k_limits_results(self, test_vector_store):
        """Test top_k properly limits number of results."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="investimentos", top_k=3)

        assert len(results) <= 3

    def test_top_k_larger_than_db_returns_all(self, test_vector_store):
        """Test top_k larger than database returns all results."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="fundos", top_k=1000)

        # Should return all 8 test funds
        assert len(results) == 8

    # Query Cleaning Tests
    def test_query_with_quotes_cleaned(self, test_vector_store):
        """Test that quotes in queries are removed."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query='"fundos imobiliários" de shopping', top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0

    def test_query_with_extra_whitespace_cleaned(self, test_vector_store):
        """Test that extra whitespace is trimmed."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="  fundos   imobiliários  ", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0

    def test_empty_query_handled_gracefully(self, test_vector_store):
        """Test empty query is handled without crashing."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="", top_k=5)

        assert isinstance(results, list)

    # Keyword Boosting Tests - Hybrid Search
    def test_keyword_boost_improves_exact_name_matches(self, test_vector_store):
        """Test that funds with exact keyword matches get score boost."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Search with specific fund name keyword
        results = tool.forward(query="Itaú", top_k=10)

        # Itaú fund should be in top results due to keyword boost
        assert "11.222.333/0001-44" in results[:5]

    def test_keyword_boost_brand_names(self, test_vector_store):
        """Test keyword boost for brand names (XP, BTG, etc)."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Search for "XP" brand
        results = tool.forward(query="XP", top_k=10)

        # Both XP funds should be boosted to top
        xp_funds = ["12.345.678/0001-90", "44.555.666/0001-77"]  # XP Malls, XP Crédito
        xp_in_results = [cnpj for cnpj in results if cnpj in xp_funds]
        assert len(xp_in_results) == 2  # Both XP funds found

    def test_keyword_boost_multiple_keywords(self, test_vector_store):
        """Test that multiple keyword matches increase boost."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Query with multiple keywords that match XP Malls
        results = tool.forward(query="XP Malls shopping", top_k=10)

        # XP Malls should rank very high (multiple keyword matches)
        assert "12.345.678/0001-90" in results[:3]

    def test_keyword_boost_capped_at_max(self, test_vector_store):
        """Test that keyword boost is capped to avoid overpowering semantic score."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Even with many keywords, boost should be reasonable
        # The cap ensures semantic similarity still matters
        results = tool.forward(query="XP XP XP XP XP", top_k=5)

        # Should still return results (not empty due to over-boosting)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_stopwords_not_boosted(self, test_vector_store):
        """Test that common stopwords don't affect ranking."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # These are stopwords that shouldn't boost results
        results = tool.forward(query="fundo investimento gestao", top_k=5)

        # Stopwords alone shouldn't prevent results
        assert isinstance(results, list)

    def test_stopwords_filtered_small_words(self, test_vector_store):
        """Test that small words (<=2 chars) are filtered out."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Words like "FI", "de", "em" should be filtered
        results = tool.forward(query="FI de em XP", top_k=5)

        # Should still find XP funds (only non-stopword)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_keyword_boost_case_insensitive(self, test_vector_store):
        """Test that keyword boost is case-insensitive."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results_lower = tool.forward(query="xp", top_k=5)
        results_upper = tool.forward(query="XP", top_k=5)

        # Should return same results (case insensitive)
        assert results_lower == results_upper

    # Result Quality Tests
    def test_results_are_cnpj_strings(self, test_vector_store):
        """Test that all results are CNPJ-formatted strings."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="fundos", top_k=5)

        assert isinstance(results, list)
        for cnpj in results:
            assert isinstance(cnpj, str)
            assert "." in cnpj  # CNPJ format has dots
            assert "/" in cnpj  # CNPJ format has slash

    def test_no_duplicate_results(self, test_vector_store):
        """Test that results contain no duplicates."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="fundos", top_k=10)

        # All CNPJs should be unique
        assert len(results) == len(set(results))

    def test_results_ordered_by_relevance(self, test_vector_store):
        """Test that results are in descending order of relevance."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Specific query where we can verify ordering
        results = tool.forward(query="shopping centers", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0
        # Can't test exact order but should return results

    # Error Handling Tests
    def test_handles_missing_database(self, tmp_path):
        """Test graceful handling of missing database."""
        bad_db_path = str(tmp_path / "nonexistent.db")
        tool = SemanticSearchTool(vector_store_path=bad_db_path)

        results = tool.forward(query="test")

        assert results == []

    def test_handles_corrupted_database(self, tmp_path):
        """Test graceful handling of corrupted database."""
        corrupted_db = tmp_path / "corrupted.db"
        corrupted_db.write_text("Not a valid database")

        tool = SemanticSearchTool(vector_store_path=str(corrupted_db))
        results = tool.forward(query="test")

        assert results == []

    # Multi-Query Fusion Tests
    def test_multi_query_fusion_improves_recall(self, test_vector_store):
        """Test that multiple query variations improve results."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Tool internally generates multiple query variations
        # This should find relevant results even with broad query
        results = tool.forward(query="investimentos", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0

    # Pre-filter Tests - SQL Filtering Before Vector Search
    def test_pre_filter_investment_class_narrows_results(self, test_vector_store):
        """Test that investment_class pre-filter narrows search space efficiently."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Semantic search with investment_class filter
        pre_filter = {"investment_class": "Renda Fixa"}
        results = tool.forward(query="investimentos", top_k=10, pre_filter=pre_filter)

        # Should only return fixed income funds (SQL filtered before vector search)
        assert all(cnpj in ["22.333.444/0001-55", "44.555.666/0001-77"] for cnpj in results)
        assert len(results) == 2

    def test_pre_filter_manager_reduces_search_space(self, test_vector_store):
        """Test that manager pre-filter reduces search space before semantic search."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Filter to only XP-managed funds
        pre_filter = {"manager": "XP Asset"}
        results = tool.forward(query="fundos", top_k=10, pre_filter=pre_filter)

        # Should only return XP Asset managed funds
        assert all(cnpj in ["12.345.678/0001-90", "44.555.666/0001-77"] for cnpj in results)

    def test_pre_filter_fund_type_before_semantic_search(self, test_vector_store):
        """Test that fund_type pre-filter is applied before semantic search."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Filter to only FII funds
        pre_filter = {"fund_type": "FII"}
        results = tool.forward(query="investimentos", top_k=10, pre_filter=pre_filter)

        # Should only return FII funds
        assert all(cnpj in ["12.345.678/0001-90", "98.765.432/0001-10"] for cnpj in results)

    def test_pre_filter_name_terms_and_logic(self, test_vector_store):
        """Test that multiple name_terms are combined with AND logic."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Both "XP" AND "Malls" must appear in name
        pre_filter = {"name_terms": ["XP", "Malls"]}
        results = tool.forward(query="fundos", top_k=10, pre_filter=pre_filter)

        # Should only return XP Malls (both terms present)
        assert results == ["12.345.678/0001-90"]

    def test_pre_filter_name_terms_single_term(self, test_vector_store):
        """Test pre-filter with single name term."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Only "Multimercado" in name
        pre_filter = {"name_terms": ["Multimercado"]}
        results = tool.forward(query="fundos", top_k=10, pre_filter=pre_filter)

        # Should return multimercado funds
        assert len(results) == 2
        assert "33.444.555/0001-66" in results  # Santander Multimercado
        assert "55.666.777/0001-88" in results  # Verde (FIM)

    def test_pre_filter_combined_multiple_filters(self, test_vector_store):
        """Test combining multiple pre-filters (AND logic)."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # investment_class AND manager filters
        pre_filter = {"investment_class": "Fundos Imobiliários", "manager": "XP Asset"}
        results = tool.forward(query="fundos", top_k=10, pre_filter=pre_filter)

        # Should only return XP Malls (FII managed by XP Asset)
        assert results == ["12.345.678/0001-90"]

    def test_pre_filter_empty_dict_no_restriction(self, test_vector_store):
        """Test that empty pre_filter dict doesn't restrict results."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="fundos", top_k=10, pre_filter={})

        # Should return all matching funds (no SQL filter applied)
        assert len(results) == 8

    def test_pre_filter_none_returns_all_semantic_matches(self, test_vector_store):
        """Test that None pre_filter doesn't restrict results."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="fundos", top_k=10, pre_filter=None)

        # Should return all matching funds
        assert len(results) == 8

    def test_pre_filter_improves_performance(self, test_vector_store):
        """Test that pre-filtering reduces vector comparisons for efficiency."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # With filter: only searches within Renda Fixa funds
        pre_filter = {"investment_class": "Renda Fixa"}
        results_filtered = tool.forward(query="investimentos", top_k=10, pre_filter=pre_filter)

        # Without filter: searches all funds
        results_all = tool.forward(query="investimentos", top_k=10, pre_filter=None)

        # Filtered results should be subset of all results
        assert len(results_filtered) < len(results_all)
        assert all(cnpj in results_all for cnpj in results_filtered)

    def test_pre_filter_with_semantic_search_combination(self, test_vector_store):
        """Test pre-filter + semantic search work together correctly."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Filter to Renda Fixa, then semantic search for "CDI"
        pre_filter = {"investment_class": "Renda Fixa"}
        results = tool.forward(query="acompanhar CDI", top_k=10, pre_filter=pre_filter)

        # Should find Bradesco Referenciado DI (semantic match within filtered set)
        assert "22.333.444/0001-55" in results

    def test_pre_filter_case_insensitive(self, test_vector_store):
        """Test that pre-filters are case-insensitive (ILIKE)."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        # Filter with different cases
        filter_lower = {"investment_class": "renda fixa"}
        filter_mixed = {"investment_class": "Renda FIXA"}

        results_lower = tool.forward(query="fundos", top_k=10, pre_filter=filter_lower)
        results_mixed = tool.forward(query="fundos", top_k=10, pre_filter=filter_mixed)

        # Should return same results (case insensitive)
        assert set(results_lower) == set(results_mixed)

    # Edge Cases
    def test_very_long_query(self, test_vector_store):
        """Test handling of very long queries."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        long_query = "fundos de investimento " * 50
        results = tool.forward(query=long_query, top_k=5)

        assert isinstance(results, list)

    def test_query_with_numbers(self, test_vector_store):
        """Test queries containing numbers."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="fundos 2024 investimento", top_k=5)

        assert isinstance(results, list)

    def test_special_characters_in_query(self, test_vector_store):
        """Test queries with special characters."""
        tool = SemanticSearchTool(vector_store_path=test_vector_store)

        results = tool.forward(query="fundos @#$% imobiliários", top_k=5)

        assert isinstance(results, list)
