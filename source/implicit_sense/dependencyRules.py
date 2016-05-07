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
from nltk.stem.porter import PorterStemmer
def bcOneLinePairDataFirstIteration(relation, parses):
  lineDict = {}

  docId = relation['DocID']
  previousSentenceNumber = -1
  dependencyRules = None
  for tokenList in relation['Arg1']['TokenList']:
    sentenceNumber = tokenList[3] 
    if not sentenceNumber == previousSentenceNumber:
      dependencyRules = createDependencyTree(parses, docId, sentenceNumber)
    position = tokenList[4] 
    if dependencyRules[position]== None:
      continue
    line = dependencyRules[position][3]+'->'
    loopPrevention = 0 
    skip = False
    while not (dependencyRules[position] == None or dependencyRules[position][0] == 'root'or dependencyRules[position][0] == 'subroot'):
      if loopPrevention < 10:
        loopPrevention=loopPrevention+1
      else:
        skip = True
        break
      if skip:
        continue
      line = line+ dependencyRules[position][0]+","
      position = dependencyRules[position][2]
      lineDict ['Arg1:'+line]=1

  previousSentenceNumber = -1
  for tokenList in relation['Arg2']['TokenList']:
    sentenceNumber = tokenList[3]
    if not sentenceNumber == previousSentenceNumber:
      dependencyRules = createDependencyTree(parses, docId, sentenceNumber)
    position = tokenList[4]
    if position == -1 or dependencyRules[position]== None:
      continue
 
    line = dependencyRules[position][3]+'->'
    loopPrevention = 0
    skip = False
    while not (dependencyRules[position]==None or dependencyRules[position][0] == 'root'or dependencyRules[position][0] == 'subroot'):
      if loopPrevention < 10:
        loopPrevention=loopPrevention+1
      else:
        skip = True
        break
      if skip:
        continue
      line = line+ dependencyRules[position][0]+","
      position = dependencyRules[position][2]
      lineDict ['Arg2:'+line]=1

  return lineDict 

def bcOneLinePairDataSecondIteration(relation, parses,filterList):
  lineDict = {}

  docId = relation['DocID']
  previousSentenceNumber = -1
  dependencyRules = None
  for tokenList in relation['Arg1']['TokenList']:
    sentenceNumber = tokenList[3]
    if not sentenceNumber == previousSentenceNumber:
      dependencyRules = createDependencyTree(parses, docId, sentenceNumber)
    position = tokenList[4]
    if dependencyRules[position]== None:
      continue
    line = dependencyRules[position][3]+'->'
    loopPrevention = 0
    skip = False
    while not (dependencyRules[position] == None or dependencyRules[position][0] == 'root'or dependencyRules[position][0] == 'subroot'):
      if loopPrevention < 10:
        loopPrevention=loopPrevention+1
      else:
        skip = True
        break
      if skip:
        continue
      line = line+ dependencyRules[position][0]+","
      position = dependencyRules[position][2]
      if 'Arg1:'+line in filterList:
        lineDict ['Arg1:'+line]=1

  previousSentenceNumber = -1
  for tokenList in relation['Arg2']['TokenList']:
    sentenceNumber = tokenList[3]
    if not sentenceNumber == previousSentenceNumber:
      dependencyRules = createDependencyTree(parses, docId, sentenceNumber)
    position = tokenList[4]
    if position == -1 or dependencyRules[position]== None:
      continue

    line = dependencyRules[position][3]+'->'
    loopPrevention = 0
    skip = False
    while not (dependencyRules[position]==None or dependencyRules[position][0] == 'root'or dependencyRules[position][0] == 'subroot'):
      if loopPrevention < 10:
        loopPrevention=loopPrevention+1
      else:
        skip = True
        break
      if skip:
        continue
      line = line+ dependencyRules[position][0]+","
      position = dependencyRules[position][2]
      if 'Arg2:'+line in filterList:
        lineDict ['Arg2:'+line]=1

  return lineDict

def createDependencyTree(parses, docId, sentenceNumber):
  maxPos=0


  for depNode in parses[docId]['sentences'][sentenceNumber]['dependencies']:
    position=int(depNode[1].split('-')[-1])
    maxPos = max(maxPos,position)+50

  dependencyTree = [None]*(maxPos+2)

  for depNode in parses[docId]['sentences'][sentenceNumber]['dependencies']:
    tempArray = [depNode[0],depNode[1].split('-')[0].lower(),int(depNode[1].split('-')[-1])-1, depNode[2].split('-')[0].lower(),int(depNode[2].split('-')[-1])-1]
    try:
      dependencyTree[int(depNode[2].split('-')[-1])-1] = tempArray #append(tempArray)
    except:
      pass
#  for node in enumerate(dependencyTree):
#    if dependencyTree[node[2]]==None:
#      dependencyTree[node[2]] = ['subroot', 'subroot', 0, dependencyTree[node[1]],dependencyTree[node[2]]]
  return dependencyTree    
def create5OrLessBCRules(relations, parses, fileName = 'BCrules.txt',cutoff=10):
    if not  os.path.isfile(fileName):
      allBCList = {}
      print "creating bc rules"
      #production rule tree:

      for relation in relations:
        lineData = bcOneLinePairDataFirstIteration(relation, parses)
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

def calculateMI(bcRules5OrLess, relations, parses,fileName, numberOfRules):
  if not  os.path.isfile(fileName):
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
           oneLine= bcOneLinePairDataSecondIteration(relation,parses, bcRules5OrLess)
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
