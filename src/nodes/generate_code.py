from src.state import AgentState
from langchain.chat_models import init_chat_model
from langgraph.types import Command
from typing import Literal
from pydantic import BaseModel, Field

llm = init_chat_model(model="gpt-4o-mini", temperature=0)

GENERATE_CODE_PROMPT = """
# Identity
You are a coding assistant that generates Python code compatible with Python 3.13.

# Instructions
1. Make sure the code is well indented and formatted.
2. Always use snake_case for variable and function names.
3. Return only raw Python code (no markdown formatting, explanations, or extra text).
4. Follow best practices for readability and type hints where appropriate.
5. Ensure the code runs without modification in Python 3.13.

# Examples

<example_1>
<user_query>
Generate a function that prints "Hello, World!"
</user_query>

<assistant_response>
def print_hello_world():
    print("Hello, World!")
</assistant_response>
</example_1>

<example_2>
<user_query>
Generate a function that accepts two numbers and returns their sum.
</user_query>

<assistant_response>
def add_two_numbers(a: int, b: int) -> int:
    return a + b
</assistant_response>
</example_2>

<example_3>
<user_query>
Generate a function that accepts two strings and returns their concatenation with a space in between.
</user_query>

<assistant_response>
def combine_strings(a: str, b: str) -> str:
    return a + " " + b
</assistant_response>
</example_3>



<user_query>
{user_query}
</user_query>
"""

def generate_code(state: AgentState) -> Command[Literal["generate_test"]]:
    """Generate code."""
    user_query = state["messages"][-1].content

    system_instruction = GENERATE_CODE_PROMPT.format(user_query=user_query)

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": "Generate a python code based on the user query"},
    ]

    response = llm.invoke(messages)

    return Command(goto="generate_test", update={"code": response.content})
