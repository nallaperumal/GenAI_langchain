from FileManager import FileManager
from EmbeddingManager import EmbeddingManager

context_bun = ""

fileMan  = FileManager()
context_bun = fileMan.ReadFromFile()
embedMan = EmbeddingManager()

chunk_list = embedMan.GetChunks(context_bun)
embedMan.convert_txt_to_embed(chunk_list)
print(f"number of chunks is {len(chunk_list)}")

# for each_chunk in chunk_list:
#     print(each_chunk)
#     print("===================================")

# print("\n============------==========\n".join(chunk_list))