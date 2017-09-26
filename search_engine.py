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
    i = 0 
    for line in disk_index:
        i += 1
        nltk_line = nltk.word_tokenize(line)
        # nltk parser issue
        if '.' in nltk_line: 
            if nltk_line[1] == '.':
                nltk_line[0] = nltk_line[0] + nltk_line[1]
            while '.' in nltk_line:
                nltk_line.remove('.')
                
        # Add entry to memory index
        memory_index[nltk_line[0]] = nltk_line[1:]

    return memory_index


def searchForDocuments(index):
    None

def main():
    displayWelcomePrompt()
    checkIfIndex()
    index = loadIndexToMemory()
    searchForDocuments(index)

if __name__ == '__main__':
    main()