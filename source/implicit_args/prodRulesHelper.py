import codecs
import json
# import ParsedInput
import nltk
from nltk.tree import *
# import scikit-learn
import nltk.metrics
import os.path
import regex;
from implicit_args import Clause;


class prodRulesHelper:

    listOfProdRules ={}
    listOfProdBuildingRules = {}

    #Adds all rules in pTreeRoot into rulesDict
    def buildProdRules(self, pTreeRoot, rulesDict):
      rule = pTreeRoot.label()+" -> "
      hasChild = False
      for children in pTreeRoot:
        if hasattr(children, 'label'):
          rule = rule + children.label()+", "
          self.buildProdRules(children,rulesDict)
          hasChild=True
      if hasChild:
        if rule in rulesDict:
          rulesDict[rule]=rulesDict[rule]+1
        else:
          rulesDict[rule]=1

    #Puts all rules involving the word at position index, in the sentence ptree, into rulesDict
    def addProdRuleLine(self, index, ptree,rulesDict):
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

    def getClausesFromParseTree(self, parseTree):
        clauses = [];
        parts = parseTree.split("(SBAR")[:];
        for part in parts:
            clause = regex.findall('[A-Z]?[a-z]+', part);
            if clause:
                clauses.append(Clause.Clause(' '.join(clause), part));
        return clauses;

    #Creates a prod rule file if necessary, then fills listOfProdRules wiuth the results
    def createProdRules(self, parses):
        #Creates rule list if it doesn't already exist
        if not  os.path.isfile("prodRules.txt"):
          print "creating prod rules"
          #production rule tree:
          f = open('prodRules.txt','w+')

          for parse in parses:
            for i in range(len(parses[parse]['sentences'])):
                parseTree=parses[parse]['sentences'][i]['parsetree']
                clauses = self.getClausesFromParseTree(parseTree);
                for clause in clauses:
                    ptree = ParentedTree.fromstring(clause.parseTree);
                    self.buildProdRules(ptree.root(),self.listOfProdBuildingRules)


          for key in self.listOfProdBuildingRules:
            if self.listOfProdBuildingRules[key] >5:
              f.write(key+'\n')
          f.close()
          print "finished prodRules"
        else:
          print "skipping generating prodRule.txt"
        #reads rule list
        f = open('prodRules.txt', 'r')
        for line in f:
          self.listOfProdRules[line[0:-1]]=0

    #Gets the prod rule features
    def prodFeatures(self, relation, parses):
                arg1Rules = self.listOfProdRules.copy()
                arg2Rules = self.listOfProdRules.copy()
                arg1and2Rules = self.listOfProdRules.copy()
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
                  self.addProdRuleLine(inSentencePosition,parseTree,arg1Rules)

                sentenceNum = -1
                parseTree = None
                for wordList in arg2['TokenList']:
                  if wordList[3] != sentenceNum:
                    sentenceNum = wordList[3]
                    #generate parse tree
                    parseTreeString = parses[docId]['sentences'][sentenceNum]['parsetree']
                    parseTree =  ParentedTree.fromstring(parseTreeString)
                  inSentencePosition = wordList[4]
                  self.addProdRuleLine(inSentencePosition,parseTree,arg2Rules)

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
