import codecs
import json
# import ParsedInput
import nltk
from nltk.tree import *
# import scikit-learn
import nltk.metrics
import os.path

errorCount = 0
listOfProdRules ={}
listOfProdBuildingRules = {}
		
#Adds all rules in pTreeRoot into rulesDict
def buildProdRules(pTreeRoot, rulesDict):
  rule = pTreeRoot.label()+" -> "
  hasChild = False
  for children in pTreeRoot:
    if hasattr(children, 'label'):
      rule = rule + children.label()+", "
      buildProdRules(children,rulesDict)
      hasChild=True
  if hasChild:
    if rule in rulesDict:
      rulesDict[rule]=rulesDict[rule]+1
    else:
      rulesDict[rule]=1

#Puts all rules involving the word at position index, in the sentence ptree, into rulesDict
def addProdRuleLine(index, ptree,rulesDict):
    leaf=ptree
    try:
      path=ptree.leaf_treeposition(index)
    except:
#      errorCount = errorCount+1
      return
    for ind in path[0:(len(path)-1)]:

        rule = leaf.label()+" -> "
        for leaves in leaf:
          rule = rule + leaves.label()+", "
        if rule in rulesDict:
          rulesDict[rule]= 1
        leaf=leaf[ind]

#Reads the relations and parses files
def readFiles(path='/home/jtk0/competition2/development/data/conll16st-en-01-12-16-train/'):

        print "reading parses"
        pdtb_file = codecs.open(path + '/parses.json', encoding='utf8');
        parses = json.load(pdtb_file)
        print "done"

        print "reading relations"
        relations = []
        with open(path+"relations.json") as f:
               for line in f:
                 relations.append(json.loads(line))
        print "done"
        return relations, parses

#Creates a prod rule file if necessary, then fills listOfProdRules wiuth the results
def createProdRules(parses):
        #Creates rule list if it doesn't already exist
        if not  os.path.isfile("prodRules.txt"):
          print "creating prod rules" 
          #production rule tree:
          f = open('prodRules.txt','w+')

          for parse in parses:
            for i in range(len(parses[parse]['sentences'])):
              parseTree=parses[parse]['sentences'][i]['parsetree']
              ptree = ParentedTree.fromstring(parseTree);
              buildProdRules(ptree.root(),listOfProdBuildingRules)


          for key in listOfProdBuildingRules:
            if listOfProdBuildingRules[key] >5:
              f.write(key+'\n')
          f.close()
          print "finished prodRules"
        else:
          print "skipping generating prodRule.txt"
#reads rule list
        f = open('prodRules.txt', 'r')
        for line in f:
          listOfProdRules[line[0:-1]]=0

#Gets the prod rule features
def prodFeatures(relation, parses):
                arg1Rules = listOfProdRules.copy()
                arg2Rules = listOfProdRules.copy()
                arg1and2Rules = listOfProdRules.copy()
                cType = relation['Type'];
            
                docId = relation["DocID"]
                arg1 = relation['Arg1']
                arg2 = relation['Arg2']
                #get the parse tree for a given sentence, then iterate through for each word
                sentenceNum = -1
                parseTree = None
                for wordList in arg1['TokenList']:
                  if wordList[3] != sentenceNum: 
                    sentenceNum = wordList[3]
                    #generate parse tree
                    parseTreeString = parses[docId]['sentences'][sentenceNum]['parsetree']
                    parseTree =  ParentedTree.fromstring(parseTreeString)
                  inSentencePosition = wordList[4]
                  addProdRuleLine(inSentencePosition,parseTree,arg1Rules)

                sentenceNum = -1
                parseTree = None
                for wordList in arg2['TokenList']:
                  if wordList[3] != sentenceNum:
                    sentenceNum = wordList[3]
                    #generate parse tree
                    parseTreeString = parses[docId]['sentences'][sentenceNum]['parsetree']
                    parseTree =  ParentedTree.fromstring(parseTreeString)
                  inSentencePosition = wordList[4]
                  addProdRuleLine(inSentencePosition,parseTree,arg2Rules)

                for rule in arg1Rules:
                  if arg1Rules[rule]==1 and arg2Rules[rule]==1:
                    arg1and2Rules[rule] = 1
                features={}             
                #Adds values to final list
                for rule in arg1Rules:
                  features['arg1'+rule] = arg1Rules[rule]

                for rule in arg2Rules:
                  features['arg2'+rule] = arg2Rules[rule]

                for rule in arg1and2Rules:
                  features['arg1and2'+rule] = arg1and2Rules[rule]
                return features

#Gets the gold standard sense of a relation
def getSense(relation):
    feature = None
    sense = relation['Sense']
    senseSplit = sense[0].split('.')
    if len(senseSplit)==1:
      feature=sense[0]
    else:
      feature= senseSplit[0]+'.'+senseSplit[1]
    return feature

#Creates the first last rules for a realtion
def firstLast(arg1,arg2):
  firstWordArg2 = secondWordArg2 = thirdWordArg2 = lastWordArg1 = secondLastWordArg1 = ''
  thirdLastWordArg1= firstWordArg1= secondWordArg1 = thirdWordArg1 = ''

  arg1split = arg1.split()
  arg2split = arg2.split()

  if len(arg1split)>0:
    lastWordArg1 = arg1split[-1]
    firstWordArg1 = arg1split[0]
  if len(arg1split)>1:
    secondLastWordArg1 = arg1split[-2]
    secondWordArg1 = arg1split[1]
  if len(arg1split)>2:
    thirdLastWordArg1 = arg1split[-3]
    thirdWordArg1 = arg1split[2]
  if len(arg2split)>0:
    firstWordArg2 = arg2split[0]
  if len(arg2split)>1:
    secondWordArg2 = arg2split[1]
  if len(arg2split)>2:
    thirdWordArg2 = arg2split[2]
  features = {}
  features['first3last3'] = thirdLastWordArg1+"_"+secondLastWordArg1+"_"+lastWordArg1+"_"+firstWordArg2+'_'+secondWordArg2+'_'+thirdWordArg2
  features['first2last2'] = secondLastWordArg1+"_"+lastWordArg1+"_"+firstWordArg2+'_'+secondWordArg2
  features['first1last1'] = lastWordArg1+"_"+firstWordArg2
  features['first3first3'] = firstWordArg1+'_'+secondWordArg1+'_'+thirdWordArg1+'_'+firstWordArg2+'_'+secondWordArg2+'_'+thirdWordArg2
  return features

###Main function reads files, trains classifiers and gives results
def readInput( relations=None, parses=None):
        trainingPath =  '/home/jtk0/competition2/development/data/conll16st-en-01-12-16-train/'
        if (relations ==None or parses==None):
          relations, parses = readFiles(trainingPath)
        createProdRules(parses)

        allFeatures = []
        counter = 0
        print "generating features"
        counter = 0
        classifier = None
        for relation in relations:
            if counter%100==0:
              print counter
            if relation['Type'] == 'Implicit' or relation['Type'] == 'AltLex' or relation['Type'] == "EntRel":
                counter = counter+1
#----------------features go here
                features = {}
                features.update(prodFeatures(relation,parses))
                features.update(firstLast(relation['Arg1']['RawText'], relation['Arg2']['RawText']))
                allFeatures.append((features,getSense(relation)) )

#----------------features end here
        print "training start"
        classifier =   nltk.classify.MaxentClassifier.train(allFeatures)
        print "training done"


        testingPath = "/home/jtk0/competition2/development/data/conll16st-en-01-12-16-dev/"
        testingRelations, testingParses = readFiles(testingPath)
        testingCount = 0
        correct = 0
        wrong = 0
        for testRelation in testingRelations:
          testingCount = testingCount +1
          if testingCount %20 ==0:
            print testingCount
          if testingCount == 1800:
            break
          if testRelation['Type'] == 'Implicit'  or relation['Type'] == 'AltLex' or relation['Type'] == "EntRel":
            testingCount = testingCount +1
#----------------make sure this is the same as above
            features = {}
            features.update(prodFeatures(testRelation, testingParses))
            features.update(firstLast(testRelation['Arg1']['RawText'], testRelation['Arg2']['RawText']))
#-----------------------
            result = classifier.classify(features)
            if result == getSense(testRelation):
              correct = correct+1
            else:
               wrong = wrong +1
               #print result,"     ", getSense(testRelation)
        print "correct", correct
        print "wrong", wrong

