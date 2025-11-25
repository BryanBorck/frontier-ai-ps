import dspy

from src.agent.models.fund import FundResult, MergedSearchResults, SearchResultItem
from src.agent.models.query import (
    FundSearchCriteria,
    ParsedQuery,
    PositionSearchCriteria,
)
from src.agent.modules.normalization import EntityNormalizer
from src.agent.tools.search_funds.tool import FundSearchTool
from src.agent.tools.search_performance.tool import PerformanceSearchTool
from src.agent.tools.search_positions.tool import PositionSearchTool
from src.agent.tools.search_semantic.tool import SemanticSearchTool
from src.agent.tools.search_snapshots.tool import SnapshotSearchTool
from src.agent.utils.tracing import TracingManager


class SearchRouter:
    """
    Routes parsed query to appropriate search tools based on INTENTS.

    INTENT → TOOL MAPPING:
    - find_by_name → SemanticSearchTool
    - find_by_strategy → SemanticSearchTool
    - find_by_criteria → FundSearchTool
    - find_by_exposure → PositionSearchTool
    - has_numeric_filter → SnapshotSearchTool / PerformanceSearchTool
    """

    def __init__(
        self,
        fund_tool: FundSearchTool,
        position_tool: PositionSearchTool,
        snapshot_tool: SnapshotSearchTool,
        semantic_tool: SemanticSearchTool,
        performance_tool: PerformanceSearchTool,
        normalizer: EntityNormalizer,
        tracer: TracingManager,
    ):
        self.fund_tool = fund_tool
        self.position_tool = position_tool
        self.snapshot_tool = snapshot_tool
        self.semantic_tool = semantic_tool
        self.performance_tool = performance_tool
        self.normalizer = normalizer
        self.tracer = tracer

    def execute(
        self, parsed: ParsedQuery, context_fund_ids: list[str] | None = None
    ) -> list[FundResult]:
        """
        Execute search based on INTENTS in parsed query.
        Routes to appropriate tools based on what the user is asking for.

        Args:
            parsed: The parsed query with intents and extracted entities.
            context_fund_ids: Fund IDs from previous turn (for follow-up context).
        """
        all_results: list[FundResult] = []
        intents = parsed.intents

        # --- Normalize entities ---
        self._normalize_query(parsed)

        # Determine result limit (default 20 for semantic, 50 for others)
        # If user specified a number (e.g. "top 10"), use that.
        limit_override = None
        if parsed.numeric_filter and parsed.numeric_filter.top_n:
            limit_override = parsed.numeric_filter.top_n

        semantic_limit = limit_override or 20
        structured_limit = limit_override or 50

        # --- STEP 0: Targeted Lookup (Explicit Context) ---
        if parsed.targeted_fund_ids:
            # 1. Fetch metadata from SQL (FundSearchTool)
            # Use empty criteria as we are searching by ID
            metadata_results = self._call_fund_tool(
                criteria=None,
                fund_ids=parsed.targeted_fund_ids,
                limit=len(parsed.targeted_fund_ids),
                reason="targeted_lookup_metadata",
            )
            all_results.extend(metadata_results)

            # 2. Fetch text content from Vector DB (SemanticSearchTool)
            content_results = self._call_semantic_lookup(
                parsed.targeted_fund_ids, reason="targeted_lookup_content"
            )
            all_results.extend(content_results)

        # --- STEP 1: Semantic Search (find_by_name or find_by_strategy) ---
        # Use full query for semantic search - it handles fuzzy matching and multi-query fusion
        if "find_by_name" in intents or "find_by_strategy" in intents:
            query_text = parsed.semantic_query or parsed.query
            if query_text:
                # Determine search mode based on intent
                if "find_by_name" in intents and "find_by_strategy" not in intents:
                    search_mode = "name"
                    reason = "name_search"
                else:
                    # For strategy search OR combined, use "all" to catch names that contain the strategy keyword (e.g. "Ouro")
                    search_mode = "all"
                    reason = (
                        "strategy_search"
                        if "find_by_strategy" in intents
                        else "name_and_strategy_search"
                    )

                # Extract Manager Filter from extracted entities
                pre_filter = {}
                if parsed.service_provider_entity:
                    # Take the first provider as the primary manager filter
                    pre_filter["manager"] = parsed.service_provider_entity[0]

                # Extract Category Filters (Class/Type) for Semantic Search
                if parsed.investment_class:
                    pre_filter["investment_class"] = parsed.investment_class[0]
                if parsed.fund_type:
                    pre_filter["fund_type"] = parsed.fund_type[0]

                # Add Name Terms Filter (e.g. "ouro" for "gold fund")
                if parsed.required_name_terms:
                    pre_filter["name_terms"] = parsed.required_name_terms

                semantic_results = self._call_semantic_tool(
                    query_text, semantic_limit, reason, search_mode, pre_filter
                )
                all_results.extend(semantic_results)

        # --- STEP 2: Structured Search (find_by_criteria) ---
        # Only use FundSearchTool for explicit structured filters
        if "find_by_criteria" in intents:
            fund_criteria = FundSearchCriteria(
                fund_type=parsed.fund_type,
                investment_class=parsed.investment_class,
                target_audience=parsed.target_audience,
                service_provider_entity=parsed.service_provider_entity,
                fund_of_funds=parsed.fund_of_funds,
                manager_type=parsed.manager_type,
                is_exclusive_fund=parsed.is_exclusive_fund,
                can_invest_abroad_100_pct=parsed.can_invest_abroad_100_pct,
                has_long_term_taxation=parsed.has_long_term_taxation,
            )

            # Only call if there are actual criteria to filter on
            if fund_criteria.has_any_criteria():
                criteria_results = self._call_fund_tool(
                    fund_criteria, limit=structured_limit, reason="criteria"
                )
                all_results.extend(criteria_results)

        # --- STEP 3: Exposure Search (find_by_exposure) ---
        if "find_by_exposure" in intents:
            position_criteria = PositionSearchCriteria(
                asset_name=parsed.asset_name,
                asset_tickers=parsed.asset_tickers,
                asset_type=parsed.asset_type,
            )

            # Get fund IDs from previous results if any (to filter)
            fund_ids_filter = [r.fund_id for r in all_results] if all_results else None

            # If no current results but we have context, use context to filter exposure?
            # Usually exposure search is independent unless "do THEY hold...".
            # But if all_results is empty, we might want to search globally OR use context.
            # Let's default to context if available AND all_results is empty.
            if not fund_ids_filter and context_fund_ids:
                fund_ids_filter = context_fund_ids

            exposure_results = self._call_position_tool(
                position_criteria, fund_ids_filter, structured_limit, "exposure"
            )

            if fund_ids_filter:
                # Filter to only funds that have the exposure
                all_results = exposure_results
            else:
                all_results.extend(exposure_results)

        # --- STEP 4: Numeric Filter (has_numeric_filter) ---
        if "has_numeric_filter" in intents and parsed.numeric_filter:
            if parsed.numeric_filter.metric == "return":
                # Performance tool handles its own filtering usually, but maybe needs ID filter?
                # Current impl doesn't take IDs. Assuming global search unless refined.
                perf_results = self._call_performance_tool(
                    parsed.numeric_filter, structured_limit, "performance"
                )
                all_results.extend(perf_results)
            else:
                # Snapshot filter (AUM, holders)
                # Use current results OR context results
                fund_ids = [r.fund_id for r in all_results] if all_results else context_fund_ids

                snapshot_results = self._call_snapshot_tool(
                    parsed.numeric_filter, fund_ids, structured_limit, "snapshot"
                )

                if fund_ids:
                    # Apply as filter/enrichment
                    snapshot_fund_ids = {r.fund_id for r in snapshot_results}
                    if all_results:
                        # Filter existing results
                        all_results = [r for r in all_results if r.fund_id in snapshot_fund_ids]
                    else:
                        # Use snapshot results directly (enriched context funds)
                        all_results = snapshot_results

                    # Merge snapshot data
                    snapshot_map = {r.fund_id: r for r in snapshot_results}
                    for result in all_results:
                        if result.fund_id in snapshot_map:
                            result.aum = snapshot_map[result.fund_id].aum
                            result.holders = snapshot_map[result.fund_id].holders
                else:
                    all_results = snapshot_results

        return all_results

    def _normalize_query(self, parsed: ParsedQuery) -> None:
        """Normalize query entities."""
        if parsed.asset_name:
            normalized_assets = []
            for raw_name in parsed.asset_name:
                norm_result = self.normalizer(query_text=raw_name, entity_type="ASSET")
                normalized_assets.append(norm_result.normalized_name or raw_name)
            parsed.asset_name = normalized_assets

        if parsed.service_provider_entity:
            normalized_providers = []
            for raw_provider in parsed.service_provider_entity:
                norm_result = self.normalizer(query_text=raw_provider, entity_type="PROVIDER")
                normalized_providers.append(norm_result.normalized_name or raw_provider)
            parsed.service_provider_entity = normalized_providers

    # --- Traced Tool Calls ---

    def _format_results_for_trace(
        self, results: list[FundResult], max_items: int = 5
    ) -> list[dict]:
        """Format results for trace output with key fund info."""
        return [
            {
                "fund_id": r.fund_id,
                "legal_name": r.legal_name,
                "cnpj": r.cnpj,
                "fund_type": r.fund_type,
                "match_score": r.match_score,
            }
            for r in results[:max_items]
        ]

    def _call_fund_tool(
        self,
        criteria: FundSearchCriteria | None,
        name: str | None = None,
        fund_ids: list[str] | None = None,
        limit: int = 50,
        reason: str = "fund_search",
    ) -> list[FundResult]:
        with self.tracer.tool_call(
            "FundSearchTool",
            {
                "criteria": criteria.model_dump() if criteria else None,
                "name": name,
                "fund_ids_count": len(fund_ids) if fund_ids else 0,
                "limit": limit,
                "reason": reason,
            },
        ) as span:
            results = self.fund_tool(criteria=criteria, name=name, fund_ids=fund_ids, limit=limit)
            span.set_outputs(
                {
                    "result_count": len(results),
                    "top_results": self._format_results_for_trace(results),
                }
            )
            return results

    def _call_position_tool(
        self,
        criteria: PositionSearchCriteria,
        fund_ids: list[str] | None,
        limit: int,
        reason: str,
    ) -> list[FundResult]:
        with self.tracer.tool_call(
            "PositionSearchTool",
            {
                "criteria": criteria.model_dump() if criteria else None,
                "fund_ids_count": len(fund_ids) if fund_ids else 0,
                "limit": limit,
                "reason": reason,
            },
        ) as span:
            results = self.position_tool(criteria=criteria, fund_ids=fund_ids, limit=limit)
            span.set_outputs(
                {
                    "result_count": len(results),
                    "top_results": self._format_results_for_trace(results),
                }
            )
            return results

    def _call_snapshot_tool(
        self,
        numeric_filter,
        fund_ids: list[str] | None,
        limit: int,
        reason: str,
    ) -> list[FundResult]:
        with self.tracer.tool_call(
            "SnapshotSearchTool",
            {
                "numeric_filter": numeric_filter.model_dump() if numeric_filter else None,
                "fund_ids_count": len(fund_ids) if fund_ids else 0,
                "limit": limit,
                "reason": reason,
            },
        ) as span:
            results = self.snapshot_tool(
                numeric_filter=numeric_filter, fund_ids=fund_ids, limit=limit
            )
            span.set_outputs(
                {
                    "result_count": len(results),
                    "top_results": self._format_results_for_trace(results),
                }
            )
            return results

    def _call_semantic_tool(
        self,
        query: str,
        top_k: int,
        reason: str,
        search_mode: str = "all",
        pre_filter: dict | None = None,
    ) -> list[FundResult]:
        with self.tracer.tool_call(
            "SemanticSearchTool",
            {
                "query": query,
                "top_k": top_k,
                "search_mode": search_mode,
                "pre_filter": pre_filter,
                "reason": reason,
            },
        ) as span:
            results = self.semantic_tool(
                query=query, top_k=top_k, search_mode=search_mode, pre_filter=pre_filter
            )
            span.set_outputs(
                {
                    "result_count": len(results),
                    "top_results": self._format_results_for_trace(results),
                }
            )
            return results

    def _call_performance_tool(self, numeric_filter, limit: int, reason: str) -> list[FundResult]:
        with self.tracer.tool_call(
            "PerformanceSearchTool",
            {
                "numeric_filter": numeric_filter.model_dump() if numeric_filter else None,
                "limit": limit,
                "reason": reason,
            },
        ) as span:
            results = self.performance_tool(numeric_filter=numeric_filter, limit=limit)
            span.set_outputs(
                {
                    "result_count": len(results),
                    "top_results": self._format_results_for_trace(results),
                }
            )
            return results

    def _call_semantic_lookup(self, fund_ids: list[str], reason: str) -> list[FundResult]:
        with self.tracer.tool_call(
            "SemanticSearchTool.get_by_ids",
            {"fund_ids": fund_ids, "reason": reason},
        ) as span:
            results = self.semantic_tool.get_by_ids(fund_ids)
            span.set_outputs(
                {
                    "result_count": len(results),
                    "top_results": self._format_results_for_trace(results),
                }
            )
            return results


class SearchManager(dspy.Module):
    """Orchestrates search execution and result merging."""

    def __init__(
        self,
        db_path: str = "src/infrastructure/database/br_funds.db",
        vector_store_path: str = "src/infrastructure/database/vector_store.db",
        tracer: TracingManager | None = None,
    ):
        super().__init__()

        self.normalizer = EntityNormalizer()
        self.fund_tool = FundSearchTool(db_path)
        self.position_tool = PositionSearchTool(db_path)
        self.snapshot_tool = SnapshotSearchTool(db_path)
        self.semantic_tool = SemanticSearchTool(vector_store_path)
        self.performance_tool = PerformanceSearchTool(db_path)

        self.tracer = tracer or TracingManager(enabled=False)

        self.router = SearchRouter(
            self.fund_tool,
            self.position_tool,
            self.snapshot_tool,
            self.semantic_tool,
            self.performance_tool,
            self.normalizer,
            self.tracer,
        )

    def forward(
        self, parsed_query: ParsedQuery, context_fund_ids: list[str] | None = None
    ) -> dspy.Prediction:
        results = self.router.execute(parsed_query, context_fund_ids)
        merged = self._merge_results(results, parsed_query)
        return dspy.Prediction(merged_results=merged)

    def _merge_results(
        self, results: list[FundResult], parsed: ParsedQuery | None = None
    ) -> MergedSearchResults:
        if not results:
            return MergedSearchResults(items=[])

        # Merge duplicates
        merged_map: dict[str, FundResult] = {}
        for r in results:
            if r.fund_id not in merged_map:
                merged_map[r.fund_id] = r
                if not hasattr(r, "_sources"):
                    r._sources = set()

                source = "structured"
                if r.match_score:
                    source = "semantic"
                elif r.position_value:
                    source = "position"
                elif r.aum and not r.legal_name:
                    source = "snapshot"

                r._sources.add(source)
            else:
                existing = merged_map[r.fund_id]
                if r.aum:
                    existing.aum = r.aum
                if r.holders:
                    existing.holders = r.holders
                if r.position_value:
                    existing.position_value = r.position_value
                if r.asset_name:
                    existing.asset_name = r.asset_name
                if r.match_score:
                    existing.match_score = max(existing.match_score or 0, r.match_score)
                if r.description:
                    existing.description = r.description

                source = "structured"
                if r.match_score:
                    source = "semantic"
                elif r.position_value:
                    source = "position"
                existing._sources.add(source)

        # Score & Convert
        items = []
        for r in merged_map.values():
            score = 0.0
            if r.match_score:
                score += r.match_score * 0.6
            if len(getattr(r, "_sources", [])) > 1:
                score += 0.3
            score += 0.2

            sources = getattr(r, "_sources", set())
            primary_source = "structured"
            if "semantic" in sources:
                primary_source = "semantic"
            if len(sources) > 1:
                primary_source = "both"

            items.append(
                SearchResultItem(
                    fund_id=r.fund_id,
                    legal_name=r.legal_name,
                    cnpj=r.cnpj,
                    source=primary_source,  # type: ignore
                    combined_score=score,
                    match_reason=f"Found via {', '.join(sources)}",
                    fund_details=r,
                )
            )

        items.sort(key=lambda x: x.combined_score, reverse=True)

        # Ambiguity detection - only trigger if results are VERY close
        # Use actual match_score for semantic results, not combined_score
        has_ambiguity = False
        candidates = []

        is_semantic = parsed and parsed.semantic_query
        if is_semantic and len(items) >= 2:
            # Get actual match scores (before combined_score compression)
            score1 = items[0].fund_details.match_score or 0
            score2 = items[1].fund_details.match_score or 0

            # Only ambiguous if scores are within 2% AND both are high confidence
            # This prevents "bradesco gold" from being ambiguous when there's a clear winner
            if score1 > 0 and score2 > score1 * 0.98:
                has_ambiguity = True
                candidates = items[:3]

        return MergedSearchResults(
            items=items,
            semantic_count=sum(1 for i in items if i.source == "semantic"),
            structured_count=sum(1 for i in items if i.source == "structured"),
            both_count=sum(1 for i in items if i.source == "both"),
            has_ambiguity=has_ambiguity,
            disambiguation_candidates=candidates,
        )
