from __future__ import division

import argparse
import json
import codecs
from nltk.tree import ParentedTree
from nltk.metrics import precision, recall, f_measure
import sys
import operator
import os
import subprocess
import time

LOW_TERM_FREQ = 10
LOW_FREQ_THRESHOLD = 2
TERM_SET_SIZE = 1000

FEATURE_NUM = 29

trainingSet = [];
testSet = [];

goldList = [];


def containNode(t, node):
    try:
        if isinstance(t, basestring):
            if t==node:
                return True
            else:
                return False
        else:
            flag = False
            for child in t:
                flag = flag  | containNode(child, node)
            return flag
    except:
        print "Unexpected error:", sys.exc_info()[0]
        return ""

def current_to_root(index, ptree):
    leaf=ptree
    path=ptree.leaf_treeposition(index)
    for ind in path[0:(len(path)-1)]:
        leaf=leaf[ind]
    label=''
    for ind in path[0:(len(path)-1)]:
        label=leaf.parent().label()+'_'+label		
        leaf=leaf.parent()

    return label


def self_category(indexes, words, ptree):
    leaf=ptree
    for index in indexes:
        if index >= len(ptree.leaves()):
            return ''
        
    #Find the path to the specified leaf
    #Return a tuple which records the path from root to the specified leaf. 
    #For example, a "0" component in the tuple means choosing the 0th child of a node, while "1" means selecting the 1th child
    path=ptree.leaf_treeposition(indexes[0])
    for ind in path[0:(len(path)-1)]:
        leaf=leaf[ind]
    label=''
    
    #Single connective word case
    if(len(indexes) < 2):
        parent = leaf.parent()
        #Search for the highest node which contains only the connective word
        while (parent is not None and len(parent) <= 1):
            leaf = parent
            parent = parent.parent()
        label=leaf.label()
        return label
    
    #Multiple connective words case
    findAllWords = False
    while (leaf is not None and not findAllWords):
        findAllWords = True
        #Check whether all the words are children of current leaf
        for i in range(1, len(indexes)):
            findAllWords = findAllWords & containNode(leaf, words[i])
            if(findAllWords):
                #Strict SELF_CATEGORY definition
                nLeaves = len(leaf.leaves())
                nWords = len(indexes)
                if nLeaves == nWords:#Check whether there're other words under this node beyond the connective words
                    label = leaf.label() 
                    return label
                else:
                    return ''
        leaf = leaf.parent()
    
    return ''

def parent_category(indexes, words, ptree):
    leaf=ptree
    for index in indexes:
        if index >= len(ptree.leaves()):
            return ''
        
    #Find the path to the specified leaf
    #Return a tuple which records the path from root to the specified leaf. 
    #For example, a "0" component in the tuple means choosing the 0th child of a node, while "1" means selecting the 1th child
    path=ptree.leaf_treeposition(indexes[0])
    for ind in path[0:(len(path)-1)]:
        leaf=leaf[ind]
    label=''
    
    #Single connective word case
    if(len(indexes) < 2):
        parent = leaf.parent()
        #Search for the highest node which contains only the connective word
        while (parent is not None and len(parent) <= 1):
            leaf = parent
            parent = parent.parent()
        label=leaf.parent().label()
        return label
    
    #Multiple connective words case
    findAllWords = False
    while (leaf is not None and not findAllWords):
        findAllWords = True
        #Check whether all the words are children of current leaf
        for i in range(1, len(indexes)):
            findAllWords = findAllWords & containNode(leaf, words[i])
            if(findAllWords):
                #Strict PARENT_CATEGORY definition
                nLeaves = len(leaf.leaves())
                nWords = len(indexes)
                if nLeaves == nWords:#Check whether there're other words under this node beyond the connective words
                    label = leaf.parent().label() 
                    return label
                else:
                    return ''
        leaf = leaf.parent()
    
    return ''

def parent_category_linked_context(indexes, words, ptree):
    leaf=ptree
    for index in indexes:
        if index >= len(ptree.leaves()):
            return ''
        
    #Find the path to the specified leaf
    #Return a tuple which records the path from root to the specified leaf. 
    #For example, a "0" component in the tuple means choosing the 0th child of a node, while "1" means selecting the 1th child
    path=ptree.leaf_treeposition(indexes[0])
    for ind in path[0:(len(path)-1)]:
        leaf=leaf[ind]
    label = ''
    
    #Single connective word case
    if(len(indexes) < 2):
        parent = leaf.parent()
        #Search for the highest node which contains only the connective word
        while (parent is not None and len(parent) <= 1):
            leaf = parent
            parent = parent.parent()
        parentLabel=leaf.parent().label()
        #Get grandparent labels
        if leaf.parent().parent() is not None:
            grandParentLabel = leaf.parent().parent().label()
        else:
            grandParentLabel = ''
        
        #Get children labels of the connective's parent
        children = []
        for child in leaf.parent():
            children.append(child.label())
        childrenLabel = '_'.join(children)
        
        label = grandParentLabel + '_' + parentLabel + '_' + childrenLabel
        return label 
    
    #Multiple connective words case
    findAllWords = False
    while (leaf is not None and not findAllWords):
        findAllWords = True
        #Check whether all the words are children of current leaf
        for i in range(1, len(indexes)):
            findAllWords = findAllWords & containNode(leaf, words[i])
            if(findAllWords):
                #Strict PARENT_CATEGORY definition
                nLeaves = len(leaf.leaves())
                nWords = len(indexes)
                if nLeaves == nWords:#Check whether there're other words under this node beyond the connective words
                    parentLabel = leaf.parent().label() 
                    #Get grandparent labels
                    if leaf.parent().parent() is not None:
                        grandParentLabel = leaf.parent().parent().label()
                    else:
                        grandParentLabel = ''
                    children = []
                    for child in leaf.parent():
                        children.append(child.label())
                    childrenLabel = '_'.join(children)
                    
                    label = grandParentLabel + '_' + parentLabel + '_' + childrenLabel
                    return label
                else:
                    return ''
        leaf = leaf.parent()
    
    return ''

def right_sibling(indexes, words, ptree):
    leaf=ptree
    for index in indexes:
        if index >= len(ptree.leaves()):
            return ''
        
    #Find the path to the specified leaf
    #Return a tuple which records the path from root to the specified leaf. 
    #For example, a "0" component in the tuple means choosing the 0th child of a node, while "1" means selecting the 1th child
    path=ptree.leaf_treeposition(indexes[0])
    for ind in path[0:(len(path)-1)]:
        leaf=leaf[ind]
    label=''
    
    #Single connective word case
    if(len(indexes) < 2):
        parent = leaf.parent()
        #Search for the highest node which contains only the connective word
        while (parent is not None and len(parent) <= 1):
            leaf = parent
            parent = parent.parent()
        rightSibling = leaf.right_sibling()
        if rightSibling == None:
            return ''
        else:
            label=rightSibling.label()
            return label
    
    #Multiple connective words case
    findAllWords = False
    while (leaf is not None and not findAllWords):
        findAllWords = True
        #Check whether all the words are children of current leaf
        for i in range(1, len(indexes)):
            findAllWords = findAllWords & containNode(leaf, words[i])
            if(findAllWords):
                #Strict RIGHT_SIBLING_CATEGORY definition
                nLeaves = len(leaf.leaves())
                nWords = len(indexes)
                if nLeaves == nWords:#Check whether there're other words under this node beyond the connective words
                    rightSibling = leaf.right_sibling()
                    if rightSibling == None:
                        return ""
                    else:
                        label = rightSibling.label() 
                        return label
                else:
                    return ''
        leaf = leaf.parent()
    
    return ''

def left_sibling(indexes, words, ptree):
    leaf=ptree
    for index in indexes:
        if index >= len(ptree.leaves()):
            return ''
        
    #Find the path to the specified leaf
    #Return a tuple which records the path from root to the specified leaf. 
    #For example, a "0" component in the tuple means choosing the 0th child of a node, while "1" means selecting the 1th child
    path=ptree.leaf_treeposition(indexes[0])
    for ind in path[0:(len(path)-1)]:
        leaf=leaf[ind]
    label=''
    
    #Single connective word case
    if(len(indexes) < 2):
        parent = leaf.parent()
        #Search for the highest node which contains only the connective word
        while (parent is not None and len(parent) <= 1):
            leaf = parent
            parent = parent.parent()
        leftSibling = leaf.left_sibling()
        if leftSibling == None:
            return ''
        else:
            label=leftSibling.label()
            return label
    
    #Multiple connective words case
    findAllWords = False
    while (leaf is not None and not findAllWords):
        findAllWords = True
        #Check whether all the words are children of current leaf
        for i in range(1, len(indexes)):
            findAllWords = findAllWords & containNode(leaf, words[i])
            if(findAllWords):
                #Strict LEFT_SIBLING_CATEGORY definition
                nLeaves = len(leaf.leaves())
                nWords = len(indexes)
                if nLeaves == nWords:#Check whether there're other words under this node beyond the connective words
                    leftSibling = leaf.left_sibling()
                    if leftSibling == None:
                        return ""
                    else:
                        label = leftSibling.label() 
                        return label
                else:
                    return ''
        leaf = leaf.parent()
    
    return ''

def previous_conn_string(dataset):
    features = dataset[-1][0]
    connectiveWords = features['f01']
    
    return connectiveWords

def previous_conn_pos(dataset):
    features = dataset[-1][0]
    poss = features['f10']
    
    return poss

def prune(featureIndex, dataset):
    valueDict = {}
    for rel in dataset:
        features = rel[0]
        if not featureIndex in features.keys():
            continue
        value = features[featureIndex]
        if not value in valueDict.keys():
            valueDict[value] = 1
        else:
            valueDict[value] = valueDict[value] + 1
    
    lowFreqSet = set()
    for value in valueDict.keys():
        if valueDict[value] <= LOW_FREQ_THRESHOLD:
            lowFreqSet.add(value)
    
    for rel in dataset:
        features = rel[0]
        if not featureIndex in features.keys():
            continue
        value = features[featureIndex]
        if value is not None and value in lowFreqSet:
            features[featureIndex] = ''

def readInput(relationFilePath, parseFilePath, trainOrTest):
    
    print("In function: readInput");
    #Read relations.json
    print("Reading relations.json");
    pdtb_file = codecs.open(relationFilePath, encoding='utf8');
    relations = [json.loads(x) for x in pdtb_file];
    print("Done");
    
    #Read parses.json
    print ("Reading parses.json");
    parse_file = codecs.open(parseFilePath, encoding='utf8')
    en_parse_dict = json.load(parse_file)
    print ("Done");
    
    counter = 0;
    print "Extracting features from Relations..."
    countOfExplicit = 0;
    multiWordConn = 0;
    for relation in relations:
        cType = relation['Type']; 
        if cType == 'Explicit':
#             instanceID = ''
            countOfExplicit = countOfExplicit + 1;
            
            #Get the labels
            if len(relation['Sense']) > 1:
                print "\nRelation Number " + str(counter) + " has multiple senses:"
                for sense in relation['Sense']:
                    print "---[" + sense + "]"
            label = relation['Sense'][0]
            
            #Ignore relations with invalid senses
#             if not label in validator.EN_SENSES:
#                 continue
            
            if trainOrTest == 'test':
                goldList.append(relation) 
            
            #print "Extracting features from Relation [" + str(counter) + "]..."
            #print "Relation Number " + str(counter) + " has explicit connective with connective word being : '" + relation['Connective']['RawText'] + "'";
            relation_DocID = relation['DocID'];
            parseJSON_sentence_number_arg2 = relation['Arg2']['TokenList'][0][3];
            connectiveWordIDs = []
            #Check whether multiple-token connective or not
            if (len(relation['Connective']['TokenList']) > 1):
                multiWordConn += 1
            for i in range(len(relation['Connective']['TokenList'])):
                connectiveWordIDs.append(relation['Connective']['TokenList'][i][4]);

            #Skip the instances with in-consecutive multiple-token connective words
#             if len(connectiveWordIDs) > 1:
#                 if connectiveWordIDs[-1] - connectiveWordIDs[0] > len(connectiveWordIDs) - 1:
#                     continue
            
            #Parses.json object for that relation
            parseObjectArg2 = en_parse_dict[relation_DocID]['sentences'][parseJSON_sentence_number_arg2];
            connectiveWords = []
            for i in range(len(connectiveWordIDs)):
                connectiveWords.append(parseObjectArg2['words'][connectiveWordIDs[i]][0]);

            #Building Feature Set
            features = dict();
            
            #Feature 1: Connective Token 1
            token1 = connectiveWords[0]
            features['f01'] = token1
            
            #Feature 2: Connective Token 2
            token2 = ''
            if len(connectiveWords) >= 2:
                token2 = connectiveWords[1]
                features['f02'] = token2
            
            #Feature 3: Connective String (C)
            strConnectiveWords = '_'.join(connectiveWords);
            features['f03'] = strConnectiveWords; 
            
            #Feature 4: Previous Word
            prev_1 = str(parseObjectArg2['words'][connectiveWordIDs[0] - 1][0]);
            features['f04'] = prev_1
            
            #Feature 5: Next Word
            nextWordID = connectiveWordIDs[-1] + 1
            if nextWordID < len(parseObjectArg2['words']):
                next_1 = str(parseObjectArg2['words'][nextWordID][0]);
            else:
                next_1 = ''
            features['f05'] = next_1
            
            #Feature 6: prev_1 + C
            prev_1_plus_C = prev_1 + "+" + strConnectiveWords;
            features['f06'] = prev_1_plus_C;
             
            #Feature 7: C + Next Word
            c_next = strConnectiveWords + '+' + next_1
            features['f07'] = c_next
             
            #Feature 8: Prev Word + Next Word
            prev_next = prev_1 + '+' + next_1
            features['f08'] = prev_next
             
            #Feature 9: Prev Word + C + Next Word
            prev_c_next = prev_1 + '+' + strConnectiveWords + '+' + next_1
            features['f09'] = prev_c_next
             
            #Feature 10: POS of Connective
            connectivePOSs = []
            for i in range(len(connectiveWordIDs)):
                connectivePOSs.append(str(parseObjectArg2['words'][connectiveWordIDs[i]][1]['PartOfSpeech']));
            features['f10'] = '_'.join(connectivePOSs);
             
            #Feature 11: self_category
            pt = parseObjectArg2['parsetree'];
            ptree = ParentedTree.fromstring(pt);
            selfCategory = self_category(connectiveWordIDs, connectiveWords, ptree)
            if len(selfCategory) > 0:
                features['f11'] = selfCategory
               
            #Feature 12: parent_category
            parentCategory = parent_category(connectiveWordIDs, connectiveWords, ptree)
            if len(parentCategory) > 0:
                features['f12'] = parentCategory
                
            #Feature 13: left_sibling
            leftSibling = left_sibling(connectiveWordIDs, connectiveWords, ptree)
            if len(leftSibling) > 0:
                features['f13'] = leftSibling
                
            #Feature 14: right_sibling
            rightSibling = right_sibling(connectiveWordIDs, connectiveWords, ptree)
            if len(rightSibling) > 0:
                features['f14'] = rightSibling
              
            #Feature 15: C String + Self Category
            c_selfCategory = strConnectiveWords + "+" + selfCategory
            if len(selfCategory) > 0:
                features['f15'] = c_selfCategory
              
            #Feature 16: C String + Parent Category
            c_parentCategory = strConnectiveWords + "+" + parentCategory
            if len(parentCategory) > 0:
                features['f16'] = c_parentCategory
              
            #Feature 17: C String + Left Sibling
            c_leftSibling = strConnectiveWords + "+" + leftSibling
            if len(leftSibling) > 0:
                features['f17'] = c_leftSibling
              
            #Feature 18: C String + Right Sibling
            c_rightSibling = strConnectiveWords + "+" + rightSibling
            if len(rightSibling) > 0:
                features['f18'] = c_rightSibling
              
            #Feature 19: Self Category + Parent Category
            selfCategory_parentCategory = selfCategory + "+" + parentCategory
            if len(selfCategory) > 0:
                features['f19'] = selfCategory_parentCategory
              
            #Feature 20: Self Category + Left Sibling
            selfCategory_leftSibling = selfCategory + "+" + leftSibling
            if len(selfCategory) > 0:
                features['f20'] = selfCategory_leftSibling
              
            #Feature 21: Self Category + Right Sibling
            selfCategory_rightSibling = selfCategory + "+" + rightSibling
            if len(selfCategory) > 0:
                features['f21'] = selfCategory_rightSibling
              
            #Feature 22: Parent Category + Left Sibling
            parentCategory_leftSibling = parentCategory + "+" + leftSibling
            if len(parentCategory) > 0:
                features['f22'] = parentCategory_leftSibling
              
            #Feature 23: Parent Category + Right Sibling
            parentCategory_rightSibling = parentCategory + "+" + rightSibling
            if len(parentCategory) > 0:
                features['f23'] = parentCategory_rightSibling
              
            #Feature 24: Left Sibling + Right Sibling
            leftSibling_rightSibling = leftSibling + "+" + rightSibling
            if len(leftSibling) > 0 and len(rightSibling) > 0 :
                features['f24'] = leftSibling_rightSibling
              
            #Feature 25: parent_category linked context
            parentCategoryLinkedContext = parent_category_linked_context(connectiveWordIDs, connectiveWords, ptree)
            if len(parentCategoryLinkedContext) > 0:
                features['f25'] = parentCategoryLinkedContext
               
            #Feature 26: previous connective words of current connective word 'as'
            #Feature 27: previous connective POSs of current connective word 'as'
            preConnStrings = ''
            preConnPOSs = ''
            if strConnectiveWords.lower() == 'as':
                if(trainOrTest == 'train'):
                    dataset = trainingSet
                else:
                    dataset = testSet
                preConnStrings = previous_conn_string(dataset)
                preConnPOSs = previous_conn_pos(dataset)
            if len(preConnStrings) > 0:
                features['f26'] = preConnStrings
            if len(preConnPOSs) > 0:
                features['f27'] = preConnPOSs
              
            #Feature 28: previous connective words of current connective word 'when'
            #Feature 29: previous connective POSs of current connective word 'when'
            preConnStrings = ''
            preConnPOSs = ''
            if strConnectiveWords.lower() == 'when':
                if(trainOrTest == 'train'):
                    dataset = trainingSet
                else:
                    dataset = testSet
                preConnStrings = previous_conn_string(dataset)
                preConnPOSs = previous_conn_pos(dataset)
            if len(preConnStrings) > 0:
                features['f28'] = preConnStrings
            if len(preConnPOSs) > 0:
                features['f29'] = preConnPOSs
            
#             instanceID = 'DocID-' + str(relation_DocID) + ':SentID-' + str(parseJSON_sentence_number_arg2) + ':RelID-' + str(counter)
            
            if(trainOrTest == 'train'):
                trainingSet.append((features, label));
            else:
                testSet.append((features, label)); 
            
        counter = counter + 1;
        
    print "\nNumber of Explicit Relations: " + str(countOfExplicit);
    print "Number of multiple-token connectives: " + str(multiWordConn) + ", " + '{:.2%}'.format(multiWordConn/countOfExplicit) 


def findAllClasses(dataSet):
    result = set()
    
    for dataTuple in dataSet:
        result.add(dataTuple[1])
    
    return result

def calcAllClassesPrecision(classSet, refsets, testsets):
    pSum = 0.0
    denominator = 0
    for category in classSet:
        num = precision(refsets[category], testsets[category])
        if num is None:
            continue
        pSum += num
        denominator += 1
    
    return pSum/denominator

def calcAllClassesRecall(classSet, refsets, testsets):
    rSum = 0.0
    denominator = 0
    for category in classSet:
        num = recall(refsets[category], testsets[category])
        if num is None:
            continue
        rSum += num
        denominator += 1
    
    return rSum/denominator

def calcAllClassesFMeasure(classSet, refsets, testsets):
    fSum = 0.0
    denominator = 0
    for category in classSet:
        num = f_measure(refsets[category], testsets[category])
        if num is None:
            continue
        fSum += num
        denominator += 1
    
    return fSum/denominator

def exportLBJFeatureFile(outputFile, dataSet):
    print "\nExporting features into LBJ file..."
    counter = 0
    with open(outputFile, 'w') as f:
        for rel in dataSet:
            columns = []
            features = rel[0]
            label = rel[1]
            connStr = features['f01']
            columns.append(connStr)
            columns.append(label)
            columns.append('startend')
            columns.append('RelID:' + str(counter))

            for i in range(1, FEATURE_NUM+1):
                iStr = '%02d' % i
                fKey = 'f' + iStr
                if fKey in features.keys():
                    columns.append(fKey + ':' + features[fKey])
                else:
                    columns.append(fKey + ':' + 'None')
            line = ' '.join(columns)
            f.write(line + '\n')
            counter += 1
    print str(counter), 'instances have been exported to', outputFile
    
def exportLBJPredictions(lbjOutput, predictFile):
    print "\nExporting LBJ predictions..."
    outputDict = dict()
    with open(lbjOutput, 'r') as f:
        for line in f:
            columns = line.split(' ')
            entryDict = dict();
            relID = columns[3].split(':')[1]
            relation = goldList[int(relID)]
            sense = columns[2].split('=')[1]
            
            entryDict['DocID'] = relation['DocID'];
            arg1TokenList = getTokenList(relation['Arg1'])
            arg2TokenList = getTokenList(relation['Arg2'])
            entryDict['Arg1'] = dict({"TokenList":arg1TokenList});
            entryDict['Arg2'] = dict({"TokenList":arg2TokenList});
            connectiveTokenList = getTokenList(relation['Connective'])
            entryDict['Connective'] = dict({"TokenList":connectiveTokenList});
            entryDict['Sense'] = [sense];
            entryDict['Type'] = 'Explicit';
            outputDict[relID] = entryDict        
        
    sortedList = sorted(outputDict.items(), key=operator.itemgetter(0))        
    with open(predictFile, 'w') as f:
        for item in sortedList:
            entryDict = item[1]
            json.dump(entryDict, f)
            f.write("\n");

def exportUpdatedRelations(lbjOutput, updatedRelationsFile):
    print "\nExporting LBJ predictions..."
#     outputDict = dict()
    with open(lbjOutput, 'r') as f:
        for line in f:
            columns = line.split(' ')
            relID = columns[3].split(':')[1]
            sense = columns[2].split('=')[1]
            goldList[int(relID)]['Sense'] = [sense]
                  
    with open(updatedRelationsFile, 'w') as f:
        for item in goldList:
            json.dump(item, f)
            f.write("\n");

def getTokenList(arg):
    tokenList = []
    for token in arg['TokenList']:
        tokenList.append(token[2])
    
    return tokenList

def trainAndTest(LBJDir):
    print "\nTraining and classifying test data set by LBJ and Perceptron..."
    
    LBJPredictionFile = LBJDir + os.sep + 'outputFile'
    
    #Train and classify test data set and produce predictions with LBJ
    #ASSUME LBJ has been installed under the LBJDir path and the LBJ jars already added to CLASSPATH !!! 
    if PLATFORM == 'Linux':
        command1 = './ExplicitSenseClassifier.sh'
    else:
        command1 = 'ExplicitSenseClassifier.bat'
    commands = [command1]
    p = subprocess.Popen(commands, cwd = LBJDir, shell = True)
    p.wait()
    
    return LBJPredictionFile

def testWithExistingModel(LBJDir):
    print "\nClassifying test data set by LBJ and Perceptron using existing model..."
    
    LBJPredictionFile = LBJDir + os.sep + 'outputFile'
    
    #Classify test data set and produce predictions with LBJ using existing model
    #ASSUME LBJ has been installed under the LBJDir path, LBJ jars already added to CLASSPATH, and explicit sense classifier has been trained !!!
    if PLATFORM == 'Linux':
        command1 = './ExplicitSensePredictor.sh'
    else:
        command1 = 'ExplicitSensePredictor.bat'
    commands = [command1]
    p = subprocess.Popen(commands, cwd = LBJDir, shell = True)
    p.wait()
    
    return LBJPredictionFile

def calculateRunTime(function, *args):
    """run a function and return the run time and the result of the function
    if the function requires arguments, those can be passed in too"""
    startTime = time.time()
    result = function(*args)
    return time.time() - startTime, result
    
def pruneFeatures():
    prune('f01', trainingSet)
    prune('f02', trainingSet)     
    prune('f03', trainingSet)
    prune('f04', trainingSet)
    prune('f05', trainingSet)
    prune('f06', trainingSet)
    prune('f07', trainingSet)
    prune('f08', trainingSet)
    prune('f09', trainingSet)
    prune('f10', trainingSet)
    prune('f11', trainingSet)
    prune('f12', trainingSet)
    prune('f13', trainingSet)
    prune('f14', trainingSet)
    prune('f15', trainingSet)
    prune('f16', trainingSet)
    prune('f17', trainingSet)      
    prune('f18', trainingSet)
    prune('f20', trainingSet)
    prune('f21', trainingSet)
    prune('f22', trainingSet)
    prune('f23', trainingSet)
    prune('f24', trainingSet)
    prune('f25', trainingSet)
    prune('f26', trainingSet)
    prune('f27', trainingSet)
    prune('f28', trainingSet)
    prune('f29', trainingSet)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="The explicit sense classifier")
    parser.add_argument('relationsfile', help='Path to relations.json')
    parser.add_argument('parsesfile', help='Path to parses.json')
    parser.add_argument('modeldir', help='Path to pre-trained classifier model directory')
    parser.add_argument('outputfile',
                        help='Path to the output files (relations.json)')
    args = parser.parse_args()

    if len(sys.argv) < 4:
        print "Please Specify Proper Arguments:"
        print "relationsfile : default relations.json"
        print "parsesfile : default parses.json"
        print "modeldir : default lbj"
        print "outputfile : default ./relations.json"
        print "Thus, the default command to run would be:"
        print "    python explicit_sense_perceptron_predict.py parses.json lbj ."
        sys.exit(1)
    
    PLATFORM = 'Linux'
    #PLATFORM = 'Windows'
    
    LBJDir = args.modeldir
    #LBJDir = '/home/xuancs/lbj'
    #LBJDir = 'D:\\eclipse\\WorkspacePy\\CoNLL2016\\LBJ'
    
    #Set path of input files
    testRelationFilePath = args.relationsfile
    #testRelationFilePath = '/home/development/data/conll16st-en-01-12-16-dev/relations.json'
    #testRelationFilePath = 'D:\\Test\\CS6804\\conll16st-en-01-12-16-dev\\relations.json'
    testParseFilePath = args.parsesfile
    #testParseFilePath = '/home/development/data/conll16st-en-01-12-16-dev/parses.json'
    #testParseFilePath = 'D:\\Test\\CS6804\\conll16st-en-01-12-16-dev\\parses.json'
    
    #Read the test data set
    results = calculateRunTime(readInput, testRelationFilePath, testParseFilePath, 'test')
    print '\nReading test data set DONE in', '{0:.2f}'.format(results[0]), 'Seconds'
    
    #Export test data sets to LBJ feature files
    testFeatureFile = LBJDir + os.sep + 'testES.column'
    exportLBJFeatureFile(testFeatureFile, testSet)
    
    #Run ONLY ONE of the two functions: trainAndTest() or testWithExistingModel !!!
    
    #Classify test data set and produce predictions with LBJ using existing model
    #ASSUME LBJ has been installed under the LBJDir path, LBJ jars already added to CLASSPATH, and explicit sense classifier has been trained !!! 
    timeCost, LBJPredictionFile = calculateRunTime(testWithExistingModel, LBJDir)
    print '\nClassifying using existing model DONE in', '{0:.2f}'.format(timeCost), 'Seconds'

    #Export predictions for official scorer
    #outputJsonFile = os.getcwd() + os.sep + 'output-dev.json'
    #exportLBJPredictions(LBJPredictionFile, outputJsonFile)
    
    #Update the relations with predicted sense and export the updated relations for other classifiers
    updatedRelationsFile = args.outputfile
    #updatedRelationsFile = os.getcwd() + os.sep + 'relations-explicit-sense.json.json'
    exportUpdatedRelations(LBJPredictionFile, updatedRelationsFile)
    
    print "Done";

