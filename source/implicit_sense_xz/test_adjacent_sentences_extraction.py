'''
Created on May 5, 2016

@author: Xuan Zhang
'''
from sys import argv,exit
import extract_adjacent_sentences
# INPUT: Predicted relations.json, parses.json, raw documents directory
# OUTPUT: Adjacent sentences in relations.json format

if len(argv)<5:
    print """
    ./test_adjacent_sentences_extraction.py <predictionsF> <parsesF> <documentDir> <writeF>    
    """
    exit()

predictionsF=argv[1]
parsesF=argv[2]
docDir = argv[3]
writeF = argv[4]

extract_adjacent_sentences.produceRelationsFile(predictionsF, parsesF, docDir, writeF)