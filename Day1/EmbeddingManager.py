from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer, util
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

class EmbeddingManager:
    def __init__(self):
        print("init")
        embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            collection_name="my_documents",
            embedding_function=embeddings,
            persist_directory="./chroma_db")
        self.chunk_list = []
   
    def compute_cosing_similarity(self, srchtext: str):
        # model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  
        # search_txt_as_embdding = model.encode(srchtext)
        client = OpenAI()
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input = srchtext
        )
        search_txt_as_embdding = response.data[0].embedding
        print(f"...{srchtext}'s embedding is  {search_txt_as_embdding[:3]} ({len(search_txt_as_embdding)})")
        similarities = util.cos_sim(search_txt_as_embdding, self.embeddings )
        print(f"... similarities: {similarities}")

    def GetChunks(self, full_content:str):
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1500,
            chunk_overlap = 150,
            separators = ["\n##", "\n###", "\n\n"," ", ""]
        )

        chunk_list = [chunk for chunk in text_splitter.split_text(full_content)] 
        self.chunk_list = chunk_list
        return chunk_list
    def convert_txt_to_embed(self, chunks):
        # client = OpenAI()
        # response = client.embeddings.create(
        #     model="text-embedding-3-small",
        #     input = chunks
        # )
        # self.embeddings = [item.embedding for item in response.data]
        print(f"chunks.... {chunks}")
        self.vectorstore.add_texts(texts=chunks)
        # for emb in self.embeddings:
        #     print(f"len is....{len(emb)}.. sample {emb[:3]}")
    def search(self, srch_text: str, k=3):
        # results = self.vectorstore.similarity_search(srch_text, k=k)
        # return results
        vector_retriever = self.vectorstore.as_retriever(           
            search_kwargs={
                "k": k
            }
        )
        results = vector_retriever.invoke(srch_text)
        return results    
