import SPIMI as spimi
import os
import nltk

def displayWelcomePrompt():
    print "======================================="
    print "Welcome to Tim's Reuters Search Engine"
    print "======================================="

def checkIfIndex():
    if 'merged_index.dat' not in os.listdir(os.getcwd()):
        print "No index found. Creating one, please wait."
        spimi.main()
        print "Index successfully created."

def loadIndexToMemory():
    disk_index = open('merged_index.dat', 'r')
    memory_index = {}
    for line in disk_index:
        term = line.split(" ")[0]
        postings = line.split()[1:]
        memory_index[term] = postings
    return memory_index

# Implement this next
def searchForDocuments(index):
    None 

def main():
    displayWelcomePrompt()
    checkIfIndex()
    index = loadIndexToMemory()
    searchForDocuments(index)

if __name__ == '__main__':
    main()