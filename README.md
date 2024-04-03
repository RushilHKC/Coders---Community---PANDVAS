# legal-case-retrieval-system
Information Retrieval system to parse Boolean and free text queries to retrieve relevant law documents for a module's homework

Indexing: $ python index.py -i dataset-file -d dictionary-file -p postings-file

Searching: $ python search.py -d dictionary-file -p postings-file -q query-file -o output-file-of-results
