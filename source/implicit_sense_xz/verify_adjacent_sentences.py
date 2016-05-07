'''
Created on May 1, 2016

@author: Xuan Zhang
'''

from sys import argv,exit
import codecs
import json

def inPredictions(relation, predictions):
    relDocID = relation['DocID']
    for pred in predictions:
        DocID = pred['DocID']
        if not DocID == relDocID:
            continue
        sen1ID = pred['Arg1']['TokenList'][0][3]
        sen2ID = pred['Arg2']['TokenList'][0][3]
        arg1SenID = relation['Arg1']['TokenList'][0][3]
        arg2SenID = relation['Arg2']['TokenList'][0][3]
        if sen1ID == arg1SenID and sen2ID == arg2SenID:
            return True
    return False

def adjacentArgs(relation):
    arg1SenID = relation['Arg1']['TokenList'][0][3]
    arg2SenID = relation['Arg2']['TokenList'][0][3]
    if abs(arg1SenID - arg2SenID) == 1:
        return True
    else:
        return False

if len(argv)<3:
    print """
    ./verify_adjacent_sentences.py <predictionsF> <relationsF>    
    """
    exit()

predictionsF=argv[1]
relationsF=argv[2]

#Read predicted relations.json
print("Reading predicted relations.json");
pdtb_file = codecs.open(predictionsF, encoding='utf8');
predictions = [json.loads(x) for x in pdtb_file];
print("Done");

#Read gold standard relations.json
print ("Reading gold standard relations.json");
relations_file = codecs.open(relationsF, encoding='utf8')
relations = [json.loads(x) for x in relations_file]
print ("Done");

matchCount = 0
nonExplicitCount = 0
nonAdjacentArgCount = 0

for relation in relations:
    relType = relation['Type']
    if relType == 'Explicit':
        continue
    nonExplicitCount += 1
    if not adjacentArgs(relation):
        nonAdjacentArgCount += 1
    if inPredictions(relation, predictions):
        matchCount += 1

print str(matchCount) + "/" + str(nonExplicitCount) + " Non-Explicit relations found in predictions"
print str(nonAdjacentArgCount) + "/" + str(nonExplicitCount) + " relations have Non-Adjacent arguments"

