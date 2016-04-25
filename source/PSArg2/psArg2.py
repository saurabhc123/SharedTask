#!/usr/bin/python
from sys import argv,exit,stderr
import json
import codecs
import func 

if len(argv)<4:
	print """
	./psArg1.py <relation.json> <parses.json> <writeF>
	[resources/verbList.txt]
	"""
	exit()

relationsFile=argv[1]
parsesFile=argv[2]
relationsF=codecs.open(relationsFile, encoding='utf8')
#relationsF=open(relationsFile)
parsesF=codecs.open(parsesFile, encoding='utf8')
#parsesF=open(parsesFile)
outF=open(argv[3],'w')
parseDict=json.load(parsesF)
relations = [json.loads(x) for x in relationsF]

verbListF=open("resources/verbList.txt",'r')
verbList={}
for l in verbListF:
	terms=l.split()
	freq=int(terms[0])
	if freq>=5:
		verbList[terms[1]]=1



def makeDataForArg2PSExplicit(dictByDocID,dictByTokenID,parseDict,relationDict,verbList,relations,outF):
   for relation in relations:
	sense=relation['Sense'] #this is a list since some examples have multiple senses
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
	   #print >>stderr, 'arg1Loc', arg1Loc, relID
	   if arg1Loc=='PS':
	      #split sentence into clauses
	      clausesArg2= func._ps_arg2_clauses(parseDict, relation, 'Arg2')
	      print  'clausesArg2',len(clausesArg2), relID
	      if len(clausesArg2)==0:
			print 'Empty clauses', relID
	      parse_tree = parseDict[docID]["sentences"][arg2SentID]["parsetree"].strip()
	      for clause in clausesArg2:
		print '*Clause*'
		for wID in clause[0]:
			print dictByDocID[docID][arg2SentID][wID]['word'],
		print
	      #goldArg1IDs=[]
	      #goldArg2IDs=[]
	      arg2WordIDList=func.getWordIDsList(relation,'Arg2')
	      connWordIDList=func.getWordIDsList(relation,'Connective')
	      #check if Arg2 is the same as the rest of the sentence following the connective
	      #(tokenIDsAfterConn, wordIDsAfterConn)=func.getTokenIDsAfterConnective(relation,dictByDocID,docID)
	      #(wordIDsAfterConn, tokenIDsAfterConn)=func.removePuncArg2(wordIDsAfterConn, tokenIDsAfterConn,dictByDocID, docID,arg2SentID)
	      (tokenIDsAfterConn, wordIDsAfterConn)=func.getBaselinePSArg2(relation,dictByDocID, docID)
	      if arg2WordIDList==wordIDsAfterConn:
	      #if len(dictByDocID[docID][arg1SentID])==len(goldArg1IDs)+1:
                        print '***Baseline: Same as sentence without connective***'
              else:
                        print '***Different from sentence without connective***'
	      print '***Connective***',
	      printWords(dictByDocID,docID,arg2SentID,connWordIDList)
	      print '*Sentence Arg2*', 'Sense', sense
	      for i in dictByDocID[docID][arg2SentID]:
			#print dictByDocID[docID][arg1SentID][i]['tokenID'],dictByDocID[docID][arg1SentID][i]['word'],
			print dictByDocID[docID][arg2SentID][i]['word'],
	      print
	      print "***Gold argument 2***", docID, 'relID', relID
	      printWords(dictByDocID,docID,arg2SentID,arg2WordIDList)

	      print '***Baseline argument 2***', docID, 'relID', relID
	      printWords(dictByDocID,docID,arg2SentID,wordIDsAfterConn)
	      
	      for clauseIndex in range(len(clausesArg2)):
		 clause=clausesArg2[clauseIndex][0]
                 features=getFeaturesExplicitPSArg2(dictByDocID,relation,docID,arg2SentID,clausesArg2,verbList,clauseIndex,parseDict)
                 label=getClauseLabelPSArg1(clausesArg2,clauseIndex,arg2WordIDList)
		 print '***Clause***', 'label', label, 'clauseIndex', clauseIndex
		 printWords(dictByDocID,docID,arg2SentID,clause)
		 clauseWordIDsStr=''
		 for i in clausesArg2[clauseIndex][0]:
			clauseWordIDsStr+='_'+str(i)
	         exID='docID-'+docID+':sentID-'+str(arg2SentID)+':clauseWordIDs-'+clauseWordIDsStr+':relID-'+str(relID)
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

def getClauseIDBeforeConn(listOfClauses,connWordIDs,wordBeforeConn,relation):
	print >>stderr, 'connWordIDs', connWordIDs
	for i in range(len(listOfClauses)):
		clause=listOfClauses[i][0]
		print >>stderr, 'clause', clause[-1]
		if clause[-1]+1 in connWordIDs:
			return i
		elif clause[-1]+2 in connWordIDs and wordBeforeConn==',':
			return i
	print >>stderr, 'ClauseIDBeforeConn', 'relID', relation['ID']
	return 'NA'

def getClauseIDAfterConn(listOfClauses,connWordIDs,wordAfterConn):
	#print >>stderr, 'connWordIDs', connWordIDs
        for i in range(len(listOfClauses)):
                clause=listOfClauses[i][0]
	#	print >>stderr, 'clause', clause[0]
                if clause[0]-1 in connWordIDs:
                        return i
                elif clause[0]-2 in connWordIDs and wordAfterConn==',':
                        return i
	#print >>stderr, 'ClauseIDAfterConn', 'NA'
	return 'NA'


def getMoreFeaturesExplicitPSArg2(dictDyDocID,relation,docID,sentID,listOfClauses,verbList, clauseIndex,parseDict):
	features=[]
	connWordIDs=[]
	for i in relation['Connective']['TokenList']:
		connWordIDs.append(i[4])
	clauseWordIDs=listOfClauses[clauseIndex][0]
	isClauseBeforeConn='0'
	if clauseWordIDs and clauseWordIDs[-1]+1 in connWordIDs:
		isClauseBeforeConn='1'
	isClauseAfterConn='0'
	wordBeforeConn=wordAfterConn='NA'
	if connWordIDs[0]-1>=0:
		wordBeforeConn=dictDyDocID[docID][sentID][connWordIDs[0]-1]['word']
	if connWordIDs[-1]+1<len(dictDyDocID[docID][sentID]):
		wordAfterConn=dictDyDocID[docID][sentID][connWordIDs[-1]+1]['word']
	isConnBeforeClause=isConnAfterClause='0'
	#check if clause is immediately before or after connective
	if clauseWordIDs[0]-1 in connWordIDs:
		isConnBeforeClause='1'
	elif clauseWordIDs[0]-2 in connWordIDs and wordBeforeConn==',':
		isConnBeforeClause='1'
	if clauseWordIDs[-1]+1 in connWordIDs:
		isConnAfterClause='1'
	elif clauseWordIDs[-1]+2 in connWordIDs and wordAfterConn==',':
		isConnAfterClause='1'
	features.append('isConnBeforeClause:'+isConnBeforeClause)
	features.append('isConnAfterClause:'+isConnAfterClause)
	dist='NA'
	clauseIDBeforeConn=getClauseIDBeforeConn(listOfClauses,connWordIDs,wordBeforeConn,relation)
	clauseIDAfterConn=getClauseIDAfterConn(listOfClauses,connWordIDs,wordAfterConn)
	if clauseIDAfterConn!='NA':
	 if clauseIndex<clauseIDAfterConn:
		#print >>stderr, clauseIDAfterConn
		dist=clauseIndex-clauseIDAfterConn
	 else:
		dist=clauseIndex-clauseIDAfterConn+1
	print >>stderr, 'Distance',
	if dist=='NA':
		print 'Distance not found', 'clauseIDAfterConn', clauseIDAfterConn, 'clauseIndex', clauseIndex
	else:
		
		print 'Distance found', 'dist', dist, 'clauseIDAfterConn', clauseIDAfterConn, 'clauseIndex', clauseIndex
	features.append('dist:'+str(dist))
	return features
	
	
			
def getFeaturesExplicitPSArg2(dictDyDocID,relation,docID,sentID,listOfClauses,verbList, clauseIndex,parseDict):
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
   clausePos='NA'
   if clauseIndex==0:
	clausePos='Start'
   elif clauseIndex==len(listOfClauses)-1 and len(listOfClauses)>1:
	clausePos='End'
   else:
	clausePos='Mid'
   features.append('clausePosition:'+clausePos)
   connectiveWords=func.getConnectiveWords(relation, dictByDocID,docID)
   connectivePOSList=func.getConnectivePOS(relation, dictByDocID,docID)
   cString='_'.join(connectiveWords).lower()
   if connectiveWords==[]:
	cString='NA'
   cPOSString='_'.join( connectivePOSList).lower()
   if connectiveWords==[]:
	cPOSString='NA'
   features.append('cString:'+cString)
   features.append('cPOSString:'+cPOSString)
   features.append('cStringClausePosition:'+cString+'-'+clausePos)
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
   connWordIDs=func.getConnectiveWordIDs(relation)
   connPathToRoot=func.get_conn_to_root_path(parseDict,docID,sentID,connWordIDs)
   connCompressedPathToRoot=func.get_conn_to_root_compressed_path(parseDict,docID,sentID,connWordIDs)
   #cParentToRoot=func.get_CParent_to_root_path_node_names(parseDict,docID,sentID,connWordIDs)
   connWordsAndContext=func.get_conn_connCtx(parseDict,docID,sentID,connWordIDs,connectiveWords)
   productionRules=func.get_curr_production_rule(parseDict,docID,sentID,connWordIDs,clauseWordIDs)
   shortRules2='-'.join(func.modifyProductionRules2(productionRules)).replace(' ','_').lower()
   shortRules3='-'.join(func.modifyProductionRules3(productionRules)).replace(' ','_').lower()
   productions='-'.join(productionRules).replace(' ','_')
   print >>stderr, 'productionRules', productionRules
   print >>stderr, 'shortRules2', shortRules2
   print >>stderr, 'shortRules3', shortRules3
   #print >>stderr, 'pathToRoot', connPathToRoot
   #print >>stderr, 'compressedPathToRoot', connCompressedPathToRoot
   #print >>stderr, 'cParentToRoot', cParentToRoot
   #print >>stderr, 'connWordsAndContext', connWordsAndContext
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
   #path feature
   features.append('connPathToRoot:'+connPathToRoot)
   features.append('connCompressedPathToRoot:'+connCompressedPathToRoot)
   features.append('connWordsAndContext:'+connWordsAndContext)
   features.append('productionRules:'+productions)
   features.append('shortRules2:'+shortRules2)
   features.append('shortRules3:'+shortRules3)
   #verb features
   verbFeatures=func.getVerbFeatures(dictByDocID,docID,sentID,clauseWordIDs,verbList)
   features=features+verbFeatures
   features=features+getMoreFeaturesExplicitPSArg2(dictDyDocID,relation,docID,sentID,listOfClauses,verbList, clauseIndex,parseDict)
   return features

	
dictByDocID=func.makeDictByDocID(parseDict)
dictByTokenID=func.makeDictByTokenID(dictByDocID)
relationDict=func.makeRelationDict(relations)
makeDataForArg2PSExplicit(dictByDocID,dictByTokenID,parseDict,relationDict,verbList,relations,outF)
