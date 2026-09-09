from langgraph.graph import StateGraph, START, END
from langfuse.langchain import CallbackHandler
from langfuse import get_client
from dotenv import load_dotenv
from AppState import AgentState
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
import random
from CakeTools import fetch_inventory_data, fetch_user_preference, save_preference_tool_response, save_inventory_tool_response

num = random.randint(1000, 10100)
session_id= f"session_{num}"

load_dotenv()
langfuse_callback = CallbackHandler()


preference_llm = ChatOpenAI( model="gpt-5.6-luna", reasoning_effort="none")
inventory_llm = ChatOpenAI( model="gpt-5.6-luna", reasoning_effort="none")
federated_llm = ChatOpenAI( model="gpt-5.6-luna", reasoning_effort="none")
flavour_xtract_llm = ChatOpenAI( model="gpt-5.6-luna", reasoning_effort="none")

preference_llm_with_tools = preference_llm.bind_tools([fetch_user_preference])
inventory_llm_with_tools = inventory_llm.bind_tools([fetch_inventory_data])


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

def preference_router(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print("\nROUTER: Preference LLM wants to call tool")
        return "pref_tool"    
    print("\nROUTER: No preference available -> END")
    return "end"

def inventory_llm_node(state: AgentState): 
    desired_flavour = state["desired_flavour"]   
    messages_to_send = [
            {
                "role": "system",
                "content": """
                           You are the Inventory LLM.

                            Your job is to check whether the requested cake flavour
                            is available in inventory.

                            You have access to the fetch_inventory_data tool.

                            You MUST call fetch_inventory_data with the flavour name
                            provided by the user.

                            """
            },
            {
                "role": "user",
                "content": f"""check in the inventory for flavour:- {desired_flavour}"""
            }
        ]
    response = inventory_llm_with_tools.invoke(
        messages_to_send
    )
    print("\ninventory LLM response:")
    print(response)

    return {
        "messages": [response]
    }

def federated_llm_node(state: AgentState): 
    preference = state["desired_flavour"]
    last_message = state["messages"][-1]
    user_name = state["user"]
    inventory = last_message.content 
    messages_to_send = [
            {
                "role": "system",
                "content": """
                          you are teh final federal llm. Based on the user preference and inventory. Based on these provide a proper response

                            """
            },
            {
                "role": "user",
                "content": f"""Can the user {user_name} get flavour:- {preference} with inventory details {inventory}"""
            }
        ]
    response = federated_llm.invoke(
        messages_to_send
    )
    print("\n\n......federated LLM response:....\n\n")
    print(response.content)
    return {
        "messages": [response],
        "federated_response": response.content
    }

def inventory_router(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print("\nROUTER: Inventory LLM wants to call tool")
        return "inv_tool"    
    print("\nROUTER: No stock available -> END")
    return "end"

def xtract_flavour_node(state: AgentState):    
    messages = state["messages"]
    last_message = messages[-1]
    tool_result = last_message.content
    messages_to_send = [
            {
                "role": "system",
                "content": """
                            You are the cake flavour extractor LLM.
                            From the sentence, you extract the flavour name alone in one word
                            """
            },
            {
                "role": "user",
                "content": f"""Find the cake flavour from:{tool_result}"""
            }
        ]
    response = flavour_xtract_llm.invoke(
        messages_to_send
    )
    print("\nPreference LLM response:")
    print(response)

    return {
        "messages": [response],
        "desired_flavour": response.content
    }
preference_tool_node = ToolNode([fetch_user_preference])
inventory_tool_node = ToolNode([fetch_inventory_data])

builder = StateGraph(AgentState)
builder.add_node("pref_llm", preference_llm_node)
builder.add_node("pref_tool", preference_tool_node)
builder.add_node("xtract_flav", xtract_flavour_node)
builder.add_node("inv_node", inventory_llm_node)
builder.add_node("inv_tool", inventory_tool_node)
builder.add_node("fed_node", federated_llm_node)
builder.add_node("save_pref_result", save_preference_tool_response)
builder.add_node("save_inv_result", save_inventory_tool_response)

builder.add_edge(START, "pref_llm")
builder.add_conditional_edges(
    "pref_llm",
    preference_router,
    {
        "pref_tool":"pref_tool",
        "end" : END
    }
)
# builder.add_edge("pref_tool", "xtract_flav")
builder.add_edge("pref_tool", "save_pref_result")
builder.add_edge("save_pref_result", "xtract_flav")

builder.add_edge("xtract_flav", "inv_node")
builder.add_conditional_edges(
    "inv_node",
    inventory_router,
    {
        "inv_tool" : "inv_tool",
        "end" : END
    }
)
builder.add_edge("inv_tool", "save_inv_result")
builder.add_edge("save_inv_result", "fed_node")
builder.add_edge("fed_node", END)
app = builder.compile()

initial_input = {"user":"nickith", "messages":[], "desired_flavour":"", "avg_price":"", "federated_response":""}
final_state = app.invoke(initial_input,
    config ={
    "callbacks" : [langfuse_callback],
    "metadata" :{
        "langfuse_session_id" : session_id,
        "langfuse_user_id" :  "nalla_chain"
    }})
print("\n\n...........\n\n")
print(final_state)
get_client().flush()

