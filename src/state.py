from langgraph.graph.message import MessagesState

class AgentState(MessagesState):
    """State for the agent."""
    code: str
    tests: str
    test_report: str