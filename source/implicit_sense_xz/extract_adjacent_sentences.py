#!/usr/bin/python
import sys
import func
import codecs
import json
import os
from nltk.tokenize import sent_tokenize


# INPUT: Predicted relations.json, parses.json, raw documents directory
# OUTPUT: Adjacent sentences in relations.json format

# if len(argv)<5:
# 	print """
# 	./extract_adjacent_sentences.py <predictionsF> <parsesF> <documentDir> <writeF>	
# 	"""
# 	exit()

# predictionsF=argv[1]
# parsesF=argv[2]
# docDir = argv[3]
# writeF=open(argv[4],'w')

# relationsF = codecs.open(predictionsF, encoding='utf8')
# relations = [json.loads(x) for x in relationsF]
# parsesF=codecs.open(parsesF, encoding='utf8')
# parseDict=json.load(parsesF)
# dictByDocID=func.makeDictByDocID(parseDict)

def writeOutputFormat(relations,outF):
	for relation in relations:
		try:
			outF.write('%s\n' % json.dumps(relation))
		except:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			sys.stderr.write(exc_type + '\t' + fname + '\t' + exc_tb.tb_lineno)
			continue

def produceNonExplicitRelationCandidates(predictionsF, parsesF, docDir):
	relations = []	
	print("In function: produceNonExplicitRelationCandidates");
	
	#Read predicted relations.json
	print("Reading predicted relations.json");
	pdtb_file = codecs.open(predictionsF, encoding='utf8');
	predictions = [json.loads(x) for x in pdtb_file];
	print("Done");
	
	#Read parses.json
	print ("Reading parses.json");
	parse_file = codecs.open(parsesF, encoding='utf8')
	parses = json.load(parse_file)
	print ("Done");
	
	dictByDocID=func.makeDictByDocID(parses)
	
	nonMatchNum = 0
	exceptNum = 0
	for DocID in parses.keys():
		#print
		relationCount = 0
		senList = parses[DocID]['sentences']
		toCheckParagraph = False
		senLineDict = createSentenceLineDict(DocID, docDir)
		if len(senList) == len(senLineDict):
			toCheckParagraph = True
		else:
			nonMatchNum += 1
			#print "Doc [" + DocID + "]: Sentence count in parses.json <" + str(len(senList)) + "> does NOT match the count in raw file <" + str(len(senLineDict)) + ">"
		
		for sen1ID in range (0, len(senList)-1):
			try:
				sen2ID = sen1ID + 1
				#Extract a adjacent sentences pair
				sen1 = senList[sen1ID]
				sen2 = senList[sen2ID]
				
				#Check whether they are in different paragraphs
				if toCheckParagraph:				
					if not inSameParagraph(sen1ID, sen2ID, senLineDict):
						continue	
				
				#Check whether a sentence pair already has explicit relation
				if isExplicitRelation(sen1ID, sen2ID, DocID, predictions):
					continue
				
				#For valid sentence pairs, create a relation
				relation = {}
				
				#do DocID
				relation['DocID'] = DocID
				
				#do Arg1
				arg1 = extractArgFields(DocID, sen1, sen1ID, dictByDocID)
				if len(arg1['TokenList']) < 1:
					continue
				relation['Arg1'] = arg1
				
				#do Arg2
				arg2 = extractArgFields(DocID, sen2, sen2ID, dictByDocID)
				if len(arg2['TokenList']) < 1:
					continue
				relation['Arg2'] = arg2
				
				#Append relation
				relationCount += 1
				relations.append(relation)
			
			except:
				exceptNum += 1
				continue
		#print 'Create ' + str(relationCount) + ' non-explicit relations out of ' + str(len(senList)) + ' sentences from Doc [' + DocID + ']'
	
	print '\n' + str(len(relations)) + ' Non-Explicit relations created in total'
	print str(nonMatchNum) + '/' + str(len(parses)) + ' documents have inconsistent sentence counts in parses.json and raw files'
	
	#sys.stderr.write( str(exceptNum) + ' adjacent sentences omitted while ' + str(len(relations)) + ' candidate adjacent sentences produced')
	
	#add explicit relations
	for relation in predictions:
		relations.append(relation)
	print '\nExporting ' + str(len(relations)) + ' relations (both explicit and non-explicit) in total'
	
	return relations

# Create a dictionary where the key is sentence index while the value is its line number in the raw file 
def createSentenceLineDict(DocID, docDir):
	result = {}
	lineCount = 0
	senCount = 0
	with open(docDir + os.sep + DocID, 'r') as f:
		for line in f:
			content = line.strip()
			if lineCount > 0 and len(content) > 0:
				try:
					sent_tokenize_list = sent_tokenize(content)
				except:
					result[senCount] = lineCount
					senCount += 1
					lineCount += 1
					continue
				for sen in sent_tokenize_list:
					if len(sen) > 0:					
						result[senCount] = lineCount
						senCount += 1
			lineCount += 1
	return result


# Check whether the two sentences are in the same paragraph (line difference is just 1)
def inSameParagraph(sen1ID, sen2ID, senLineDict):
	if not (sen1ID in senLineDict and sen2ID in senLineDict):
		return False
	
	lineDiff = senLineDict[sen2ID] - senLineDict[sen1ID]
	if lineDiff > 1:
		return False
	else:
		return True


def isExplicitRelation(sen1ID, sen2ID, DocID, predictions):
	for relation in predictions:
		relType = relation['Type']
		if not relType == 'Explicit':
			continue
		relDocID = relation['DocID']
		if not DocID == relDocID:
			continue
		arg1SenID = relation['Arg1']['TokenList'][0][3]
		arg2SenID = relation['Arg2']['TokenList'][0][3]
		if sen1ID == arg1SenID and sen2ID == arg2SenID:
			return True
	return False

def extractArgFields(DocID, sen, senID, dictByDocID):
	arg = {}
	
	tokenList=[]
	for t in range(0, len(sen['words'])-1):
		try:
			tokenID = dictByDocID[DocID][senID][t]['tokenID']
			#character offset begin, character offset end, token offset within the document, sentence offset, token offset within the sentence
			elementTokenList=[-1,-1,tokenID,senID,t]
			tokenList.append(elementTokenList)
		except:
			continue
	arg['TokenList']=tokenList
	return arg

# Wrapper function
def produceRelationsFile(predictionsF, parsesF, docDir, writeF):
	relations = produceNonExplicitRelationCandidates(predictionsF, parsesF, docDir)
	outputF=open(writeF,'w')
	writeOutputFormat(relations, outputF)
	outputF.close()
	

# relations = produceNonExplicitRelationCandidates(predictionsF, parsesF, docDir)
# writeOutputFormat(relations, writeF)
