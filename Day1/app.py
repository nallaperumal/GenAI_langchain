from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from langfuse.langchain import CallbackHandler
import random
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableLambda, RunnableParallel
from FileManager import FileManager
from EmbeddingManager import EmbeddingManager

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

# ctxt_txt = "The bun is rewritten completely with rust instead of zig. This was done in 11 days with 65 bots and an expense of 1,64,000 USD."

ctxt_txt1 = ""
ctxt_txt2 = ""

fileMan  = FileManager()
context_bun = fileMan.ReadFromFile()
embedMan = EmbeddingManager()

chunk_list = embedMan.GetChunks(context_bun)
embedMan.convert_txt_to_embed(chunk_list)
res1 = embedMan.search("what is bun?")
res2 = embedMan.search("what is bun?")
ctxt_txt1  = "\n".join([txt.page_content for txt in res1])
ctxt_txt2  = "\n".join([txt.page_content for txt in res2])

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

parallel_chain = RunnableParallel(
    out1= RunnableLambda(lambda abc: chain.invoke({'context': abc['ctxt1'], 'question':abc['q']})),
    out2= RunnableLambda(lambda abc: chain.invoke({'context': abc['ctxt2'], 'question':abc['q']}))
)

resp = parallel_chain.invoke({
    'ctxt1': ctxt_txt1,
    'ctxt2': ctxt_txt2,
    'q' : "what is bun?"
},  config ={
    "callbacks" : [langfuse_callback],
    "metadata" :{
        "langfuse_session_id" : session_id,
        "langfuse_user_id" :  "nalla_chain"
    }
})

# resp = chain.invoke({'context': ctxt_txt, 'question':"what is bun?"}, config ={
#     "callbacks" : [langfuse_callback],
#     "metadata" :{
#         "langfuse_session_id" : session_id,
#         "langfuse_user_id" :  "nalla_chain"
#     }
# })
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