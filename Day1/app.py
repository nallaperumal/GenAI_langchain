from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from langfuse.langchain import CallbackHandler

load_dotenv()
langfuse_callback = CallbackHandler()

llm = ChatOpenAI(
    model="gpt-5.6-luna",
    max_tokens = 1000,
    temperature = 0.2,
    timeout=15,
)

conversation = [
    {"role" : "system", "content": "You are a software expert. Answer precisely in 2 sentence"},
    {"role" : "user", "content": "In which programming language was bun written?"},
    {"role" : "assistant", "content": "Bun is written in zig"},
    {"role" : "user", "content": "Was it rewritten in rust?"}
]

response = llm.invoke(conversation, config ={
    "callbacks" : [langfuse_callback]
})  

print(response.content)