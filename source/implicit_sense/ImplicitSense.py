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
import pickle
import dependencyRules as dr
#import polarity_feature_extractor
LOW_FREQ_THRESHOLD = 5

polarityKeySet = set()

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

def implicitSenseExample():
   trainingParses = '/home/jtk0/competition2/development/data/conll16st-en-01-12-16-train/parses.json'
   trainingRelations = '/home/jtk0/competition2/development/data/conll16st-en-01-12-16-train/relations.json'
   myDirectory ='/home/jtk0/competition2/development/code/conll-shared-task/code/'
   
   testingParses = '/home/jtk0/competition2/development/data/conll16st-en-01-12-16-dev/parses.json'
#   testingRelations = '/home/jtk0/competition2/development/data/conll16st-en-01-12-16-dev/relations.json'
   testingRelations ='/home/jtk0/competition2/development/code/conll-shared-task/code/test.json' 
   result = '/home/jtk0/competition2/development/code/conll-shared-task/code/implicitResults.json'
   relationOrResult = "result"
   return   implicitSense(trainingParses, trainingRelations, myDirectory,testingParses, testingRelations, result, relationOrResult)

#Use this!!!!!
def implicitSense(testingRelations,testingParses, result):
  relationOrResult = "relation"
  trainingParses=None
  trainingRelation = None
  myDirectory = "implicit_sense/"
  classifier=training(trainingParses, trainingRelation, myDirectory)
  testing(classifier, testingParses, testingRelations,myDirectory,result,relationOrResult)
  return classifier

def training( parsesPath, relationsPath, myDirectory):

        if os.path.isfile(myDirectory+'ImplicitModel.model'):
           print 'loading model'
           a=pickle.load(open(myDirectory+'ImplicitModel.model', 'r'))
           print 'finished loading model'
           return a
        relations, parses = bc.readFiles(relationsPath, parsesPath)

        print "pruning away uncommon bc rules"
        fiveOrLessBCRules =bc.create5OrLessBCRules(relations,parses,myDirectory+"BCRules.txt", 5,myDirectory)
        print "Only finding high MI rules"
        baseBCDict = bc.createBaseBCDict(myDirectory)
        finalBCDict =  bc.calculateMI(fiveOrLessBCRules, parses,relations,myDirectory+'BCMIRules.txt', 50,myDirectory)

        print "pruning away uncommon bc rules"
        fiveOrLessBCArgsRules =bca.create5OrLessBCRules(relations,parses,myDirectory+"BCArgsRules.txt", 5,myDirectory)
        print "Only finding high MI rules"
        finalBCArgsDict =  bca.calculateMI(fiveOrLessBCArgsRules, parses,relations,myDirectory+'BCArgsMIRules.txt', 50,myDirectory)

        print "pruning away uncommon prod rules"
        fiveOrLessProdRules =pr.create5OrLessBCRules(relations,parses,myDirectory+"ProdRules.txt", 5)
        print "Only finding high MI rules"
        prodDict =  pr.calculateMI(fiveOrLessProdRules, relations,parses,myDirectory+'ProdMIRules.txt', 50)

        print "pruning away uncommon FL rules"
        fiveOrLessFLArgsRules =fl.create5OrLessBCRules(relations, parses,myDirectory+"FLRules.txt", 5)
        print "Only finding high MI rules"
        finalFLDict =  fl.calculateMI(fiveOrLessFLArgsRules, parses,relations,myDirectory+'FLMIRules.txt', 50)

        print "pruning away uncommon dependency rules"
        fiveOrLessDRArgsRules =dr.create5OrLessBCRules(relations, parses,myDirectory+"DRRules.txt", 5)
        print "Only finding high dependency rules"
        finalDRDict =  dr.calculateMI(fiveOrLessDRArgsRules, relations,parses,myDirectory+'DRMIRules.txt', 50)

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
                features.update(bc.bcOneLinePairDataSecondIteration(relation,baseBCDict,finalBCDict, parses))

                features.update(finalBCArgsDict)
                features.update(bca.bcOneLineArgumentDataSecondIteration(relation,baseBCDict,finalBCArgsDict,parses))

                features.update(prodDict)
                features.update(pr.bcOneLinePairDataSecondIteration(relation,parses,prodDict))
 
                features.update(finalFLDict)
                features.update(fl.bcOneLinePairDataSecondIteration(relation,None,finalFLDict,parses))

                features.update(finalDRDict)
                features.update(dr.bcOneLinePairDataSecondIteration(relation,parses,finalDRDict))
 
#                polarityFeatures, polarityKeySet = polarity_feature_extractor.get_polarity_features(relation, parses)
#                features.update(polarityFeatures)

                allFeatures.append((features,getSense(relation)) )

#----------------features end here
#        for item in polarityKeySet:
#            prune(item, allFeatures)

        print "training start"
        classifier =   nltk.classify.NaiveBayesClassifier.train(allFeatures)
        #classifier =   nltk.classify.MaxentClassifier.train(allFeatures,max_iter=12, trace=3)

        print "training done"  
        pickle.dump( classifier, open(myDirectory+'ImplicitModel.model', 'w+'))
        return classifier

def testing(classifier, parses,relations, myDirectory,finalFile,relationOrResult):
        print "starting testing"

        baseBCDict = bc.createBaseBCDict(myDirectory)
        testingRelations, testingParses = bc.readFiles(relations, parses)

        print "pruning away uncommon bc rules"
        fiveOrLessBCArgsRules =bca.create5OrLessBCRules(testingRelations,testingParses,myDirectory+"BCArgsRules.txt", 5,myDirectory)
        print "Only finding high MI rules"
        finalBCArgsDict =  bca.calculateMI(fiveOrLessBCArgsRules, testingParses,testingRelations,myDirectory+'BCArgsMIRules.txt', 30,myDirectory)

        print "pruning away uncommon bc rules"
        fiveOrLessBCRules =bc.create5OrLessBCRules(None,testingParses,myDirectory+"BCRules.txt", 10,myDirectory)
        print "Only finding high MI rules"
        finalBCDict =  bc.calculateMI(fiveOrLessBCRules, testingParses,None,myDirectory+'BCMIRules.txt', 30,myDirectory)

        print "pruning away uncommon prod rules"
        fiveOrLessProdRules =pr.create5OrLessBCRules(testingRelations,testingParses,myDirectory+"ProdRules.txt", 5)
        print "Only finding high MI rules"
        prodDict =  pr.calculateMI(fiveOrLessProdRules, testingRelations,testingParses,myDirectory+'ProdMIRules.txt', 30)

        print "pruning away uncommon FL rules"
        fiveOrLessFLArgsRules =fl.create5OrLessBCRules(testingRelations, testingParses,myDirectory+"FLRules.txt", 5)
        print "Only finding high MI rules"
        finalFLDict =  fl.calculateMI(fiveOrLessFLArgsRules, testingParses,testingRelations,myDirectory+'FLMIRules.txt', 30)

        print "pruning away uncommon dependency rules"
        fiveOrLessDRArgsRules =dr.create5OrLessBCRules(testingRelations, testingParses, myDirectory+"DRRules.txt", 5)
        print "Only finding high dependency rules"
        finalDRDict =  dr.calculateMI(fiveOrLessDRArgsRules, testingRelations,testingParses,myDirectory+'DRMIRules.txt', 50)

        allFeatures = []
        print "generating features"
        testingCount = 0
        correct = 0
        wrong = 0
        print finalFile
        finalFile =open(finalFile,'w+')
        for testRelation in testingRelations:

          result = None
          testingCount = testingCount +1
          try:
            if testingCount %100 ==0:
              print testingCount
            if 'Type' in testRelation and testRelation['Type'] == 'Explicit':
              json.dump(testRelation, finalFile);
              finalFile.write("\n");
              continue
            if (not 'Type' in testRelation) or testRelation['Type'] == 'Implicit'  or testRelation['Type'] == 'AltLex' or testRelation['Type'] == "EntRel":
#----------------make sure this is the same as above
              features = {}
              features.update(finalBCDict)
              features.update(bc.bcOneLinePairDataSecondIteration(testRelation,baseBCDict,finalBCDict, testingParses))
  
              features.update(finalBCArgsDict)
              features.update(bca.bcOneLineArgumentDataSecondIteration(testRelation,baseBCDict,finalBCArgsDict, testingParses))
              
              features.update(prodDict)
              features.update(pr.bcOneLinePairDataSecondIteration(testRelation,testingParses,prodDict))
 
              features.update(finalFLDict)
              features.update(fl.bcOneLinePairDataSecondIteration(testRelation,None,finalFLDict,testingParses))

              features.update(finalDRDict)
              features.update(dr.bcOneLinePairDataSecondIteration(testRelation,testingParses,finalDRDict))

#            polarityFeatures, polarityKeySet = polarity_feature_extractor.get_polarity_features(testRelation, testingParses)
#            features.update(polarityFeatures)

#--------------------------------           
              result = classifier.classify(features)
              if  'Type' in testRelation:
                if [result] == [getSense(testRelation)]:
                  correct = correct +1
                else:
                  wrong = wrong +1
          except:
            print "THERE WAS AN ERROR!!!!!!!!!!!!!! RELATION IS:",testRelation
            continue
          #    print correct, wrong, [result], getSense(testRelation)
          if 'Type' in testRelation: 
            connectiveType = testRelation['Type']
          else:
            connectiveType = 'Implicit'
          arg1TokenList = testRelation['Arg1']['TokenList'];
          arg2TokenList = testRelation['Arg2']['TokenList'];
          relationDocId = testRelation['DocID'];
          relationSense = None
          if result ==None:
            relationSense= testRelation['Sense']
            continue
          else:
            relationSense=[result] 
          
          if relationOrResult == "relation":
            finalResult = {}
            finalResult["Arg1"]={}
            finalResult["Arg1"]["TokenList"]= arg1TokenList
            finalResult["Arg2"]={}
            finalResult["Arg2"]["TokenList"]= arg2TokenList
            finalResult["Connective"]={}
            finalResult["Connective"]["TokenList"]=[]
            finalResult["Connective"]["CharacterSpanList"]=[]
            finalResult["DocID"]=relationDocId
            finalResult["ID"]=200000+wrong+correct
            finalResult["Sense"]= relationSense
            if relationSense == ["EntRel"]:
              finalResult["Type"] = "EntRel"
            else:
              finalResult["Type"] = "Implicit"

            json.dump(finalResult , finalFile);
          elif relationOrResult=="result":
            connectiveTokenList = []#list(map(lambda tokenList: tokenList[2], testRelation['Connective']['TokenList']))
            arg1TokenListFinal = map(lambda tokenList: tokenList[2], arg1TokenList) ;
            arg2TokenListFinal = map(lambda tokenList: tokenList[2], arg2TokenList) ;
            result="EntRel"
            output =  outputRecord.OutputRecord.loadFromParameters(relationDocId, relationSense, connectiveType, [], arg1TokenListFinal, arg2TokenListFinal);
            formattedOutput = output.getFormattedOutput();
            json.dump(formattedOutput , finalFile);
          else:
            ThisShouldntHappenrelationOrResultIsIncorrect()
 
          finalFile.write("\n");


def getSense(relation):
    sense = relation['Sense']
    return sense[0]
