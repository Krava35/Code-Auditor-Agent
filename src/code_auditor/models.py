from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


CheckName = Literal["ruff", "radon"]
Severity = Literal["low", "medium", "high", "critical"]
ReactAction = Literal["run_parallel_checks", "finish"]


class UserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(..., min_length=5, description="Текстовый запрос пользователя на аудит кода.")
    target_path: str = Field(..., description="Путь к файлу или директории для аудита.")


class AuditPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    checks: list[CheckName] = Field(
        default_factory=lambda: ["ruff", "radon"],
        description="Список инструментов, которые нужно запустить для этого запроса.",
    )
    scope: str = Field(..., description="Короткое описание области анализа.")
    priority: Literal["speed", "balanced", "depth"] = Field(
        default="balanced",
        description="Глубина/строгость аудита.",
    )


class ReactDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: ReactAction
    reason: str = Field(..., min_length=5)
    done: bool = Field(..., description="Нужно ли завершать выполнение на текущем шаге.")


class ToolInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: CheckName
    target_path: str
    options: dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: Severity
    file: str
    message: str
    suggestion: str


class ToolOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: CheckName
    ok: bool
    findings: list[Finding] = Field(default_factory=list)
    raw_output: str = ""
    error: str | None = None


class AuditReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    key_risks: list[str] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)

