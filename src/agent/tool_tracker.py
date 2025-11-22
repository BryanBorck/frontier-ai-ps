"""Track tool usage and LM calls for the agent."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ToolCall:
    """Record of a single tool invocation."""

    tool_name: str
    timestamp: datetime
    args: dict[str, Any]
    result: Any = None
    error: str | None = None
    duration_ms: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for display."""
        return {
            "tool": self.tool_name,
            "timestamp": self.timestamp.isoformat(),
            "args": self.args,
            "result": str(self.result)[:100] if self.result else None,
            "error": self.error,
            "duration_ms": round(self.duration_ms, 2),
        }


@dataclass
class AgentTrace:
    """Complete trace of agent execution including LM and tool usage."""

    question: str
    answer: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    lm_usage: dict[str, Any] | None = None
    total_duration_ms: float = 0.0

    def add_tool_call(self, tool_call: ToolCall):
        """Add a tool call to the trace."""
        self.tool_calls.append(tool_call)

    def to_dict(self) -> dict:
        """Convert to dictionary for display."""
        return {
            "question": self.question,
            "answer": self.answer,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls],
            "lm_usage": self.lm_usage,
            "total_duration_ms": round(self.total_duration_ms, 2),
        }

    def has_tool_calls(self) -> bool:
        """Check if any tools were called."""
        return len(self.tool_calls) > 0


class ToolTracker:
    """Track tool usage across agent calls."""

    def __init__(self):
        """Initialize the tool tracker."""
        self.current_trace: AgentTrace | None = None
        self.traces: list[AgentTrace] = []

    def start_trace(self, question: str):
        """Start tracking a new agent execution."""
        self.current_trace = AgentTrace(question=question, answer="")
        self.traces.append(self.current_trace)

    def record_tool_call(
        self,
        tool_name: str,
        args: dict[str, Any],
        result: Any = None,
        error: str | None = None,
        duration_ms: float = 0.0,
    ):
        """Record a tool invocation."""
        if self.current_trace is None:
            return

        tool_call = ToolCall(
            tool_name=tool_name,
            timestamp=datetime.now(),
            args=args,
            result=result,
            error=error,
            duration_ms=duration_ms,
        )
        self.current_trace.add_tool_call(tool_call)

    def end_trace(self, answer: str, lm_usage: dict | None = None, duration_ms: float = 0.0):
        """Complete the current trace."""
        if self.current_trace:
            self.current_trace.answer = answer
            self.current_trace.lm_usage = lm_usage
            self.current_trace.total_duration_ms = duration_ms
            self.current_trace = None

    def get_last_trace(self) -> AgentTrace | None:
        """Get the most recent trace."""
        return self.traces[-1] if self.traces else None

    def clear_traces(self):
        """Clear all traces."""
        self.traces = []
        self.current_trace = None
