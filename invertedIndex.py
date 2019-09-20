def writeFiles(invertedIndex):
    term_index = open('term_index.txt', 'w')
    term_info = open('term_info.txt', 'w')
    termFrequency = 0
    offSet = 0  # first term is at the start of document

    for termid in invertedIndex:

        term_index.write('%d\t%s\n' % (
        termid, '\t'.join(['\t'.join(value) for key, value in sorted(invertedIndex[termid].iteritems())])))

        termFreq = 0
        for values in invertedIndex[termid].itervalues():  # calculate term frequency
            termFreq = termFreq + len(values)

        docFrequency = len(invertedIndex[termid])
        termInfo = '%d\t%d\t%d\t%d\n' % (termid, offSet, termFreq, docFrequency)
        term_info.write(termInfo)
        offSet = term_index.tell()  # get the current position of File Pointer

    term_info.close()
    term_index.close()


if __name__ == '__main__':
    doc_index = open('doc_index.txt', 'rU')
    invertedIndex = {}

    for line in doc_index.readlines():
        dictionary = {}
        indexes = line.strip().split('\t')

        docid = int(indexes[0])  # document ID
        termid = int(indexes[1])  # Term ID
        positions = [int(x) for x in indexes[2:]]  # Positions

        if termid not in invertedIndex:  # to keep it unique
            lastDocID = 0
            if dictionary:
                lastDocID = sorted(dictionary.keys())[
                    -1]  # retrieve the lastDocID with respect to the DOC ID at the last index of Dictionary

            # For Delta Encoding
            adjacentDocID = docid - lastDocID
            adjacentPositions = []
            adjacentPositions = adjacentPositions + [
                '%d:%d' % (adjacentDocID, positions[0])]  # position 0 is first position
            for index, pos in enumerate(positions):
                if index == len(positions) - 1:
                    break
                adjacentPositions = adjacentPositions + ['%d:%d' % (0, positions[index + 1] - positions[index])]

            dictionary[docid] = adjacentPositions
            invertedIndex[termid] = dictionary
        else:
            dictionary = invertedIndex[termid]
            lastDocID = 0
            if dictionary:
                lastDocID = sorted(dictionary.keys())[-1]

            # For Delta Encoding
            adjacentDocID = docid - lastDocID
            adjacentPositions = []
            adjacentPositions = adjacentPositions + [
                '%d:%d' % (adjacentDocID, positions[0])]  # position 0 is first position
            for index, pos in enumerate(positions):
                if index == len(positions) - 1:
                    break
                adjacentPositions = adjacentPositions + ['%d:%d' % (0, positions[index + 1] - positions[index])]

            dictionary[docid] = adjacentPositions
            invertedIndex[termid] = dictionary

    doc_index.close()
    writeFiles(invertedIndex)
