# Code Auditor - Lab1

**Локальный AI-аудитор кода** на `LangGraph` с паттерном **ReAct**, **Pydantic-схемами**, **retry** и **параллельными** шагами анализа.

Проект задуман как “техническая” лабораторная: мы анализируем код локальными CLI-инструментами (`ruff`, `radon`), а LLM используется для **планирования**, **выбора следующего шага** (ReAct) и **сборки отчёта**.

## Идея проекта

Сделать агента-аудитора, который по запросу на естественном языке:

- строит **план аудита** (какие проверки и в каком порядке),
- запускает локальные проверки кода (tools),
- собирает **структурированный отчёт** с рисками и следующими шагами.

## Архитектура

Архитектура — это граф `LangGraph` со state-моделью (TypedDict) и строгими схемами данных (Pydantic).

- **PlannerNode**: LLM генерирует `AuditPlan` (что проверяем, область, приоритет).
- **ReactDecisionNode**: LLM в стиле ReAct выбирает следующий шаг (`run_parallel_checks` или `finish`) на основе состояния.
- **ParallelChecksNode (Tools)**: параллельно запускает локальные проверки `ruff` и `radon`, результаты сохраняет в `state.tool_outputs`.
- **WriterNode**: LLM собирает `AuditReport` (summary, key_risks, findings, next_steps).


## Реализация (что где лежит)

- `src/code_auditor/models.py`: Pydantic-модели контрактов данных:
  - `UserRequest`, `AuditPlan`, `ReactDecision`, `Finding`, `ToolOutput`, `AuditReport`.
- `src/code_auditor/state.py`: `AuditState` + `build_initial_state(...)`.
- `src/code_auditor/config.py`: фабрика LLM `create_llm(...)` через переменные окружения.
- `src/code_auditor/nodes.py`: узлы графа (`planner_node`, `react_decision_node`, `writer_node`) с разными system-промптами и `with_structured_output(...)`.
- `src/code_auditor/tools.py`: локальные инструменты:
  - `run_ruff_check(...)` (lint, JSON output),
  - `run_radon_complexity(...)` (цикломатическая сложность, JSON output),
  - retry для демонстрации устойчивости (`tenacity`, `TransientToolError`).
- `src/code_auditor/graph.py`: сборка `StateGraph`, условная маршрутизация, параллельный узел на `ThreadPoolExecutor`, публичная функция `run_audit(...)`.
- `notebooks/demo.ipynb`: демонстрация всех пунктов лабораторной (визуализация графа, параллелизм, retry, сквозной запуск).


## Стек

- `langchain>=1.0.0`
- `langgraph>=1.0.0`
- `langchain-openai>=1.0.0`
- `pydantic>=2.7`
- `tenacity>=9.0.0`
- `ruff`, `radon`


## Демонстрация retry

В `run_audit(...)` есть флаг `simulate_retry=True`, который включает **однократную** симуляцию “временной” ошибки для `ruff`, чтобы показать работу повторных попыток.

## Демо в ноутбуке

Для демонстрации агента используется мой очень старый код - лежит в `test_project`