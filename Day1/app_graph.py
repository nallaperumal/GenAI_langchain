from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langfuse.langchain import CallbackHandler

# Step 1: Define the shared State that moves through the graph
class AgentState(TypedDict):
    text: str
    steps_taken: list[str]


langfuse_callback = CallbackHandler()

# Step 2: Define your Node functions
# Each node receives the current state and returns updates to that state
def upper_case_node(state: AgentState) -> dict:
    print("-> Processing in Upper Case Node")
    return {
        "text": state["text"].upper(),
        "steps_taken": ["converted_to_uppercase"]
    }

def exclaim_node(state: AgentState) -> dict:
    print("-> Processing in Exclaim Node")
    # LangGraph automatically merges dictionary updates back into the state
    return {
        "text": f"{state['text']}!!!",
        "steps_taken": state["steps_taken"] + ["added_exclamation"]
    }

# Step 3: Initialize the Graph Builder with the state schema
builder = StateGraph(AgentState)

# Step 4: Add nodes to the graph
builder.add_node("make_uppercase", upper_case_node)
builder.add_node("add_exclamation", exclaim_node)

# Step 5: Define the Edges (the control flow)
builder.add_edge(START, "make_uppercase")        # Start -> node 1
builder.add_edge("make_uppercase", "add_exclamation") # Node 1 -> Node 2
builder.add_edge("add_exclamation", END)          # Node 2 -> End

# Step 6: Compile the workflow into a runnable app
app = builder.compile()

# Step 7: Invoke the graph with an initial state
initial_input = {"text": "hello langgraph", "steps_taken": []}
final_state = app.invoke(initial_input, config ={
    "callbacks" : [langfuse_callback],
    "metadata" :{
        "langfuse_session_id" : "graph_sess",
        "langfuse_user_id" :  "nalla_chain"
    }
})

print("\n--- Final Graph Output ---")
print(final_state)