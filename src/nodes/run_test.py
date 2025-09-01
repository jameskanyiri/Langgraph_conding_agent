import json
from src.state import AgentState
from langgraph.types import Command
from typing import Literal
from langgraph.graph import END

import os
from langchain_core.messages import AIMessage
from dotenv import load_dotenv

load_dotenv()

from e2b_code_interpreter import Sandbox


def run_test(state: AgentState) -> Command[Literal[END, "wrap_up"]]:
    """Execute the code with generated tests and return results."""

    code = state["code"]
    tests = state["tests"]

    function_name = tests["function_name"]
    test_cases = tests["tests"]

    # Build test harness as Python code
    harness = f"""
import json

tests = {json.dumps(test_cases)}

results = []
for case in tests:
    args = case.get("args", [])
    kwargs = case.get("kwargs", dict())
    expect = case.get("expect")
    try:
        result = {function_name}(*args, **kwargs)
        ok = result == expect
    except Exception as e:
        result = str(e)
        ok = False
    
    results.append({{
        "args": args,
        "kwargs": kwargs,
        "expect": expect,
        "result": result,
        "ok": ok
    }})

print(json.dumps({{"cases": results}}))
"""

    # Combine generated code + harness
    program = code + "\n\n" + harness

    # Run in sandbox
    try:

        sbx = Sandbox.create()
        execution = sbx.run_code(program)
    except Exception as e:
        return Command(
            goto=END,
            update={
                "messages": [
                    AIMessage(content=f"Failed to run code in sandbox: {str(e)}"),
                ],
            },
        )

    # Convert execution results to a JSON-serializable format
    try:
        # Parse stdout and stderr logs as JSON if possible
        try:
            stdout_json = [json.loads(log) for log in execution.logs.stdout]
        except json.JSONDecodeError:
            stdout_json = execution.logs.stdout

        try:
            stderr_json = [json.loads(log) for log in execution.logs.stderr]
        except json.JSONDecodeError:
            stderr_json = execution.logs.stderr

        test_report = {
            "results": execution.results,
            "logs": {"stdout": stdout_json, "stderr": stderr_json},
            "error": str(execution.error) if execution.error else None,
        }
        json_report = json.dumps(test_report)
    except Exception as e:
        return Command(
            goto=END,
            update={
                "messages": [
                    AIMessage(
                        content=f"Failed to serialize test report to JSON: {str(e)}"
                    ),
                ],
            },
        )

    return Command(
        goto="wrap_up",
        update={
            "test_report": json_report,
        },
    )
