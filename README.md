File Parser has a collection of helper functions that have been used to make processing the text files easier. 

readFile is for opening the larger content files that have 50=s to mark a new section. It returns a list with each item being a section 

EvalParse is for reading output and storing it in the correct format for the JSON parser to read.

parseToJSON writes and parsed EVAL file into a JSON format. It **appends** to a list that is in it's file. 

clearEnters converts all "\n" to " " and clears the starting file. Was used for narrative pair collection

readNarratives(start=0, total=-1, skip=0) returns narrative pairs in a list [['NewsXXX', Story1, Story2], ...] 
    - Start tells you which narrative to start with. 0 being the first (Default is First) ~Must be positive number
    - Total is maximum narratives to return. 0 or less is all. (Default is all) ~Note Maximum. If Start or skip is not 0, then not all will be returned
    - Skip is how many narrative pairs to skip before returning a new one. Skip 1 returns 1, 3, 5 ...

# Format for Output documents (Judgement doesn't exist in summary docs only Eval)
News: xxxx
Comparison Type: xxxx
Prompt Level: xxxx
Response:
xxxx
Judgement:
xxxx
