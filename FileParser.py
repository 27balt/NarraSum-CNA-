import json

#Reads any file stored with proper notation. Returns a list based on the line breaks
def readFile(inputFile):
    with open(inputFile,"r") as f:
        segments = f.read().split("\n" + "=" * 50 + "\n\n")
    return segments

#For Eval Files
def EvalParse(inputFileName,outputFileName,clearOutput = False):
    #Clears outputfile (Just incase)
    if clearOutput:
        with open(outputFileName, "w") as f:
            pass
    #Store the ratings
    ratings = []
    segments = readFile(inputFileName)
    #A segment is a single narrative, subtask, level pair.
    for segment in segments:
        split_item = segment.split("\n", 3)
        if split_item[0] == "":
            break
        tempItem = {"News": split_item[0][6:]}
        tempItem["Comparison Type"] = split_item[1][17:]
        tempItem["Prompt Level"] = split_item[2][14:]
        #spliting Judgement off of Summary
        subsplit_item = (split_item[3].split("Judgement:\n"))
        tempItem["Summary"] = subsplit_item[0][9:]
        tempItem["Judgment"] = subsplit_item[-1].split("\n")
        print(tempItem["Judgment"])
        Judgments = tempItem["Judgment"]

        #Part that cleans ratings
        x = 0
        tempItem["Judgment"] = []

        for rating in Judgments:
            x +=1
            #clear if empty
            # makes a translation table to cut everything
            transTable = str.maketrans("SAD", "SAD", " qwertyuioplkjhgfdsazxcvbnm*:.()0987654321_+-=[]{}\\,!@#$%^&")
            rating = rating[-5:].translate(transTable)
            if rating == "":
                continue
            #Stores Ex (1. SA)
            tempItem["Judgment"].append(f"{rating}")
        #close for loop
        with open(outputFileName,"a") as f:
            f.write(f"News: {tempItem["News"]}\n")
            f.write(f"Comparison Type: {tempItem["Comparison Type"]}\n")
            f.write(f"Prompt Level: {tempItem["Prompt Level"]}\n")
            f.write("Summary:\n")
            f.write(tempItem["Summary"] + "\n")
            f.write(f"Judgement: {tempItem["Judgment"]}\n")
            f.write("\n" + "=" * 50 + "\n\n")

#12 judgements have 6 aspects. Should only be 5
#(GPT4Eval)

#EvalParse("GPT4Eval(LLM4).txt","storeJudgements.txt")

#Clears
def parseToJson(inputFile,LLM,outputFile="JSONStorage.json"):
    finalStorage = []
    with open(outputFile,"r") as f:
        finalStorage = json.load(f)

    #[{"News":X, "LLM":Y,"Subtask":A,"Level":Z,"Cretria":{"A":Ranking,"B":ranking,...}}]
    segments = readFile(inputFile)
    for segment in segments:
        parts = segment.split("\n",3)
        if parts[0] == "":
            continue
        tempSum = parts[3]
        parts[3]=tempSum.split("\nJudgement: ")[1]
        tempDict = {"News":parts[0][6:]}
        #Set manually now.
        tempDict["LLM"] = LLM
        tempDict["Subtask"] = parts[1][17:]
        tempDict["Level"] = parts[2][14:]
        #Lots of things to make sure this parses into a list
        tempDict["Criteria"] = parts[3].split(", ")
        tempDict["Criteria"][0] = tempDict["Criteria"][0][2:-1]
        tempDict["Criteria"][1] = tempDict["Criteria"][1][1:-1]
        tempDict["Criteria"][2] = tempDict["Criteria"][2][1:-1]
        tempDict["Criteria"][3] = tempDict["Criteria"][3][1:-1]
        tempDict["Criteria"][4] = tempDict["Criteria"][4][1:-3]
        finalStorage.append(tempDict)
    #Clears old data, but should have copied it already.
    # Make sure this code finishes
    with open(outputFile,"w") as f:
        json.dump(finalStorage,f)
def clearEnters(inputFile,outputFile):
    with open(inputFile,"r") as f:
        text = f.read()
    with open(inputFile,"w") as f:
        pass
    text = text.replace("\n"," ")
    with open(outputFile,"w") as f:
        f.write(text)
#Reads the narrative pairs you request
#-> Returns a list of narrative pairs
#Starting at 0, if you say 5 you'll skip the first 5
#Total is how many narratives you want returned
#Skip is a pattern to skip them, 0 means all in a row, 1 is every other
def readNarratives(start=0,total=-1,skip=0):
    with open('Narrative Doc.txt','r') as f:
        Narratives = f.read().split("=====\n")
    x = 0
    returnList = []
    storageList = []
    for set in Narratives:
        tempList = set.split('\n')
        tempList[1] = tempList[1][8:]
        tempList[2] = tempList[2][8:]
        storageList.append(tempList)
    if total <=0:
        #Allow all if 0 or less
        total = len(storageList)

    for i in range(start,len(storageList),skip+1):
        if x >= total:
            break
        x += 1
        returnList.append(storageList[i])
    return returnList
