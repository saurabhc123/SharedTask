from __future__ import division

import json
import codecs
import nltk
from nltk.tree import ParentedTree
import collections
from nltk.metrics import precision, recall, f_measure
import sys
import operator
import os

LOW_TERM_FREQ = 10
LOW_FREQ_THRESHOLD = 3
TERM_SET_SIZE = 1000

FEATURE_NUM = 27

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
    poss = features['f02']
    
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

def readInput(inputFilenamePath, trainOrTest):
    
    print("In function: readInput");
    #Read relations.json
    print("Reading relations.json");
    pdtb_file = codecs.open(inputFilenamePath+'/relations.json', encoding='utf8');
    relations = [json.loads(x) for x in pdtb_file];
    print("Done");
    
    #Read parses.json
    print ("Reading parses.json");
    parse_file = codecs.open(inputFilenamePath+'/parses.json', encoding='utf8')
    en_parse_dict = json.load(parse_file)
    print ("Done");
    
    counter = 0;
    flag = 0;

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
            
            print "Relation Number " + str(counter) + " has explicit connective with connective word being : '" + relation['Connective']['RawText'] + "'";
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
            
            #Feature 1: Connective String (C)
            strConnectiveWords = '_'.join(connectiveWords);
            features['f01'] = strConnectiveWords; 
             
            #Feature 2: POS of Connective
            connectivePOSs = []
            for i in range(len(connectiveWordIDs)):
                connectivePOSs.append(str(parseObjectArg2['words'][connectiveWordIDs[i]][1]['PartOfSpeech']));
            features['f02'] = '_'.join(connectivePOSs);
             
            #Feature 3: prev_1 + C
            prev_1 = str(parseObjectArg2['words'][connectiveWordIDs[0] - 1][0]);
            prev_1_plus_C = prev_1 + "+" + strConnectiveWords;
            features['f03'] = prev_1_plus_C;
             
            #Feature 4: self_category
            pt = parseObjectArg2['parsetree'];
            ptree = ParentedTree.fromstring(pt);
            selfCategory = self_category(connectiveWordIDs, connectiveWords, ptree)
            if len(selfCategory) > 0:
                features['f04'] = selfCategory
              
            #Feature 5: parent_category
            parentCategory = parent_category(connectiveWordIDs, connectiveWords, ptree)
            if len(parentCategory) > 0:
                features['f05'] = parentCategory
               
            #Feature 6: left_sibling
            leftSibling = left_sibling(connectiveWordIDs, connectiveWords, ptree)
            if len(leftSibling) > 0:
                features['f06'] = leftSibling
               
            #Feature 7: right_sibling
            rightSibling = right_sibling(connectiveWordIDs, connectiveWords, ptree)
            if len(rightSibling) > 0:
                features['f07'] = rightSibling
             
            #Feature 8: C String + Self Category
            c_selfCategory = strConnectiveWords + "+" + selfCategory
            if len(selfCategory) > 0:
                features['f08'] = c_selfCategory
             
            #Feature 9: C String + Parent Category
            c_parentCategory = strConnectiveWords + "+" + parentCategory
            if len(parentCategory) > 0:
                features['f09'] = c_parentCategory
             
            #Feature 10: C String + Left Sibling
            c_leftSibling = strConnectiveWords + "+" + leftSibling
            if len(leftSibling) > 0:
                features['f10'] = c_leftSibling
             
            #Feature 11: C String + Right Sibling
            c_rightSibling = strConnectiveWords + "+" + rightSibling
            if len(rightSibling) > 0:
                features['f11'] = c_rightSibling
             
            #Feature 12: Self Category + Parent Category
            selfCategory_parentCategory = selfCategory + "+" + parentCategory
            if len(selfCategory) > 0:
                features['f12'] = selfCategory_parentCategory
             
            #Feature 13: Self Category + Left Sibling
            selfCategory_leftSibling = selfCategory + "+" + leftSibling
            if len(selfCategory) > 0:
                features['f13'] = selfCategory_leftSibling
             
            #Feature 14: Self Category + Right Sibling
            selfCategory_rightSibling = selfCategory + "+" + rightSibling
            if len(selfCategory) > 0:
                features['f14'] = selfCategory_rightSibling
             
            #Feature 15: Parent Category + Left Sibling
            parentCategory_leftSibling = parentCategory + "+" + leftSibling
            if len(parentCategory) > 0:
                features['f15'] = parentCategory_leftSibling
             
            #Feature 16: Parent Category + Right Sibling
            parentCategory_rightSibling = parentCategory + "+" + rightSibling
            if len(parentCategory) > 0:
                features['f16'] = parentCategory_rightSibling
             
            #Feature 17: Left Sibling + Right Sibling
            leftSibling_rightSibling = leftSibling + "+" + rightSibling
            if len(leftSibling) > 0 and len(rightSibling) > 0 :
                features['f17'] = leftSibling_rightSibling
             
            #Feature 18: parent_category linked context
            parentCategoryLinkedContext = parent_category_linked_context(connectiveWordIDs, connectiveWords, ptree)
            if len(parentCategoryLinkedContext) > 0:
                features['f18'] = parentCategoryLinkedContext
              
            #Feature 19: previous connective words of current connective word 'as'
            #Feature 20: previous connective POSs of current connective word 'as'
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
                features['f19'] = preConnStrings
            if len(preConnPOSs) > 0:
                features['f20'] = preConnPOSs
             
            #Feature 21: previous connective words of current connective word 'when'
            #Feature 22: previous connective POSs of current connective word 'when'
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
                features['f21'] = preConnStrings
            if len(preConnPOSs) > 0:
                features['f22'] = preConnPOSs
            
            #Feature 23: Previous Word
            features['f23'] = prev_1
            
            #Feature 24: Next Word
            next_1 = str(parseObjectArg2['words'][connectiveWordIDs[-1] + 1][0]);
            features['f24'] = next_1
            
            #Feature 25: C + Next Word
            c_next = strConnectiveWords + '+' + next_1
            features['f25'] = c_next
            
            #Feature 26: Prev Word + Next Word
            prev_next = prev_1 + '+' + next_1
            features['f26'] = prev_next
            
            #Feature 27: Prev Word + C + Next Word
            prev_c_next = prev_1 + '+' + strConnectiveWords + '+' + next_1
            features['f27'] = prev_c_next
            
#             instanceID = 'DocID-' + str(relation_DocID) + ':SentID-' + str(parseJSON_sentence_number_arg2) + ':RelID-' + str(counter)
            if flag >= 0 and flag < 20:
                print "\nRelation[" + str(counter) + "]:"
                print "Raw String: " + relation['Arg2']['RawText'];
                print "Connective Words: " + strConnectiveWords;
                print "Features: " + str(features);
                flag += 1;
            
            if(trainOrTest == 'train'):
                trainingSet.append((features, label));
            else:
                testSet.append((features, label)); 
            
        counter = counter + 1;
        
    print "\nNumber of Explicit Relations: " + str(countOfExplicit);
    print "Number of multiple-token connectives: " + str(multiWordConn) + ", " + '{:.2%}'.format(multiWordConn/countOfExplicit) 
    print "Size of Training Set: " + str(len(trainingSet));


def findAllClasses(dataSet):
    result = set()
    
    for dataTuple in dataSet:
        result.add(dataTuple[1])
    
    return result

def classifyText(train, test):
    print "In function: classifyText";
    print "Training: " + str(train[0]);
    print "Test: " + str(test[0]);
    
    #Train classifier
#     classifier = nltk.NaiveBayesClassifier.train(train);
    algorithm = nltk.classify.MaxentClassifier.ALGORITHMS[0]
    classifier = nltk.MaxentClassifier.train(train, algorithm,max_iter=20)
    #Show top features
    classifier.show_most_informative_features(100)
    
    #Test the classifier on the DEV data set
    accuracy = nltk.classify.util.accuracy(classifier, test);
    #print 'accuracy:', nltk.classify.util.accuracy(classifier, trainingSet[testcv[0]:testcv[len(testcv)-1]])
    refsets = collections.defaultdict(set)
    testsets = collections.defaultdict(set)
#     truth = set();
#     predicted = set();
    for i, (feats, label) in enumerate(test):
        refsets[label].add(i)
        observed = classifier.classify(feats)
        testsets[observed].add(i)
    
    #Print the performance statistics
    classSet = findAllClasses(test)
    p = calcAllClassesPrecision(classSet, refsets, testsets)
    r = calcAllClassesRecall(classSet, refsets, testsets)
    f = calcAllClassesFMeasure(classSet, refsets, testsets)
    
    print "Accuracy:", '{:.2%}'.format(accuracy);
    print "Precision:", '{:.2%}'.format(p);
    print "Recall:", '{:.2%}'.format(r);
    print "F-measure:", '{:.2%}'.format(f);
    
    return testsets

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
    
def exportNLTKPredictions(outputFile, testsets):
    print "\nExporting NLTK predictions..."
    outputDict = dict()
    
    for sense in testsets.keys():
        relSet = testsets[sense]
        for relID in relSet:
            relation = goldList[relID]
            entryDict = dict();
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
    with open(outputFile, 'w') as f:
        for item in sortedList:
            entryDict = item[1]
            json.dump(entryDict, f)
            f.write("\n");
    
    print str(len(sortedList)), "predictions have been exported to", outputFile
    

def getTokenList(arg):
    tokenList = []
    for token in arg['TokenList']:
        tokenList.append(token[2])
    
    return tokenList      

if __name__ == '__main__':
    print ("Classify explicit senses...\n");
    
    #readInput('/home/development/data/conll16st-en-01-12-16-train', 'train');
    readInput('D:\\Test\\CS6804\\conll16st-en-01-12-16-train', 'train');
    #readInput('D:\\Test\\CS6804\\conll16st-en-01-12-16-trial', 'train');
    
    #Do pruning to features
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
    prune('f22', trainingSet)
    
    prune('f23', trainingSet)
    prune('f24', trainingSet)
    prune('f25', trainingSet)
    prune('f26', trainingSet)
    prune('f27', trainingSet)
    
    #print "Training Set: ", trainingSet;
    
    #readInput('/home/development/data/conll16st-en-01-12-16-dev', 'test');
    #readInput('D:\\Test\\CS6804\\conll16st-en-01-12-16-trial', 'test');
    readInput('D:\\Test\\CS6804\\conll16st-en-01-12-16-dev', 'test');
    #print "Test Set: ", testSet; 
    
    #Classify test data set
    testsets = classifyText(trainingSet, testSet);
    
    #Export predictions for official scorer
#     exportNLTKPredictions(os.getcwd() + os.sep + 'output-trial.json', testsets)
    exportNLTKPredictions(os.getcwd() + os.sep + 'output-dev.json', testsets)
    print "Done";
