from timeit import default_timer
from argparse import ArgumentParser


def docInfo(docId):
    docIndexFile = open('doc_index.txt', 'rU')

    totalTerms = 0
    uniqueTerms = 0
    for line in docIndexFile.readlines():
        indexes = line.strip().split('\t')
        if docId == int(indexes[0]):
            totalTerms = totalTerms + len(indexes[2:])
            uniqueTerms = uniqueTerms + 1
        if int(indexes[0]) > docId:
            docIndexFile.close()
            return uniqueTerms, totalTerms

    docIndexFile.close()
    return uniqueTerms, totalTerms


def termInfo(termId):
    termInfo = {}
    infoFile = open('term_info.txt', 'rU')

    for line in infoFile.readlines():
        indexes = line.strip().split('\t')
        if termId == int(indexes[0]):
            offSet = int(indexes[1])
            termFreq = int(indexes[2])
            docFreq = int(indexes[3])
            termInfo = (offSet, termFreq, docFreq)  # tuple
            infoFile.close()
            return termInfo

    infoFile.close()
    return termInfo


def getTermID(term):
    term_ids_file = open('termids.txt', 'rU')

    for line in term_ids_file.readlines():
        indexes = line.strip().split('\t')
        if term == indexes[1]:
            term_ids_file.close()
            return int(indexes[0])

    term_ids_file.close()
    return 0


def getDocID(document):
    doc_ids_file = open('docids.txt', 'rU')

    for line in doc_ids_file.readlines():
        indexes = line.strip().split('\t')
        if document == indexes[1]:
            doc_ids_file.close()
            return int(indexes[0])

    doc_ids_file.close()
    return 0


if __name__ == '__main__':
    start = default_timer()
    parser = ArgumentParser()
    parser.add_argument('--doc')
    parser.add_argument('--term')
    args = parser.parse_args()

    if args.term and args.doc:
        termID = getTermID(args.term)
        if termID:
            term_stats = termInfo(termID)
            docID = getDocID(args.doc)
            if docID:
                doc_stats = docInfo(docID)
                offset = term_stats[0]  # offset point where the inverted list is starting

                term_index_file = open('term_index.txt', 'rU')
                term_index_file.seek(offset)  # go to the point where particular docID is
                line = term_index_file.readline()
                term_index_file.close()
                indexes = line.split('\t')
                invertedIndex = indexes[1:]  # inverted index starting from 2nd index
                positionsList = {}
                prevDoc = 0
                prevPositions = 0

                for item in invertedIndex:
                    postings = []
                    doc = int(item.split(':')[0]) + prevDoc
                    termPosition = int(item.split(':')[1])
                    if doc == docID:
                        if doc not in positionsList:
                            prevPositions = 0
                        else:
                            postings = positionsList[doc]

                        postings.append(termPosition + prevPositions)
                        positionsList[doc] = postings
                        prevPositions += termPosition
                    prevDoc = doc

                if positionsList:
                    print('Inverted list for term: %s' % args.term)
                    print('In document: %s' % args.doc)
                    print('TERMID: %d' % termID)
                    print('DOCID: %d' % docID)
                    print('Term frequency in document: %d' % (len(positionsList[docID])))
                    print('Positions:', )
                    for value in positionsList[docID]:
                        print('%s,' % value, )

                else:
                    print('Term not found in this Document')

            else:
                print('No such document exists in Corpus')
        else:
            print('No such term exists in Corpus')

    elif args.term:
        termID = getTermID(args.term)
        if termID:
            term_stats = termInfo(termID)
            print('Listing for term: %s' % args.term)
            print('TERMID: %d' % termID)
            print('Number of documents containing term: %d' % (term_stats[2]))
            print('Term frequency in corpus: %d' % (term_stats[1]))
            print('Inverted list offset: %d' % (term_stats[0]))
        else:
            print('No such term exists in Corpus')

    elif args.doc:
        docID = getDocID(args.doc)
        if docID:
            doc_stats = docInfo(docID)
            distinctTerms = doc_stats[0]
            totalTerms = doc_stats[1]
            print('Listing for document: %s' % args.doc)
            print('DOCID: %d' % docID)
            print('Distinct Terms: %d' % distinctTerms)
            print('Total Terms: %d' % totalTerms)
        else:
            print('No such document exists in Corpus')
