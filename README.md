# info-retrieval-reuters

## Overview
There are three main python files in this project: `SPIMI.py`, `search_engine.py` and `BM25.py`. The dependencies for these files can be found at the begining of each of them. 
To run the project, you will need to create a `blocks` and `reuters` directory under the main project folder (`info-retrieval-reuters`). The `blocks` folder can be left empty -- it will be populated by `SPIMI.py`, and the `reuters` directory should contain the Reuters files, in the `reut2-XXX.sgm` format, where `XXX` is the number of the file. 

### SPIMI.py
`SPIMI.py` is the file that builds the index from the Reuters collection. In order to make testing quicker, it will only create blocks if the `blocks` directory is empty, then it will only merge them into `merged_index.dat` if that file does not exist, and finally it will only compress the index into `compressed_index.dat` if again no such file exists. Therefore, if you want to re-generate the index, you will need to delete those files (or update the SPIMI `main()` method). 

### seach_engine.py
`search_engine.py` is the file to run in order to run queries against the corpus. It checks if a compressed index exists, and loads it into memory if so. Otherwise, it will call `SPIMI.main()` to generate it. 

The queries in the search engine are "ANDed" by default. To use OR queries, you need to put the terms in parentheses. For example, the query `"(A B)"` will return `"A OR B"`, while the query `"A B"` will return `"A AND B"`. Nested queries, such as `(A (B C))` are not supported, but combinasions of queries, such as `(A B) C` should work. 

For AND queries, the documents are returned in increasing `docID` size. For OR queries, the documents are sorted by the number of query terms they contain. For example, if we search for `(A B C)` and `doc1` has all of the terms, `doc2` and `doc3` both have 2 terms, and `doc4` only has one of the terms, the result will be `[doc1, doc3, doc2, doc4]` or `[doc1, doc2, doc3, doc4]`, where the "tie-break" between `doc2` and `doc3` is arbitrary, based on the order of these documents in the corpus.  

### BM25.py 
`BM25.py` is a copy of search_engine.py which implements the BM25 ranking algorithm. 