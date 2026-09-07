from FileManager import FileManager
from EmbeddingManager import EmbeddingManager
from dotenv import load_dotenv

load_dotenv()

context_bun = ""

fileMan  = FileManager()
context_bun = fileMan.ReadFromFile()
embedMan = EmbeddingManager()

chunk_list = embedMan.GetChunks(context_bun)
embedMan.convert_txt_to_embed(chunk_list)
print(f"number of chunks is {len(chunk_list)}")

embedMan.compute_cosing_similarity("How long did it take for rewrite?")

# for each_chunk in chunk_list:
#     print(each_chunk)
#     print("===================================")

# print("\n============------==========\n".join(chunk_list))