#!/usr/bin/python
import re
import sys
import getopt

import math
import json
import tf_idf
import nltk
import random
from index import makeUniGrams, preprocess
import csv



# =========================================================================
#
#                           ARGS PASS
#
# =========================================================================

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

# =========================================================================
#
#                           Posting Class
#
# ========================================================================= 
class Posting:
    def __init__(self, docID, titleCount, contentCount, dateCount, courtCount):
        self.currentDocID = docID
        self.currentTitleCount = titleCount
        self.currentContentCount = contentCount
        self.currentDateCount = dateCount
        self.currentCourtCount = courtCount
        self.currentCombinedTF = titleCount + contentCount + dateCount + courtCount
        
        
    def getDocID(self):
        return self.currentDocID
        
    def getTitleCount(self):
        return self.currentTitleCount
        
    def getContentCount(self):
        return self.currentContentCount
       
    def getDateCount(self):
        return self.currentDateCount
        
    def getCourtCount(self):
        return self.currentCourtCount
        
    def getTF(self):
        return self.currentCombinedTF
    
# =========================================================================
#
#                           PostingHandler Class
#
# =========================================================================
class PostingHandler:
    def __init__(self, dictionary_file, postings_file):
        self.dictionaryFile = dictionary_file
        self.postingsFile = open(postings_file, 'r')
        self.dictionary = importDS(self.dictionaryFile)
        self.currentPostingsList = ""
        self.currentWord = ""
        self.currentPointer = None 
        self.currentDocFreq = 0
        self.postingIndex = 0
        self.currentPosting = None
        
        
    def getDocLength(self, docID):
        return self.dictionary["DOC_ID"][docID][1]

    def getNumDoc(self):
        return len(self.dictionary["DOC_ID"])
        
    def getDocName(self, docID):
        return self.dictionary["DOC_ID"][docID][0]
        
    def getDocFreq(self, word):
        if word in self.dictionary:
            return self.dictionary[word]["docFreq"]
        else:
            return 0
            
    def getStartPointer(self, word):
        if word in self.dictionary:
            return self.dictionary[word]["index"]
        else:
            print("No such word: " + word + "in dictionary!")
            
    def extractPostingList(self, word):
        self.currentWord = word
        if word not in self.dictionary:
            self.currentPostingsList = ""
            self.currentPointer = None 
            self.currentDocFreq = 0
            self.postingIndex = 0
            return False
        startPointer = self.getStartPointer(word)
        self.postingsFile.seek(startPointer)
        postingList = self.postingsFile.readline()
        
        self.currentPostingsList = postingList
        self.currentPointer = 0
        self.currentDocFreq = self.getDocFreq(word)
        self.postingIndex = 0
        
        return True 
        
    def getNextPosting(self):
        self.postingIndex += 1
        if self.postingIndex > self.currentDocFreq:
            return None
            
        nextStartPointer = self.currentPointer
    
        docIDLen = int(self.currentPostingsList[nextStartPointer : nextStartPointer + 2])
        nextStartPointer += 2
        docID = self.currentPostingsList[nextStartPointer : nextStartPointer + docIDLen]
        nextStartPointer += docIDLen
        titleCountLen = int(self.currentPostingsList[nextStartPointer : nextStartPointer + 1])
        nextStartPointer += 1
        titleCount = int(self.currentPostingsList[nextStartPointer : nextStartPointer + titleCountLen])
        nextStartPointer += titleCountLen
        contentCountLen = int(self.currentPostingsList[nextStartPointer : nextStartPointer + 1])
        nextStartPointer += 1
        contentCount = int(self.currentPostingsList[nextStartPointer : nextStartPointer + contentCountLen])
        nextStartPointer += contentCountLen
        dateCountLen = int(self.currentPostingsList[nextStartPointer : nextStartPointer + 1])
        nextStartPointer += 1
        dateCount = int(self.currentPostingsList[nextStartPointer : nextStartPointer + dateCountLen])
        nextStartPointer += dateCountLen
        courtCountLen = int(self.currentPostingsList[nextStartPointer : nextStartPointer + 1])
        nextStartPointer += 1
        courtCount = int(self.currentPostingsList[nextStartPointer : nextStartPointer + courtCountLen])
        nextStartPointer += courtCountLen
        
        self.currentPointer = nextStartPointer
        self.currentPosting = Posting(docID, titleCount, contentCount, dateCount, courtCount)
        
        return self.currentPosting
 
# =========================================================================
#
#                           QUERY EXPANSION
#
# ========================================================================= 
def ThesurusQueryExpandRandom(list_of_query):
    newSet = list()
    
    for query in set:
        newSet.append(query)
        syns = wn.synsets(query)
        if len(syns) < 1:
            newSet.append(query)
            continue
        synsSet = random.choice(syns)
        newWord = random.choice(synsSet.lemma_names())
        if newWord is not query:
            newSet.append(newWord)
        else:
            newSet.append(random.choice(synsSet.lemma_names()))
        
    
    return newSet
    
def ThesurusQueryExpandAll(list_of_query):
    newSet = list()
    
    for query in set:
        newSet.append(query)
        syns = wn.synsets(query)
        if len(syns) < 1:
            newSet.append(query)
            continue
        for set in syns:
            for word in set.lemma_names():
                newSet.append(word)
        
    
    return newSet

# =========================================================================
#
#                           MAIN
#
# =========================================================================
def main():
    f = open(file_of_queries)
    queries = f.readlines()
    f.close()

    output = []
    for line in queries:
        line = line.replace('\n', '')
        if line.find(" AND ") != -1:
            output.append(processBoolQuery(line) + '\n')
        else:
            output.append(processFreeText(line) + '\n')

    f = open(file_of_output, 'w+')
    f.writelines(output)
    f.close()

# =========================================================================
#
#                           Free Text Query
#
# =========================================================================

# =========================================================================
#       Return the docName given DOC_ID
#           input: dictionary, DOC_ID(int)
#           output: docName(String)
# =========================================================================
def getDocName(dictionary, docID):
    return dictionary["DOC_ID"][docID][0]

def getTitleFromDocName(docName):
    # Assuming the title is the first part before the pipe separator
    title = docName.split('|')[0].strip()
    return title

# =========================================================================
#       Return the query as a dict with normalized scores
#           input: dictionary, query(dict)
#           output: query_scores(dict)
# =========================================================================
def queryToScore(query):
    postingHandler = PostingHandler(dictionary_file, postings_file)
    uniDict = makeUniGrams(preprocess(query))
    q_len = tf_idf.getLtcLen(postingHandler, uniDict)
    N = postingHandler.getNumDoc()
    for word in uniDict:
        df = postingHandler.getDocFreq(word)
        uniDict[word] = tf_idf.get_ltc(uniDict[word], N, df, q_len)
    return uniDict


# =========================================================================
#       Processes a free text query
#           input: dictionary, query(String)
#           output: sorted_results(list)
# =========================================================================
# def processFreeText(query):
#     postingHandler = PostingHandler(dictionary_file, postings_file)
#     q_score = queryToScore(query)
#     score_list = {}
#     for q_word in q_score:
#         print(q_word)
#         postingHandler.extractPostingList(q_word)
#         posting = postingHandler.getNextPosting()
#         while posting is not None:
#             docID = posting.getDocID()
#             docName = postingHandler.getDocName(docID)
#             temp_score = [0.0, 0.0, 0.0, 0.0, 0.0]
#             # Scores are contained as
#             # [docID, court, title, date, content] as per descending importance
#             temp_score[0] = 1 if docID == q_word else 0
#             temp_score[1] = 1 if posting.getCourtCount() > 0 else 0
#             temp_score[2] = 1 if posting.getTitleCount() > 0 else 0
#             temp_score[3] += tf_idf.get_lnc(posting.getDateCount(), postingHandler.getDocLength(docID)) * q_score[q_word]
#             temp_score[4] += tf_idf.get_lnc(posting.getContentCount(), postingHandler.getDocLength(docID)) * q_score[q_word]
#             if sum(temp_score) > 0:
#                 if docName not in score_list:
#                     score_list[docName] = temp_score
#                 else:
#                     for i in range(5):
#                         if temp_score[i] > 0:
#                             score_list[docName][i] += temp_score[i] + 1

#             posting = postingHandler.getNextPosting()

#     sorted_results = sorted(score_list.items(), key=lambda k:k[1], reverse=True)
#     res_list = []
#     for s in sorted_results:
#         res_list.append(str(s[0]))
#     return ' '.join(res_list)

def getTitleAndContentFromDocName(docName, posting):
    
    parts = docName.split('|',1)
   
    title = parts[0].strip()

    # Assuming that the content is stored in a CSV file
    content = parts[0].strip()  # Adjust this part based on your data structure
    
    return title, content

def getContentFromCSV(docID):
    # Replace 'your_dataset.csv' with the actual name of your CSV file
    with open('striped_dataset1.csv', 'r') as csvfile:
        csv.field_size_limit(10**9)
        
        reader = csv.DictReader(csvfile,delimiter='|')
        # reader = csv.DictReader(csvfile, delimiter='|')
        # a = int(docID)
        # a+=2
        # docID = str(a)
        print(docID)
        for row in reader:
            if row['docID'] == (docID):
                return row['content']
    
    # Return an empty string or handle the case where content is not found
    return "harsh"

import csv

# def processFreeText(query):
#     postingHandler = PostingHandler(dictionary_file, postings_file)
#     q_score = queryToScore(query)
#     score_list = {}

#     for q_word in q_score:
#         postingHandler.extractPostingList(q_word)
#         posting = postingHandler.getNextPosting()

#         while posting is not None:
#             docID = posting.getDocID()
#             docName = postingHandler.getDocName(docID)

#             # Extract title from docName
#             title = getTitleFromDocName(docName)

#             # Extract content from CSV file using docID
#             content = getContentFromCSV(docID)

#             temp_score = [0.0, 0.0, 0.0, 0.0, 0.0]

#             # Scores are contained as [docID, court, title, date, content] as per descending importance
#             temp_score[0] = 1 if docID == q_word else 0
#             temp_score[1] = 1 if posting.getCourtCount() > 0 else 0
#             temp_score[2] = 1 if posting.getTitleCount() > 0 else 0
#             temp_score[3] += tf_idf.get_lnc(posting.getDateCount(), postingHandler.getDocLength(docID)) * q_score[q_word]
#             temp_score[4] += tf_idf.get_lnc(posting.getContentCount(), postingHandler.getDocLength(docID)) * q_score[q_word]

#             if sum(temp_score) > 0:
#                 if docName not in score_list:
#                     score_list[docName] = {'title': title, 'content': content, 'scores': temp_score}
#                 else:
#                     for i in range(5):
#                         if temp_score[i] > 0:
#                             score_list[docName]['scores'][i] += temp_score[i] + 1

#             posting = postingHandler.getNextPosting()

#     sorted_results = sorted(score_list.items(), key=lambda k: k[1]['scores'], reverse=True)
#     res_list = []

#     for s in sorted_results:
#         title = s[1]['title']
#         content = s[1]['content']
#         res_list.append(f'Title: {title}\nContent: {content}\n')

#     return '\n'.join(res_list)

def processFreeText(query):
    # Your existing code to process the query and fetch results

    postingHandler = PostingHandler(dictionary_file, postings_file)
    q_score = queryToScore(query)
    score_list = {}

    for q_word in q_score:
        postingHandler.extractPostingList(q_word)
        posting = postingHandler.getNextPosting()

        while posting is not None:
            docID = posting.getDocID()
            docName = postingHandler.getDocName(docID)

            # Extract title from docName
            title = getTitleFromDocName(docName)

            # Extract content from CSV file using docID
            content = getContentFromCSV(docID)

            temp_score = [0.0, 0.0, 0.0, 0.0, 0.0]

            # Scores are contained as [docID, court, title, date, content] as per descending importance
            temp_score[0] = 1 if docID == q_word else 0
            temp_score[1] = 1 if posting.getCourtCount() > 0 else 0
            temp_score[2] = 1 if posting.getTitleCount() > 0 else 0
            temp_score[3] += tf_idf.get_lnc(posting.getDateCount(), postingHandler.getDocLength(docID)) * q_score[q_word]
            temp_score[4] += tf_idf.get_lnc(posting.getContentCount(), postingHandler.getDocLength(docID)) * q_score[q_word]

            if sum(temp_score) > 0:
                if docName not in score_list:
                    score_list[docName] = {'title': title, 'content': content, 'scores': temp_score}
                else:
                    for i in range(5):
                        if temp_score[i] > 0:
                            score_list[docName]['scores'][i] += temp_score[i] + 1

            posting = postingHandler.getNextPosting()

    sorted_results = sorted(score_list.items(), key=lambda k: k[1]['scores'], reverse=True)
    result_list = []

    for s in sorted_results:
        title = s[1]['title']
        content = s[1]['content']
        result_list.append({"title": title, "content": content})

    # Convert the list of dictionaries to JSON
    result_json = json.dumps(result_list)

    return result_json



# =========================================================================
#       Imports the dataStructure using pickle interface
#           input: outputFile(String)
#           output: DS(Object)
# =========================================================================
def importDS(outputFile):
    data = open(outputFile, 'r')
    DS = json.load(data)
    return DS

# =========================================================================
#
#           Boolean Search
#
# =========================================================================
def processBoolQuery(query):
    # Since only boolean operator is AND, each element in this list will be AND-merged
    query = query.split(" AND ")
    query2 = []
    for i in range(len(query)):
        query2.extend(preprocess(query[i]))
    query = query2
    convertToScores(query)

    # Since skip lists aren't implemented, no need to prioritise shortest query
    while len(query) > 1:
        query[0] = doAnd(query[0], query[1])
        del query[1]

    query = query[0]
    if len(query) == 0:
        return ""
    else:
        query.sort(key=lambda x: x[1], reverse=True)
        # print query
        result = [str(i) for i in zip(*query)[0]]
        return ' '.join(result)

def convertToScores(list):
    # Retrieve postings and calculate lnc.ltc
    # Returns array of postings of format [str(docID), float(lnc)]
    ph = PostingHandler(dictionary_file, postings_file)

    ltc = {}
    sum = 0
    for i in range(len(list)):
        word = list[i]
        ph.extractPostingList(word)
        df = int(ph.getDocFreq(word))
        if df != 0:
            ltc[word] = math.log10(1.0/df)
        else:
            ltc[word] = 0
        sum += pow(ltc[word], 2)
    if sum == 0:
        sum = 1
    for word in ltc:
        ltc[word] /= pow(sum, 0.5)

    lnc = []
    for i in range(len(list)):
        word = list[i]
        list[i] = []
        ph.extractPostingList(word)
        sum = 0
        for count in range(int(ph.getDocFreq(word))):
            post = ph.getNextPosting()

            docID = ph.getDocName(post.getDocID())
            tf = post.getTF()
            lnc.append([docID, 1 + math.log10(tf)])
            sum += pow(1 + math.log10(tf), 2)
        if sum == 0:
            sum = 1
        for j in range(len(lnc)):
            docID = lnc[j][0]
            lncScore = lnc[j][1] / pow(sum, 0.5)

            list[i].append([docID, lncScore * ltc[word]])

def doAnd(t1, t2):
    # AND-merge of two nested arrays of format [[docID, score], ...]
    # Returns nested array of similar format
    i = j = 0
    result = []
    while i < len(t1) and j < len(t2):
        # print("i: %d of %d\nj: %d of %d" % (i, len(t1), j, len(t2)))
        d1, s1 = t1[i]
        d2, s2 = t2[j]
        if d1 == d2:
            result.append([d1, s1 * s2])
            i += 1
            j += 1
        elif d1 < d2:
            i += 1
        else:
            j += 1

    return result


# =========================================================================
#
#                           RUN
#
# =========================================================================

if __name__ == "__main__":
    dictionary_file = postings_file = file_of_queries = output_file_of_results = None

    try:
        #opts = (('-d', 'dictionary.txt'), ('-p', 'postings.txt'), ('-q','q1-2.txt'), ('-o','output.txt'))
        opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
    except getopt.GetoptError(err):
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == '-d':
            dictionary_file = a
        elif o == '-p':
            postings_file = a
        elif o == '-q':
            file_of_queries = a
        elif o == '-o':
            file_of_output = a
        else:
            assert False, "unhandled option"

    if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None:
        usage()
        sys.exit(2)

    main()
