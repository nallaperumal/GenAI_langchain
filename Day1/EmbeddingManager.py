from langchain_text_splitters import RecursiveCharacterTextSplitter

class EmbeddingManager:

    def GetChunks(self, full_content:str):
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1500,
            chunk_overlap = 150,
            separators = ["\n##", "\n###", "\n\n"," ", ""]
        )

        chunk_list = [chunk for chunk in text_splitter.split_text(full_content)] 
        return chunk_list