import nltk
import copy

article_file = open('reuters/reut2-000.sgm', 'r')


document_words = []
doc_index = 0
document_words.append([]) 

# Get all the words
for line in article_file:
	token_line = nltk.word_tokenize(line)
	token_line_lowcase = [token.lower() for token in token_line] # Make tokens lowercase
	if "REUTERS" in token_line:	# Start a new document	 
		doc_index += 1
		document_words.append([token_line_lowcase])
	elif doc_index < 1:
		continue		# Skip everything until first document is created
	document_words[doc_index].append(token_line_lowcase)
	if "/REUTERS" in token_line:	# End of the document, merge all the token_line lists together
		document_words[doc_index] = [item for sublist in document_words[doc_index] for item in sublist]

print "Number of documents: ", doc_index+1
print "Sample document split into words:"
print document_words[doc_index]
print "\n"

# Remove stop words
metadata__words = ['REUTERS', 'TOPICS=', 'YES', 'LEWISSPLIT=', 'TRAIN', 'CGISPLIT=', 'TRAINING-SET', 'OLDID=',
		'NEWID=', '>', 'REUTERS', 'TOPICS=', 'YES', 'LEWISSPLIT=', 'TRAIN', 'CGISPLIT=', 'NEWID=','DATE',
 		"''", "", " ", "' '", '3-MAR-1987', '09:17:32.30', '<', '/DATE', '>', '<', 'TOPICS', '>', '<', 'D', '>', '<', '/D',
 		'.', '/TOPICS', '>', '<', 'PLACES', '>', '<', 'D', '>', 'usa', '<', '/D', '>', '<', '/PLACES', '>', 
		',', 'PEOPLE', '>', '<', '/PEOPLE', '>', '<', 'ORGS', '>', '<', '/ORGS', '>', '<', 'EXCHANGES', '>', 
		'<', '/EXCHANGES', '>', '<', 'COMPANIES', '>', '<', '/COMPANIES', '>', '<', 'UNKNOWN', '>', '&', '#', 
		'&', '#', '', '&', '#', ';', '&', '#', ';', '&', '#', ';', '&', '#', ';', 'f0284', '#', '<', '/UNKNOWN', 
		'>', '<', 'TEXT', '>', '<', 'TITLE', '>', '/TITLE', '>', '<', 'DATELINE', '>', '-', '<', '/DATELINE', 
		'...', 'pct', 'BODY', 'lt', ';', 'cts', '/BODY', 'reuter', 'mln', 'dlrs',  '<', '/TEXT', '>', '<', '/REUTERS', 'reute']

stop_word_file = open('stopwords.txt', 'r')
common_stop_words = stop_word_file.read().split()

stop_words = metadata__words + common_stop_words
stop_words = list(set(stop_words)) # Ensure uniqueness
stop_words = [word.lower() for word in stop_words] # Make all stopwords lowercase

# Make integers < 1000 into stopwords
for i in xrange(1, 999):
	stop_words.append("%i" % i)

# Make single ASCII characters into stopwords
for i in xrange(127):
	stop_words.append("%c" % chr(i))

doc_words_no_stop_words = []
doc_index = 0 

# Create new documents without stop words
for document in document_words:
	doc_words_no_stop_words.append([])
	for word in document:
		if word not in stop_words: 
			doc_words_no_stop_words[doc_index].append(word)
	doc_index += 1

print "Same document without stopwords: "
print doc_words_no_stop_words[doc_index-1], "\n\n"

# Build a dictionary
dictionary = {}
doc_index = 0 

for document in doc_words_no_stop_words:
	for word in document:
		try: 
			if word in dictionary:
				dictionary[word].append(doc_index)
				dictionary[word] = sorted(set(dictionary[word]))
			else:
				dictionary[word] = [doc_index]
		except TypeError:
			pass	
	doc_index += 1	
print "Number of words in dictionary: ", len(dictionary)


