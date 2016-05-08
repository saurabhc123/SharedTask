#!/usr/bin/python
from sys import argv,exit,stderr
import codecs
import json
import func

if len(argv)<4:
	print """
	./convertOutputToRelation.py <outputF> <parsesF> <writeF>	
	"""
	exit()

outputF=argv[1]
parsesFile=argv[2]
writeF=open(argv[3],'w')

relationsF=codecs.open(outputF, encoding='utf8')
relations = [json.loads(x) for x in relationsF]
parsesF=codecs.open(parsesFile, encoding='utf8')
parseDict=json.load(parsesF)
dictByDocID=func.makeDictByDocID(parseDict)

def writeOutputFormat(relations,outF):
        for relation in relations:
                outF.write('%s\n' % json.dumps(relation))

def outputToRelationFormat(relation,dictByTokenID,outF):
   docID=relation['DocID']
	#do connective
   if 'Connective' in relation:
	#print >>stderr, relation['Connective']
	connectiveTokenIDs=relation['Connective']['TokenList']
	tokenList=[]
	for t in connectiveTokenIDs:
		print >>stderr, t, docID
		sentID=dictByTokenID[docID][t]['sentID']
		wordID=dictByTokenID[docID][t]['wordID']
		elementTokenList=[-1,-1,t,sentID,wordID]
		tokenList.append(elementTokenList)
	relation['Connective']['TokenList']=tokenList
	
	#do Arg1
   if 'Arg1' in relation:
	arg1TokenIDs=relation['Arg1']['TokenList']
	tokenList=[]
        for t in arg1TokenIDs:
                sentID=dictByTokenID[docID][t]['sentID']
                wordID=dictByTokenID[docID][t]['wordID']
                elementTokenList=[-1,-1,t,sentID,wordID]
                tokenList.append(elementTokenList)
        relation['Arg1']['TokenList']=tokenList
	
	#do Arg2
   if 'Arg2' in relation:
	arg2TokenIDs=relation['Arg2']['TokenList']
        tokenList=[]
        for t in arg2TokenIDs:
                sentID=dictByTokenID[docID][t]['sentID']
                wordID=dictByTokenID[docID][t]['wordID']
                elementTokenList=[-1,-1,t,sentID,wordID]
                tokenList.append(elementTokenList)
	relation['Arg2']['TokenList']=tokenList
	
   writeOutputFormat([relation], outF)

dictByTokenID=func.makeDictByTokenID(dictByDocID)
for relation in relations:
	outputToRelationFormat(relation, dictByTokenID, writeF)	
