from os import listdir, path
from argparse import ArgumentParser
import re

termsDict = {}  # contains term_ids for each stem
doc_ids = []
doc_index = []


def getStopWords():
    file = open('/home/adil/PythonProjects/IR-Assignment/stoplist.txt', 'rU')
    return set(file.read().split())  # set having no duplicate elements


def tokenize(direc, stopWords):
    global termsDict, doc_ids, doc_index

    # termsDict -> ids for terms
    # terms -> all positions for single term in current file

    terms = {}
    for ID, name in enumerate(listdir(direc), start=1):
        terms.clear()  # clearing terms for next file

        file = open(path.join(direc, name), encoding="ISO-8859-1")
        text = getFileText(file.read())

        # Stemming for current file
        saveStems(re.finditer('\w+(\.?\w+)*', text.strip(), flags=re.IGNORECASE), stopWords, terms)

        # Saving the tokens' ids and positions for current file
        for termid, pos_list in sorted(terms.items()):
            tmp = '\t'.join([str(x) for x in sorted(pos_list)])  # list of positions of single term in document
            doc_index.append('%d\t%d\t%s' % (ID, termid, tmp))  # DocID + termID (in Dictionary) + list of positions
        doc_ids.append('%d\t%s' % (ID, name))  # DocID + fileName
        file.close()


def saveStems(iterator, stopWords, terms):
    global termsDict, doc_ids, doc_index

    token_id = len(termsDict) + 1  # if termsDic contains terms already
    position = 0
    stems = {}

    import Stemmer  # snowall pystemmer
    stemmer = Stemmer.Stemmer('english')
    for i in iterator:
        position = position + 1
        token = i.group()
        if token is not None and token not in stopWords:  # if !StopWord
            token = token.lower()
            stem = stemmer.stemWord(token)

            if stem in stems:  # checking if already in stems
                stemid = termsDict[stem]
                tmp = terms[stemid]  # positions in rest of document
                tmp.add(position)  # add new position
                terms[stemid] = tmp
            else:
                stems[stem] = token_id
                positions = set()
                positions.add(position)
                if stem not in termsDict:
                    termsDict[stem] = token_id
                    terms[token_id] = positions
                    token_id = token_id + 1  # for new token
                else:
                    terms[termsDict[stem]] = positions


def getFileText(html):
    # removing file Headers
    html = re.sub(r'<.*?html', '<html', html, count=1, flags=re.IGNORECASE)
    pmatch = re.search(r'<html.*?>', html, flags=re.IGNORECASE)
    begin = -1
    if pmatch is not None:
        begin = pmatch.start()  # getting index of <html> tag from the file
    if begin > -1:
        html = html[begin:]
    text = ''
    if html is not None and html != '':
        from bs4 import UnicodeDammit
        import lxml.html.clean
        import lxml.html
        doc = UnicodeDammit(html, is_html=True)  # converting to utf-8
        # cleaning html data and getting Text
        tree = lxml.html.document_fromstring(html, parser=lxml.html.HTMLParser(encoding=doc.original_encoding))
        tree = lxml.html.clean.Cleaner(style=True).clean_html(tree)
        text = tree.text_content()
    return " ".join(text.split())


def saveFiles():
    from operator import itemgetter
    global doc_ids, doc_index, termsDict

    # getting term_ids tuple from term dictionary for each term
    term_ids = ['%d\t%s' % (tId, term) for term, tId in sorted(termsDict.items(), key=itemgetter(1))]

    writeFile('/home/adil/PythonProjects/IR-Assignment/docids.txt', '\n'.join(doc_ids))
    writeFile('/home/adil/PythonProjects/IR-Assignment/termids.txt', '\n'.join(term_ids))
    writeFile('/home/adil/PythonProjects/IR-Assignment/doc_index.txt', '\n'.join(doc_index))


def writeFile(direct, data):
    file = open(direct, 'w')
    file.write(data)
    file.close()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-f', '--folder')
    args = parser.parse_args()
    tokenize(args.folder, getStopWords())
    saveFiles()
