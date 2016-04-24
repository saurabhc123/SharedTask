from __future__ import division

import json
import codecs
from pprint import pprint
import os
#import ParsedInput
import nltk
from nltk.tree import *
import collections
#import scikit-learn
import sklearn
from sklearn import cross_validation
import nltk.metrics
from nltk.metrics import precision, recall, f_measure
import sys

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

trainingSet = [];
testSet = [];

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
                #Loose SELF_CATEGORY definition
                label = leaf.label() 
                return label
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
                #Loose SELF_CATEGORY definition
                label = leaf.parent().label() 
                return label
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
                #Loose RIGHT_SIBLING_CATEGORY definition
                rightSibling = leaf.right_sibling()
                if rightSibling == None:
                    return ""
                else:
                    label = rightSibling.label() 
                    return label
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
                #Loose LEFT_SIBLING_CATEGORY definition
                leftSibling = leaf.left_sibling()
                if leftSibling == None:
                    return ""
                else:
                    label = leftSibling.label() 
                    return label
        leaf = leaf.parent()
    
    return ''
    

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
#     featureSet = [];
#     labelSet = [];
    
    #trainingSet = [];
    #testSet = [];
    countOfExplicit = 0;
    multiWordConn = 0;
    for relation in relations:
        cType = relation['Type']; 
        if cType == 'Explicit':
            countOfExplicit = countOfExplicit + 1;    
            
            #Get the labels    
            label = relation['Sense'][0]
            
            print "Relation Number " + str(counter) + " has explicit connective with connective word being : '" + relation['Connective']['RawText'] + "'";
            relation_DocID = relation['DocID'];
            parseJSON_sentence_number = relation['Arg2']['TokenList'][0][3];
            connectiveWordIDs = []
            if (len(relation['Connective']['TokenList']) > 1):
                multiWordConn += 1
            for i in range(len(relation['Connective']['TokenList'])):
                connectiveWordIDs.append(relation['Connective']['TokenList'][i][4]);

            #Parses.json object for that relation
            parseObject = en_parse_dict[relation_DocID]['sentences'][parseJSON_sentence_number];
            connectiveWords = []
            for i in range(len(connectiveWordIDs)):
                connectiveWords.append(parseObject['words'][connectiveWordIDs[i]][0]);
            
            #Building Feature Set
            features = dict();
            
            #Feature 1: Connective String (C)
            strConnectiveWords = ' '.join(connectiveWords);
            features['f1'] = strConnectiveWords; 
            
            
            #Feature 2: POS of Connective
            connectivePOSs = []
            for i in range(len(connectiveWordIDs)):
                connectivePOSs.append(str(parseObject['words'][connectiveWordIDs[i]][1]['PartOfSpeech']));
            features['f2'] = ' '.join(connectivePOSs);
            
            #Feature 3: prev_1 + C
            prev_1 = '';
            if connectiveWordIDs > 0:
                prev_1 = str(parseObject['words'][connectiveWordIDs[0] - 1][0]);
            
            prev_1_plus_C = prev_1 + "_" + ' '.join(connectiveWords);
            features['f3'] = prev_1_plus_C;
            
            #Feature 4: self_category
            pt = parseObject['parsetree'];
            ptree = ParentedTree.fromstring(pt);
            selfCategory = self_category(connectiveWordIDs, connectiveWords, ptree)
#             print "f4:", selfCategory
            features['f4'] = selfCategory
              
            #Feature 5: parent_category
            parentCategory = parent_category(connectiveWordIDs, connectiveWords, ptree)
#             print "f5:", parentCategory
            features['f5'] = parentCategory
              
#             #Feature 6: left_sibling
            leftSibling = left_sibling(connectiveWordIDs, connectiveWords, ptree)
#             print "f6:", leftSibling
            features['f6'] = leftSibling
             
#             #Feature 7: right_sibling
            rightSibling = right_sibling(connectiveWordIDs, connectiveWords, ptree)
#             print "f7:", rightSibling
            features['f7'] = rightSibling
            
            #Feature 8: C String + Self Category
            c_selfCategory = strConnectiveWords + "_" + selfCategory
            features['f08'] = c_selfCategory
            
            #Feature 9: C String + Parent Category
            c_parentCategory = strConnectiveWords + "_" + parentCategory
            features['f09'] = c_parentCategory
            
            #Feature 10: C String + Left Sibling
            c_leftSibling = strConnectiveWords + "_" + leftSibling
            features['f10'] = c_leftSibling
            
            #Feature 11: C String + Right Sibling
            c_rightSibling = strConnectiveWords + "_" + rightSibling
            features['f11'] = c_rightSibling
            
            #Feature 12: Self Category + Parent Category
            selfCategory_parentCategory = selfCategory + "_" + parentCategory
            features['f12'] = selfCategory_parentCategory
            
            #Feature 13: Self Category + Left Sibling
            selfCategory_leftSibling = selfCategory + "_" + leftSibling
            features['f13'] = selfCategory_leftSibling
            
            #Feature 14: Self Category + Right Sibling
            selfCategory_rightSibling = selfCategory + "_" + rightSibling
            features['f14'] = selfCategory_rightSibling
            
            #Feature 15: Parent Category + Left Sibling
            parentCategory_leftSibling = parentCategory + "_" + leftSibling
            features['f15'] = parentCategory_leftSibling
            
            #Feature 16: Parent Category + Right Sibling
            parentCategory_rightSibling = parentCategory + "_" + rightSibling
            features['f16'] = parentCategory_rightSibling
            
            #Feature 17: Left Sibling + Right Sibling
            leftSibling_rightSibling = leftSibling + "_" + rightSibling
            features['f17'] = leftSibling_rightSibling
            
            if flag >= 0 and flag < 20:
                print "Raw String : " + relation['Arg2']['RawText'];
#                 print "Connective Word: " + parseObject['words'][connectiveWordIDs][0];
                print "Connective Word: " + strConnectiveWords;
                print "Features : " + str(features);
                flag += 1;
            
#             tup1 = ();
            if(trainOrTest == 'train'):
                #trainingSet.append('('+str(features)+','+str(label)+')');
                trainingSet.append((features, label));
            else:
                #testSet.append('('+str(features)+')');
                #testSet.append('('+str(features)+','+str(label)+')');
                testSet.append((features, label)); 
            
            #trainingSet.append((features, label));
            #featureSet.append(features);
            #labelSet.append(label);
        counter = counter + 1;
        
    print "Number of Explicit Relations: " + str(countOfExplicit);
    print "Number of multi-word connectives: " + str(multiWordConn) + ", " + '{:.2%}'.format(multiWordConn/countOfExplicit) 
    #print "Size of Feature Set: " + str(len(featureSet));
    #print "Size of Label Set: " + str(len(labelSet));
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
    classifier = nltk.MaxentClassifier.train(train, algorithm,max_iter=15)
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
    
if __name__ == '__main__':
    print ("Hello World");
    readInput('/home/development/data/conll16st-en-01-12-16-train', 'train');
    #readInput('D:\\Test\\CS6804\\conll16st-en-01-12-16-train', 'train');
    #print "Training Set: ", trainingSet;
    readInput('/home/development/data/conll16st-en-01-12-16-dev', 'test');
    #readInput('D:\\Test\\CS6804\\conll16st-en-01-12-16-dev', 'test');
    #print "Test Set: ", testSet; 
    classifyText(trainingSet, testSet);
    #test_maxent(nltk.classify.MaxentClassifier.ALGORITHMS, trainingSet, testSet);
    print "Done";
