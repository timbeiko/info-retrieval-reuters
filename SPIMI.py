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

    # Output final block if not empty
    if token_stream != []:
        SPIMI_invert(token_stream, blockNumber)

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
    # Open all blocks 
    blocks = []
    for filename in os.listdir(os.getcwd()+ "/blocks"):
        blocks.append(open("blocks/" + filename, 'r'))
    
    current_lines = {}
    merged_index = []
    largest_doc_index = 0

    # Initialize all blocks to their first line 
    for b in blocks:
        line = nltk.word_tokenize(b.readline())
        current_lines[b] = {line[0]: line[1:]}

    while(len(blocks) > 0): 
        lowest_alphabetical_string = "~~~"
        # Find lowest alphabetical string 
        for block in blocks:
            if current_lines[block].keys()[0] < lowest_alphabetical_string:
                lowest_alphabetical_string = current_lines[block].keys()[0]

        # Add lowest string to dictionary
        merged_index.append({lowest_alphabetical_string: []})
 
        for block in blocks:
            # Add postings lists if blocks have lowest_alphabetical_string
            if current_lines[block].keys()[0] == lowest_alphabetical_string:
                merged_index[-1].values()[0] += current_lines[block][lowest_alphabetical_string]
                line = nltk.word_tokenize(block.readline())
                # nltk parser issue
                if '.' in line: 
                    if line[1] == '.':
                        line[0] = line[0] + line[1]
                    while '.' in line:
                        line.remove('.')
                if len(line) <= 1:
                    # Remove blocks when we reach the ends
                    blocks.remove(block)
                    current_lines.pop(block)
                else:
                    current_lines[block] = {line[0]: line[1:]}
                    if max(map(int, line[1:])) > largest_doc_index:
                        largest_doc_index = max(map(int, line[1:]))

        # Sort and remove duplicates in merged index for the last term
        merged_index[-1].values()[0] = sorted(set(merged_index[-1].values()[0]))

        # This is to flag words that appear in >25% of queries, in case we want to make them stopwords
        if len(merged_index[-1].values()[0]) > largest_doc_index/4:
            print "Term", merged_index[-1].keys()[0], "appears in >1/4 docs"

    # Write out merged index
    index_output = open("merged_index.dat", 'w')
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
