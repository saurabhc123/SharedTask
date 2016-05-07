import numpy 
import codecs
import json
# import ParsedInput
import nltk
from nltk.tree import *
import collections
# import scikit-learn
from sklearn import cross_validation
import nltk.metrics
from nltk.metrics import precision, recall, f_measure
import sys
import NlpUtils
import Sentence
import os.path
import math
import operator
import BrownClustering as bc
import ProdRules as pr
import outputRecord
import BrownClusteringArgs as bca
import firstLast as fl

def training( relations=None, parses=None):
        trainingPath =  '/home/jtk0/competition2/development/data/conll16st-en-01-12-16-train/'
        if (relations ==None or parses==None):
          relations, parses = bc.readFiles(trainingPath)
        print "pruning away uncommon bc rules"
        fiveOrLessBCRules =bc.create5OrLessBCRules(relations,trainingPath,"BCRules.txt", 5)
        print "Only finding high MI rules"
        baseBCDict = bc.createBaseBCDict()
        finalBCDict =  bc.calculateMI(fiveOrLessBCRules, trainingPath,relations,'BCMIRules.txt', 40)

        print "pruning away uncommon bc rules"
        fiveOrLessBCArgsRules =bca.create5OrLessBCRules(relations,trainingPath,"BCArgsRules.txt", 5)
        print "Only finding high MI rules"
        finalBCArgsDict =  bca.calculateMI(fiveOrLessBCArgsRules, trainingPath,relations,'BCArgsMIRules.txt', 50)

        print "pruning away uncommon prod rules"
        fiveOrLessProdRules =pr.create5OrLessBCRules(relations,parses,trainingPath,"ProdRules.txt", 5)
        print "Only finding high MI rules"
        prodDict =  pr.calculateMI(fiveOrLessProdRules, trainingPath,relations,parses,'ProdMIRules.txt', 50)

        print "pruning away uncommon FL rules"
        fiveOrLessFLArgsRules =fl.create5OrLessBCRules(relations,trainingPath,"FLRules.txt", 5)
        print "Only finding high MI rules"
        finalFLDict =  fl.calculateMI(fiveOrLessFLArgsRules, trainingPath,relations,'FLMIRules.txt', 50)

        allFeatures = []
        print "generating features"
        counter = 0
        classifier = None
        for relation in relations:
            if relation['Type'] == 'Implicit' or relation['Type'] == 'AltLex' or relation['Type'] == "EntRel":
                if counter%100==0 and counter>0:
                  print counter

                counter = counter+1
#----------------features go here
                features = {}
                features.update(finalBCDict)
                features.update(bc.bcOneLinePairDataSecondIteration(relation,baseBCDict,finalBCDict,trainingPath))

                features.update(finalBCArgsDict)
                features.update(bca.bcOneLineArgumentDataSecondIteration(relation,baseBCDict,finalBCArgsDict,trainingPath))

#                features.update(pr.firstLast(relation['Arg1'], relation['Arg2'],trainingPath+'/raw/'+relation['DocID']))
                features.update(prodDict)
                features.update(pr.bcOneLinePairDataSecondIteration(relation,parses,prodDict,trainingPath))
 
                features.update(finalFLDict)
                features.update(fl.bcOneLinePairDataSecondIteration(relation,None,finalFLDict,trainingPath))
                allFeatures.append((features,getSense(relation)) )

#----------------features end here
        print "training start"
        classifier =   nltk.classify.NaiveBayesClassifier.train(allFeatures)
        #classifier =   nltk.classify.MaxentClassifier.train(allFeatures,max_iter=12, trace=3)

        print "training done"
        return classifier

def testing(classifier):
        print "starting testing"
        testingPath = "/home/jtk0/competition2/development/data/conll16st-en-01-12-16-dev/"

        baseBCDict = bc.createBaseBCDict()
        testingRelations, testingParses = bc.readFiles(testingPath)

        print "pruning away uncommon bc rules"
        fiveOrLessBCArgsRules =bca.create5OrLessBCRules(testingRelations,testingPath,"BCArgsRules.txt", 5)
        print "Only finding high MI rules"
        finalBCArgsDict =  bca.calculateMI(fiveOrLessBCArgsRules, testingPath,testingRelations,'BCArgsMIRules.txt', 20)

        print "pruning away uncommon bc rules"
        fiveOrLessBCRules =bc.create5OrLessBCRules(None,testingPath,"BCRules.txt", 10)
        print "Only finding high MI rules"
        finalBCDict =  bc.calculateMI(fiveOrLessBCRules, testingPath,None,'BCMIRules.txt', 30)

        print "pruning away uncommon prod rules"
        fiveOrLessProdRules =pr.create5OrLessBCRules(testingRelations,testingPath,testingParses,"ProdRules.txt", 5)
        print "Only finding high MI rules"
        prodDict =  pr.calculateMI(fiveOrLessProdRules, testingPath,testingRelations,testingParses,'ProdMIRules.txt', 20)

        print "pruning away uncommon FL rules"
        fiveOrLessFLArgsRules =fl.create5OrLessBCRules(testingRelations,testingPath,"FLRules.txt", 5)
        print "Only finding high MI rules"
        finalFLDict =  fl.calculateMI(fiveOrLessFLArgsRules, testingPath,testingRelations,'FLMIRules.txt', 30)

        allFeatures = []
        print "generating features"

        testingCount = 0
        correct = 0
        wrong = 0
        finalFile =open("implicitSenseResult.json",'w+')
        for testRelation in testingRelations:
          result = None
          testingCount = testingCount +1
          if testingCount %100 ==0:
            print testingCount
          if testRelation['Type'] == 'Implicit'  or testRelation['Type'] == 'AltLex' or testRelation['Type'] == "EntRel":
#----------------make sure this is the same as above
            features = {}
            features.update(finalBCDict)
            features.update(bc.bcOneLinePairDataSecondIteration(testRelation,baseBCDict,finalBCDict,testingPath))

            features.update(finalBCArgsDict)
            features.update(bca.bcOneLineArgumentDataSecondIteration(testRelation,baseBCDict,finalBCArgsDict,testingPath))
            
            features.update(prodDict)
            features.update(pr.bcOneLinePairDataSecondIteration(testRelation,testingParses,prodDict,testingPath))
 
            features.update(finalFLDict)
            features.update(fl.bcOneLinePairDataSecondIteration(testRelation,None,finalFLDict,testingPath))

#--------------------------------           
            result = classifier.classify(features)
            if [result] == [getSense(testRelation)]:
              correct = correct +1
            else:
             wrong = wrong +1
            print correct, wrong, [result], getSense(testRelation)
          connectiveType = testRelation['Type']
          arg1TokenList = testRelation['Arg1']['TokenList'];
          arg2TokenList = testRelation['Arg2']['TokenList'];
          relationDocId = testRelation['DocID'];
          relationSense = None
          if result ==None:
            relationSense= 'Temporal'#testRelation['Sense']
          else:
            relationSense=[result] 
          connectiveTokenList = list(map(lambda tokenList: tokenList[2], testRelation['Connective']['TokenList']))
          arg1TokenListFinal = map(lambda tokenList: tokenList[2], arg1TokenList) ;
          arg2TokenListFinal = map(lambda tokenList: tokenList[2], arg2TokenList) ;

          output =  outputRecord.OutputRecord.loadFromParameters(relationDocId, relationSense, connectiveType, connectiveTokenList, arg1TokenListFinal, arg2TokenListFinal);
          formattedOutput = output.getFormattedOutput();
          json.dump(formattedOutput , finalFile);
          finalFile.write("\n");


def getSense(relation):
    sense = relation['Sense']
    return sense[0]
