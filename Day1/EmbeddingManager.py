from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

class EmbeddingManager:

    def GetChunks(self, full_content:str):
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1500,
            chunk_overlap = 150,
            separators = ["\n##", "\n###", "\n\n"," ", ""]
        )

        chunk_list = [chunk for chunk in text_splitter.split_text(full_content)] 
        return chunk_list

    def convert_txt_to_embed(self, chunks):
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        embeddings  = model.encode(chunks)
        for emb in embeddings:
            print(f"len is....{len(emb)}.. sample {emb[:3]}")
