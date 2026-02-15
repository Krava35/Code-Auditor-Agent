from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from langgraph.graph import END, START, StateGraph

from code_auditor.models import ToolOutput
from code_auditor.nodes import planner_node, react_decision_node, writer_node
from code_auditor.state import AuditState, build_initial_state
from code_auditor.tools import run_radon_complexity, run_ruff_check


def parallel_checks_node(state: AuditState) -> dict[str, Any]:
    target_path = state["user_request"].target_path

    def _ruff() -> ToolOutput:
        return run_ruff_check(
            target_path=target_path,
            options={"simulate_transient_once": state["simulate_retry"]},
        )

    def _radon() -> ToolOutput:
        return run_radon_complexity(target_path=target_path, options={})

    with ThreadPoolExecutor(max_workers=2) as pool:
        ruff_future = pool.submit(_ruff)
        radon_future = pool.submit(_radon)
        ruff_result = ruff_future.result()
        radon_result = radon_future.result()

    return {"tool_outputs": state["tool_outputs"] + [ruff_result, radon_result]}


def route_from_react(state: AuditState) -> str:
    if state["next_action"] == "run_parallel_checks":
        return "parallel_checks_node"
    return "writer_node"


def build_graph():
    workflow = StateGraph(AuditState)
    workflow.add_node("planner_node", planner_node)
    workflow.add_node("react_decision_node", react_decision_node)
    workflow.add_node("parallel_checks_node", parallel_checks_node)
    workflow.add_node("writer_node", writer_node)

    workflow.add_edge(START, "planner_node")
    workflow.add_edge("planner_node", "react_decision_node")
    workflow.add_conditional_edges(
        "react_decision_node",
        route_from_react,
        {
            "parallel_checks_node": "parallel_checks_node",
            "writer_node": "writer_node",
        },
    )
    workflow.add_edge("parallel_checks_node", "react_decision_node")
    workflow.add_edge("writer_node", END)
    return workflow.compile()


def run_audit(
    *,
    query: str,
    target_path: str,
    simulate_retry: bool = False,
    max_loops: int = 3,
):
    app = build_graph()
    initial_state = build_initial_state(
        query=query,
        target_path=target_path,
        simulate_retry=simulate_retry,
        max_loops=max_loops,
    )
    return app.invoke(initial_state)

