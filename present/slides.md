---
layout: fact
---

# Langchain

--- 

# Agenda

<v-clicks>

- Retrieval
- LCEL intro
- Combining RAG and langchain
- Middleware 
- Langgraph

</v-clicks>

---

# Chroma db Init

```py {lines:true}
class EmbeddingManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        self.vectorstore = Chroma(
            collection_name="my_documents",
            embedding_function=self.embeddings,
            persist_directory="./chroma_db"
        )
        self.chunk_list = []
```

---

# Retriever

```py {1|*|2-6|7-|*} {lines:true}
def search(self, srch_text: str, k=3):
    vector_retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": k
            }
        )
    results = vector_retriever.invoke(srch_text)
    return results    
```

---

# Sparse retriever 

```py {1|2-|*} {lines:true}
def search(self, srch_text: str, k=3):
        bm25_retriever = BM25Retriever.from_texts(self.chunk_list)
        bm25_retriever.k = k
```

---

# Hybrid Retriever

```py {2-7|9-18|19-|*} {lines:true}
def search(self, srch_text: str, k=3):
        bm25_retriever = BM25Retriever.from_texts(self.chunk_list)
        bm25_retriever.k = k
        vector_retriever = self.vectorstore.as_retriever(
                search_kwargs={
                    "k": k
                }
            )
        hybrid_retriever = EnsembleRetriever(
            retrievers=[
                vector_retriever,
                bm25_retriever
            ],
            weights=[
                0.7,
                0.3
            ]
        )
        results = hybrid_retriever.invoke(srch_text)
        return results[:k] 
```

---

# Chunking optimization

```py {1-6|7-10|11-18|19-|*} {lines:true}
def split_to_chunks(self, full_text):
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=360,
            chunk_overlap=30,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
        )
    import re
    pattern = r"(.*?)(```[\s\S]*?```|$)"
    chunks = []
    matches = re.finditer(pattern, full_text, re.DOTALL)
    for match in matches:
        prose = match.group(1).strip()
        code_block = match.group(2).strip()
        if prose:
            prose_chunks = text_splitter.split_text(prose)
            chunks.extend([c for c in prose_chunks if c.strip()])
        if code_block:
            chunks.append(code_block)

    self.chunk_list = chunks
    return self.chunk_list
```        

---

# Reranking

<v-clicks>

- Improves accuracy
- Improves the relevance sorting
- full cross attention between every text and word 

</v-clicks>

---

# Code sample

```sh {1-14|12-|*} {lines:true}
from langchain_community.retrievers import BM25Retriever
...

class EmbeddingManager:

  def search(self, srch_text: str, k=3):
    bm25_retriever = BM25Retriever.from_texts(self.chunk_list)
    bm25_retriever.k = fetch_k
    vector_retriever = self.vectorstore.as_retriever(
        search_kwargs={"k": fetch_k}
    )
    hybrid_retriever = EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever], weights=[0.7, 0.3]
    )
    compressor = CohereRerank(
        model="rerank-english-v3.0", top_n=k
    )  # Requires COHERE_API_KEY environment variable
    rerank_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=hybrid_retriever
    )
    results = rerank_retriever.invoke(srch_text)
    return results

  def split_to_chunks(self, full_text):
    ...
    return self.chunk_list

  def convert_chunks_to_embeddings(self, chunk_list):
    self.vectorstore.add_texts(texts=chunk_list)

```

---

# Retrieved result

```json
[
    Document(
        page_content="Text content of chunk 1...",
        metadata={"source": "doc1.txt"}  # Any metadata attached to the chunk
    ),
    Document(
        page_content="Text content of chunk 2...",
        metadata={"source": "doc2.txt"}
    )
]
```

---

# Rernked Retrieved result

```json
[
    Document(
        page_content="Text content of chunk 1...",
        metadata={"source": "doc1.txt", "relevance_score": 0.9841203}  # Any metadata attached to the chunk
    ),
    Document(
        page_content="Text content of chunk 2...",
        metadata={"source": "doc2.txt","relevance_score": 0.868337}
    )
]
```


---

# Ford motors

<v-clicks>

- First company failed
- Producion Speed matters
- Assembly line was introduced
- LCEL is similar 

</v-clicks>



---

# Langchain (before LCEL)

- Varied function for different process
- 1000s of function
- Bloate SDKs

---

# LCEL

- Runnable

```py
chain =  Runnablepassthrough | llm | stroutputparser

chain.invoke()
```

---

# include langfuse session

```py
response = llm.invoke(user_msg, 
                          config = {
                              "callbacks":[langfuse_handler],
                              "metadata":
                                {
                                "langfuse_session_id":"Bun sesssion_1",
                                "langfuse_user_id": "nalla"
                                }
                              }
                          )
```

---

# Without LCEL

```py
from langchain_core.prompts import ChatPromptTemplate

ctxt_txt = "The bun is rewritten completely with rust instead of zig. This was done in 11 days with 65 bots and an expense of 1,64,000 USD."

prompt_template = ChatPromptTemplate([("human","with the available context : {context}.\n provide the response for {question}")])
prompt = prompt_template.invoke({"context":ctxt_txt, "question":user_msg})
response = llm.invoke(prompt, config ...) 
```

---

# With LCEL

```
from langchain_core.output_parsers import StrOutputParser

chain = prompt_template | llm | StrOutputParser()
resp = chain.invoke({"context":ctxt_txt, "question":user_msg})
```

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

---

# guard rails

```py 
def execute_guarded_chain(resp: QA_KensingtonResponse):
    if resp.confidence < 0.6:
        resp.answer = "I am unable to answer this question based strictly on the provided context."
        resp.found_in_context = False
    return resp
...
chain =  conversation_template | structured_llm | RunnableLambda(execute_guarded_chain)

print(response.answer)
print(response.found_in_context)
```
