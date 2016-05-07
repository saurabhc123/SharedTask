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
def bcOneLinePairDataFirstIteration(relation, basicBCList,parses):
  stemmer= PorterStemmer()
  lineDict = {}
#  arg1Word=parses[relation['DocID']]['sentences'][arg1WordList[3]]['words'][arg1WordList[4]][0].lower()

  firstWord1 = lastWord1 =thirdWord1=thirdLastWord1 = firstWord2 = secondWord2 = thirdWord2 = secondWord1 =secondLastWord1 ='NONE'
  if len(relation['Arg1']['TokenList'])>=1:
    firstWordList = relation['Arg1']['TokenList'][0]
    firstWord1 =   stemmer.stem(parses[relation['DocID']]['sentences'][firstWordList[3]]['words'][firstWordList[4]][0]).lower()
    lastWordList = relation['Arg1']['TokenList'][-1]
    lastWord1 =   stemmer.stem(parses[relation['DocID']]['sentences'][lastWordList[3]]['words'][lastWordList[4]][0]).lower()

  if len(relation['Arg1']['TokenList'])>=2:
    secondWordList = relation['Arg1']['TokenList'][1]
    secondWord1 =   stemmer.stem(parses[relation['DocID']]['sentences'][secondWordList[3]]['words'][secondWordList[4]][0]).lower()
    secondLastWordList = relation['Arg1']['TokenList'][-2]
    secondLastWord1 =  stemmer.stem(parses[relation['DocID']]['sentences'][secondLastWordList[3]]['words'][secondLastWordList[4]][0]).lower()

  if len(relation['Arg1']['TokenList'])>=3:
    thirdWordList = relation['Arg1']['TokenList'][2]
    thirdWord1 =   stemmer.stem(parses[relation['DocID']]['sentences'][thirdWordList[3]]['words'][thirdWordList[4]][0]).lower()
    thirdLastWordList = relation['Arg1']['TokenList'][-3]
    thirdLastWord1 =  stemmer.stem(parses[relation['DocID']]['sentences'][thirdLastWordList[3]]['words'][thirdLastWordList[4]][0]).lower()

  
  if len(relation['Arg2']['TokenList'])>=1:
    firstWordList = relation['Arg2']['TokenList'][0]
    firstWord2 =   stemmer.stem(parses[relation['DocID']]['sentences'][firstWordList[3]]['words'][firstWordList[4]][0]).lower()
  if len(relation['Arg2']['TokenList'])>=2:
    secondWordList = relation['Arg2']['TokenList'][1]
    secondWord2 =   stemmer.stem(parses[relation['DocID']]['sentences'][secondWordList[3]]['words'][secondWordList[4]][0]).lower()
  if len(relation['Arg2']['TokenList'])>=3:
    thirdWordList = relation['Arg2']['TokenList'][2]
    thirdWord2 =  stemmer.stem(parses[relation['DocID']]['sentences'][thirdWordList[3]]['words'][thirdWordList[4]][0]).lower()

  firstArg2="a2f1:"+firstWord2
  firstTwoArg2="a2f2:"+firstWord2+secondWord2
  firstThreeArg3="a2f3:"+firstWord2+secondWord2+thirdWord2
  lastArg1="a1l1:"+lastWord1
  lastArg2="a1l2:"+secondLastWord1+lastWord1
  lastArg3="a1l3:"+thirdLastWord1+secondLastWord1+lastWord1
  first1Both="a12f1:"+firstWord1+firstWord2
  first2Both="a12f2:"+firstWord1+secondWord1+firstWord2+secondWord2
  first3Both="a12f3:"+firstWord1+secondWord1+thirdWord1+firstWord2+secondWord2+thirdWord2
  firstLastBoth="a1l1a2f1"+lastWord1+firstWord2
  firstLast2Both="a1l2a2f2"+secondLastWord1+lastWord1+firstWord2+secondWord2
  firstLast3Both="a1l3a2f3"+thirdLastWord1+secondLastWord1+lastWord1+firstWord2+secondWord2+thirdWord2
  lineDict[first1Both]=1
  lineDict[first2Both]=1
  lineDict[first3Both]=1
  lineDict[firstLastBoth]=1
  lineDict[firstLast2Both]=1
  lineDict[firstLast3Both]=1

  lineDict[firstArg2]=1
  lineDict[firstTwoArg2]=1
  lineDict[firstThreeArg3]=1
  lineDict[lastArg1]=1
  lineDict[lastArg2]=1
  lineDict[lastArg3]=1
  return lineDict
def bcOneLinePairDataSecondIteration(relation, basicBCList,filterList,parses):
  stemmer= PorterStemmer()
  lineDict = {}
#  arg1Word=parses[relation['DocID']]['sentences'][arg1WordList[3]]['words'][arg1WordList[4]][0].lower()

  firstWord1 = lastWord1 =thirdWord1=thirdLastWord1 = firstWord2 = secondWord2 = thirdWord2 = secondWord1 =secondLastWord1 ='NONE'
  if len(relation['Arg1']['TokenList'])>=1:
    firstWordList = relation['Arg1']['TokenList'][0]
    firstWord1 =   stemmer.stem(parses[relation['DocID']]['sentences'][firstWordList[3]]['words'][firstWordList[4]][0]).lower()
    lastWordList = relation['Arg1']['TokenList'][-1]
    lastWord1 =   stemmer.stem(parses[relation['DocID']]['sentences'][lastWordList[3]]['words'][lastWordList[4]][0]).lower()

  if len(relation['Arg1']['TokenList'])>=2:
    secondWordList = relation['Arg1']['TokenList'][1]
    secondWord1 =   stemmer.stem(parses[relation['DocID']]['sentences'][secondWordList[3]]['words'][secondWordList[4]][0]).lower()
    secondLastWordList = relation['Arg1']['TokenList'][-2]
    secondLastWord1 =  stemmer.stem(parses[relation['DocID']]['sentences'][secondLastWordList[3]]['words'][secondLastWordList[4]][0]).lower()

  if len(relation['Arg1']['TokenList'])>=3:
    thirdWordList = relation['Arg1']['TokenList'][2]
    thirdWord1 =   stemmer.stem(parses[relation['DocID']]['sentences'][thirdWordList[3]]['words'][thirdWordList[4]][0]).lower()
    thirdLastWordList = relation['Arg1']['TokenList'][-3]
    thirdLastWord1 =  stemmer.stem(parses[relation['DocID']]['sentences'][thirdLastWordList[3]]['words'][thirdLastWordList[4]][0]).lower()


  if len(relation['Arg2']['TokenList'])>=1:
    firstWordList = relation['Arg2']['TokenList'][0]
    firstWord2 =   stemmer.stem(parses[relation['DocID']]['sentences'][firstWordList[3]]['words'][firstWordList[4]][0]).lower()
  if len(relation['Arg2']['TokenList'])>=2:
    secondWordList = relation['Arg2']['TokenList'][1]
    secondWord2 =   stemmer.stem(parses[relation['DocID']]['sentences'][secondWordList[3]]['words'][secondWordList[4]][0]).lower()
  if len(relation['Arg2']['TokenList'])>=3:
    thirdWordList = relation['Arg2']['TokenList'][2]
    thirdWord2 =  stemmer.stem(parses[relation['DocID']]['sentences'][thirdWordList[3]]['words'][thirdWordList[4]][0]).lower()


  firstArg2="a2f1:"+firstWord2
  firstTwoArg2="a2f2:"+firstWord2+secondWord2
  firstThreeArg3="a2f3:"+firstWord2+secondWord2+thirdWord2
  lastArg1="a1l1:"+lastWord1
  lastArg2="a1l2"+secondLastWord1+lastWord1
  lastArg3="a1l3"+thirdLastWord1+secondLastWord1+lastWord1

  first1Both="a12f1:"+firstWord1+firstWord2
  first2Both="a12f2:"+firstWord1+secondWord1+firstWord2+secondWord2
  first3Both="a12f3:"+firstWord1+secondWord1+thirdWord1+firstWord2+secondWord2+thirdWord2
  firstLastBoth="a1l1a2f1"+lastWord1+firstWord2
  firstLast2Both="a1l2a2f2"+secondLastWord1+lastWord1+firstWord2+secondWord2
  firstLast3Both="a1l3a2f3"+thirdLastWord1+secondLastWord1+lastWord1+firstWord2+secondWord2+thirdWord2
  if first1Both in filterList:
    lineDict[first1Both]=1
  if first2Both in filterList:
    lineDict[first2Both]=1
  if first3Both in filterList:
    lineDict[first3Both]=1
  if firstLastBoth in filterList:
    lineDict[firstLastBoth]=1
  if firstLast2Both in filterList:
    lineDict[firstLast2Both]=1
  if firstLast3Both in filterList:
    lineDict[firstLast3Both]=1
 
  if firstArg2 in filterList:
    lineDict[firstArg2]=1
  if firstTwoArg2 in filterList:
    lineDict[firstTwoArg2]=1
  if firstThreeArg3 in filterList:
    lineDict[firstThreeArg3]=1
  if lastArg1 in filterList:
    lineDict[lastArg1]=1
  if lastArg2 in filterList:
    lineDict[lastArg2]=1
  if lastArg3 in filterList:
    lineDict[lastArg3]=1

  return lineDict

def create5OrLessBCRules(relations, parses,fileName = 'BCrules.txt',cutoff=10):
    if not  os.path.isfile(fileName):
      allBCList = {}
      print "creating bc rules"
      #production rule tree:

      for relation in relations:
        lineData = bcOneLinePairDataFirstIteration(relation, None,parses)
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

def calculateMI(bcRules5OrLess, parses, relations, fileName, numberOfRules):
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
           oneLine= bcOneLinePairDataSecondIteration(relation,None, bcRules5OrLess,parses)
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
