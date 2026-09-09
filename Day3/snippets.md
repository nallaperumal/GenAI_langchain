# Code snippets

- Imports

```py
from langgraph.graph import StateGraph, START, END
from langfuse.langchain import CallbackHandler
from langfuse import get_client
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
import sqlite3
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

```


```py
class AgentState(TypedDict):
    user: str
    messages: Annotated[list, add_messages]
    desired_flavour: str
    avg_price : str
    federated_response: str
```

```py
@tool
def fetch_user_preference(user_name: str) -> str:
    """Fetches a user's past orders of cake flavour and order value.""" 
    conn = sqlite3.connect("cake.db")
    cursor = conn.cursor()    
    try:       
        cursor.execute("SELECT user, flavour, price FROM orders WHERE user = ? COLLATE NOCASE", (user_name,))
        rows = cursor.fetchall()            
       
        if rows:
            orderHistory = "\n".join([f"{itm[0]} ordered {itm[1]} for Rs. {itm[2]}"  for itm in rows])            
            return orderHistory
        return f"No flavour data found for name: {user_name}"        
    except sqlite3.Error as e:
        return f"Database error encountered: {str(e)}"
    finally:
        conn.close()
```

```py
preference_llm = ChatOpenAI(
    model="gpt-5.6-luna",
    reasoning_effort="none",
    temperature=0
)
```

```py
preference_llm_with_tools = preference_llm.bind_tools(
    [fetch_user_preference]
)
```

```py
def preference_llm_node(state: AgentState):    
    messages_to_send = [
            {
                "role": "system",
                "content": """
                            You are the Preference LLM.

                            You have received the result from the preference database tool.

                            Analyze the tool result and determine the user's preferred
                            cake flavour.

                            Do not call the tool again.

                            If there is valid preference information, respond with
                            the preferred flavour and relevant information.

                            If no preference information was found, clearly say so.
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
    print("\nPreference LLM response:")
    print(response)

    return {
        "messages": [response],
        "desired_flavour": response.content
    }
```

```py
def preference_router(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print("\nROUTER: Preference LLM wants to call tool")
        return "preference_tool"    
    print("\nROUTER: No preference available -> END")
    return "end"
```

```py
def xtract_flavour_node(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    tool_result = last_message.content
    preference_result = tool_result
    messages = [
        {
            "role": "system",
            "content": """
                You are a cake flavour extraction system.

                Extract ONLY the cake flavour name from the supplied
                preference information.

                Return ONLY the flavour name.

                Do not return:
                - explanations
                - sentences
                - price
                - quantity
                - punctuation
                - prefixes such as "Flavour:"

                Example:

                Input:
                "The user's preferred flavour is Chocolate."

                Output:
                Chocolate

                Input:
                "Nickith has previously ordered Red Velvet for Rs. 500."

                Output:
                Red Velvet
            """
        },
        {
            "role": "user",
            "content": f"""
                Preference LLM result:

                {preference_result}

                Extract the cake flavour name only.
            """
        }
    ]

    response = flavour_xtract_llm.invoke(messages)
    flavour = response.content.strip()
    print("\nExtracted flavour:")
    print(flavour)

    return {
        "desired_flavour": flavour,
        "messages": [response]
    }
```

```py

def inventory_llm_node(state: AgentState):
    desired_flavour = state["desired_flavour"]
    messages = [
        {
            "role": "system",
            "content": """
                    You are the Inventory LLM.

                    Your job is to check whether the user's preferred cake
                    flavour is currently available.

                    You have access to the fetch_inventory_data tool.

                    You MUST use the tool to check inventory.

                    Extract the actual cake flavour from the preference
                    information supplied by the previous LLM.

                    Do not invent inventory information.
                    """
        },
        {
            "role": "user",
            "content": f"""
                User:
                {state["user"]}

                Preference LLM result:
                {desired_flavour}

                Check the inventory for the user's preferred flavour.
                """
        }
    ]

    response = inventory_llm_with_tools.invoke(
        messages
    )

    print("\nInventory LLM response:")
    print(response)

    return {
        "messages": [response]
    }

```

```py
def federated_llm_node(state: AgentState):
    preference = state.get(
        "desired_flavour",
        "No preference information available"
    )

    messages = state["messages"]
    last_message = messages[-1]
    inventory = last_message.content
    messages = [
        {
            "role": "system",
            "content": """
                You are the final Federated LLM.

                You combine the results produced by two specialist LLMs:

                1. Preference LLM
                2. Inventory LLM

                Provide a concise final recommendation to the user.

                Do not invent information.

                If the preferred flavour is available, clearly state
                that it is available and mention the price and quantity
                when provided.

                If it is not available, clearly state that.
                """
        },
        {
            "role": "user",
            "content": f"""
                        User:
                        {state["user"]}

                        PREFERENCE LLM RESULT:
                        {preference}

                        INVENTORY LLM RESULT:
                        {inventory}

                        Provide the final recommendation.
                        """
        }
    ]

    response = federated_llm.invoke(
        messages
    )

    print("\nFederated LLM response:")
    print(response.content)

    return {
        "messages": [response],
        "federated_response": response.content
    }
```

```py
builder = StateGraph(AgentState)
builder.add_node(   "preference_llm",    preference_llm_node)

builder.add_edge(    START,    "preference_llm")

builder.add_conditional_edges(
    "preference_llm",
    preference_router,
    {
        "preference_tool": "preference_tool",
        "end": END
    }
)
```


