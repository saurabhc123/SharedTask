#!/usr/bin/python
from sys import argv,exit,stderr
import os
import json
import codecs
import func 
#print >>stderr, argv[0]
if len(argv)<4:
	print """
	./psArg1.py <relation.json> <parses.json> <writeF>
	[resources/verbList.txt]
	"""
	exit()
terms=argv[0].split('/')
curDir='/'.join(terms[:-1])
relationsFile=argv[1]
parsesFile=argv[2]
relationsF=codecs.open(relationsFile, encoding='utf8')
#relationsF=open(relationsFile)
parsesF=codecs.open(parsesFile, encoding='utf8')
#parsesF=open(parsesFile)
outF=open(argv[3],'w')
parseDict=json.load(parsesF)
relations = [json.loads(x) for x in relationsF]

#verbListF=open("resources/verbList.txt",'r')
verbListF=open(curDir+"/resources/verbList.txt",'r')
verbList={}
for l in verbListF:
	terms=l.split()
	freq=int(terms[0])
	if freq>=5:
		verbList[terms[1]]=1


#clausesArg1 is a list of pairs
#each clause is a pair, where the first element is a list of wordIDs of that clauses
def getUpperBoundClauseSplittingPSArg1(clausesArg1,dictByDocID,relationDict,relID,docID,sentID,goldArgWordIDs):
	goldWords=[]
	for i in goldArgWordIDs:
		w=dictByDocID[docID][sentID][i]['word']
		goldWords.append(w)
	allClauseCombinations=getAllClauseCombinations(clausesArg1,dictByDocID,relationDict,relID,docID)
	flag=0
	for clauseList in allClauseCombinations:
		#if a combination contains multiple clauses; if clauses are consecutive, need to add
		#punctuation if it was deleted; otherwise do not add punctuation
		wordList=[]
		sentWords=dictByDocID[docID][sentID]
		for i in range(len(clauseList)):
			clause=clauseList[i]
			#add missing punctuation that has been removed at clause splitting
			#if i:
			#	print 'prev', clauseList[i-1][-1], clause[0]
			if i and clause[0]-clauseList[i-1][-1]==2:
				#print 'punc'
				puncWordID=clause[0]-1
				punc=dictByDocID[docID][sentID][puncWordID]['word']
				wordList.append(punc)
			for wordID in clause:
				w=dictByDocID[docID][sentID][wordID]['word']
				wordList.append(w)
		if len(wordList)==len(dictByDocID[docID][sentID])-1:
			wordList=[]
			for j in dictByDocID[docID][sentID]:
				wordList.append(dictByDocID[docID][sentID][j]['word'])
			wordList=wordList[:-1]
		print '*Word list*', ' '.join(wordList)
		if wordList==goldWords:
			print '***Found match***', len(clauseList)
			flag=1
			break

	if not flag:
		print '***Match not found***'
def getAllClauseCombinations(clausesArg1,dictByDocID,relationDict,relID,docID):
   totalClauses=len(clausesArg1)
   #base case
   if totalClauses==0:
	return []
   else:
	result=[]
	#fix one clause
   	for i in range (totalClauses):
		currentClause=clausesArg1[i][0]
		rest=clausesArg1[i+1:]
		combinations=getAllClauseCombinations(rest,dictByDocID,relationDict,relID,docID)
		result.append([currentClause])
		result=result+combinations
		for c in combinations:
			result.append([currentClause]+c)
	newResult=[]
	for r in result:
		if r not in newResult:
			newResult.append(r)
	result=newResult
	return result
		

def makeDataForArg1PSExplicit(dictByDocID,dictByTokenID,parseDict,relationDict,verbList,relations,outF):
   for relation in relations:
#	sense=relation['Sense'] #this is a list since some examples have multiple senses
	relType=relation['Type'] #Explicit, Implicit,Entrel,AltLex
	docID=relation['DocID']
	relID=relation['ID']
	#get only explicit relations
	if relType=='Explicit':
	   #print >>stderr, relType, sense
	  #get tokenIDs for Arg1 and Arg2
	   arg1TokenList=func.getTokenIDsList(relation,'Arg1')
	   arg2TokenList=func.getTokenIDsList(relation,'Arg2')
	   #take sentID of first token of arg1 as sentID of arg1
	   arg1SentID=relation['Arg1']['TokenList'][0][3]
	   arg2SentID=relation['Arg2']['TokenList'][0][3]
	   arg1Loc=func.getArg1Location(relation)
	   print >>stderr, 'arg1Loc', arg1Loc
	   if arg1Loc=='PS':
	      #split sentence into clauses
	      clausesArg1= func._ps_arg1_clauses(parseDict, relation, 'Arg1')
	      print  'clausesArg1',len(clausesArg1)
	      parse_tree = parseDict[docID]["sentences"][arg1SentID]["parsetree"].strip()
	      for clause in clausesArg1:
		print '*Clause*'
		for wID in clause[0]:
			print dictByDocID[docID][arg1SentID][wID]['word'],
		print
	      goldArg1IDs=[]
	      goldArg2IDs=[]
	      #print >>stderr, 'TokenIDs', arg1TokenList
	      for i in arg1TokenList:
			#print >>stderr, i
			goldArg1IDs.append(dictByTokenID[docID][i]['wordID'])
	      clauseCombinations=getUpperBoundClauseSplittingPSArg1(clausesArg1,dictByDocID,relationDict,relID,docID,arg1SentID,goldArg1IDs)
	      for i in arg2TokenList:
		goldArg2IDs.append(dictByTokenID[docID][i]['wordID'])

	      #check if Arg1 is the same as the entire sentence
	      if len(dictByDocID[docID][arg1SentID])==len(goldArg1IDs)+1:
                        print '***Same as sentence***'
              else:
                        print '***Different from sentence***'

	      print '*Sentence Arg1*'#, 'Sense', sense
	      for i in dictByDocID[docID][arg1SentID]:
			#print dictByDocID[docID][arg1SentID][i]['tokenID'],dictByDocID[docID][arg1SentID][i]['word'],
			print dictByDocID[docID][arg1SentID][i]['word'],
	      print
	      print "***Gold argument 1***", docID, 'relID', relID
	      printWords(dictByDocID,docID,arg1SentID,goldArg1IDs)
	      
	      for clauseIndex in range(len(clausesArg1)):
		 clause=clausesArg1[clauseIndex][0]
                 features=getFeaturesExplicitPSArg1(dictByDocID,relation,docID,arg1SentID,relID,clausesArg1,verbList,clauseIndex)
                 label=getClauseLabelPSArg1(clausesArg1,clauseIndex,goldArg1IDs)
		 print '***Clause***', label, 
		 printWords(dictByDocID,docID,arg1SentID,clause)
		 clauseWordIDsStr=''
		 for i in clausesArg1[clauseIndex][0]:
			clauseWordIDsStr+='_'+str(i)
	         exID='docID-'+docID+':sentID-'+str(arg1SentID)+':clauseWordIDs-'+clauseWordIDsStr+':relID-'+str(relID)
	     # print '_'.join(tokenList), senseLabel,'startend',exID,
	         outF.write("None %s startend %s " % (label, exID))
	         for feat in features:
		    pair=feat.split(':')
		    newFeat=feat
		    if 'NA' in pair[1]:
			newFeat=pair[0]+':NA'
	#	print feat,
	    	    outF.write("%s " % (newFeat))
	         outF.write("\n")
	      print '**************************************************'	    
	  #    print


def printWords(dictByDocID,docID,sentID,wordIDs):
#	print 'Word Ids', wordIDs
	words=[]
	for i in dictByDocID[docID][sentID]:
		if i in wordIDs:
			words.append(dictByDocID[docID][sentID][i]['word'])
	print ' '.join(words)


def getClauseLabelPSArg1(clausesArg1,clauseIndex,goldArgWordIDs):
        clauseWordIDs=clausesArg1[clauseIndex][0]
	return isClauseInGold(clauseWordIDs,goldArgWordIDs)
#check whether clause is part of gold argument
def isClauseInGold(clauseWordIDs,goldArgWordIDs):
	flag=1
	for wordID in clauseWordIDs:
		if wordID not in goldArgWordIDs:
			return 0
	return 1
			
def getFeaturesExplicitPSArg1(dictDyDocID,relation,docID,sentID,relID,listOfClauses,verbList, clauseIndex):
   clauseWordIDs=listOfClauses[clauseIndex][0]
   
   #print >>stderr, clauseWordIDs
   prevClauseWords=[]
   prevClauseWordIDs=[]
   nextClauseWordIDs=[]
   if clauseIndex:
	prevClauseWordIDs=listOfClauses[clauseIndex-1][0]
   if clauseIndex<len(listOfClauses)-1:
	nextClauseWordIDs=listOfClauses[clauseIndex+1][0]

   sentWords=func.getWordListFromSentence(dictByDocID,docID,sentID)
   clauseWords=func.getClauseWordsFromSentence(dictByDocID,docID,sentID,clauseWordIDs)
   prevClauseWords=func.getClauseWordsFromSentence(dictByDocID,docID,sentID,prevClauseWordIDs)
   nextClauseWords=func.getClauseWordsFromSentence(dictByDocID,docID,sentID,nextClauseWordIDs)
   features=[]
   isFirst=isLast=0
   if clauseIndex==0: #start of sentence
	isFirst=1
   if clauseIndex==len(listOfClauses)-1:
	isLast=1
   sameAsSent=0
   if len(clauseWords)==len(sentWords)-1:
	sameAsSent=1
   features.append('isLast:'+str(isLast))
   features.append('isFirst:'+str(isFirst))
   features.append('sameAsSent:'+str(sameAsSent))
   connectiveWords=func.getConnectiveWords(relation,dictByDocID,docID)
   cString='_'.join(connectiveWords).lower()
   if connectiveWords==[]:
	cString='NA'
   features.append('cString:'+cString)
   #add lexical features
   curFirstWord=curLastWord=curFirstSecond=prevLast=nextFirst=curFirstPOS=curLastPOS=curFirstSecondPOS=prevLastPOS=nextFirstPOS='NA'
   if clauseWords:
	curFirstWord=clauseWords[0].lower()
 	#print >>stderr, dictByDocID[docID][sentID][clauseWordIDs[0]].keys()
        curFirstPOS=dictByDocID[docID][sentID][clauseWordIDs[0]]['pos']
   if len(clauseWords)>1:
	curLastWord=clauseWords[-1].lower()
 	curLastPOS=dictByDocID[docID][sentID][clauseWordIDs[-1]]['pos']
   	curFirstSecond='_'.join(clauseWords[:2]).lower()
        curFirstSecondPOS=curFirstPOS+'_'+dictByDocID[docID][sentID][clauseWordIDs[1]]['pos']
   if prevClauseWords:
	prevLast=prevClauseWords[-1].lower()
	prevLastPOS=dictByDocID[docID][sentID][prevClauseWordIDs[-1]]['pos']
   if nextClauseWords:
	nextFirst=nextClauseWords[0].lower()
	nextFirstPOS=dictByDocID[docID][sentID][nextClauseWordIDs[0]]['pos']
   prevLastCurFirst=prevLast+'_'+curFirstWord	
   curLastNextFirst=curLastWord+'_'+nextFirst
   commaBefore='NA'
   commaAfter='NA'
   #print >>stderr, 'Getting commas', 'docID', docID, 'sentID', sentID
   if prevClauseWordIDs and clauseWordIDs:
	prevWordID=prevClauseWordIDs[-1]
	curFirstID=clauseWordIDs[0]
	curLastID=clauseWordIDs[-1]
	if curFirstID-prevWordID==2:
		commaBefore=dictByDocID[docID][sentID][prevWordID+1]['word']
   if nextClauseWordIDs:
	nextFirstID=nextClauseWordIDs[0]
	curLastID=clauseWordIDs[-1]
	if nextFirstID-curLastID==2:
		#print >>stderr, 'Comma found', docID, sentID
		commaAfter=dictByDocID[docID][sentID][curLastID+1]['word']
   (allVerbs,tags)=func.getVerbsFromClause(dictByDocID,docID,sentID,clauseWordIDs)
   verbs=[]
   for v in allVerbs:
	if v in verbList:
		verbs.append(v)
   if len(verbs)<len(allVerbs):
      print 'Verbs', verbs, len(allVerbs), len(verbs)
   v1=v2=v3='NA'
   if len(verbs):
	v1=verbs[0]
   if len(verbs)>1:
	v2=verbs[1]
   if len(verbs)>2:
	v3=verbs[2]
   features.append('curFirstWord:'+curFirstWord)
   features.append('curLastWord:'+curLastWord)
   features.append('curFirstSecond:'+curFirstSecond)
   features.append('prevLast:'+prevLast)
   features.append('nextFirst:'+nextFirst)
   features.append('prevLastCurFirst:'+prevLastCurFirst)
   features.append('curLastNextFirst:'+curLastNextFirst)
   features.append('commaBefore:'+commaBefore)
   features.append('commaAfter:'+commaAfter)
#   curFirstPOS=curLastPOS=curFirstSecondPOS=prevLastPOS=nextFirstPOS
   features.append('curFirstPOS:'+curFirstPOS)
   features.append('curLastPOS:'+curLastPOS)
   features.append('curFirstSecondPOS:'+curFirstSecondPOS)
   features.append('prevLastPOS:'+prevLastPOS)
   features.append('nextFirstPOS:'+nextFirstPOS)
   features.append('prevLastAndComma:'+prevLast+'_'+commaBefore)
   features.append('nextFirstAndComma:'+nextFirst+'_'+commaAfter)
   features.append('commaAndcurFirstWord:'+commaBefore+'_'+curFirstWord)
   features.append('curLastWordAndComma:'+curLastWord+'_'+commaAfter)
   features.append('commaAndcurFirstPOS:'+commaBefore+'_'+curFirstPOS)
   features.append('curLastPOSAndComma:'+curLastPOS+'_'+commaAfter)
   features.append('verb1:'+v1)
   features.append('verb2:'+v2)
   features.append('verb3:'+v3)
   return features

   
	
	
	
dictByDocID=func.makeDictByDocID(parseDict)
#func.getAllVerbsFromData(dictByDocID)
#exit()
dictByTokenID=func.makeDictByTokenID(dictByDocID)
#for i in dictByDocID:
#	print >>stderr, i, dictByDocID[i].keys()
#print >>stderr, dictByDocID.keys()
#print >>stderr, len(relations)
#exit()
relationDict=func.makeRelationDict(relations)
makeDataForArg1PSExplicit(dictByDocID,dictByTokenID,parseDict,relationDict,verbList,relations,outF)
#makeDataForImplicitSenseGold(dictByDocID,relationDict,outF) #will use gold arguments for implicit relations
#exit()
