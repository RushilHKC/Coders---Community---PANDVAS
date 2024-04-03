#!/usr/bin/python
# coding=utf-8
import re
import sys
import getopt
from nltk.corpus import stopwords
import time

import json
import tf_idf
import nltk
nltk.download('stopwords')
import csv
import io


# =========================================================================
#
#                           ARGS PASS
#
# =========================================================================

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


# =========================================================================
#
#                           Methods
#
# =========================================================================
class Indexer:
    def __init__(self, input_dictionary, output_file_dictionary, output_file_postings):
        self.input_dictionary = input_dictionary
        self.dictionaryFile = output_file_dictionary
        self.postingsFile = output_file_postings
        self.tempPostingA = "tempA.txt"
        self.tempPostingB = "tempB.txt"
        self.numberOfFiles = len(self.input_dictionary)
        self.whichFile = 1
        data = open(self.tempPostingA, "w")
        data.write("")
        data.close()
        data = open(self.tempPostingB, "w")
        data.write("")
        data.close()

    def indexDictionary(self, numberOfFilesToProcess=0):
        if numberOfFilesToProcess == 0:
            numberOfFilesToProcess = self.numberOfFiles
        dictionary = self.processFiles(numberOfFilesToProcess, self.input_dictionary)
        print("Pickle")
        exportDS(dictionary, self.dictionaryFile)

    # =========================================================================
    #       Processes Files given into the end product
    #           input: numberOfFilesToProcess(int), input_dictionary
    #           output: global_dictionary
    # =========================================================================
    def processFiles(self, numberOfFilesToProcess, input_dictionary):
        Main_Dictionary = dict()
        Main_Dictionary["DOC_ID"] = dict()
        local_posting_asList = list()
        local_dictionary = dict()
        count = 0
        totalRawLen = 0
        averageLen = 0
        filesSkipped = 0
        for caseID in input_dictionary:
            if count > numberOfFilesToProcess:
                break

            if count > 5000 and calcRawLen(input_dictionary[caseID]) > 100 * averageLen:
                print("skipping file " + str(count + 1))
                count += 1
                totalRawLen += calcRawLen(input_dictionary[caseID])
                averageLen = totalRawLen / count
                filesSkipped += 1
                continue

            titleDict = makeAllGrams(input_dictionary[caseID]["title"])
            contentDict = makeGrams(input_dictionary[caseID]["content"])
            dateDict = makeAllGrams(input_dictionary[caseID]["date_posted"])
            courtDict = makeAllGrams(input_dictionary[caseID]["court"])
            dictToProcess = dict(title=titleDict, content=contentDict, date_posted=dateDict, court=courtDict)
            length = tf_idf.getLncLen(makeUniGrams(input_dictionary[caseID]["content"]))
            Main_Dictionary["DOC_ID"][str(count)] = tuple((caseID, length))
            local_dictionary, local_posting_asList = self.addWords(dictToProcess, str(count), local_posting_asList,
                                                                   local_dictionary)

            if ((count + 1) % 100) == 0:
                print(str(count + 1) + " out of " + str(numberOfFilesToProcess) + " files processed.")
                print("Average length = " + str(averageLen))

            # Saves locally when RAM is insufficient
            # if ((count + 1) % 20000) is 0:
            # print("Writing to disk")
            # if self.whichFile is 1:
            # oldFile = self.tempPostingA
            # newFile = self.tempPostingB
            # self.whichFile *= -1
            # else:
            # oldFile = self.tempPostingB
            # newFile = self.tempPostingA
            # self.whichFile *= -1
            # Main_Dictionary = self.mergePosting(local_dictionary, local_posting_asList, oldFile, newFile, Main_Dictionary, numberOfFilesToProcess)
            # local_dictionary = dict()
            # local_posting_asList = list()
            count += 1
            totalRawLen += calcRawLen(input_dictionary[caseID])
            averageLen = totalRawLen/count

        print("Processing Completed. " + str(filesSkipped) + " files skipped.")

        if self.whichFile == 1:
            oldFile = self.tempPostingA
            newFile = self.tempPostingB
            self.whichFile *= -1
        else:
            oldFile = self.tempPostingB
            newFile = self.tempPostingA
            self.whichFile *= -1
        print("Writing to disk")
        Main_Dictionary = self.mergePosting(local_dictionary, local_posting_asList, oldFile, self.postingsFile,
                                            Main_Dictionary, numberOfFilesToProcess)

        return Main_Dictionary

    # =========================================================================
    #       Adds each word in the file to self.dictionary and self.local_posting_asList
    #           input: words(Dictionary), fileIndex(String), local_posting_asList, local_dictionary
    #           output: local_dictionary, local_posting_asList
    # =========================================================================
    def addWords(self, dictionary, fileIndex, local_posting_asList, local_dictionary):
        for word in dictionary["title"]:
            # print(word)
            local_dictionary, local_posting_asList = self.addWord(word, fileIndex, local_dictionary,
                                                                  local_posting_asList)
            index = local_dictionary[word]["index"]
            if fileIndex not in local_posting_asList[index]:
                local_posting_asList[index][fileIndex] = dict(title=0, content=0, date_posted=0, court=0)
                local_dictionary[word]["docFreq"] += 1
            # local_posting_asList[index][fileIndex]["title"] += dictionary["title"][word]

            local_posting_asList[index][fileIndex]["title"] += dictionary["title"][word]
            # Also add the title to the content posting
            local_posting_asList[index][fileIndex]["content"] += dictionary["title"][word]

        for word in dictionary["content"]:
            # print(word)
            local_dictionary, local_posting_asList = self.addWord(word, fileIndex, local_dictionary,
                                                                  local_posting_asList)
            index = local_dictionary[word]["index"]
            if fileIndex not in local_posting_asList[index]:
                local_posting_asList[index][fileIndex] = dict(title=0, content=0, date_posted=0, court=0)
                local_dictionary[word]["docFreq"] += 1
            # local_posting_asList[index][fileIndex]["content"] += dictionary["content"][word]

            local_posting_asList[index][fileIndex]["content"] += dictionary["content"][word]
            # Also add the content to the title posting
            local_posting_asList[index][fileIndex]["title"] += dictionary["content"][word]

        for word in dictionary["date_posted"]:
            # print(word)
            local_dictionary, local_posting_asList = self.addWord(word, fileIndex, local_dictionary,
                                                                  local_posting_asList)
            index = local_dictionary[word]["index"]
            if fileIndex not in local_posting_asList[index]:
                local_posting_asList[index][fileIndex] = dict(title=0, content=0, date_posted=0, court=0)
                local_dictionary[word]["docFreq"] += 1
            local_posting_asList[index][fileIndex]["date_posted"] += dictionary["date_posted"][word]

        for word in dictionary["court"]:
            # print(word)
            local_dictionary, local_posting_asList = self.addWord(word, fileIndex, local_dictionary,
                                                                  local_posting_asList)
            index = local_dictionary[word]["index"]
            if fileIndex not in local_posting_asList[index]:
                local_posting_asList[index][fileIndex] = dict(title=0, content=0, date_posted=0, court=0)
                local_dictionary[word]["docFreq"] += 1
            local_posting_asList[index][fileIndex]["court"] += dictionary["court"][word]

        return local_dictionary, local_posting_asList

    # =========================================================================
    #       Adds a word in the file to local_dictionary and local_posting_asList
    #           input: word, fileIndex(String), local_dictionary, local_posting_asList
    #           output: None
    # =========================================================================
    def addWord(self, word, fileIndex, local_dictionary, local_posting_asList):
        if word not in local_dictionary:
            # print("found new word " + word + " in document " + str(fileIndex))
            local_dictionary[word] = dict(docFreq=1, index=len(local_posting_asList))
            tempList = dict()
            tempList[fileIndex] = dict(title=0, content=0, date_posted=0, court=0)
            local_posting_asList.append(tempList)

        return local_dictionary, local_posting_asList

    # =========================================================================
    #       Merges local posting with global posting that is stored on disk.
    #           Can also be used to simply save the postings on disk.
    #           input: local_dictionary, local_posting_asList, oldPostingFilePath, newPostingFile, Main_Dictionary, numberOfFiles
    #           output: Main_Dictionary(global dictionary)
    # =========================================================================
    def mergePosting(self, local_dictionary, local_posting_asList, oldPostingFilePath, newPostingFile, Main_Dictionary,
                     numberOfFiles):
        oldPostingFile = open(oldPostingFilePath, 'r')
        data = open(newPostingFile, "w")
        data.write("")
        data.close()
        count = 0

        with open(newPostingFile, "a+") as data:
            for word in local_dictionary:
                if word in Main_Dictionary:
                    posting = extractPostingList(word, Main_Dictionary, oldPostingFile).rstrip()
                    index = local_dictionary[word]["index"]
                    posting = createPosting(local_posting_asList[index], posting)
                    startPointer = addPosting(posting, data)
                    Main_Dictionary[word]["index"] = startPointer
                    Main_Dictionary[word]["docFreq"] += local_dictionary[word]["docFreq"]
                else:
                    # if local_dictionary[word]["docFreq"] > (numberOfFiles * 3 / 4):
                    # continue
                    posting = ""
                    index = local_dictionary[word]["index"]
                    posting = createPosting(local_posting_asList[index], posting)
                    startPointer = addPosting(posting, data)
                    Main_Dictionary[word] = dict()
                    Main_Dictionary[word]["index"] = startPointer
                    Main_Dictionary[word]["docFreq"] = local_dictionary[word]["docFreq"]

                count += 1
                if ((count + 1) % 10000) == 0:
                    print(str(count + 1) + " out of " + str(len(local_dictionary)) + " written.")

            undone = set(Main_Dictionary) - set(local_dictionary)

            for word in undone:
                if word == "DOC_ID":
                    continue
                posting = extractPostingList(word, Main_Dictionary, oldPostingFile)
                startPointer = addPosting(posting, data)
                Main_Dictionary[word]["index"] = startPointer

        return Main_Dictionary


def calcRawLen(dict):
    return len(dict["content"]) + len(dict["title"]) + len(dict["date_posted"]) + len(dict["court"])


# =========================================================================
#       Processes input of dictionary of lists into dictionary of dictionary
#       (THIS IS AN INTERFACE)
#           input: list of words)
#           output: dictionary of grams
# ========================================================================= 
def makeGrams(list):
    dictOfGrams = dict()

    dictOfGrams.update(makeUniGrams(list))
    dictOfGrams.update(makeBiGrams(list))

    return dictOfGrams


# =========================================================================
#       Processes list into dictionary of uniGrams
#           input: list of words
#           output: dictionary of uniGrams
# =========================================================================
def makeUniGrams(list):
    words = dict()
    for word in list:
        if word not in words:
            # print(word)
            words[word] = 1
        else:
            words[word] += 1
    return words


# =========================================================================
#       Processes list into dictionary of biGrams
#           input: list of words
#           output: dictionary of uniGrams
# =========================================================================
def makeBiGrams(list):
    words = dict()
    count = 0
    for word in list:
        if count > 0:
            biWord = prevWord + " " + word
            if biWord not in words:
                # print(biWord)
                words[biWord] = 1
            else:
                words[biWord] += 1
        prevWord = word
        count += 1
    return words


# =========================================================================
#       Processes list into dictionary of triGrams
#           input: list of words
#           output: dictionary of uniGrams
# =========================================================================
def makeTriGrams(list):
    words = dict()
    count = 0
    for word in list:
        if count > 1:
            triWord = prevPrevWord + " " + prevWord + " " + word
            if triWord not in words:
                # print(triWord)
                words[triWord] = 1
            else:
                words[triWord] += 1
        if count > 0:
            prevPrevWord = prevWord
        prevWord = word
        count += 1
    return words


# =========================================================================
#       More efficient in generating all 1,2,3grams (1 pass)
#           input: list of words
#           output: dictionary of uniGrams
# =========================================================================
def makeAllGrams(list):
    words = dict()
    count = 0
    for word in list:

        if word not in words:
            # print(word)
            words[word] = 1
        else:
            words[word] += 1

        if count > 0:
            biWord = prevWord + " " + word
            if biWord not in words:
                # print(biWord)
                words[biWord] = 1
            else:
                words[biWord] += 1

        if count > 1:
            triWord = prevPrevWord + " " + prevWord + " " + word
            if triWord not in words:
                # print(triWord)
                words[triWord] = 1
            else:
                words[triWord] += 1

        if count > 0:
            prevPrevWord = prevWord
        prevWord = word
        count += 1
    return words


# =========================================================================
#       Creates posting for one word first two digits represent the length
#           of fileIndex, followed by fileIndex, followed by two digits 
#           representing the length of termFreq, followed by termFreq \n
#           This version appends to the previous posting. 
#           input: postings(list of dictionary),posting(String)
#           output: posting(String)
# =========================================================================
def createPosting(postings, posting):
    list_of_str = list()
    for fileIndex in postings:
        list_of_str.append(str(len(fileIndex)).zfill(2) + fileIndex)
        list_of_str.append(str(len(str(postings[fileIndex]["title"]))).zfill(1))
        list_of_str.append(str(postings[fileIndex]["title"]))
        list_of_str.append(str(len(str(postings[fileIndex]["content"]))).zfill(1))
        list_of_str.append(str(postings[fileIndex]["content"]))
        list_of_str.append(str(len(str(postings[fileIndex]["date_posted"]))).zfill(1))
        list_of_str.append(str(postings[fileIndex]["date_posted"]))
        list_of_str.append(str(len(str(postings[fileIndex]["court"]))).zfill(1))
        list_of_str.append(str(postings[fileIndex]["court"]))
    posting = posting + "".join(list_of_str) + "\n"

    return posting


# =========================================================================
#       Add the posting to the outputFile 
#           input: posting(String), outputFile(String)
#           output: startPointer
# =========================================================================
def addPosting(Posting, outputData):
    outputData.seek(0, 2)
    startPointer = outputData.tell()
    outputData.write(Posting)
    return startPointer


# =========================================================================
#       Extracts a posting list for a word
#           input: Word, dictionary, posting list(type: file object)
#           returns: postingList(type: String)
# =========================================================================
def extractPostingList(word, dictionary, postingsFile):
    startPointer = dictionary[word]["index"]
    postingsFile.seek(startPointer)
    postingList = postingsFile.readline()
    return postingList


# =========================================================================
#       Exports the dataStructure using pickle interface
#           input:DS(object), outputFile(String)
#           output: None
# =========================================================================
def exportDS(DS, outputFile):
    DS_string = json.dumps(DS)
    outputFile = open(outputFile, 'w')
    outputFile.write(DS_string)
    outputFile.close()
    return


# =========================================================================
#       preprocess string (stemming and tokenize)
# =========================================================================    

def preprocess(string):
    tokens = nltk.word_tokenize(string)
    words = list()
    sw = set(stopwords.words('english'))
    Stemmer = nltk.stem.porter.PorterStemmer()
    for token in tokens:
        token = ''.join(e for e in token if e.isalnum())
        if len(token) < 2 or token in sw:
            continue
        word = Stemmer.stem(token)
        words.append(word)
    return list(words)

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
#       fix decoding problems
# =========================================================================  

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

# =========================================================================
#       Translate CSV file to dictionary without using pandas
#           input:csv path
#           output: dictionary
# ========================================================================= 

# def translateCSVtoDictionary(path):
#     csv.field_size_limit(500 * 1024 * 1024)
#     dummyDocs = dict()
#     rows = list()
#     count = 0
#     columns = ["title", "content", "date_posted", "court"]
#     csvfile =  io.open(path, 'r',encoding = 'utf-8')
#     reader = unicode_csv_reader(csvfile)
#     rows = [row for row in reader]
#     # rows = []
#     # for i in range(50):
#     #     rows.append(reader.next())
#     # print(rows[0])
#     iniT = time.time()
#     t1 = time.time()
#     for row in rows:
#         if time.time() - t1 > 5:
#             print("Files processed :" + str(count))
#             t1 = time.time()
#         if count == 0:
#             count+=1
#             continue
#         dummyDoc = dict()
#         for columnid in range(4):
#             dummyDoc[columns[columnid]] = preprocess(row[columnid + 1])
#         dummyDocs[row[0]] = dummyDoc
#         count += 1
#     csvfile.close()
#     print("Indexing took " + str(time.time() - iniT))
#     return dummyDocs

import pandas as pd

import pandas as pd
import io
import time

def translateCSVtoDictionary(path):
    csv.field_size_limit(500 * 1024 * 1024)
    dummyDocs = dict()
    count = 0
    # Update column names based on your actual CSV file
    columns = ["title", "content", "date_posted", "court"]

    # Read CSV file using pandas
    df = pd.read_csv(path,delimiter='|')

    # Print column names to check if 'title' is present
    print("Column Names:", df.columns)

    iniT = time.time()
    t1 = time.time()

    for index, row in df.iterrows():
        if time.time() - t1 > 5:
            print("Files processed: " + str(count))
            t1 = time.time()

        dummyDoc = dict()
        for columnid in range(4):
            column_name = columns[columnid]
            if column_name not in df.columns:
                print(f"Column '{column_name}' not found in DataFrame.")
                continue

            dummyDoc[column_name] = preprocess(row[column_name])

        # Assuming 'title' is still a valid column name
        dummyDocs[row["title"]] = dummyDoc
        count += 1

    print("Indexing took " + str(time.time() - iniT))
    return dummyDocs

# def addRowToDict(row):
#     dummyDoc = dict()
#     global input_dictionary
#     columns = ["title", "content", "date_posted", "court"]
#     for columnid in range(4):
#         dummyDoc[columns[columnid]] = preprocess(row[columnid + 1])
#     input_dictionary[row[0]] = dummyDoc

def addRowToDict(row):
    dummyDoc = dict()
    global input_dictionary
    columns = ["title", "content", "date_posted", "court"]
    for columnid in range(4):
        dummyDoc[columns[columnid]] = preprocess(row[columnid + 1])
    input_dictionary[row[0]] = dummyDoc


# =========================================================================
#
#                           RUN
#
# =========================================================================
if __name__ == "__main__":

    input_directory = output_file_dictionary = output_file_postings = None

    try:
        #opts = (('-i', 'dataset.csv'), ('-d', 'dictionary2.txt'), ('-p','postings2.txt'))
        opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
    except getopt.GetoptError(err):
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == '-i':  # input csv
            input_dictionary = a
        elif o == '-d':  # dictionary file
            output_file_dictionary = a
        elif o == '-p':  # postings file
            output_file_postings = a
        else:
            assert False, "unhandled option"

    if input_dictionary == None or output_file_postings == None or output_file_dictionary == None:
        usage()
        sys.exit(2)

    print("importing dict")
    input_dictionary = translateCSVtoDictionary(input_dictionary)
    #input_dictionary = importDS(input_dictionary)
    print("import done")
    indexer = Indexer(input_dictionary, output_file_dictionary, output_file_postings)
    indexer.indexDictionary(0)
# python index.py -i dataset.csv -d dictionary.txt -p postings.txt
