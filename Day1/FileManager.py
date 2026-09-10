class FileManager:

   def ReadFromFile(self, filename = "bun_in_rust_overview.md"):      
        with open(filename, "r") as fi:
            all_lines = fi.readlines()
            context_lst = [this_line for this_line in all_lines]
            context_bun = "".join(context_lst) 
            return context_bun   