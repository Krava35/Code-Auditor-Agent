from __future__ import annotations

import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from code_auditor.config import create_llm
from code_auditor.models import AuditPlan, AuditReport, Finding, ReactDecision
from code_auditor.state import AuditState


def _to_json(data: Any) -> str:
    if hasattr(data, "model_dump"):
        return json.dumps(data.model_dump(), ensure_ascii=False, indent=2)
    return json.dumps(data, ensure_ascii=False, indent=2)


def planner_node(state: AuditState) -> dict[str, Any]:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Ты PlannerNode. Сформируй короткий и практичный план аудита кода. "
                "Разрешенные проверки: только ruff и radon. "
                "Пиши содержимое полей на русском языке и верни строго валидную схему.",
            ),
            (
                "human",
                "Запрос пользователя:\n{request_json}\n\n"
                "Верни AuditPlan с полями checks, scope и priority.",
            ),
        ]
    )

    llm = create_llm(temperature=0.0).with_structured_output(AuditPlan)
    request_json = _to_json(state["user_request"])
    try:
        plan = llm.invoke(prompt.format_messages(request_json=request_json))
    except Exception:
        # Keep workflow robust for local/offline troubleshooting.
        plan = AuditPlan(
            checks=["ruff", "radon"],
            scope=f"Аудит цели: {state['user_request'].target_path}",
            priority="balanced",
        )

    return {"plan": plan}


def react_decision_node(state: AuditState) -> dict[str, Any]:
    loop_count = state["loop_count"]
    max_loops = state["max_loops"]

    if loop_count >= max_loops:
        decision = ReactDecision(
            action="finish",
            reason="Reached max loop count guard.",
            done=True,
        )
    else:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Ты ReactDecisionNode. Прочитай текущее состояние и выбери следующий шаг. "
                    "Сначала используй run_parallel_checks, затем finish, когда результаты инструментов уже получены. "
                    "Пояснение reason пиши на русском языке.",
                ),
                (
                    "human",
                    "План:\n{plan_json}\n\n"
                    "Количество результатов инструментов: {tool_outputs_count}\n"
                    "Последние результаты:\n{tool_outputs_json}\n\n"
                    "Верни ReactDecision.",
                ),
            ]
        )
        llm = create_llm(temperature=0.0).with_structured_output(ReactDecision)
        try:
            decision = llm.invoke(
                prompt.format_messages(
                    plan_json=_to_json(state["plan"]) if state["plan"] else "{}",
                    tool_outputs_count=len(state["tool_outputs"]),
                    tool_outputs_json=_to_json([t.model_dump() for t in state["tool_outputs"]]),
                )
            )
        except Exception:
            decision = ReactDecision(
                action="run_parallel_checks" if not state["tool_outputs"] else "finish",
                reason="Резервная детерминированная политика.",
                done=bool(state["tool_outputs"]),
            )

    if not state["tool_outputs"]:
        decision = ReactDecision(
            action="run_parallel_checks",
            reason=decision.reason,
            done=False,
        )
    elif decision.action != "finish":
        decision = ReactDecision(
            action="finish",
            reason=decision.reason,
            done=True,
        )

    return {
        "react_history": state["react_history"] + [decision],
        "next_action": decision.action,
        "loop_count": loop_count + 1,
    }


def writer_node(state: AuditState) -> dict[str, Any]:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Ты WriterNode. Подготовь краткий и практичный итоговый отчет аудита. "
                "Сначала выделяй самые рискованные находки и конкретные следующие шаги. "
                "Пиши содержимое полей на русском языке и верни строго валидную схему.",
            ),
            (
                "human",
                "Запрос пользователя:\n{request_json}\n\n"
                "План:\n{plan_json}\n\n"
                "Результаты инструментов:\n{tool_outputs_json}\n\n"
                "Верни AuditReport.",
            ),
        ]
    )

    llm = create_llm(temperature=0.1).with_structured_output(AuditReport)
    try:
        report = llm.invoke(
            prompt.format_messages(
                request_json=_to_json(state["user_request"]),
                plan_json=_to_json(state["plan"]) if state["plan"] else "{}",
                tool_outputs_json=_to_json([t.model_dump() for t in state["tool_outputs"]]),
            )
        )
    except Exception:
        findings: list[Finding] = []
        for tool_output in state["tool_outputs"]:
            findings.extend(tool_output.findings)
        report = AuditReport(
            summary="Сформирован резервный отчет без ответа LLM.",
            key_risks=[f.message for f in findings[:3]],
            findings=findings,
            next_steps=[
                "Сначала исправить находки с высокой критичностью.",
                "После изменений повторно запустить аудит.",
                "Добавить тесты для рискованных модулей.",
            ],
        )

    return {"report": report}

