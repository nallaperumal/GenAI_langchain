from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from langfuse.langchain import CallbackHandler
import random
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableLambda

load_dotenv()
langfuse_callback = CallbackHandler()

llm = ChatOpenAI(
    model="gpt-5.6-luna",
    max_tokens = 1000,
    temperature = 0.2,
    timeout=15,
)


num = random.randint(1000, 10100)
session_id= f"session_{num}"

ctxt_txt = "The bun is rewritten completely with rust instead of zig. This was done in 11 days with 65 bots and an expense of 1,64,000 USD."

prompt_template = ChatPromptTemplate([("human","with the available context : {context}.\n provide the response for {question}")])

class DesiredResponse(BaseModel):
    answer: str = Field(description="Direct answer based strictly on the provided context")
    confidence: float = Field(description="Confidence level: 0 to 5")
    found_in_context: bool = Field(description="True if context contains the answer, False otherwise")

structured_llm = llm.with_structured_output(DesiredResponse)

def execute_guarded_chain(resp: DesiredResponse):
    if resp.confidence < 0.6:
        resp.answer = "I am unable to answer this question based strictly on the provided context."
        resp.found_in_context = False
    return resp

chain = prompt_template | structured_llm | RunnableLambda(execute_guarded_chain)


resp = chain.invoke({'context': ctxt_txt, 'question':"what is bun?"}, config ={
    "callbacks" : [langfuse_callback],
    "metadata" :{
        "langfuse_session_id" : session_id,
        "langfuse_user_id" :  "nalla_chain"
    }
})
print(resp)

# conversation = [
#     {"role" : "system", "content": "You are a software expert. Answer precisely in 2 sentence"},
#     {"role" : "user", "content": "In which programming language was bun written?"},
#     {"role" : "assistant", "content": "Bun is written in zig"},
#     {"role" : "user", "content": "Was it rewritten in rust?"}
# ]

# num = random.randint(1000, 10100)
# session_id= f"session_{num}"

# response = llm.invoke(conversation, config ={
#     "callbacks" : [langfuse_callback],
#     "metadata" :{
#         "langfuse_session_id" : session_id,
#         "langfuse_user_id" :  "nalla"
#     }
# })  

# print(response.content)