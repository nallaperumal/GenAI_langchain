---
layout: fact
---

# Welcome to Gen AI 

---

# Agenda

<v-clicks>

- Basics of LLM
- A Case Study
- Setting up Python environment
- Openai with python samples
- Semantic search 
- Hybrid search
</v-clicks>

---
layout: fact
---

# Coding needed?

---

# Why Coding Needed?

<v-clicks>

- Technical debt
- Hallucination in production
- Token cost
- Ability the judge the quality of code

</v-clicks>
---

# Case Study 


<v-clicks>

- what is Bun (Software)?
- It is Software runtime similar to Nodejs
- It works with Javscript/TypeScript
- Super fast
- Written on Zig
- Rewritten in Rust in May 2026
- With around 64 agents in just 11 days 
- 6500 commits costing 1,65,000 USD

</v-clicks>

---

# LLM

<v-clicks>

- AI is not new
- Attention is all you need
- Transformer Architecture
- Temperature and top k
- Refer [here](https://poloclub.github.io/transformer-explainer/)
- and [here](https://bbycroft.net/llm)

</v-clicks>

---

# Tools

<v-clicks>

- Langchain
- Langfuse
- Chromadb

</v-clicks>

---

# Langfuse

<v-clicks>

- Observability
- Traceability
- Test/evaluate
- Opensource

</v-clicks>

---

# Let's code

- Libraries
```md
langchain_openai
dotenv
```

- Installation

```sh
pip install -r requirements.txt
```

- Environment creation
```sh
python -m venv my_env
my_env\Scripts\activate
```
- .env
```md {1|2-|*}  
OPENAI_API_KEY=sk....

LANGFUSE_SECRET_KEY="sk..."
LANGFUSE_PUBLIC_KEY="pk..."
LANGFUSE_BASE_URL="https://cloud.langfuse.com"

```

---

```py {1,4|2,6-8|10-|*} {lines:true}
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="gpt-5.6-luna",
)

response = llm.invoke("what is bun framework in Software?")

print(response.content)
```

---
layout: fact
---

# RAG

---

# Reading comprehension

<v-clicks>

- Passage with 3 or 4 paragraphs
- 4 or 5 questions given
- Quesions can be simple or tricky

</v-clicks>

---

# Challenges in RAG

<v-clicks>

- Huge content
- Cost of tokens
- Hallucinations with large data

</v-clicks>

---

# Steps involved in RAG

<v-clicks>

- Chunking
- Embedding Conversion
- Retrieval (or Hybrid Search)
- Context setup

</v-clicks>

---

# Chunking Strategy

<v-clicks>

- Fixed Size Chunking
- Recursive chunking
- Document structure aware-chunking
- Semantic Chunking
- Agentic chunking

</v-clicks>

---

# Embeddings

<v-clicks>

- Non-deterministic
- Similarty rather than equality
- Dimensionality
- Cosine similarity/euclidean distance 

</v-clicks>

---

# Choosing the right embeddings

<v-clicks>

- Open source sentence transformers
- Open AI sentence transformers
- Cohere Embddings 
- Google Embeddings 2

</v-clicks>


---

# Retrieval

<v-clicks>

- Dense retieval (Semantic)
- Sparse retrieval (BM26 type)
- Hybrid retrieval

</v-clicks>