import nltk
import copy
import os
import sys 
import json
import itertools

blockSizeLimitMB = 0.1
stop_word_file = open('stop_words.txt', 'r')
stop_words = stop_word_file.read().split()

def create_SPIMI_index(input_file):
    token_stream = []
    docID = 0 
    blockNumber = 0 

    for line in input_file:

        # Memory full 
        if (sys.getsizeof(token_stream)/1024.0/1024) >= blockSizeLimitMB:
            SPIMI_invert(token_stream, blockNumber)
            token_stream = []
            blockNumber += 1

        # Tokenize line of document 
        token_line = nltk.word_tokenize(line)
        token_line = [token.lower() for token in token_line] # Make tokens lowercase

        # First line of each file
        if "doctype" in token_line:
            continue

        if "newid=" in token_line: # value of newid is 2 tokens past the "newid=" tag 
            docID = int(token_line[token_line.index("newid=")+2]) 

        # Add tokens to token_stream if they are not a stop word 
        for token in token_line:
            if token not in stop_words:
                token_stream.append([token, docID])

    return token_stream

def SPIMI_invert(token_stream, blockNumber):
    output_file = "blocks/output_block_" + str(blockNumber) + ".dat"
    dictionary = {}

    # Build dictionary with tokens
    for token in token_stream:
        if token[0] not in dictionary:
            dictionary[token[0]] = [token[1]]
        else:
            dictionary[token[0]].append(token[1])
            dictionary[token[0]] = sorted(set(dictionary[token[0]]))

    # json dump to disk 
    # json.dump(dictionary, open(output_file, 'w'), sort_keys=True, indent=2, separators

    # Write dictionary to disk 
    block_output = open(output_file, 'w')
    for word in sorted(dictionary):
        posting_list = dictionary[word]
        entry = word + " "
        for p in posting_list:
            entry += str(p) 
            entry += " "
        block_output.write(entry)
        block_output.write('\n')

    print "Block #", blockNumber, "written to disk"
        
def merge_blocks():
    output_file = "merged_blocks.dat"
    blocks = []

    # Open all blocks 
    for filename in os.listdir(os.getcwd()+ "/blocks"):
        blocks.append(open("blocks/" + filename, 'r'))
    
    current_lines = {}
    merged_index = []

    # Initialize all blocks to their first line 
    for b in blocks:
        line = nltk.word_tokenize(b.readline())
        current_lines[b] = {line[0]: line[1:]}

    while(len(blocks) > 0): # Remove blocks when we reach the ends
        lowest_alphabetical_string = "~~~"
        # Find lowest alphabetical string 
        for block in blocks:
            if current_lines[block].keys()[0] < lowest_alphabetical_string:
                lowest_alphabetical_string = current_lines[block].keys()[0]

        # Add lowest string to dictionary
        merged_index.append({lowest_alphabetical_string: []})

        # Add postings lists if blocks have this string 
        for block in blocks:
            if current_lines[block].keys()[0] == lowest_alphabetical_string:
                merged_index[-1].values()[0] += current_lines[block][lowest_alphabetical_string]
                line = nltk.word_tokenize(block.readline())
                if len(line) <= 1:
                    blocks.remove(block)
                    current_lines.pop(block)
                else:
                    current_lines[block] = {line[0]: line[1:]}

        # Sort and remove duplicates in merged index
        merged_index[-1].values()[0] = sorted(set(merged_index[-1].values()[0]))

    print merged_index
    index_output = open(output_file, 'w')

    for term in merged_index:
        s = term.keys()[0] + " "
        for doc in term.values()[0]:
            s += doc + " "
        index_output.write(s)
        index_output.write('\n')



def main():
    # Will need to iterate over all .sgm files eventually.
    current_file = open('reuters/reut2-000.sgm', 'r')
    create_SPIMI_index(current_file)
    merge_blocks()

if __name__ == '__main__':
    main()
