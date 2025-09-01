from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes.generate_code import generate_code
from src.nodes.generate_test import generate_test
from src.nodes.run_test import run_test
from src.nodes.wrap_up import wrap_up



graph_builder = StateGraph(AgentState)

graph_builder.add_node("generate_code", generate_code)
graph_builder.add_node("generate_test", generate_test)
graph_builder.add_node("run_test", run_test)
graph_builder.add_node("wrap_up", wrap_up)




graph_builder.set_entry_point("generate_code")

graph = graph_builder.compile()