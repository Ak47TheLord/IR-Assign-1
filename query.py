from timeit import default_timer
from argparse import ArgumentParser
from lxml import etree
from math import sqrt, log10
import re
from tokenize import getStopWords
import Stemmer
import helper

userQueries = {}
stemQueries = {}


def getQueries():
    global userQueries, stemQueries
    doc = etree.parse('topics.xml', parser=etree.XMLParser())
    root = doc.getroot()

    for child in root.iter('topic'):
        query = child.find('query').text.strip()
        query = re.split(r'\W+(\.?\W+)*', query, flags=re.IGNORECASE)  # same Regex from tokenizing
        userQueries[int(child.attrib['number'])] = query

    stopWords = getStopWords()
    stemmer = Stemmer.Stemmer('english')
    for id in sorted(userQueries):
        stemQueries[id] = []  # stemming using query id
        for query in userQueries[id]:
            if query and query is not None and query not in stopWords:
                token = query.lower()
                stem = stemmer.stemWord(token)
                stemQueries[id].append(stem)


def tf(docTermIndexes, docs, queries, stemQueries):
    terms = helper.getTerms()
    avgQueryLength = helper.getAvgQueryLength(queries)
    avgDocLength = helper.getAvgDocLength(docTermIndexes, docs)
    file = open('tf_output.txt', 'w+')

    for id in sorted(queries):
        stemList = stemQueries[id]  # stems of the user query
        queryTf = helper.getQueryTf(stemList, terms)
        queryNorm = 0
        vector = {}  # query vector

        # Query Scoring
        for stem in stemList:
            if stem in terms:
                termId = terms[stem]
                vector[termId] = okapiTf(stemList, termId, docTermIndexes, avgQueryLength, False, 0, queryTf)
                queryNorm += vector[termId] * vector[termId]

        # Document Scoring
        docRanking = {}
        for docId in sorted(docTermIndexes):
            docRanking[docId] = cosineSimilarity(docTermIndexes, docId, vector, queryNorm,
                                                 helper.getDocLength(docTermIndexes, docId), avgDocLength)

        printOutput(id, docRanking, docs, file)
    file.close()


def okapiTf(obj, termId, docTermIndexes, avgDocLength, DOC, docLength, queryTf):
    if DOC:
        # obj = DocID
        tf = docTermIndexes[obj][termId]  # tf(d,i)
        okapiTfDoc = tf / (tf + 0.5 + (1.5 * (docLength / avgDocLength)))
        return okapiTfDoc
    else:
        # obj = Query List
        tf = queryTf[termId]
        okapiTfQuery = tf / (tf + 0.5 + (1.5 * (len(obj) / avgDocLength)))
        return okapiTfQuery


def cosineSimilarity(docTermIndexes, docId, queryVector, queryNorm, docLength, avgDocLength):
    vector = queryVector
    docVector = {}
    dotProd = 0
    norm = 0
    for termId in docTermIndexes[docId]:
        docVector[termId] = okapiTf(docId, termId, docTermIndexes, avgDocLength, True, docLength,
                                    None)  # document vector
        norm += docVector[termId] * docVector[termId]
        if termId in vector:
            dotProd += docVector[termId] * vector[termId]
    return dotProd / sqrt(norm * queryNorm)


def tfIdf(docTermIndexes, docs, queries, stemQueries):
    terms = helper.getTerms()
    queryDF = helper.getQueryDF(stemQueries, terms)
    avgQueryLength = helper.getAvgQueryLength(queries)
    termsDF = helper.getTermDF()
    avgDocLength = helper.getAvgDocLength(docTermIndexes, docs)

    file = open('tfidf_output.txt', 'w+')

    for id in sorted(queries):
        stemList = stemQueries[id]
        queryTf = helper.getQueryTf(stemList, terms)
        vector = {}
        queryNorm = 0

        # Query Scoring
        for stem in stemList:
            if stem in terms:
                termId = terms[stem]
                vector[termId] = okapiTf(stemList, termId, docTermIndexes, avgQueryLength, False, 0, queryTf)
                vector[termId] *= log10(len(queries) / queryDF[termId])
                queryNorm += vector[termId] * vector[termId]

        # Document Scoring
        docRanking = {}
        for docId in sorted(docTermIndexes):
            docVector = {}
            docNorm = 0
            dotProd = 0
            for termId in docTermIndexes[docId]:
                docVector[termId] = okapiTf(docId, termId, docTermIndexes, avgDocLength, True,
                                            helper.getDocLength(docTermIndexes, docId), None)
                docVector[termId] *= log10(len(docs) / termsDF[termId])
                docNorm += docVector[termId] * docVector[termId]
                if termId in vector:
                    dotProd += (docVector[termId] * vector[termId])
            docRanking[docId] = dotProd / sqrt(docNorm * queryNorm)

        printOutput(id, docRanking, docs, file)
    file.close()


def bm25(docTermIndexes, docs, queries, stemQueries):
    terms = helper.getTerms()
    termsDF = helper.getTermDF()
    avgDocLength = helper.getAvgDocLength(docTermIndexes, docs)
    k1 = 1.2
    k2 = 150  # randint(0, 1000)
    b = 0.75

    file = open('bm25_output.txt', 'w+')

    for id in sorted(queries):
        stemList = stemQueries[id]
        queryTF = helper.getQueryTf(stemList, terms)
        docRanking = {}
        for docId in sorted(docTermIndexes):
            score = 0
            for stem in stemList:
                if stem in terms:
                    termId = terms[stem]
                    qTF = queryTF[termId]

                    if termId in docTermIndexes[docId]:
                        tDF = termsDF[termId]

                        K = k1 * ((1 - b) + b * (helper.getDocLength(docTermIndexes, docId) / avgDocLength))
                        dTF = docTermIndexes[docId][termId]  # number of occurences of termId in docId

                        score = score + ((log10((len(docs) + 0.5) / (tDF + 0.5))) * ((1 + k1) * dTF / (K + dTF)) * (
                            (1 + k2) * qTF / (k2 + qTF)))
                        docRanking[docId] = score

        printOutput(id, docRanking, docs, file)
    file.close()


def jmSmoothing(docTermIndexes, docs, queries, stemQueries):
    terms = helper.getTerms()
    term_freq = helper.getTermTf()
    allDocsLength = 0
    for docId in docTermIndexes:
        allDocsLength = allDocsLength + helper.getDocLength(docTermIndexes, docId)
    lamda = 0.2

    file = open('jmsmoothing_output.txt', 'w+')

    for id in sorted(queries):
        stemList = stemQueries[id]
        docRanking = {}
        for docId in sorted(docTermIndexes):
            score = 0
            for stem in stemList:
                if stem in terms:
                    termId = terms[stem]
                    operand1 = 0
                    if termId in docTermIndexes[docId]:
                        dTF = docTermIndexes[docId][termId]  # number of occurences of termId in docId
                        doc_length = helper.getDocLength(docTermIndexes, docId)
                        operand1 = dTF / doc_length

                    score = score + ((lamda * operand1) + ((1 - lamda) * (term_freq[termId] / allDocsLength)))
                    docRanking[docId] = score

        printOutput(id, docRanking, docs, file)
    file.close()


def printOutput(id, docRanking, docs, file):
    # highest doc rank at top
    for rank, docId in enumerate(sorted(docRanking, key=docRanking.get, reverse=True), start=1):
        print('%d 0 %s %d %f run1' % (id, docs[docId], rank, docRanking[docId]))
        file.write('%d 0 %i %s %d %f run1 %s' % (id, docId, docs[docId], rank, docRanking[docId], '\n'))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--score', help='the scoring function to be used')
    args = parser.parse_args()

    function = {'TF': tf, 'TF-IDF': tfIdf, 'BM25': bm25, 'JM': jmSmoothing}
    if args.score:

        start = default_timer()

        getQueries()
        docTermIndexes = helper.getDocTermIndexes()

        tmp = function[args.score.strip()]  # assigning function
        if tmp:
            # Calling scoring function
            tmp(docTermIndexes, helper.getDocs(), userQueries, stemQueries)

            # Calculating total time
            print('Total Time : %f seconds' % (default_timer() - start))
