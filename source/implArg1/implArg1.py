#!/usr/bin/python
from sys import argv,exit,stderr
import json
import codecs
import func 

if len(argv)<4:
	print """
	./implArg1.py <relation.json> <parses.json> <writeF>
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

verbListF=open("implArg1/resources/verbList.txt",'r')
verbList={}
for l in verbListF:
	terms=l.split()
	freq=int(terms[0])
	if freq>=5:
		verbList[terms[1]]=1


def makeDataForArg1Implicit(dictByDocID,dictByTokenID,parseDict,relationDict,verbList,relations,outF):
   for relation in relations:
#	sense=relation['Sense'] #this is a list since some examples have multiple senses
	relType=relation['Type'] #Explicit, Implicit,Entrel,AltLex
	docID=relation['DocID']
	relID=relation['ID']
	#get only explicit relations
	if relType=='Implicit':
	   arg1TokenList=func.getTokenIDsList(relation,'Arg1')
	   arg2TokenList=func.getTokenIDsList(relation,'Arg2')
	   #take sentID of first token of arg1 as sentID of arg1
	   if len(arg1TokenList) > 0:
                arg1SentID=relation['Arg1']['TokenList'][0][3]
           else:
                arg1SentenceNumber = -1
	   
           arg2SentID=relation['Arg2']['TokenList'][0][3]
	   if 1 and (arg1SentID > -1) :
	      #split sentence into clauses
	      clausesArg1= func._ps_arg1_clauses(parseDict, relation, 'Arg1')
	      print  'clausesArg1',len(clausesArg1), relID
	      if len(clausesArg1)==0:
			print 'Empty clauses'
	      parse_tree = parseDict[docID]["sentences"][arg1SentID]["parsetree"].strip()
	      for clause in clausesArg1:
		print '*Clause*'
		for wID in clause[0]:
			print dictByDocID[docID][arg1SentID][wID]['word'],
		print
	      goldArg1IDs=[]
	      goldArg2IDs=[]
	      for i in arg1TokenList:
			goldArg1IDs.append(dictByTokenID[docID][i]['wordID'])
	      for i in arg2TokenList:
		goldArg2IDs.append(dictByTokenID[docID][i]['wordID'])
	      totWords=len(dictByDocID[docID][arg1SentID])
	      #check if Arg1 is the same as the entire sentence
	      if len(dictByDocID[docID][arg1SentID])==len(goldArg1IDs)+1:
                        print '***Same as sentence***'
	      elif dictByDocID[docID][arg1SentID][0]['word']=='``' and len(dictByDocID[docID][arg1SentID])==len(goldArg1IDs)+2:
			print '***Same as sentence***'
	      elif totWords>1 and dictByDocID[docID][arg1SentID][0]['word']=='``' and dictByDocID[docID][arg1SentID][totWords-1]['word']=="''" and len(dictByDocID[docID][arg1SentID])==len(goldArg1IDs)+3:
			print '***Same as sentence***'
              else:
                        print '***Different from sentence***', relID

	      print '*Sentence Arg1*'#, 'Sense', sense
	      for i in dictByDocID[docID][arg1SentID]:
			#print dictByDocID[docID][arg1SentID][i]['tokenID'],dictByDocID[docID][arg1SentID][i]['word'],
			print dictByDocID[docID][arg1SentID][i]['word'],
	      print
	      print "***Gold argument 1***", docID, 'relID', relID
	      printWords(dictByDocID,docID,arg1SentID,goldArg1IDs)
	      
	      for clauseIndex in range(len(clausesArg1)):
		 clause=clausesArg1[clauseIndex][0]
                 features=getFeaturesImplicitArg1(dictByDocID,relation,docID,arg1SentID,relID,clausesArg1,verbList,clauseIndex)
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

def printWords1(dictByDocID,docID,sentID,wordIDs):
#       print 'Word Ids', wordIDs
        words=[]
        for i in dictByDocID[docID][sentID]:
                if i in wordIDs:
                        words.append(dictByDocID[docID][sentID][i]['word'])
        print >>stderr, ' '.join(words)

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

def getSentIDsImplicit(dictByDocID,relations):
	arg1={}
	arg2={}
	arg1All={}
	arg2All={}
	sentTotal=0
	for relation in relations:
	   relType=relation['Type'] #Explicit, Implicit,Entrel,AltLex
           docID=relation['DocID']
           relID=relation['ID']
           #arg1TokenList=func.getTokenIDsList(relation,'Arg1')
           #arg2TokenList=func.getTokenIDsList(relation,'Arg2')
           #take sentID of first token of arg1 as sentID of arg1
           arg1SentID=docID+'-'+str(relation['Arg1']['TokenList'][0][3])
           arg2SentID=docID+'-'+str(relation['Arg2']['TokenList'][0][3])
	   if relType not in arg1:
		arg1[relType]={}
	   if relType not in arg2:
		arg2[relType]={}
	   arg1[relType][arg1SentID]=1
	   arg2[relType][arg2SentID]=1
	   if arg1SentID in arg1All or arg1SentID in arg2All:
		print >>stderr, 'Arg1 SentID exists', arg1SentID
	   if arg2SentID in arg2All or arg2SentID in arg1All:
		print >>stderr, 'Arg2 SentID exists', arg2SentID
	   arg1All[arg1SentID]=1
	   arg2All[arg2SentID]=1
	#check which sentences are not an argument
	for docID in dictByDocID:
		prevSentID='None'
		for i in dictByDocID[docID]:
			sentTotal+=1
			sentID=docID+'-'+str(i)
			if prevSentID!='None' and prevSentID not in arg1All and prevSentID not in arg2All:
			   if sentID not in arg1All and sentID not in arg2All:
				print >>stderr, 'SentID not an argument', sentID
			prevSentID=sentID
	print >>stderr, 'Sents total', sentTotal
	print >>stderr, 'arg1All', len(arg1All)
	print >>stderr, 'arg2All', len(arg2All)
	   
	   
			
def getFeaturesImplicitArg1(dictDyDocID,relation,docID,sentID,relID,listOfClauses,verbList, clauseIndex):
   clauseWordIDs=listOfClauses[clauseIndex][0]
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
   elif len(clauseWords)==len(sentWords)-2 and sentWords[0]=='``':
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
   (r1 , r2, r3, r1r2, r1r2r3,filteredRules)= getProductionRuleFeatures(parseDict,docID, sentID,clauseWordIDs,relID)
   (r1P , r2P, r3P, r1r2P, r1r2r3P,filteredRulesPrev)= getProductionRuleFeatures(parseDict,docID, sentID,prevClauseWordIDs,relID)
   (r1N , r2N, r3N, r1r2N, r1r2r3N,filteredRulesNext)= getProductionRuleFeatures(parseDict,docID, sentID,nextClauseWordIDs,relID)
   totRules=len(filteredRules)   
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
   features.append('r1:'+r1)
   features.append('r2:'+r2)
   features.append('r3:'+r3)
   features.append('r1r2:'+r1r2)
   features.append('r1r2r3:'+r1r2r3)
   features.append('r1PAndr1:'+r1P+'_'+r1)
   features.append('r1PAndr1r2:'+r1P+'_'+r1r2)
   features.append('r1Andr1N:'+r1+'_'+r1N)
   features.append('r1r2Andr1N:'+r1r2+'_'+r1N)
   features.append('r1r2PAndr1r2:'+r1r2P+'_'+r1r2)
   features.append('r1r2Andr1r2N:'+r1r2+'_'+r1N)
   features.append('totalRules:'+str(totRules))
   features.append('wordsInArg:'+str(len(clauseWordIDs)))
   features.append('verb1:'+v1)
   features.append('verb2:'+v2)
   features.append('verb3:'+v3)
   
   return features

def getProductionRuleFeatures(parseDict,docID, sentID,clauseWordIDs,relID):
   productionRules=func.get_curr_production_rules_for_clause(parseDict,docID,sentID,clauseWordIDs)
   #productionRules=func.filterProductionRules(productionRules)
   productions='-'.join(productionRules).replace(' ','_')
   print >>stderr, '***Clause***'
   printWords1(dictByDocID,docID,sentID,clauseWordIDs)
   print >>stderr, 'productionRules', relID
   for r in productionRules:
                print >>stderr, 'Production rule', r
   productionRules=func.filterProductionRules(productionRules)
   print >>stderr, '***Clause and filtered production rules***'
   printWords1(dictByDocID,docID,sentID,clauseWordIDs)
   print >>stderr, 'Filtered production rules', relID
   for r in productionRules:
        print >>stderr, 'Filtered production rule', r
   r1=r2=r3=r1r2=r1r2r3='NA'
   if len(productionRules):
        r1=productionRules[0].replace(' ','-')
   if len(productionRules)>1:
        r2=productionRules[1].replace(' ','-')
        r1r2=r1+'_'+r2
   if len(productionRules)>2:
        r3=productionRules[2].replace(' ','-')
        r1r2r3=r1+'_'+r2+'_'+r3
   return (r1,r2,r3,r1r2,r1r2r3,productionRules)
	
	
	
dictByDocID=func.makeDictByDocID(parseDict)
dictByTokenID=func.makeDictByTokenID(dictByDocID)
#getSentIDsImplicit(dictByDocID,relations)
#exit()
relationDict=func.makeRelationDict(relations)
makeDataForArg1Implicit(dictByDocID,dictByTokenID,parseDict,relationDict,verbList,relations,outF)
