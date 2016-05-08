#!/usr/bin/python
from sys import argv, exit, stderr
import json
import codecs
import func
import operator

FEATURE_NUM = 300
if len(argv) < 4:
    print """
	./implArg1.py <relation.json> <parses.json> <writeF>
	[resources/verbList.txt]
	"""
    exit()

relationsFile = argv[1]
parsesFile = argv[2]
relationsF = codecs.open(relationsFile, encoding='utf8')
# relationsF=open(relationsFile)
parsesF = codecs.open(parsesFile, encoding='utf8')
# parsesF=open(parsesFile)
outF = open(argv[3], 'w')
parseDict = json.load(parsesF)
relations = [json.loads(x) for x in relationsF]

verbListF = open("resources/verbList.txt", 'r')
verbList = {}
for l in verbListF:
    terms = l.split()
    freq = int(terms[0])
    if freq >= 5:
        verbList[terms[1]] = 1
prodRulesTrainF = codecs.open("prodRules.train", encoding='utf8')
prodRulesTrain = [json.loads(x) for x in prodRulesTrainF]
prodRulesDict = {}
prodRulesTrain.sort()
prodRulesTrain.reverse()
tot = 0
for i in prodRulesTrain:
    tot += 1
#     if tot > 100:
#         break
    prodRulesDict[i[0]] = i[1]


def makeDataForSenseImplicit(dictByDocID, dictByTokenID, parseDict, relationDict, verbList, relations, prodRulesDict, outF):
    cutoff = 5
    curRel = 0
    dataset = []
    for relation in relations:
        if curRel % 1000 == 0:
            print >>stderr, 'Processed relation ' + str(curRel) + '/' + str(len(relations))
        curRel += 1
        # this is a list since some examples have multiple senses
        sense = relation['Sense']
        relType = relation['Type']  # Explicit, Implicit,Entrel,AltLex
        docID = relation['DocID']
        relID = relation['ID']

#        sense=relation['Sense']
        # get only implicit relations
        if relType != 'Explicit':
            # arg1TokenList = func.getTokenIDsList(relation, 'Arg1')
            # arg2TokenList = func.getTokenIDsList(relation, 'Arg2')
            # take sentID of first token of arg1 as sentID of arg1
            arg1SentID = relation['Arg1']['TokenList'][0][3]
            arg2SentID = relation['Arg2']['TokenList'][0][3]
            arg1SentIDs = func.getArgSentIDs(relation, 'Arg1')
            arg2SentIDs = func.getArgSentIDs(relation, 'Arg2')
            if len(arg1SentIDs) != 1 or len(arg2SentIDs) != 1:
                print >>stderr, 'Multi-sentential arguments', relID
            # exclude arguments that span multiple sentences
            if len(arg1SentIDs) == 1 and len(arg2SentIDs) == 1:
                # parse_tree = parseDict[docID]["sentences"][
                #   arg1SentID]["parsetree"].strip()
                clausesArg1 = func.getClausesForArgument(
                    relation, 'Arg1', dictByDocID, docID, arg1SentID, parseDict)
                clausesArg2 = func.getClausesForArgument(
                    relation, 'Arg2', dictByDocID, docID, arg2SentID, parseDict)
                productionsArg1 = []
                productionsArg2 = []
                for clauseWordIDs in clausesArg1:
                    productionsArg1 += func.get_curr_production_rules_for_clause(
                        parseDict, docID, arg1SentID, clauseWordIDs)
                for clauseWordIDs in clausesArg2:
                    productionsArg2 += func.get_curr_production_rules_for_clause(
                        parseDict, docID, arg2SentID, clauseWordIDs)
                label = sense[0].replace(' ', '-')
                exID = 'docID-' + docID + ':sentID-' + \
                    str(arg1SentID) + ':relID-' + str(relID)
                print "Extract production rule features for Relation[" + exID + "]..."
                features = getProductionFeaturesImplicitArg1(
                    dictByDocID, relation, docID, relID, productionsArg1, productionsArg2, prodRulesDict)
                # features=[]
                
                dataset.append([features, exID, label])

#     freqFeatures = sortFreqFeatures(dataset)
#     exportFreqFeatures(freqFeatures, 'FrequentFeatures.txt')
    #freqFeatures = readOverallFreqFeatures('FrequentFeatures.txt')
    freqFeatures = readFreqFeaturesSeparately('FrequentFeatures.txt')
    print "\nExport LBJ data file..."
    for inst in dataset:
        features = inst[0]
        exID = inst[1]
        label = inst[2]
        outF.write("None %s startend %s " % (label, exID))
        for feat in features:
            pair = feat.split(':')
            if pair[0] in freqFeatures:
                newFeat = feat
                if 'NA' in pair[1]:
                    newFeat = pair[0] + ':NA'
  
                outF.write("%s " % (newFeat))
    	outF.write("\n")
    print "\nLBJ data file DONE"

def exportFreqFeatures(freqFeatures, freqFeaturePath):
	print "\nCreating PRUNED feature frequency dictionary..."

	f = open(freqFeaturePath, 'w+')
	for item in freqFeatures:
	  if item[1] > 5:
	    f.write(item[0] + ':' + str(item[1]) + '\n')
	f.close()

	print "PRUNED feature frequency EXPORTED."


def readOverallFreqFeatures(freqFeaturePath):
    print "\nReading Frequent Feature dictionary..."
    featureList = []
    f = open(freqFeaturePath, 'r')
    count = 0
    for line in f:
        count += 1
        if count > FEATURE_NUM:
            break
    	featureList.append(line.split(":")[0])
    f.close()
    return featureList

def readFreqFeaturesSeparately(freqFeaturePath):
    print "\nReading Frequent Feature dictionary..."
    featureList = []
    
    #Add ARG1 frequent features
    f = open(freqFeaturePath, 'r')
    count = 0
    for line in f:
        count += 1
        if count > FEATURE_NUM / 2:
            break
        if line.split("_")[0] == 'Arg1':
            featureList.append(line.split(":")[0])
    f.close()
    
    #Add ARG2 frequent features
    f = open(freqFeaturePath, 'r')
    count = 0
    for line in f:
        count += 1
        if count > FEATURE_NUM / 2:
            break
        if line.split("_")[0] == 'Arg2':
            featureList.append(line.split(":")[0])
    f.close()
    
    return featureList
	
def sortFreqFeatures(dataset):
    print "\nSelecting frequent features..."
    freqDict = {}
    for data in dataset:
        features = data[0]
        for feature in features:
            pair = feature.split(':')
            if not pair[1] == 'NA':
                if pair[0] in freqDict.keys():
                    freqDict[pair[0]] += 1
                else:
                    freqDict[pair[0]] = 1
    sortedList = sorted(freqDict.items(), key=operator.itemgetter(1))
    sortedList.reverse()
    print "\nFeature selection DONE"
    return sortedList


def printWords(dictByDocID, docID, sentID, wordIDs):
    #	print 'Word Ids', wordIDs
    words = []
    for i in dictByDocID[docID][sentID]:
        if i in wordIDs:
            words.append(dictByDocID[docID][sentID][i]['word'])
    print ' '.join(words)


def printWords1(dictByDocID, docID, sentID, wordIDs):
    #       print 'Word Ids', wordIDs
    words = []
    for i in dictByDocID[docID][sentID]:
        if i in wordIDs:
            words.append(dictByDocID[docID][sentID][i]['word'])
    print >>stderr, ' '.join(words)


def getSentIDsImplicit(dictByDocID, relations):
    arg1 = {}
    arg2 = {}
    arg1All = {}
    arg2All = {}
    sentTotal = 0
    for relation in relations:
        relType = relation['Type']  # Explicit, Implicit,Entrel,AltLex
        docID = relation['DocID']
        relID = relation['ID']
        # arg1TokenList=func.getTokenIDsList(relation,'Arg1')
        # arg2TokenList=func.getTokenIDsList(relation,'Arg2')
        # take sentID of first token of arg1 as sentID of arg1
        arg1SentID = docID + '-' + str(relation['Arg1']['TokenList'][0][3])
        arg2SentID = docID + '-' + str(relation['Arg2']['TokenList'][0][3])
        if relType not in arg1:
            arg1[relType] = {}
        if relType not in arg2:
            arg2[relType] = {}
        arg1[relType][arg1SentID] = 1
        arg2[relType][arg2SentID] = 1
        if arg1SentID in arg1All or arg1SentID in arg2All:
            print >>stderr, 'Arg1 SentID exists', arg1SentID
        if arg2SentID in arg2All or arg2SentID in arg1All:
            print >>stderr, 'Arg2 SentID exists', arg2SentID
        arg1All[arg1SentID] = 1
        arg2All[arg2SentID] = 1
    # check which sentences are not an argument
    for docID in dictByDocID:
        prevSentID = 'None'
        for i in dictByDocID[docID]:
            sentTotal += 1
            sentID = docID + '-' + str(i)
            if prevSentID != 'None' and prevSentID not in arg1All and prevSentID not in arg2All:
                if sentID not in arg1All and sentID not in arg2All:
                    print >>stderr, 'SentID not an argument', sentID
            prevSentID = sentID
    print >>stderr, 'Sents total', sentTotal
    print >>stderr, 'arg1All', len(arg1All)
    print >>stderr, 'arg2All', len(arg2All)


# getProductionFeaturesImplicitArg1(dictByDocID,relation,docID,arg1SentID,relID,productionsArg1,productionsArg2,prodRulesDict)
def getProductionFeaturesImplicitArg1(dictByDocID, relation, docID, relID, productionsArg1, productionsArg2, prodRulesDict):
    #   clauseWordIDs=listOfClauses[clauseIndex][0]
    #   sentWords=func.getWordListFromSentence(dictByDocID,docID,sentID)
    features = []
#   isFirst=isLast=0
    cur = 0
    for p in prodRulesDict:
        val1 = val2 = valBoth = 'NA'
        if p in productionsArg1:
            val1 = '1'
        if p in productionsArg2:
            val2 = '1'
        if p in productionsArg1 and p in productionsArg2:
            valBoth = '1'
        f1 = 'Arg1_' + str(cur) + ':' + val1
        f2 = 'Arg2_' + str(cur) + ':' + val2
        f3 = 'Both_' + str(cur) + ':' + valBoth
        features.append(f1)
        features.append(f2)
        features.append(f3)
        cur += 1
    return features

    #(r1 , r2, r3, r1r2, r1r2r3,filteredRules)= getProductionRuleFeatures(parseDict,docID, sentID,clauseWordIDs,relID)
    #(r1P , r2P, r3P, r1r2P, r1r2r3P,filteredRulesPrev)= getProductionRuleFeatures(parseDict,docID, sentID,prevClauseWordIDs,relID)
    #(r1N , r2N, r3N, r1r2N, r1r2r3N,filteredRulesNext)= getProductionRuleFeatures(parseDict,docID, sentID,nextClauseWordIDs,relID)


dictByDocID = func.makeDictByDocID(parseDict)
dictByTokenID = func.makeDictByTokenID(dictByDocID)
# getSentIDsImplicit(dictByDocID,relations)
# exit()
relationDict = func.makeRelationDict(relations)
makeDataForSenseImplicit(dictByDocID, dictByTokenID, parseDict,
                         relationDict, verbList, relations, prodRulesDict, outF)
