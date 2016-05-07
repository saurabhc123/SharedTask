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

def bcOneLinePairDataFirstIteration(relation, basicBCList,parses):
  lineDict = {}
  for arg1WordList in relation['Arg1']['TokenList']:
    arg1Word=parses[relation['DocID']]['sentences'][arg1WordList[3]]['words'][arg1WordList[4]][0].lower()
    for arg2WordList in relation['Arg2']['TokenList']:
      arg2Word=parses[relation['DocID']]['sentences'][arg2WordList[3]]['words'][arg2WordList[4]][0].lower()
      if (arg1Word in basicBCList) and (arg2Word in basicBCList):
        arg1Group = basicBCList[arg1Word]
        arg2Group = basicBCList[arg2Word]
        lineDict[arg1Group+'_'+arg2Group]=1
  return lineDict
def bcOneLinePairDataSecondIteration(relation, basicBCList,filterList,parses):
#  lineDict = filterList.copy()
  lineDict = {}
  for arg1WordList in relation['Arg1']['TokenList']:
    arg1Word=parses[relation['DocID']]['sentences'][arg1WordList[3]]['words'][arg1WordList[4]][0].lower()
    try:
      for arg2WordList in relation['Arg2']['TokenList']:
        arg2Word=parses[relation['DocID']]['sentences'][arg2WordList[3]]['words'][arg2WordList[4]][0].lower()
        if (arg1Word in basicBCList) and (arg2Word in basicBCList):
          arg1Group = basicBCList[arg1Word]
          arg2Group = basicBCList[arg2Word]
       
          if arg1Group+'_'+arg2Group in filterList:
            lineDict[arg1Group+'_'+arg2Group]=1
    except:
      print relation  
  return lineDict

def createBaseBCDict(implicitDirectory):
    basicBCList={}
    if not os.path.isfile(implicitDirectory+'brownClustering.dat'):
      ifThisFunctionCausesACrashThenWeAreMissingTheBrownClusteringFile()
    f = open(implicitDirectory+'brownClustering.dat')
    for line in f:
        splitline = line .split()
        group = splitline[0]
        word=splitline[1]
        count = splitline[2]
        basicBCList[word]=group
    f.close()
    return basicBCList


def create5OrLessBCRules(relations, parses,fileName ,cutoff, myDirectory):
    if not  os.path.isfile(fileName):
      baseBCDict=createBaseBCDict(myDirectory)
      allBCList = {}
      print "creating bc rules"
      #production rule tree:

      for relation in relations:
        lineData = bcOneLinePairDataFirstIteration(relation, baseBCDict, parses)
        for column in lineData:
          if column in allBCList:
            allBCList[column] = allBCList[column]+1
          else:
            allBCList[column]=1

      f = open(fileName,'w+')
      for key in allBCList:
        if allBCList[key] >cutoff:
          f.write(key+'\n')
      f.close()
      print "finished bc rules"
    else:
      print "skipping generating bcrules.txt"
#reads rule list
    listOfBCRules={}
    f = open(fileName, 'r')
    for line in f:
      listOfBCRules[line[0:-1]]=0
    f.close()
    return listOfBCRules

def readFiles(relationsPath, parsesPath):

        print "reading parses"
        pdtb_file = codecs.open(parsesPath, encoding='utf8');
        parses = json.load(pdtb_file)
        print "done"

        print "reading relations"
        relations = []
        with open(relationsPath) as f:
               for line in f:
                 relations.append(json.loads(line))
        print "done"
        return relations, parses


def getSense(relation):
    feature = None
    sense = relation['Sense']
    senseSplit = sense[0].split('.')
    if len(senseSplit)==1:
      feature=sense[0]
    else:
      feature= senseSplit[0]+'.'+senseSplit[1]
    return feature

def calculateMI(bcRules5OrLess, parses, relations, fileName, numberOfRules, currentDirectory):
  if not  os.path.isfile(fileName):
      baseBCDict =  createBaseBCDict(currentDirectory)
      print "generating BC MI File"
      senses = ['Comparison', 'Comparison.Concession','Comparison.Contrast','Contingency','Contingency.Cause','Contingency.Condition','EntRel','Expansion','Expansion.Alternative','Expansion.Conjunction','Expansion.Exception','Expansion.Instantiation','Expansion.Restatement','Temporal','Temporal.Asynchronous','Temporal.Synchrony',]
      totalCountSense = {}
      sensesRules = {}
      for sense in senses:
          totalCountSense[sense]=0
          sensesRules[sense]={}
#def bcOneLinePairData(relation, basicBCList,rawFilePath)
      for relation in relations:

         if (relation['Type'] == 'Implicit' or relation['Type'] == 'AltLex' or relation['Type'] == "EntRel" ):
           sense = getSense(relation)
           if sense in senses:
             totalCountSense[sense]=totalCountSense[sense]+1
           else:
             continue
           oneLine= bcOneLinePairDataSecondIteration(relation,baseBCDict, bcRules5OrLess, parses)
           for rule in oneLine:
             if rule in sensesRules[sense]:
               sensesRules[sense][rule]=sensesRules[sense][rule]+1
#               sensesRules[sense][rule]=sensesRules[sense][rule]+oneLine[rule]
             else:
#               sensesRules[sense][rule]=oneLine[rule]
               sensesRules[sense][rule]=1

             #At this point totalCountSense is the total count of each sense
             #sensesRules in a dictionary of each sense rule

      finalList = {}
      for sense in senses:
           tempList = {}
           pY = totalCountSense[sense]
           for ruleKey in sensesRules[sense]:
             pXY=sensesRules[sense][ruleKey]
             pX=0
             for tempsense in senses:
               if ruleKey in sensesRules[tempsense]:
                 pX=pX+sensesRules[tempsense][ruleKey]
             if pX==0 or pY==0 or pXY==0:
               MI=0*pXY
             else:
               MI = 1*math.log(1.0*pXY/(1.*pX*pY))
             tempList[ruleKey]=MI
           sortedMI = sorted(tempList.items(), key=operator.itemgetter(1))
           sortedMI.reverse()#largest to smallest
           for i,rule in enumerate(sortedMI):
             if i<numberOfRules:
               finalList[rule[0]]=0
      print "finalRule size is "+str(len(finalList))+".  at max it could be"+ str(numberOfRules*len(senses))
      f = open(fileName,'w+')
      for rule in finalList:
              f.write(rule+'\n')
      f.close()
      print totalCountSense


  else:
    print "skipping generating BC MI file"
  finalDictionary = {}
  f = open(fileName,'r')
  for rule in f:
    finalDictionary[rule.strip()]=0
  return finalDictionary
