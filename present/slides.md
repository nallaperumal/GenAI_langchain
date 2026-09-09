---
layout: fact
---

# Multi-Agents

---

# Recap

<v-clicks>

- Ensemble-retriever
- Re-ranking
- LCEL chains
- chain with RAG
- Parallel chains

</v-clicks>

---

# Agenda

<v-clicks>

- Federated Agents
- New Case Study
- Langgraph with tool calls
- Condiditional graph
- Analyse the messages and state

</v-clicks>


---

# Case study

### Customer enquires
- Bot will search the database with his past history
- If available then it tries to fetch inventory based on his preference
- Final, federated agent will prvide response

---

# State

```py {*|1,3|*} {lines: true}
class AgentState(TypedDict):
    user: str
    messages: Annotated[list, add_messages]
    desired_flavour: str
    avg_price : str
    federated_response: str

```


<style>
:deep(pre), :deep(code) {
  font-size: 1.1rem !important;
  line-height: 1.5 !important;
}
</style>

----

# Tool node

```py {*|1-4|6-8|6,9-12|*} {lines: true}
@tool
def fetch_user_preference(user_name: str) -> str:
    """Fetches a user's past orders of cake flavour and order value.""" 
    conn = sqlite3.connect("cake.db")
    cursor = conn.cursor()         
    cursor.execute("SELECT user, flavour, price FROM orders WHERE 
                    user = ? COLLATE NOCASE", (user_name,))
    rows = cursor.fetchall()                   
    if rows:
        orderHistory = "\n".join([f"{itm[0]} ordered {itm[1]} for Rs. {itm[2]}"  
                                    for itm in rows])            
        return orderHistory
    return f"No flavour data found for name: {user_name}"        
    conn.close()
```


<style>
:deep(pre), :deep(code) {
  font-size: 1rem !important;
  line-height: 1.5 !important;
}
</style>

---

# Define LLM

```py
preference_llm = ChatOpenAI(
    model="gpt-5.6-luna",
    reasoning_effort="none"
)

inventory_llm = ChatOpenAI(
    model="gpt-5.6-luna",
    reasoning_effort="none"
)

federated_llm = ChatOpenAI(
    model="gpt-5.6-luna",
    reasoning_effort="none" 
)
```


<style>
:deep(pre), :deep(code) {
  font-size: 1.2rem !important;
  line-height: 1.5 !important;
}
</style>

---

# tool node

```py {1-4|1-2,7-9|*} {lines: true}
@tool
def fetch_user_preference(user_name: str) -> str:
    """Fetches a user's past orders of cake flavour and order value.""" 
    conn = sqlite3.connect("cake.db")
    ...

preference_llm_with_tools = preference_llm.bind_tools(
    [fetch_user_preference]
)

```


<style>
:deep(pre), :deep(code) {
  font-size: 1.2rem !important;
  line-height: 1.5 !important;
}
</style>

---

# Node

```py {1-13|14-20|*} {lines: true}
def preference_llm_node(state: AgentState):    
    messages_to_send = [
            {
                "role": "system",
                "content": """
                            You are the Preference LLM...
                            """
            },
            {
              "role": "user",
                "content": f"""Find the cake flavour preference for user:{state["user"]}"""
            }
        ]
    response = preference_llm_with_tools.invoke(
        messages_to_send
    )
    return {
        "messages": [response],
        "desired_flavour": response.content
    }

```

<style>
:deep(pre), :deep(code) {
  font-size: 0.9rem !important;
  line-height: 1.5 !important;
}
</style>


---

# Router node

```py {1-7|1,5,8-|*} {lines: true}
def preference_router(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print("\nROUTER: Preference LLM wants to call tool")
        return "preference_tool"    
    print("\nROUTER: No preference available -> END")
    return "end"


preference_tool_node = ToolNode(
    [fetch_user_preference]
)

builder.add_node("preference_tool", preference_tool_node)

```


<style>
:deep(pre), :deep(code) {
  font-size: 1.1rem !important;
  line-height: 1.5 !important;
}
</style>


---

# graph build

```py {1-4|5-13|14-|*} {lines: true}
builder = StateGraph(AgentState)
builder.add_node(   "preference_llm",    preference_llm_node)
builder.add_node(    "preference_tool",    preference_tool_node)
...
builder.add_edge(    START,    "preference_llm")
builder.add_conditional_edges(
    "preference_llm",
    preference_router,
    {
        "preference_tool": "preference_tool",
        "end": END
    }
)
...
app = builder.compile()
final_state = app.invoke(initial_input)

```


<style>
:deep(pre), :deep(code) {
  font-size: 1.1rem !important;
  line-height: 1.5 !important;
}
</style>


