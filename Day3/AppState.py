from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    user: str
    messages: Annotated[list, add_messages]
    desired_flavour: str
    avg_price : str
    federated_response: str
    preference_context: str
    inventory_context: str
    ragas_score: str