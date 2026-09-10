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


---

# Ragas

```py
data = {
    "question": [
        "What is the capital of France?"
    ],
    "answer": [
        "The capital of France is Paris."
    ],
    "contexts": [
        [
            "Paris is the capital and largest city of France."
        ]
    ],
    "ground_truth": [
        "Paris is the capital of France."
    ]
}
dataset = Dataset.from_dict(data)
llm = ChatOpenAI( model="gpt-5.6-luna", reasoning_effort="none")
result = evaluate(
    dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ],
    llm=llm
)
print(result)
```

---

```py
def ragas_evaluation_node(state: AgentState):
    question = f"""
    Can user {state["user"]} get their preferred cake flavour?
    """
    answer = state["federated_response"]
    contexts = [
        state["preference_tool_response"],
        state["inventory_tool_response"]
    ]

    dataset = Dataset.from_dict({
        "user_input": [question],
        "response": [answer],
        "retrieved_contexts": [contexts],
    })

    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy
        ],
        llm=ragas_llm
    )

    return {
        "ragas_score": str(result)
    }
```

---

```py
builder.add_node("fed_node", federated_llm_node)
builder.add_node("ragas_eval", ragas_evaluation_node)
```

```py
builder.add_edge("fed_node", "ragas_eval")
builder.add_edge("ragas_eval", END)
```

---

# Answer correctness (needs Ground truth)

```py
ground_truth = """
Yes. Nickith's preferred flavour is chocolate, and chocolate is
currently available in inventory.
"""

dataset = Dataset.from_dict({
    "user_input": [question],
    "response": [answer],
    "retrieved_contexts": [contexts],
    "reference": [ground_truth],
})
```


# With LCEL

```
from langchain_core.output_parsers import StrOutputParser

chain = prompt_template | llm | StrOutputParser()
resp = chain.invoke({"context":ctxt_txt, "question":user_msg})
```
<style>
/* Target pre or code elements inside the slide */
:deep(pre), :deep(code) {
  font-size: 1.25rem !important;
  line-height: 1.5 !important;
}
</style>
---

# Structured output

```py
from pydantic import BaseModel, Field

class DesiredResponse(BaseModel):
    answer: str = Field(description="Direct answer based strictly on the provided context")
    confidence: float = Field(description="Confidence level: 0 to 5")
    found_in_context: bool = Field(description="True if context contains the answer, False otherwise")

structured_llm = llm.with_structured_output(DesiredResponse)
...

chain = prompt_template | structured_llm | StrOutputParser()
```


<style>
/* Target pre or code elements inside the slide */
:deep(pre), :deep(code) {
  font-size: 1.1rem !important;
  line-height: 1.5 !important;
}
</style>
---

# guard rails

```py 
def execute_guarded_chain(resp: DesiredResponse):
    if resp.confidence < 0.6:
        resp.answer = "I am unable to answer this question based strictly on the provided context."
        resp.found_in_context = False
    return resp
...
chain =  conversation_template | structured_llm | RunnableLambda(execute_guarded_chain)

print(response.answer)
print(response.found_in_context)
```


<style>
/* Target pre or code elements inside the slide */
:deep(pre), :deep(code) {
  font-size: 1.1rem !important;
  line-height: 1.5 !important;
}
</style>
---

# RAG and LCEL

```py
context_bun = ""

fileMan  = FileManager()
context_bun = fileMan.ReadFromFile()
embedMan = EmbeddingManager()

chunk_list = embedMan.GetChunks(context_bun)
embedMan.convert_txt_to_embed(chunk_list)
res = embedMan.search("what is bun?")

context_bun  = "\n".join([txt.page_content for txt in res])
```


<style>
/* Target pre or code elements inside the slide */
:deep(pre), :deep(code) {
  font-size: 1.2rem !important;
  line-height: 1.5 !important;
}
</style>

---

# Dual context

```py
res1 = embedMan.search("what is bun?", 3)
res2 = embedMan.search("what is bun?", 5)

ctxt_txt1 = "\n".join([txt.page_content for txt in res1])
ctxt_txt2 = "\n".join([txt.page_content for txt in res2])
```


<style>
/* Target pre or code elements inside the slide */
:deep(pre), :deep(code) {
  font-size: 1.1rem !important;
  line-height: 1.5 !important;
}
</style>

---

# Parallel chain

```py
# resp = chain.invoke({'context': ctxt_txt, 'question':"what is bun?"})
parallel_chain = RunnableParallel(
 resp1 = RunnableLambda(lambda x: chain.invoke({'context': x['ctxt1'], 'question': x['question']})),
 resp2 = RunnableLambda(lambda x: chain.invoke({'context': x['ctxt2'], 'question': x['question']}))
    )


resp = parallel_chain.invoke({
        'ctxt1': ctxt_txt1,
        'ctxt2': ctxt_txt2,
        'question': "what is bun?"
    })
```

<style>
/* Target pre or code elements inside the slide */
:deep(pre), :deep(code) {
  font-size: 1.1rem !important;
  line-height: 1.5 !important;
}
</style>
