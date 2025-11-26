import dspy

from src.agent.fund_search.models.query import (
    FundSearchCriteria,
    ParsedQuery,
    PositionSearchCriteria,
)
from src.agent.fund_search.modules.normalization import EntityNormalizer
from src.agent.fund_search.tools.search_funds.tool import FundSearchTool
from src.agent.fund_search.tools.search_performance.tool import PerformanceSearchTool
from src.agent.fund_search.tools.search_positions.tool import PositionSearchTool
from src.agent.fund_search.tools.search_semantic.tool import SemanticSearchTool
from src.agent.fund_search.tools.search_snapshots.tool import SnapshotSearchTool
from src.agent.fund_search.utils.tracing import TracingManager


class SearchRouter:
    """
    Routes parsed query to appropriate search tools based on INTENTS.
    Returns lists of CNPJs.
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

    def execute(self, parsed: ParsedQuery, context_cnpjs: list[str] | None = None) -> list[str]:
        """
        Execute search based on INTENTS in parsed query.
        Returns a merged list of CNPJs.
        """
        results_lists: list[list[str]] = []
        intents = parsed.intents

        # --- Normalize entities ---
        self._normalize_query(parsed)

        # Determine result limit
        limit_override = None
        if parsed.numeric_filter and parsed.numeric_filter.top_n:
            limit_override = parsed.numeric_filter.top_n

        semantic_limit = limit_override or 20
        structured_limit = limit_override or 50

        # --- STEP 1: Semantic Search ---
        if "find_by_name" in intents or "find_by_strategy" in intents:
            query_text = parsed.semantic_query or parsed.query
            if query_text:
                if "find_by_name" in intents and "find_by_strategy" not in intents:
                    search_mode = "name"
                    reason = "name_search"
                else:
                    search_mode = "all"
                    reason = (
                        "strategy_search"
                        if "find_by_strategy" in intents
                        else "name_and_strategy_search"
                    )

                pre_filter = {}
                if parsed.service_provider_entity:
                    pre_filter["manager"] = parsed.service_provider_entity[0]
                if parsed.investment_class:
                    pre_filter["investment_class"] = parsed.investment_class[0]
                if parsed.fund_type:
                    pre_filter["fund_type"] = parsed.fund_type[0]
                if parsed.required_name_terms:
                    pre_filter["name_terms"] = parsed.required_name_terms

                semantic_cnpjs = self._call_semantic_tool(
                    query_text, semantic_limit, reason, search_mode, pre_filter
                )
                results_lists.append(semantic_cnpjs)

        # --- STEP 2: Structured Search ---
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

            if fund_criteria.has_any_criteria():
                # We can pass context_cnpjs here to filter immediately if desired,
                # but usually structured search is an "AND" filter on top of context if context exists.
                # However, the tools are independent. We'll intersect later.
                # BUT, if we have context_cnpjs (e.g. "from these..."), we should pass it.

                criteria_cnpjs = self._call_fund_tool(
                    fund_criteria, cnpjs=context_cnpjs, limit=structured_limit, reason="criteria"
                )
                results_lists.append(criteria_cnpjs)

        # --- STEP 3: Exposure Search ---
        if "find_by_exposure" in intents:
            position_criteria = PositionSearchCriteria(
                companies=parsed.companies,  # Simplified: only company names
                asset_type=parsed.asset_type,
            )

            # Use context if available to limit search scope
            exposure_cnpjs = self._call_position_tool(
                position_criteria, context_cnpjs, structured_limit, "exposure"
            )
            results_lists.append(exposure_cnpjs)

        # --- STEP 4: Numeric Filter ---
        if "has_numeric_filter" in intents and parsed.numeric_filter:
            if parsed.numeric_filter.metric == "return":
                perf_cnpjs = self._call_performance_tool(
                    parsed.numeric_filter, context_cnpjs, structured_limit, "performance"
                )
                results_lists.append(perf_cnpjs)
            else:
                snapshot_cnpjs = self._call_snapshot_tool(
                    parsed.numeric_filter, context_cnpjs, structured_limit, "snapshot"
                )
                results_lists.append(snapshot_cnpjs)

        # --- MERGING LOGIC ---
        # If multiple lists, we generally want intersection if the user is adding constraints.
        # But if we have distinct searches (e.g. "funds by name OR strategy"), the tools handle that internally.
        # Different steps usually imply AND logic (e.g. "Itau funds" (Structured) AND "Top 10 returns" (Numeric)).
        # However, Semantic + Structured might be fuzzy.

        # If we have NO results from tools, but we had context, maybe return context?
        # No, if intents were detected, we expect filtering.

        if not results_lists:
            # If no search performed but context exists, maybe return context?
            # Depends on caller. If intent was "show me", but no specific search triggered?
            return context_cnpjs if context_cnpjs else []

        # Intersect all result lists
        # Start with the first list
        final_set = set(results_lists[0])
        for res_list in results_lists[1:]:
            final_set.intersection_update(res_list)

        # Preserve order from the first list (primary relevance)
        final_list = [c for c in results_lists[0] if c in final_set]

        return final_list

    def _normalize_query(self, parsed: ParsedQuery) -> None:
        """Normalize query entities."""

        if parsed.service_provider_entity:
            normalized_providers = []
            for raw_provider in parsed.service_provider_entity:
                norm_result = self.normalizer(query_text=raw_provider, entity_type="PROVIDER")
                normalized_providers.append(norm_result.normalized_name or raw_provider)
            parsed.service_provider_entity = normalized_providers

    # --- Traced Tool Calls ---

    def _call_fund_tool(
        self,
        criteria: FundSearchCriteria | None,
        name: str | None = None,
        cnpjs: list[str] | None = None,
        limit: int = 50,
        reason: str = "fund_search",
    ) -> list[str]:
        with self.tracer.tool_call(
            "FundSearchTool",
            {
                "criteria": criteria.model_dump() if criteria else None,
                "name": name,
                "cnpjs_count": len(cnpjs) if cnpjs else 0,
                "limit": limit,
                "reason": reason,
            },
        ) as span:
            results = self.fund_tool(criteria=criteria, name=name, cnpjs=cnpjs, limit=limit)
            span.set_outputs({"result_count": len(results), "cnpjs": results[:5]})
            return results

    def _call_position_tool(
        self,
        criteria: PositionSearchCriteria,
        cnpjs: list[str] | None,
        limit: int,
        reason: str,
    ) -> list[str]:
        with self.tracer.tool_call(
            "PositionSearchTool",
            {
                "criteria": criteria.model_dump() if criteria else None,
                "cnpjs_count": len(cnpjs) if cnpjs else 0,
                "limit": limit,
                "reason": reason,
            },
        ) as span:
            results = self.position_tool(criteria=criteria, cnpjs=cnpjs, limit=limit)
            span.set_outputs({"result_count": len(results), "cnpjs": results[:5]})
            return results

    def _call_snapshot_tool(
        self,
        numeric_filter,
        cnpjs: list[str] | None,
        limit: int,
        reason: str,
    ) -> list[str]:
        with self.tracer.tool_call(
            "SnapshotSearchTool",
            {
                "numeric_filter": numeric_filter.model_dump() if numeric_filter else None,
                "cnpjs_count": len(cnpjs) if cnpjs else 0,
                "limit": limit,
                "reason": reason,
            },
        ) as span:
            results = self.snapshot_tool(numeric_filter=numeric_filter, cnpjs=cnpjs, limit=limit)
            span.set_outputs({"result_count": len(results), "cnpjs": results[:5]})
            return results

    def _call_semantic_tool(
        self,
        query: str,
        top_k: int,
        reason: str,
        search_mode: str = "all",
        pre_filter: dict | None = None,
    ) -> list[str]:
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
            span.set_outputs({"result_count": len(results), "cnpjs": results[:5]})
            return results

    def _call_performance_tool(
        self, numeric_filter, cnpjs: list[str] | None, limit: int, reason: str
    ) -> list[str]:
        with self.tracer.tool_call(
            "PerformanceSearchTool",
            {
                "numeric_filter": numeric_filter.model_dump() if numeric_filter else None,
                "limit": limit,
                "reason": reason,
            },
        ) as span:
            results = self.performance_tool(numeric_filter=numeric_filter, cnpjs=cnpjs, limit=limit)
            span.set_outputs({"result_count": len(results), "cnpjs": results[:5]})
            return results


class SearchManager(dspy.Module):
    """Orchestrates search execution."""

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
        self, parsed_query: ParsedQuery, context_cnpjs: list[str] | None = None
    ) -> dspy.Prediction:
        results = self.router.execute(parsed_query, context_cnpjs)
        # Return dspy.Prediction with the list of CNPJs
        return dspy.Prediction(cnpjs=results, result_count=len(results))
