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
    fileNumber = input_file.name[-7:-4]

    for line in input_file:
        # Memory full 
        if (sys.getsizeof(token_stream)/1024.0/1024) >= blockSizeLimitMB:
            SPIMI_invert(token_stream, blockNumber, fileNumber)
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

    # Output final block if not empty
    if token_stream != []:
        SPIMI_invert(token_stream, blockNumber, fileNumber)

    return token_stream

def SPIMI_invert(token_stream, blockNumber, fileNumber):
    output_file = "blocks/output_block_" + str(fileNumber) + str(blockNumber) + ".dat"
    dictionary = {}

    # Build dictionary with tokens
    for token in token_stream:
        if token[0] not in dictionary:
            dictionary[token[0]] = [token[1]]
        else:
            dictionary[token[0]].append(token[1])
            dictionary[token[0]] = sorted(set(dictionary[token[0]]))

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

    print "File #", fileNumber, "Block #", blockNumber, "written to disk"
        
def merge_blocks():
    # Open all blocks 
    blocks = []
    for filename in os.listdir(os.getcwd()+ "/blocks"):
        blocks.append(open("blocks/" + filename, 'r'))
    current_lines = {}
    merged_index = []

    # Initialize all blocks to their first line 
    for b in blocks:
        line = nltk.word_tokenize(b.readline())
        current_lines[b] = {line[0]: line[1:]}

    # Merge blocks and remove blocks when we are at the end of one
    while(len(blocks) > 0): 
        # Find lowest alphabetical string in each block
        lowest_alphabetical_string = "~~~"
        for block in blocks:
            current_term = current_lines[block].keys()[0]
            if current_term < lowest_alphabetical_string:
                lowest_alphabetical_string = current_term   

        # Add lowest string to dictionary
        merged_index.append({lowest_alphabetical_string: []})

        # Check edge case where some keys get inserted twice on the last block
        if len(merged_index) > 2 and merged_index[-1].keys() == merged_index[-2].keys():
            merged_index[-2].values()[0] += merged_index[-1].values()[0]
            merged_index.pop(-1)

        lowest_string_postings = merged_index[-1].values()[0]
 
        # Try to find lowest_alphabetical_string across blocks' current strings 
        for block in blocks:
            current_term = current_lines[block].keys()[0]
            if current_term == lowest_alphabetical_string: 
                lowest_string_postings += current_lines[block][current_term]
                line = nltk.word_tokenize(block.readline())

                # Handle nltk parser issue
                if '.' in line: 
                    if line[1] == '.':
                        line[0] = line[0] + line[1]
                    while '.' in line:
                        line.remove('.')

                # Remove blocks when we reach the end of it
                if len(line) <= 1:
                    blocks.remove(block)
                    current_lines.pop(block)
                else:
                    current_lines[block] = {line[0]: line[1:]}

    # Write out merged index
    index_output = open("merged_index.dat", 'w')
    for term in merged_index:
        s = term.keys()[0] + " "

        # Handle nltk tokenization issue
        try:
            map(int,term.values()[0])
        except ValueError, e:
            term.values()[0].remove("'s")

        # Sort posting list for term 
        sorted_values = sorted(set(map(int,term.values()[0])))
        for docID in sorted_values:
            s += str(docID) + " "
        index_output.write(s)
        index_output.write('\n')

    print "Blocks succesfully merged"

def main():
    for filename in os.listdir(os.getcwd()+ "/reuters"):
        if "reut" in filename:
            create_SPIMI_index(open("reuters/" + filename, 'r'))
    merge_blocks()

if __name__ == '__main__':
    main()
