# returns dictionary with termId along with its total document occurrences
def getDocTermIndexes():
    df = {}
    file = open('doc_index.txt', newline='')
    for line in file.readlines():
        indexes = line.strip().split('\t')
        docId = int(indexes[0])
        termId = int(indexes[1])
        termFreq = len(indexes[2:])
        if docId in df:
            termInfo = df[docId]
            termInfo[termId] = termFreq
            df[docId] = termInfo
        else:
            termInfo = {}
            termInfo[termId] = termFreq
            df[docId] = termInfo
    file.close()
    return df


def getDocs():
    all = {}
    file = open('docids.txt', newline='')
    for line in file.readlines():
        indexes = line.strip().split('\t')
        all[int(indexes[0])] = indexes[1]
    file.close()
    return all


def getTerms():
    all = {}
    file = open('termids.txt', newline='')
    for line in file.readlines():
        indexes = line.strip().split('\t')
        all[indexes[1]] = int(indexes[0])  # 0 -> ID of term at index 1
    file.close()
    return all


# returns the term frequency of the terms of corpus in documents
def getTermTf():
    freq = {}
    file = open('term_info.txt', newline='')
    for line in file.readlines():
        indexes = line.strip().split('\t')
        term_id = int(indexes[0])
        term_freq = int(indexes[2])
        freq[term_id] = term_freq
    file.close()
    return freq


# returns the document frequency for terms
# total number of documents in which term appears
def getTermDF():
    docFreq = {}
    file = open('term_info.txt', newline='')
    for line in file.readlines():
        indexes = line.strip().split('\t')
        term_id = int(indexes[0])
        if term_id not in docFreq:
            docFreq[term_id] = int(indexes[3])
    file.close()
    return docFreq


# returns the total terms in the document
def getDocLength(docTermIndexes, docId):
    sum = 0
    for term in docTermIndexes[docId]:
        sum += docTermIndexes[docId][term]
    return sum


# returns the average doc length
def getAvgDocLength(docTermIndexes, docs):
    avg = 0
    for docId in docTermIndexes:
        avg += getDocLength(docTermIndexes, docId)  # adding total terms of all documents
    return avg / len(docs)


# returns the average query length
def getAvgQueryLength(queries):
    avgQueryLength = 0
    for id in queries:
        avgQueryLength += len(queries[id])
    avgQueryLength /= len(queries)
    return avgQueryLength


# returns the term frequency of the query terms in the corpus
def getQueryTf(query_list, terms):
    tmp = {}
    for query in query_list:
        if query in terms:
            termId = terms[query]
            if query in tmp:
                tmp[termId] += 1
            else:
                tmp[termId] = 1
    return tmp


# return document frequency of query
# total number of documents in which query appears
def getQueryDF(queries, terms):
    tmp = {}
    for id in queries:
        for stem in queries[id]:
            if stem in terms:
                termId = terms[stem]
                if termId in tmp:
                    tmp[termId] += 1
                else:
                    tmp[termId] = 1
    return tmp
