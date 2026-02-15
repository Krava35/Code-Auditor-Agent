from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from code_auditor.models import Finding, ToolOutput

_TRANSIENT_FAILED_KEYS: set[str] = set()


class TransientToolError(RuntimeError):
    """Повторяемая (transient) ошибка выполнения инструмента."""


def _severity_from_ruff(code: str) -> str:
    if code.startswith(("F", "E9", "B")):
        return "high"
    if code.startswith(("E", "W")):
        return "medium"
    return "low"


def _severity_from_radon(rank: str) -> str:
    mapping = {
        "A": "low",
        "B": "low",
        "C": "medium",
        "D": "high",
        "E": "critical",
        "F": "critical",
    }
    return mapping.get(rank, "medium")


def _safe_path(path: str) -> str:
    return str(Path(path))


def _run_subprocess(command: list[str]) -> tuple[int, str, str]:
    process = subprocess.run(command, capture_output=True, text=True, check=False)
    return process.returncode, process.stdout, process.stderr


@retry(
    retry=retry_if_exception_type(TransientToolError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=2),
    reraise=True,
)
def run_ruff_check(target_path: str, options: dict[str, Any] | None = None) -> ToolOutput:
    options = options or {}
    simulate_transient_once = bool(options.get("simulate_transient_once", False))
    fail_key = f"ruff::{target_path}"
    if simulate_transient_once and fail_key not in _TRANSIENT_FAILED_KEYS:
        _TRANSIENT_FAILED_KEYS.add(fail_key)
        raise TransientToolError("Смоделированная временная ошибка для демонстрации retry.")

    command = ["ruff", "check", _safe_path(target_path), "--output-format", "json"]
    code, stdout, stderr = _run_subprocess(command)

    if code not in (0, 1):
        return ToolOutput(
            tool_name="ruff",
            ok=False,
            findings=[],
            raw_output=stdout,
            error=stderr or f"ruff завершился с кодом {code}",
        )

    try:
        rows = json.loads(stdout) if stdout.strip() else []
    except json.JSONDecodeError:
        return ToolOutput(
            tool_name="ruff",
            ok=False,
            findings=[],
            raw_output=stdout,
            error="Не удалось распарсить JSON-вывод ruff.",
        )

    findings: list[Finding] = []
    for row in rows:
        rule = row.get("code", "UNKNOWN")
        filename = row.get("filename", target_path)
        message = row.get("message", "Сообщение отсутствует")
        suggestion = "Исправьте lint-замечание и повторите аудит."
        findings.append(
            Finding(
                severity=_severity_from_ruff(rule),  # type: ignore[arg-type]
                file=str(filename),
                message=f"{rule}: {message}",
                suggestion=suggestion,
            )
        )

    return ToolOutput(
        tool_name="ruff",
        ok=True,
        findings=findings,
        raw_output=stdout,
        error=None,
    )


def run_radon_complexity(target_path: str, options: dict[str, Any] | None = None) -> ToolOutput:
    _ = options or {}
    command = ["radon", "cc", "-j", _safe_path(target_path)]
    code, stdout, stderr = _run_subprocess(command)

    if code != 0:
        return ToolOutput(
            tool_name="radon",
            ok=False,
            findings=[],
            raw_output=stdout,
            error=stderr or f"radon завершился с кодом {code}",
        )

    try:
        payload = json.loads(stdout) if stdout.strip() else {}
    except json.JSONDecodeError:
        return ToolOutput(
            tool_name="radon",
            ok=False,
            findings=[],
            raw_output=stdout,
            error="Не удалось распарсить JSON-вывод radon.",
        )

    findings: list[Finding] = []
    for filename, blocks in payload.items():
        for block in blocks:
            rank = str(block.get("rank", "C"))
            complexity = block.get("complexity", "unknown")
            block_name = block.get("name", "<unknown>")
            findings.append(
                Finding(
                    severity=_severity_from_radon(rank),  # type: ignore[arg-type]
                    file=str(filename),
                    message=f"Сложность {rank} ({complexity}) в {block_name}",
                    suggestion="Рефакторинг длинных/ветвистых функций в более мелкие блоки.",
                )
            )

    return ToolOutput(
        tool_name="radon",
        ok=True,
        findings=findings,
        raw_output=stdout,
        error=None,
    )

