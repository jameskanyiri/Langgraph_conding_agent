from src.state import AgentState
from langchain.chat_models import init_chat_model
from langgraph.types import Command
from typing import Literal
import json

llm = init_chat_model(model="gpt-4o-mini", temperature=0)

GENERATE_TEST_PROMPT = """
# Identity
You are a coding assistant that generates JSON test cases for a given Python function.

# Output format
Return **only** a valid JSON object with keys:
- "function_name": string
- "tests": array of objects, each with:
  - "args": array (positional arguments)
  - "kwargs": object (keyword arguments; may be empty)
  - "expect": expected return value

# Requirements
1) Tests must exercise happy-path and at least two edge cases.
2) Arguments and expected values must be JSON-serializable.
3) Do not include markdown, comments, or extra text outside the JSON.

# Examples
<example>
<input_code>
def add_two_numbers(a: int, b: int) -> int:
    return a + b
</input_code>
<output_json>
{
  "function_name": "add_two_numbers",
  "tests": [
    { "args": [1, 2], "kwargs": {}, "expect": 3 },
    { "args": [0, 0], "kwargs": {}, "expect": 0 },
    { "args": [-5, 2], "kwargs": {}, "expect": -3 }
  ]
}
</output_json>
</example>

"""


def generate_test(state: AgentState) -> Command[Literal["run_test"]]:
    """Generate code."""
    code = state["code"]

    system_instruction = GENERATE_TEST_PROMPT
    
    user_prompt = f"Generate a python tests based on the python code: {code}"

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_prompt},
    ]

    response = llm.invoke(messages)
    
    tests = json.loads(response.content)

    return Command(goto="run_test", update={"tests": tests})
