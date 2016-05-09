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


def makeRelationsDictForOutput(relationDict,arg1PredictionsDict,dictByDocID):
	#relations = [json.loads(x) for x in relationsF]
	total=0
	correct=0.0
	for relation in relationDict:
	   docID=relation['DocID']
	   relType=relation['Type']
	   relID=relation['ID']
	   #check that this is an explicit relation
	   if relType=='Implicit':
		arg1SentID=relation['Arg1']['TokenList'][0][3]
		arg2SentID=relation['Arg2']['TokenList'][0][3]
		if 1:
			total+=1
			#get token IDs for sentence of Arg1
			tokenIDsSent=func.getTokenIDsFromSentence(dictByDocID,docID,arg1SentID)
			
			(arg1WordIDs,arg1WordList)=getArg1PSWordIDs(relID,docID,arg1SentID,arg1PredictionsDict,dictByDocID,arg1SentID)
			arg1TokenIDsPredicted=[]
			for i in dictByDocID[docID][arg1SentID]:
				if i in arg1WordIDs:
				   tokenID=dictByDocID[docID][arg1SentID][i]['tokenID']
				   #print >>stderr, 'tokenID', tokenID
				   arg1TokenIDsPredicted.append(tokenID)
			#***baseline***: set Arg1 to be entire sentence
			if relID not in arg1PredictionsDict:
				totWords=len(dictByDocID[docID][arg1SentID])
				print >>stderr, 'Baseline'
				arg1TokenIDsPredicted=tokenIDsSent[:-1]
				if dictByDocID[docID][arg1SentID][0]['word']=='``' and dictByDocID[docID][arg1SentID][totWords-1]['word']=="''":
					arg1TokenIDsPredicted=tokenIDsSent[1:-2]
				elif dictByDocID[docID][arg1SentID][0]['word']=='``':
					arg1TokenIDsPredicted=tokenIDsSent[1:-1]
				else:
					arg1TokenIDsPredicted=tokenIDsSent[:-1]
				

			#****************************#
			#compare gold and predicted PS Arg1
			if relID in arg1PredictionsDict:
			   predictedClausesArg1=arg1PredictionsDict[relID]
			 #getCompareGoldPredictedPSArg1(predictedClausesArg1,dictByDocID,relation,relID,docID,sentID)		   
			   getCompareGoldPredictedPSArg1 (predictedClausesArg1,arg1TokenIDsPredicted,dictByDocID,relation,relID,docID,arg1SentID,arg1WordList)
			#*****************************#
	   #get tokenIDs for connective, arg1, arg2
	   #(connectiveTokenIDs, arg1TokenIDs, arg2TokenIDs)=getTokenIDsList(relation)
	   if 'Connective' in relation and relation['Connective']['TokenList']!=[]:
	   #if relType=='Explicit':
	      connectiveTokenIDs=func.getTokenIDsList(relation,'Connective')
	      relation['Connective']['TokenList']=connectiveTokenIDs
	   arg1TokenIDs=func.getTokenIDsList(relation,'Arg1')
	   arg2TokenIDs=func.getTokenIDsList(relation,'Arg2')
	   relation['Arg1']['TokenList']=arg1TokenIDs
	   relation['Arg2']['TokenList']=arg2TokenIDs
	   if relType=='Implicit':
	   #if arg1Loc=='PS':
		relation['Arg1']['TokenList']=arg1TokenIDsPredicted
		relation['Arg1']['RawText']=' '.join(arg1WordList)
		
	return relations

def isClauseCons(clauseWordIDs,relID):
	for i in range(1,len(clauseWordIDs)):
		if clauseWordIDs[i]-clauseWordIDs[i-1]>1:
			print >>stderr, 'Non-consecutive clause', clauseWordIDs, 'relID', relID
			return
#sometimes a comma is omitted when arguments are non-consecutive	
def fixNonConsArguments(argWordIDs,dictByDocID,docID,sentID,relID):
	newIDs=[]
	argWordIDs.sort()
	if not argWordIDs:
		return []
	newIDs.append(argWordIDs[0])
	for i in range(1,len(argWordIDs)):
		if argWordIDs[i]-argWordIDs[i-1]==2:
			print >>stderr, 'Missing comma found', 'relID', relID
			j=argWordIDs[i]-1
			w=dictByDocID[docID][sentID][j]['word']
			#print >>stderr, 'w', w
			if w==',':
				newIDs.append(j)
		newIDs.append(argWordIDs[i])
	print >>stderr, argWordIDs
	print >>stderr, newIDs
	return newIDs
		
def getArg1PSWordIDs(relID,docID,arg1SentID,psArg1PredictionsDict,dictByDocID,sentID):
		if relID not in psArg1PredictionsDict:
			print >>stderr, 'Not found', relID
			return ([],[])
		clauseList=psArg1PredictionsDict[relID]
		clauseList.sort()
		for c in clauseList:
			isClauseCons(c[0],relID)
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
			#case of two missing punctuations (e.g. '' ,)
			if i and clause[0]-prevClause[-1]==3:
				print 1
				puncWordID=clause[0]-1
				punc=dictByDocID[docID][sentID][puncWordID]['word']
				print 'punc', punc
				wordList.append(punc)
				arg1WordIDs.append(puncWordID)
				puncWordID=clause[0]-2
				punc=dictByDocID[docID][sentID][puncWordID]['word']
                                wordList.append(punc)
                                arg1WordIDs.append(puncWordID)
                        for wordID in clause:
				#print >>stderr, wordID, clause, dictByDocID[docID][sentID]
                                w=dictByDocID[docID][sentID][wordID]['word']
                                wordList.append(w)
				arg1WordIDs.append(wordID)
		arg1WordIDs=fixNonConsArguments(arg1WordIDs,dictByDocID,docID,sentID,relID)
		wordList=[]
		for i in dictByDocID[docID][sentID]:
			w=dictByDocID[docID][sentID][i]['word']
			if i in arg1WordIDs:
				wordList.append(w)
		#arg1 is complete sentence
                if len(wordList)==len(dictByDocID[docID][sentID])-1:
                        wordList=[]
			arg1WordIDs=[]
                        for j in dictByDocID[docID][sentID]:
                                wordList.append(dictByDocID[docID][sentID][j]['word'])
				arg1WordIDs.append(j)
                        wordList=wordList[:-1]
			arg1WordIDs=arg1WordIDs[:-1]
		return (arg1WordIDs, wordList)

#each clause is a pair, where the first element is a list of wordIDs of that clauses
def getCompareGoldPredictedPSArg1(clauseList,arg1TokenIDsPredicted,dictByDocID,relation,relID,docID,sentID,arg1WordList):
        	goldWords=[]
		goldArgTokenIDs=[]
		goldArgWordIDs=[]
		for i in relation['Arg1']['TokenList']:
			#print >>stderr, i
			goldArgWordIDs.append(i[4])
			goldArgTokenIDs.append(i[2])
        	for i in goldArgWordIDs:
                	w=dictByDocID[docID][sentID][i]['word']
                	goldWords.append(w)
                wordList=[]
		for i in dictByDocID[docID][sentID]:
			if dictByDocID[docID][sentID][i]['tokenID'] in arg1TokenIDsPredicted:
				w=dictByDocID[docID][sentID][i]['word']
				wordList.append(w)
                sentWords=dictByDocID[docID][sentID]
                if wordList==goldWords:
                        print '***Found match***', len(clauseList), 'Number of words in gold', len(goldWords), 'predicted',len(wordList), 'docID', docID, 'relID', relID

        	else:
                	print '***Match not found***', 'Number of gold words', len(goldWords), 'Predicted words', len(wordList), 'docID', docID, 'relID', relID, 'diff',  len(goldWords)-len(wordList), 'end'
		#print 'Clauses', clauseList, len(clauseList)
		print '*Sentence*', 
		for i in dictByDocID[docID][sentID]:
			print dictByDocID[docID][sentID][i]['word'],
		print
		print '*Gold Arg1*', ' '.join(goldWords)
                print '*Word list*', ' '.join(wordList)


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
