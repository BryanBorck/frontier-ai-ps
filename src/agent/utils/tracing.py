"""MLflow tracing utilities for the agent pipeline."""

from contextlib import contextmanager
from functools import wraps
from typing import Any

from mlflow.entities import SpanType

import mlflow


class TracingManager:
    """
    Manages MLflow tracing with a clean interface.
    When disabled, all operations become no-ops.
    """

    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    @contextmanager
    def span(
        self,
        name: str,
        span_type: SpanType = SpanType.CHAIN,
        inputs: dict[str, Any] | None = None,
    ):
        """
        Context manager for creating MLflow spans.
        Yields a span wrapper that handles set_outputs gracefully.
        """
        if not self.enabled:
            yield NoOpSpan()
            return

        with mlflow.start_span(name=name, span_type=span_type) as span:
            if inputs:
                span.set_inputs(inputs)
            yield SpanWrapper(span)

    def tool_call(self, name: str, inputs: dict[str, Any] | None = None):
        """Shortcut for tool-type spans."""
        return self.span(name, SpanType.TOOL, inputs)

    def llm_call(self, name: str, inputs: dict[str, Any] | None = None):
        """Shortcut for LLM-type spans."""
        return self.span(name, SpanType.LLM, inputs)

    def chain(self, name: str, inputs: dict[str, Any] | None = None):
        """Shortcut for chain-type spans."""
        return self.span(name, SpanType.CHAIN, inputs)


class SpanWrapper:
    """Wrapper around MLflow span for consistent interface."""

    def __init__(self, span):
        self._span = span

    def set_outputs(self, outputs: dict[str, Any]):
        self._span.set_outputs(outputs)

    def set_attribute(self, key: str, value: Any):
        self._span.set_attribute(key, value)

    def set_inputs(self, inputs: dict[str, Any]):
        self._span.set_inputs(inputs)


class NoOpSpan:
    """No-op span when tracing is disabled."""

    def set_outputs(self, outputs: dict[str, Any]):
        pass

    def set_attribute(self, key: str, value: Any):
        pass

    def set_inputs(self, inputs: dict[str, Any]):
        pass


def traced_tool(tracer: TracingManager, tool_name: str):
    """
    Decorator factory for tracing tool calls.

    Usage:
        @traced_tool(tracer, "FundSearchTool")
        def call_fund_tool(criteria, name=None, limit=50):
            return fund_tool(criteria=criteria, name=name, limit=limit)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract inputs for logging (exclude large objects)
            inputs = {k: _safe_serialize(v) for k, v in kwargs.items() if k not in ("self",)}

            with tracer.tool_call(tool_name, inputs) as span:
                results = func(*args, **kwargs)
                span.set_outputs({"result_count": len(results) if results else 0})
                return results

        return wrapper

    return decorator


def _safe_serialize(value: Any) -> Any:
    """Safely serialize values for MLflow logging."""
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, list) and len(value) > 10:
        return f"[list of {len(value)} items]"
    return value
