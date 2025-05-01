# Corrected FileParser.py

import json

# Reads any file stored with proper notation. Returns a list based on the line breaks
# This function seems unused by the main script but kept for completeness
def readFile(inputFile):
    """Reads a file and splits it into segments based on 50 '=' separators."""
    try:
        with open(inputFile, "r", encoding="utf-8") as f: # Added encoding
            # Ensure consistent line endings before splitting
            content = f.read().replace('\r\n', '\n')
            segments = content.split("\n" + "=" * 50 + "\n\n")
        # Remove potential leading/trailing empty segments if the file starts/ends with separator
        return [seg for seg in segments if seg.strip()]
    except FileNotFoundError:
        print(f"Error: File not found at {inputFile}")
        return []
    except Exception as e:
        print(f"Error reading file {inputFile}: {e}")
        return []


# For Eval Files (Corrected f-strings)
# This function seems unused by the main script but corrected anyway
def EvalParse(inputFileName, outputFileName, clearOutput=False):
    """Parses an evaluation file and writes formatted output."""
    # Clears outputfile (Just incase)
    if clearOutput:
        try:
            with open(outputFileName, "w", encoding="utf-8") as f: # Added encoding
                pass
        except Exception as e:
             print(f"Error clearing output file {outputFileName}: {e}")
             # Decide if continuing makes sense
             return

    # Store the ratings
    ratings = []
    segments = readFile(inputFileName)
    if not segments:
         print(f"No segments found in {inputFileName}. Aborting EvalParse.")
         return

    # A segment is a single narrative, subtask, level pair.
    try:
        with open(outputFileName, "a", encoding="utf-8") as f_out: # Open output file once
            for segment in segments:
                if not segment.strip(): # Skip empty segments
                    continue
                split_item = segment.strip().split("\n", 3) # Use strip() before split
                if len(split_item) < 4:
                     print(f"Warning: Skipping segment due to unexpected format:\n{segment[:100]}...")
                     continue

                # Use .get() for safer dictionary access, though direct assignment is fine here
                tempItem = {"News": split_item[0][6:].strip()} # Add strip()
                tempItem["Comparison Type"] = split_item[1][17:].strip()
                tempItem["Prompt Level"] = split_item[2][14:].strip()

                # Splitting Judgement off of Summary
                # Handle case where "Judgement:" might not be present
                subsplit_item = split_item[3].split("Judgement:\n", 1) # Split only once
                tempItem["Summary"] = subsplit_item[0][9:].strip() # Add strip()

                if len(subsplit_item) > 1:
                    # Split judgments by newline, remove empty strings
                    Judgments = [j.strip() for j in subsplit_item[1].strip().split("\n") if j.strip()]
                else:
                    Judgments = [] # No judgment found

                # print(Judgments) # Debugging print

                # Part that cleans ratings
                tempItem["Judgment"] = []
                # Makes a translation table to cut everything except S, A, D
                transTable = str.maketrans("", "", " qwertyuioplkjhgfdsazxcvbnm*:.()0987654321_+-=[]{}\\,!@#$%^&")

                for rating in Judgments:
                    # Apply translation only to the relevant part if format is consistent
                    # Assuming rating format might be like "1. SA" or just "SA"
                    # Taking last 5 chars is brittle; cleaning based on expected chars is better
                    cleaned_rating = rating.translate(transTable)
                    if cleaned_rating: # Only add if something remains after cleaning
                        tempItem["Judgment"].append(cleaned_rating)
                # Close for loop for judgments

                # --- CORRECTED F-STRINGS ---
                f_out.write(f"News: {tempItem['News']}\n")
                f_out.write(f"Comparison Type: {tempItem['Comparison Type']}\n")
                f_out.write(f"Prompt Level: {tempItem['Prompt Level']}\n")
                f_out.write("Summary:\n")
                f_out.write(tempItem["Summary"] + "\n") # Already stripped
                # Represent list as a string, e.g., comma-separated
                judgment_str = ", ".join(tempItem.get('Judgment', []))
                f_out.write(f"Judgement: [{judgment_str}]\n") # Corrected f-string syntax; represent list clearly
                # --- END CORRECTIONS ---

                f_out.write("\n" + "=" * 50 + "\n\n") # Separator

    except Exception as e:
        print(f"Error during EvalParse processing or writing to {outputFileName}: {e}")


# This function seems unused by the main script but kept for completeness
# Needs significant review if intended for use, logic for parsing 'Criteria' is complex
def parseToJson(inputFile, LLM, outputFile="JSONStorage.json"):
    """Parses a specific file format into a JSON list and appends to outputFile."""
    finalStorage = []
    # Load existing data or start fresh if file doesn't exist or is invalid
    try:
        with open(outputFile, "r", encoding="utf-8") as f: # Added encoding
            finalStorage = json.load(f)
        if not isinstance(finalStorage, list):
             print(f"Warning: Existing content in {outputFile} is not a list. Starting fresh.")
             finalStorage = []
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Warning: {outputFile} not found or invalid JSON. Starting fresh.")
        finalStorage = []
    except Exception as e:
        print(f"Error reading {outputFile}: {e}. Starting fresh.")
        finalStorage = []

    segments = readFile(inputFile)
    if not segments:
         print(f"No segments found in {inputFile}. Aborting parseToJson.")
         return # Or handle differently

    for segment in segments:
        if not segment.strip(): continue # Skip empty

        parts = segment.strip().split("\n", 3)
        if len(parts) < 4:
            print(f"Warning: Skipping segment in parseToJson due to format:\n{segment[:100]}...")
            continue

        # Careful splitting and indexing needed here
        tempSum_parts = parts[3].split("\nJudgement: ", 1)
        summary_text = tempSum_parts[0].strip() # Assuming summary comes before Judgement
        judgement_text = tempSum_parts[1].strip() if len(tempSum_parts) > 1 else ""

        tempDict = {"News": parts[0][6:].strip()}
        tempDict["LLM"] = LLM # Set manually now.
        tempDict["Subtask"] = parts[1][17:].strip()
        tempDict["Level"] = parts[2][14:].strip()

        # --- Parsing "Criteria" --- Highly specific and brittle logic ---
        # This assumes judgement_text is exactly like "['SA', 'A', 'D', 'S', 'SA']"
        # It's safer to use ast.literal_eval if the format is guaranteed Python list literal
        try:
            criteria_str = judgement_text.strip()
            if criteria_str.startswith('[') and criteria_str.endswith(']'):
                 # Attempt to parse as a list representation string
                 # Remove brackets, split by comma, strip quotes and spaces
                 criteria_list = [item.strip().strip("'\"") for item in criteria_str[1:-1].split(',')]
                 tempDict["Criteria"] = criteria_list
            else:
                 # Fallback or error if format is different
                 tempDict["Criteria"] = []
                 print(f"Warning: Could not parse Criteria from Judgement: {judgement_text}")

            # The original slicing logic was very specific and likely incorrect/unsafe
            # tempDict["Criteria"] = parts[3].split(", ") -> This used the wrong part
            # The slicing [0][2:-1] etc. suggests a very fixed format assumption
            # Replaced with the safer parsing above.
        except Exception as e:
            print(f"Error parsing Criteria for News {tempDict['News']}: {e}")
            tempDict["Criteria"] = [] # Assign empty list on error
        # --- End Criteria Parsing ---

        finalStorage.append(tempDict)

    # Save the updated list back to the JSON file
    try:
        with open(outputFile, "w", encoding="utf-8") as f: # Added encoding
            json.dump(finalStorage, f, indent=4, ensure_ascii=False) # Add indent for readability
        print(f"Data successfully appended and saved to {outputFile}")
    except Exception as e:
        print(f"Error writing final data to {outputFile}: {e}")


# --- CORRECTED clearEnters to match usage in the main script ---
def clearEnters(input_string):
    """Replaces newline characters in a string with spaces."""
    if not isinstance(input_string, str):
        # Handle cases where input might not be a string as expected
        print(f"Warning: clearEnters received non-string input type {type(input_string)}. Converting to string.")
        input_string = str(input_string)
    return input_string.replace("\n", " ").replace("\r", " ") # Handle \r too

# --- CORRECTED readNarratives to match usage in the main script ---
def readNarratives(file_content, start=0, total=-1, skip=0):
    """
    Reads narrative pairs from a string containing the file content.
    Splits based on "=====\n" separator.

    Args:
        file_content (str): The string content read from the narrative document.
        start (int): Index of the first narrative pair to return.
        total (int): Maximum number of narrative pairs to return (-1 for all).
        skip (int): Skips narratives (0=none, 1=every other, etc.).

    Returns:
        list: A list of narrative pairs, where each pair is a list of strings.
    """
    if not isinstance(file_content, str):
         print("Error: readNarratives expects a string input for file_content.")
         return []

    # Split the content using the specified separator
    # Ensure consistent line endings first
    file_content = file_content.replace('\r\n', '\n')
    Narratives = file_content.split("=====\n")

    storageList = []
    for i, narrative_set_str in enumerate(Narratives):
        # Skip empty strings resulting from separators at start/end or double separators
        if not narrative_set_str.strip():
            continue

        tempList = narrative_set_str.strip().split('\n')
        if len(tempList) >= 3:
            # Clean potential "Story X: " prefixes if they exist consistently
            # Be cautious if format varies
            if tempList[0].startswith("News"): # Keep News line as is for now
                 pass # No change needed based on original logic?
            if tempList[1].startswith("Story 1:"):
                 tempList[1] = tempList[1][8:].strip()
            if tempList[2].startswith("Story 2:"):
                 tempList[2] = tempList[2][8:].strip()
            storageList.append(tempList)
        else:
            print(f"Warning: Narrative set index {i} has less than 3 lines, skipping:\n'{narrative_set_str[:50]}...'")


    # Apply start, total, skip logic
    if total <= 0:
        total = len(storageList) # Allow all if 0 or less

    returnList = []
    count = 0
    # Correctly implement skip logic: range(start, end, step)
    # Step should be skip + 1
    for i in range(start, len(storageList), skip + 1):
        if count >= total:
            break
        returnList.append(storageList[i])
        count += 1

    return returnList
