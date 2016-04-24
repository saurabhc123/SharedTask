#!/usr/bin/python
from sys import argv,exit,stderr
import codecs
import json
import func


if len(argv)<5:
	print """
	./addPredictionPSArg1.py <relations.json> <parses.json> <predictionFile>  <writeF>	
	"""
	exit()
relations=argv[1] #relations.json
predictedClauses=open(argv[3],'r')
parsesFile=argv[2]
outF=open(argv[4],'w')
parsesF=codecs.open(parsesFile, encoding='utf8')
parseDict=json.load(parsesF)
dictByDocID=func.makeDictByDocID(parseDict)
relationsF=codecs.open(relations, encoding='utf8')
relations = [json.loads(x) for x in relationsF]



def writeOutputFormat(relations,outF):
	for relation in relations:
		outF.write('%s\n' % json.dumps(relation))


def makeRelationsDictForOutput(relationDict,psArg1PredictionsDict,dictByDocID):
	#relations = [json.loads(x) for x in relationsF]
	total=0
	correct=0.0
	for relation in relationDict:
	   docID=relation['DocID']
	   relType=relation['Type']
	   relID=relation['ID']
	   connectiveTokens=[]
	   if 'RawText' in relation['Connective']:
	      connectiveTokens=relation['Connective']['RawText'].split()
	   arg1Loc='None'

	   #check that this is an explicit relation
	   if relType=='Explicit':
		arg1SentID=relation['Arg1']['TokenList'][0][3]
		arg2SentID=relation['Arg2']['TokenList'][0][3]
		arg1Loc=func.getArg1Location(relation)
		if arg1Loc=='PS':
			print >>stderr, arg1Loc
		#if arg1Loc=='PS':
			total+=1
			#get token IDs for sentence of Arg1
			tokenIDsSent=func.getTokenIDsFromSentence(dictByDocID,docID,arg1SentID)
			
			(arg1PSWordIDs,arg1PSWordList)=getArg1PSWordIDs(relID,docID,arg1SentID,psArg1PredictionsDict,dictByDocID,arg1SentID)
			arg1PSTokenIDs=[]
			for i in dictByDocID[docID][arg1SentID]:
				if i in arg1PSWordIDs:
				   tokenID=dictByDocID[docID][arg1SentID][i]['tokenID']
				   #print >>stderr, 'tokenID', tokenID
				   arg1PSTokenIDs.append(tokenID)
			#***baseline***: set Arg1 to be entire sentence
			if relID not in psArg1PredictionsDict:
				print >>stderr, 'Baseline'
				arg1PSTokenIDs=tokenIDsSent[:-1]
			#arg1PSTokenIDs=tokenIDsSent[:-1]
			#****************************#
			#compare gold and predcited PS Arg1
			if relID in psArg1PredictionsDict:
			   predictedClausesArg1=psArg1PredictionsDict[relID]
			 #getCompareGoldPredictedPSArg1(predictedClausesArg1,dictByDocID,relation,relID,docID,sentID)		   
			   getCompareGoldPredictedPSArg1(predictedClausesArg1,dictByDocID,relation,relID,docID,arg1SentID,arg1PSWordList)
			#*****************************#
	   #get tokenIDs for connective, arg1, arg2
	   #(connectiveTokenIDs, arg1TokenIDs, arg2TokenIDs)=getTokenIDsList(relation)
	   connectiveTokenIDs=func.getTokenIDsList(relation,'Connective')
	   arg1TokenIDs=func.getTokenIDsList(relation,'Arg1')
	   arg2TokenIDs=func.getTokenIDsList(relation,'Arg2')
	   if relType=='Explicit' and arg1Loc=='PS':
	   #if arg1Loc=='PS':
		arg1TokenIDs=arg1PSTokenIDs
		relation['Arg1']['RawText']=' '.join(arg1PSWordList)
	   relation['Connective']['TokenList']=connectiveTokenIDs
	   relation['Arg1']['TokenList']=arg1TokenIDs
	   relation['Arg2']['TokenList']=arg2TokenIDs
	return relations

def getArg1PSWordIDs(relID,docID,arg1SentID,psArg1PredictionsDict,dictByDocID,sentID):
		if relID not in psArg1PredictionsDict:
			print >>stderr, 'Not found', relID
			return ([],[])
		clauseList=psArg1PredictionsDict[relID]
		clauseList.sort()
                #if a combination contains multiple clauses; if clauses are consecutive, need to add
                #punctuation if it was deleted; otherwise do not add punctuation
                wordList=[]
		arg1WordIDs=[]
                for i in range(len(clauseList)):
                        clause=clauseList[i][0]
                        #add missing punctuation that has been removed at clause splitting
                        #if i:
                        #       print 'prev', clauseList[i-1][-1], clause[0]
			prevClause=[]
			if i:
				prevClause=clauseList[i-1][0]
                        if i and clause[0]-prevClause[-1]==2:
                                #print 'punc'
                                puncWordID=clause[0]-1
                                punc=dictByDocID[docID][sentID][puncWordID]['word']
                                wordList.append(punc)
				arg1WordIDs.append(puncWordID)
                        for wordID in clause:
				#print >>stderr, wordID, clause, dictByDocID[docID][sentID]
                                w=dictByDocID[docID][sentID][wordID]['word']
                                wordList.append(w)
				arg1WordIDs.append(wordID)
		#arg1 is complete sentence
                if len(wordList)==len(dictByDocID[docID][sentID])-1:
                        wordList=[]
			arg1WordIDs=[]
                        for j in dictByDocID[docID][sentID]:
                                wordList.append(dictByDocID[docID][sentID][j]['word'])
				arg1WordIDs.append(j)
                        wordList=wordList[:-1]
			arg1WordIDs=arg1WordIDs[:-1]
 #               print '*Word list*', ' '.join(wordList)
                #if wordList==goldWords:
                 #       print '***Found match***', len(clauseList)
                  #      flag=1
                   #     break
		return (arg1WordIDs, wordList)

#each clause is a pair, where the first element is a list of wordIDs of that clauses
def getCompareGoldPredictedPSArg1(predictedClausesArg1,dictByDocID,relation,relID,docID,sentID,arg1WordList):
        	goldWords=[]
		goldArgWordIDs=[]
		for i in relation['Arg1']['TokenList']:
			#print >>stderr, i
			goldArgWordIDs.append(i[4])
        	for i in goldArgWordIDs:
                	w=dictByDocID[docID][sentID][i]['word']
                	goldWords.append(w)
 		clauseList=predictedClausesArg1
		clauseList.sort()
                #if a combination contains multiple clauses; if clauses are consecutive, need to add
                #punctuation if it was deleted; otherwise do not add punctuation
                wordList=[]
                sentWords=dictByDocID[docID][sentID]
                for i in range(len(clauseList)):
			#print >>stderr, 'clauseList', clauseList
			#print >>stderr, 'clause', clause
                        clause=clauseList[i][0]
			prevClause=nextClause=[]
			if i:
				prevClause=clauseList[i-1][0]
			
                        #add missing punctuation that has been removed at clause splitting
                        #if i:
                        #       print 'prev', clauseList[i-1][-1], clause[0]
                        if prevClause and clause[0]-prevClause[-1]==2:
                                #print 'punc'
                                puncWordID=clause[0]-1
                                punc=dictByDocID[docID][sentID][puncWordID]['word']
                                wordList.append(punc)
                        for wordID in clause:
			#	print >>stderr, 'wordID', wordID
			#	print >>stderr, 'wordIDs',dictByDocID[docID][sentID]
                                w=dictByDocID[docID][sentID][wordID]['word']
                                wordList.append(w)
                if len(wordList)==len(dictByDocID[docID][sentID])-1:
                        wordList=[]
                        for j in dictByDocID[docID][sentID]:
                                wordList.append(dictByDocID[docID][sentID][j]['word'])
                        wordList=wordList[:-1]
                if wordList==goldWords:
                        print '***Found match***', len(clauseList), 'Number of words in gold', len(goldWords), 'predicted',len(wordList), 'docID', docID, 'relID', relID

        	else:
                	print '***Match not found***', 'Number of gold words', len(goldWords), 'Predicted words', len(wordList), 'docID', docID, 'relID', relID, 'diff',  len(goldWords)-len(wordList)
		#print 'Clauses', clauseList, len(clauseList)
		print '*Gold Arg1*', ' '.join(goldWords)
                print '*Word list*', ' '.join(wordList)
		if arg1WordList!=wordList:
			print >>stderr, 'Different word lists'
			print >>stderr, arg1WordList
			print >>stderr, wordList



def getPredictions(f):
	dict={}
	for l in f:
		terms=l.split()
		lab=terms[1].split('=')[1]
		source=terms[0].split('=')[1]
		pred=terms[2].split('=')[1]
		exID=terms[3]
		words=exID.split(':')
		docID=words[0].split('-')[1]
		sentID=int(words[1].split('-')[1])
		clauseWordIDs=words[2].split('_')[1:]
		wordIDs=[]
		for i in clauseWordIDs:
			wordIDs.append(int(i))
		relID=int(words[3].split('-')[1])
		if docID not in dict:
			dict[docID]={}
		if relID not in dict:
			dict[relID]=[]
		if pred=='1':
			dict[relID].append((wordIDs,''))
		#dict[relID]['pred']=pred
		#dict[relID]['docID']=docID
		#dict[relID]['sentID']=sentID
		#dict[relID]['wordIDs']=wordIDs
	return dict
		
clausePredictionsDict=getPredictions(predictedClauses)
relationsWithPredictedArg1PS=makeRelationsDictForOutput(relations,clausePredictionsDict,dictByDocID)
writeOutputFormat(relationsWithPredictedArg1PS,outF)
