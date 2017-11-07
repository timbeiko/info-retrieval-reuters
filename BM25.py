# Copy of search_engine.py modified to implement the BM25 algorithm

import SPIMI_BM25 as spimibm25
import os
import nltk
from math import log

stop_word_file = open('stop_words.txt', 'r')
stop_words = stop_word_file.read().split()
DOCUMENT_COUNT = 21578    # Add this to corpus_stats.txt 
AVERAGE_DOC_LENGTH = 2000 # Placeholder -- need to calculate it, and add to corpus_stats.txt 

# Should this handle long query BM25? 
def BM25(matching_docs, index, query):
    k1 = 1.5
    k3 = 1.5
    b  = 0.75
    doc_scores = {}
    for doc in matching_docs:
        doc_scores[doc] = 0
        for term in query: 
            idf = log(DOCUMENT_COUNT/len(index[doc]))
            # Need term frequency for doc


def displayWelcomePrompt():
    print "\n==================================================="
    print "Welcome to Tim's Reuters Search Engine"
    print "===================================================\n"
    print "\n==================================================="
    print "Queries are ANDed by default. To use OR queries,"
    print "put terms in parenthesis, for example:"
    print "'(one two) (three four)' will search for:"
    print "'(one OR two) AND (three OR four)'"
    print "\n"
    print "Note: nested queries are not supported, for example:"
    print "(one (two three)) ((four five) six)"
    print "===================================================\n\n"

def checkIfIndex():
    if 'bm25_index.dat' not in os.listdir(os.getcwd()):
        print "No index found. Creating one, please wait."
        spimibm25.main()
        print "Index successfully created."
        print "==================================================="

def loadIndexToMemory():
    disk_index = open('bm25_index.dat', 'r')
    memory_index = {}
    for line in disk_index:
        term = line.split(" ")[0]
        postings = {}
        raw_text_postings = line[len(term)+1:-2]
        processed_postings = raw_text_postings.translate(None, "[]'\\/,\"()").split(" ")
        i = 1
        while (i < len(processed_postings)):
            docID = int(processed_postings[i-1])
            count = int(processed_postings[i])
            postings[docID] = count
            i += 2
        memory_index[term] = postings
    return memory_index

def preprocessQuery(query):
    query = nltk.word_tokenize(query)

    # Remove numbers
    query_no_numbers = []
    for term in query:
        try:
            float(query)
        except:
            query_no_numbers.append(term)

    # Case Folding
    query_lowercase = []
    for term in query_no_numbers:
        query_lowercase.append(term.lower())

    # Remove Stop words
    processed_query = []
    for term in query_lowercase:
        if term not in stop_words:
            processed_query.append(term)

    return processed_query

def addToResults(results, terms):
    if results == []:
        results = set(results) | set(terms)
    else:
        results = set(results) & set(terms)
    return results

def orderByNumberOfMatchingTerms(terms, matching_docs, index):
    term_count = {}
    for doc in matching_docs:
        term_count[doc] = 0

        for term in terms:
            if str(doc) in index[term]:
                term_count[doc] += 1

    doc_term_count_sorted = sorted(term_count.items(), key=lambda x: x[1], reverse=True)

    sorted_matching_docs = []
    for doc in doc_term_count_sorted:
        # Uncomment this to see that OR documents are indeed ordered by nubmer of terms present
        # if doc[1] > 1:
        #     print doc 
        sorted_matching_docs.append(doc[0])

    return sorted_matching_docs

def searchForDocuments(index):
    while(True):
        query =  raw_input("ENTER QUERY OR TYPE 'EXIT' TO QUIT: ")
        
        if query == "EXIT":
            break
            
        processed_query = preprocessQuery(query)

        # Get matching docIDs
        matching_docs = []
        or_subquery = False 
        or_postings = []
        or_query = False
        or_terms = []

        for term in processed_query:
            if term == "(": 
                or_subquery = True
                or_query = True
            elif term == ")": # Close and merge OR subquery
                or_subquery = False
                matching_docs = addToResults(matching_docs, or_postings)
                or_postings = []
            elif term not in index:
                break
            elif or_subquery: # Process interior of OR subquery
                or_postings = set(or_postings) | set(index[term])
                or_terms.append(term)
            else: # Process AND query
                matching_docs = addToResults(matching_docs, index[term])
        
        matching_docs = sorted(map(int,matching_docs))

        if or_query:
            matching_docs = orderByNumberOfMatchingTerms(or_terms, matching_docs, index)
        
        if matching_docs == []:
            print "No results.\n"
        else:
            BM25(matching_docs, index, processed_query)

def main():
    displayWelcomePrompt()
    checkIfIndex()
    index = loadIndexToMemory()
    searchForDocuments(index)
    print "\n==================================================="
    print "Thank you for using Tim's Reuters Search Engine"
    print "==================================================="

if __name__ == '__main__':
    main()