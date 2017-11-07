import nltk
import copy
import os
import sys 
import json
import itertools
from operator import itemgetter

# Global variables
blockSizeLimitMB = 1
merged_index_file = "merged_bm25_index.dat"
BM25_index_file = "bm25_index.dat"
length_of_docs = []

def create_SPIMI_index(input_file):
    token_stream = []
    docID = 0 
    blockNumber = 0 
    fileNumber = input_file.name[-7:-4]
    current_doc_length = 0 

    for line in input_file:
        # Memory full - use SPIMI to write block to disk
        if (sys.getsizeof(token_stream)/1024.0/1024) >= blockSizeLimitMB:
            SPIMI_invert(token_stream, blockNumber, fileNumber)
            token_stream = []
            blockNumber += 1

        # Tokenize line of document 
        token_line = nltk.word_tokenize(line)
        current_doc_length += len(token_line)
	
        # First line of each file
        if "DOCTYPE" in token_line:
            continue

        if "NEWID=" in token_line: 
            docID = int(token_line[token_line.index("NEWID=")+2]) # value of newid is 2 tokens past the "newid=" tag 

            # Save & reset document length
            if docID != 1:
                length_of_docs.append(current_doc_length)
                current_doc_length = 0

        # Extra processing to handle NLTK issues.
        for token in token_line:
    	    if token.endswith("'"):
    		token = token[:-1]
    	    elif token.endswith("'s"):
    		token = token[:-2]
            if len(token) > 1: 
                token_stream.append([token, docID])

    # Output final block if not empty
    if token_stream != []:
        SPIMI_invert(token_stream, blockNumber, fileNumber)
    return token_stream    

def SPIMI_invert(token_stream, blockNumber, fileNumber):
    output_file = "bm25_blocks/output_block_" + str(fileNumber) + "_" + str(blockNumber) + ".dat"
    dictionary = {}

    # Build dictionary with term and docID
    for token in token_stream:
        term = token[0]
        docID = token[1]
        if term not in dictionary:
            dictionary[term] = {docID: 1}
        elif docID not in dictionary[term].keys():
            dictionary[term][docID] = 1
        else:
            dictionary[term][docID] = dictionary[term][docID] + 1

    # Write dictionary to disk 
    block_output = open(output_file, 'w')
    for word in sorted(dictionary):
        keys = sorted(dictionary[word].keys())
        entry = word + " {"
        for key in keys:
            entry += str(key) 
            entry += " : "
            entry += str(dictionary[word][key])
            entry += " , "
        entry += "} \n"
        block_output.write(entry)
    print "File #", fileNumber, "Block #", blockNumber, "written to disk"

def merge_blocks():
    # Open all blocks 
    blocks = []
    for filename in os.listdir(os.getcwd()+ "/bm25_blocks"):
        blocks.append(open("bm25_blocks/" + filename, 'r'))
    current_lines = {}
    merged_index = []

    # Initialize all blocks to their first line 
    for b in blocks:
        line = b.readline().split(" ")[0:-1] # Stop at -1 to remove the "\n" token 
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
        merged_index.append({lowest_alphabetical_string: {}})

        # Try to match lowest_alphabetical_string across blocks' current strings 
        for block in blocks:
            current_term = current_lines[block].keys()[0]
            if current_term == lowest_alphabetical_string:
                term_frequency_map = merged_index[-1][current_term]
                docs_and_freqs = current_lines[block][current_term]

                # Remove bracket from docID
                docs_and_freqs[0] = docs_and_freqs[0][1:]
                
                i = 0 
                while (i < len(docs_and_freqs)):
                    if docs_and_freqs[i] == "}":
                        break
                    docID = int(docs_and_freqs[i])
                    if docID not in term_frequency_map:
                        term_frequency_map[docID] = docs_and_freqs[i+2]
                    else:
                        term_frequency_map[docID] =  term_frequency_map[docID] + docs_and_freqs[i+2]
                    i += 4

                # Try to move to next string of the block, remove block if we are at the end of it
                try: 
                    line = block.next().split(" ")[0:-1]
                    current_lines[block] = {line[0]: line[1:]}
                except StopIteration:
                    blocks.remove(block)
                    current_lines.pop(block)

    # Write out merged index
    index_output = open(merged_index_file, 'w')
    for entry in merged_index:
        term = entry.keys()[0]
        postings = entry[term]
        sorted_postings = sorted(postings.items())
        s = str(term) + " "
        s += str(sorted_postings)
        index_output.write(s)
        index_output.write('\n')
    print "Blocks succesfully merged"

def loadIndexToMemory():
    disk_index = open('merged_bm25_index.dat', 'r')
    memory_index = {}
    for line in disk_index:
        term = line.split(" ")[0]
        postings = line.split()[1:]
        memory_index[term] = postings
    return memory_index

def writeCorpusStats(index_stage, terms, postings):
    corpus_stats_file = open('corpus_stats.txt', 'a')
    tabs = "\t\t\t\t\t\t\t\t\t\t"
    entry = index_stage + tabs + str(terms) + tabs + str(postings) + "\n"
    corpus_stats_file.write(entry)

def compress_SPIMI_index():
    # Clear corpus stats
    corpus_stats_file = open('corpus_stats.txt', 'w')
    if length_of_docs != 0: 
        average_doc_length = float(sum(length_of_docs)) / len(length_of_docs)
        corpus_stats_file.write("Average doc length: ")
        print average_doc_length
        corpus_stats_file.write(str(average_doc_length) + "\n")

        doc_length_file = open('doc_lengths.txt', 'w')
        i = 0
        while i < len(length_of_docs):
            doc_length_file.write(str(i+1) + " " + str(length_of_docs[i]) + "\n")
            i += 1 

    corpus_stats_file.write("Size of:\t\t\t\t\t\t\t\t\t\tTerms\t\t\t\t\t\t\t\t\t\tPostings\n")
    uncompressed_index = loadIndexToMemory()

    # Get number of terms and postings of uncompressed index
    term_count = 0
    postings_count = 0
    for term, postings in uncompressed_index.iteritems():
        term_count += 1
        postings_count += len(postings)
    corpus_stats_file.write("Uncompressed\t\t\t\t\t\t\t\t\t\t" + str(term_count) + "\t\t\t\t\t\t\t\t\t\t" + str(postings_count) + "\n")

    # Remove numbers 
    index_no_numbers = {}
    no_number_term_count = 0 
    no_number_postings_count = 0
    for term, postings in uncompressed_index.iteritems():
        try:
            float(term)
        except:
            index_no_numbers[term] = postings 
            no_number_term_count += 1
            no_number_postings_count += len(postings)
    corpus_stats_file.write("No numbers\t\t\t\t\t\t\t\t\t\t" + str(no_number_term_count) + "\t\t\t\t\t\t\t\t\t\t" + str(no_number_postings_count) + "\n")

    # Case Folding
    lowercase_index = {}
    lowercase_term_count = 0
    lowercase_postings_count = 0 

    for term, postings in index_no_numbers.iteritems():
        if term.lower() not in lowercase_index:
            lowercase_index[term.lower()] = postings 
            lowercase_term_count += 1
            lowercase_postings_count += len(postings)
        else:
            lowercase_index[term.lower()] += postings
            lowercase_postings_count += len(postings)
    corpus_stats_file.write("Case Folded\t\t\t\t\t\t\t\t\t\t" + str(lowercase_term_count) + "\t\t\t\t\t\t\t\t\t\t" + str(lowercase_postings_count) + "\n")

    # Determine term frequency after case folding
    term_frequency = {}
    for term, postings in lowercase_index.iteritems():
        if term in term_frequency:
            term_frequency[term] += len(postings)
        else:
            term_frequency[term] = len(postings)
    term_frequency_list = sorted(term_frequency.items(), key=itemgetter(1), reverse=True)
    
    thirty_most_frequent = []
    thirty_one_to_one_fifty_most_frequent = []
    for tuples in term_frequency_list[:30]:
        thirty_most_frequent.append(tuples[0])

    for tuples in term_frequency_list[30:150]:
        thirty_one_to_one_fifty_most_frequent.append(tuples[0])

    # Remove 30 stop words
    index_minus_30_stop_words = {}
    minus_30_term_count = 0
    minus_30_postings_count = 0
    for term, postings in lowercase_index.iteritems():
        if term not in thirty_most_frequent:
            index_minus_30_stop_words[term] = postings
            minus_30_term_count += 1
            minus_30_postings_count += len(postings)
    corpus_stats_file.write("30 stop words\t\t\t\t\t\t\t\t\t\t" + str(minus_30_term_count) + "\t\t\t\t\t\t\t\t\t\t" + str(minus_30_postings_count) + "\n")

    # Remove 150 stop words 
    index_minus_150_stop_words = {}
    minus_150_term_count = 0
    minus_150_postings_count = 0
    for term, postings in lowercase_index.iteritems():
        if term not in thirty_one_to_one_fifty_most_frequent:
            index_minus_150_stop_words[term] = postings
            minus_150_term_count += 1
            minus_150_postings_count += len(postings)
    corpus_stats_file.write("150 stop words\t\t\t\t\t\t\t\t\t\t" + str(minus_150_term_count) + "\t\t\t\t\t\t\t\t\t\t" + str(minus_150_postings_count) + "\n")

    # Write 150 most common stop words to disk
    stop_words_file = open('stop_words.txt', 'w')
    for tuples in term_frequency_list[:150]:
        stop_words_file.write(tuples[0] + "\n")

    # Write out compressed index 
    compressed_index_output = open(BM25_index_file, 'w')
    for entry in lowercase_index:
        s = str(entry) + " "
        s += str(lowercase_index[entry])
        compressed_index_output.write(s)
        compressed_index_output.write('\n')

def main():
    # Only create SPIMI index if not aleady done 
    if len(os.listdir(os.getcwd()+ "/bm25_blocks")) == 0: 
        for filename in os.listdir(os.getcwd()+ "/reuters"):
            if "reut" in filename:
                create_SPIMI_index(open("reuters/" + filename, 'r'))
        merge_blocks()
        compress_SPIMI_index()

    # Only merge blocks into index if not already done
    if merged_index_file not in os.listdir(os.getcwd()):
        merge_blocks()
        compress_SPIMI_index()

    # Only compress index if not already done 
    # if BM25_index_file not in os.listdir(os.getcwd()):
    #     compress_SPIMI_index()

if __name__ == '__main__':
    main()