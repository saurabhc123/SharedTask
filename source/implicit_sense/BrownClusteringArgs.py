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

def bcOneLineArgumentDataFirstIteration(relation, basicBCList,parses):
  lineDict = {}
  for arg1WordList in relation['Arg1']['TokenList']:
   arg1Word=parses[relation['DocID']]['sentences'][arg1WordList[3]]['words'][arg1WordList[4]][0].lower()
   for arg2WordList in relation['Arg2']['TokenList']:
      arg2Word=parses[relation['DocID']]['sentences'][arg2WordList[3]]['words'][arg2WordList[4]][0].lower()
      if arg1Word in basicBCList:
        arg1Group = basicBCList[arg1Word]        
        lineDict["Arg1_"+arg1Group] = 1
      if arg2Word in basicBCList:
        arg2Group = basicBCList[arg2Word]
        lineDict["Arg2_"+arg2Group] = 1
      if  arg2Word in basicBCList and arg1Word in basicBCList:
        if arg1Group == arg2Group:
          lineDict["Both_"+arg1Group] = 1
  return lineDict

def bcOneLineArgumentDataSecondIteration(relation, basicBCList, filterList,parses):
  lineDict = {}
  for arg1WordList in relation['Arg1']['TokenList']:
    parses[relation['DocID']]['sentences'][arg1WordList[3]]['words'][arg1WordList[4]]
    arg1Word=parses[relation['DocID']]['sentences'][arg1WordList[3]]['words'][arg1WordList[4]][0].lower()
    for arg2WordList in relation['Arg2']['TokenList']:
      arg2Word=parses[relation['DocID']]['sentences'][arg2WordList[3]]['words'][arg2WordList[4]][0].lower()
      if arg1Word in basicBCList:
        arg1Group = basicBCList[arg1Word]
        if "Arg1_"+arg1Group in filterList:
          lineDict["Arg1_"+arg1Group] = 1
      if arg2Word in basicBCList:
        arg2Group = basicBCList[arg2Word]
        if "Arg2_"+arg2Group in filterList:
          lineDict["Arg2_"+arg2Group] = 1
      if  arg2Word in basicBCList and arg1Word in basicBCList:
        if arg1Group == arg2Group:
          if "Both_"+arg1Group in filterList:
            lineDict["Both_"+arg1Group] = 1
  return lineDict
def createBaseBCDict(myDirectory):
    basicBCList={}
    if not os.path.isfile(myDirectory+'brownClustering.dat'):
      ifThisFunctionCausesACrashThenWeAreMissingTheBrownClusteringFile()
    f = open('brownClustering.dat')
    for line in f:
        splitline = line .split()
        group = splitline[0]
        word=splitline[1]
        count = splitline[2]
        basicBCList[word]=group
    f.close()
    return basicBCList


def create5OrLessBCRules(relations, parses,fileName ,cutoff,myDirectory):
    if not  os.path.isfile(fileName):
      baseBCDict=createBaseBCDict(myDirectory)
      allBCList = {}
      print "creating bc arg rules"
      #production rule tree:

      for relation in relations:
        lineData = bcOneLineArgumentDataFirstIteration(relation, baseBCDict,parses)
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
      print "finished bc arg rules"
    else:
      print "skipping generating bcargsrules.txt"
#reads rule list
    listOfBCRules={}
    f = open(fileName, 'r')
    for line in f:
      listOfBCRules[line[0:-1]]=0
    f.close()
    return listOfBCRules

def readFiles(path):

        print "reading parses"
        pdtb_file = codecs.open(path + 'parses.json', encoding='utf8');
        parses = json.load(pdtb_file)
        print "done"

        print "reading relations"
        relations = []
        with open(path+"relations.json") as f:
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


def calculateMI(bcRules5OrLess, parses, relations, fileName, numberOfRules,myDirectory):
  if not  os.path.isfile(fileName):
      baseBCDict =  createBaseBCDict(myDirectory)
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
           oneLine= bcOneLineArgumentDataSecondIteration(relation,baseBCDict, bcRules5OrLess,parses)           
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

