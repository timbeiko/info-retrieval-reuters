import SPIMI as spimi
import os
import nltk

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
    if 'merged_index.dat' not in os.listdir(os.getcwd()):
        print "No index found. Creating one, please wait."
        spimi.main()
        print "Index successfully created."
        print "==================================================="

def loadIndexToMemory():
    disk_index = open('compressed_index.dat', 'r')
    memory_index = {}
    for line in disk_index:
        term = line.split(" ")[0]
        postings = line.split()[1:]
        memory_index[term] = postings
    return memory_index

def addToResults(results, terms):
    if results == []:
        results = set(results) | set(terms)
    else:
        results = set(results) & set(terms)
    return results

def searchForDocuments(index):
    while(True):
        query =  raw_input("ENTER QUERY OR TYPE 'EXIT' TO QUIT: ")
        
        if query == "EXIT":
            break

        # Process query
        query = nltk.word_tokenize(query.lower())
        processed_query = []
        stop_words = [] # temporary
        for term in query:
            if term == "(" or term == ")":
                processed_query.append(term)
            elif term not in stop_words: # Need to be sure we remove all numbers 
                processed_query.append(term)

        # Get matching docIDs
        matching_docs = []
        or_subquery = False 
        or_postings = []
        for term in processed_query:
            if term == "(": 
                or_subquery = True
            elif term == ")": # Close and merge OR subquery
                or_subquery = False
                matching_docs = addToResults(matching_docs, or_postings)
                or_postings = []
            elif term not in index:
                break
            elif or_subquery: # Process interior of OR subquery
                or_postings = set(or_postings) | set(index[term])
            else: # Process AND query
                matching_docs = addToResults(matching_docs, index[term])
        
        matching_docs = sorted(map(int,matching_docs))
        
        if matching_docs == []:
            print "No results.\n"
        else:
            print len(matching_docs), "matching documents:", matching_docs, "\n"

def main():
    displayWelcomePrompt()
    checkIfIndex()
    index = spimi.loadIndexToMemory()
    searchForDocuments(index)
    print "\n==================================================="
    print "Thank you for using Tim's Reuters Search Engine"
    print "==================================================="

if __name__ == '__main__':
    main()