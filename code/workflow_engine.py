from __future__ import annotations

import inspect
from typing import Any


class WorkflowEngine:
    async def execute(self, workflow, initial_context: dict[str, Any] | None = None):
        context: dict[str, Any] = dict(initial_context or {})

        if isinstance(workflow, dict):
            steps = workflow.get("steps", [])
        else:
            steps = workflow

        if not isinstance(steps, list):
            raise ValueError("workflow must provide a list of steps")

        for index, step in enumerate(steps):
            if callable(step):
                result = step(context)
                if inspect.isawaitable(result):
                    result = await result
                if isinstance(result, dict):
                    context.update(result)
                continue

            if isinstance(step, dict):
                op = step.get("op")
                if op == "set":
                    context[str(step.get("key"))] = step.get("value")
                elif op == "append":
                    key = str(step.get("key"))
                    context.setdefault(key, [])
                    if not isinstance(context[key], list):
                        raise ValueError(f"step {index}: key '{key}' is not a list")
                    context[key].append(step.get("value"))
                elif op == "delete":
                    context.pop(str(step.get("key")), None)
                else:
                    raise ValueError(f"step {index}: unsupported op '{op}'")
                continue

            raise ValueError(f"step {index}: unsupported step type {type(step).__name__}")

        return context