from __future__ import annotations

from typing import TypedDict

from code_auditor.models import AuditPlan, AuditReport, ReactDecision, ToolOutput, UserRequest


class AuditState(TypedDict):
    user_request: UserRequest
    plan: AuditPlan | None
    react_history: list[ReactDecision]
    tool_outputs: list[ToolOutput]
    report: AuditReport | None
    next_action: str | None
    loop_count: int
    max_loops: int
    simulate_retry: bool


def build_initial_state(
    *,
    query: str,
    target_path: str,
    simulate_retry: bool = False,
    max_loops: int = 3,
) -> AuditState:
    return AuditState(
        user_request=UserRequest(query=query, target_path=target_path),
        plan=None,
        react_history=[],
        tool_outputs=[],
        report=None,
        next_action=None,
        loop_count=0,
        max_loops=max_loops,
        simulate_retry=simulate_retry,
    )

