from langchain_text_splitters import RecursiveCharacterTextSplitter

context_bun = ""

with open("bun_in_rust_overview.md", "r") as fi:
    all_lines = fi.readlines()
    # for this_line in all_lines:
    #     context_bun += this_line
    context_lst = [this_line for this_line in all_lines]
    context_bun = "".join(context_lst)


text_splitter =RecursiveCharacterTextSplitter(
    chunk_size = 1500,
    chunk_overlap = 150,
    separators = ["\n##", "\n###", "\n\n"," ", ""]
)

chunk_list = [chunk  for chunk in text_splitter.split_text(context_bun)] 
print(f"number of chunks is {len(chunk_list)}")

for each_chunk in chunk_list:
    print(each_chunk)
    print("===================================")