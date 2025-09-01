from typing import Literal
from src.state import AgentState
from langchain.chat_models import init_chat_model
from langgraph.types import Command
from langgraph.graph import END


llm = init_chat_model(model="gpt-4o-mini", temperature=0)

WRAP_UP_PROMPT = """
Analyze the code and test results to produce a short, focused report with these sections:

## What Was Built
Brief description of the implemented functionality and purpose.

## Actual code
The actual code that was generated.

## Example test cases
The example test cases that were generated.

## Test report
The test report that was generated.

## Edge Cases Covered
List the key edge cases and scenarios tested.

## Remaining
Highlight any important limitations or potential improvements.

Formatted in markdown.
Make sure the report is formatted in markdown.

# Code Generated
<generated_code>
{generated_code}
</generated_code>

# Example test cases
<test_cases>
{test_cases}
</test_cases>

# Test report
<test_report>
{test_report}
</test_report>
"""


def wrap_up(state: AgentState) -> Command[Literal[END]]:
    """Wrap up the agent."""
    code = state["code"]
    tests = state["tests"]
    test_report = state["test_report"]

    system_instruction = WRAP_UP_PROMPT.format(
        generated_code=code,
        test_cases=tests,
        test_report=test_report,
    )

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": "Generate a wrap up of the code and test report."},
    ]

    response = llm.invoke(messages)

    return Command(goto=END, update={"messages": [response]})
