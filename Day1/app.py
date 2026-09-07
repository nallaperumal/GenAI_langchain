from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

llm = ChatOpenAI(
    model="gpt-5.6-luna",
    max_tokens = 1000,
    temperature = 0.2,
    timeout=15,
)

conversation = [
    SystemMessage("You are a software expert. Answer precisely in 2 sentence"),
    HumanMessage("In which programming language was bun written?"),
    AIMessage("Bun is written in zig"),
    HumanMessage("Was it rewritten in rust?")
]

response = llm.invoke(conversation)

print(response.content)