#!/usr/bin/python
from sys import argv,exit,stderr,path
path.append("/home/alla/top/conll2015_discourse-master/")
import json
import codecs
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet


import util, os, json
#from connective_dict import Connectives_dict
#from example import Example
#import model_trainer.mallet_util as mallet_util
#from model_trainer.NT_arg_extractor.constituent import Constituent
from syntax_tree import Syntax_tree
#from connective import Connective
from clause import Arg_Clauses
import copy

import parser_util
#from ete2 import Tree
from nltk.tree import Tree

def getArg1Location1(relationDict,docID,relID):
  arg1={}
  arg2={}
  arg1Loc='None'
  for i in relationDict[docID][relID]['Arg1']['TokenList']:
        sentID=i[3]
        arg1[sentID]=1
  for i in relationDict[docID][relID]['Arg2']['TokenList']:
        sentID=i[3]
        arg2[sentID]=1

  if len(arg1)==1 and len(arg2)==1:
        if arg1==arg2:
                arg1Loc='SS'
        elif arg2.keys()[0]-arg1.keys()[0]==1:
                arg1Loc='PS'
  elif len(arg1)>1:
	pass
#        print >>stderr, 'Arg1 spans multiple sentences'
  elif len(arg2)>2:
	pass
        #print >>stderr, 'Arg2 spans multiple sentences'
  return arg1Loc

def getArg1Location(relation):
  arg1={}
  arg2={}
  arg1Loc='None'
  for i in relation['Arg1']['TokenList']:
        sentID=i[3]
        arg1[sentID]=1
  for i in relation['Arg2']['TokenList']:
        sentID=i[3]
        arg2[sentID]=1

  if len(arg1)==1 and len(arg2)==1:
	#print >>stderr, arg1, arg2
        if arg1==arg2:
                arg1Loc='SS'
		#print >>stderr, 'SS'
        elif arg2.keys()[0]-arg1.keys()[0]==1:
                arg1Loc='PS'
		#print >>stderr, 'PS next to each other'
	elif arg2.keys()[0]-arg1.keys()[0]==2:
		arg1Loc='PS'
		#print >>stderr, 'Two sentences before'
	else:
		arg1Loc='PS'
		#print >>stderr, 'Not immediately preceding sentence', arg2.keys()[0]-arg1.keys()[0]
  elif len(arg1)>1:
        pass
        #print >>stderr, 'Arg1 spans multiple sentences'
  elif len(arg2)>2:
        pass
        #print >>stderr, 'Arg2 spans multiple sentences'
  return arg1Loc

def getArgSentIDs(relation, arg):
	argIDs={}
	for i in relation[arg]['TokenList']:
           sentID=i[3]
           argIDs[sentID]=1
	return  argIDs


def getAllVerbsFromData(dictByDocID):
	verbDict={}
	for docID in dictByDocID:
	   for sentID in dictByDocID[docID]:
		wordIDs=dictByDocID[docID][sentID].keys()
		(verbs,tags)=getVerbsFromClause(dictByDocID,docID,sentID,wordIDs)
		for v in verbs:
			if v.lower() not in verbDict:
				verbDict[v.lower()]=0
			verbDict[v.lower()]+=1
	for v in verbDict:
		print verbDict[v],v, 'Verb'
def makeDictByTokenID(dictByDocID):
   dict={}
   for docID in dictByDocID:
      dict[docID]={}
      for sentID in dictByDocID[docID]:
	for wordID in dictByDocID[docID][sentID]:
		tokenID=dictByDocID[docID][sentID][wordID]['tokenID']
		dict[docID][tokenID]={}
		dict[docID][tokenID]['sentID']=sentID
		dict[docID][tokenID]['wordID']=wordID
   return dict

def makeDictByDocID(parseDict):
   tokenID=0
   dictByDocID={}
   for docID in parseDict:
#      print >>stderr, docID
      tokenID=0
      dictByDocID[docID]={}
      sentences=parseDict[docID]['sentences']
      sentenceID=0
      for sentence in sentences:
	 dictByDocID[docID][sentenceID]={}
         for wordID in range(len(sentence['words'])):
	   w=sentence['words'][wordID][0]
	   pos=sentence['words'][wordID][1]['PartOfSpeech']
	   dictByDocID[docID][sentenceID][wordID]={}
	   dictByDocID[docID][sentenceID][wordID]['word']=w
	   dictByDocID[docID][sentenceID][wordID]['pos']=pos
	   dictByDocID[docID][sentenceID][wordID]['tokenID']=tokenID
	   tokenID+=1
	 sentenceID+=1  
   return dictByDocID   

#relations is a list of dicts:
#	'DocID', Arg1, Arg2,Connective,Sense,Type,ID
def makeRelationDict(relations):
	relationDict={}
	for relation in relations:
	   #print >>stderr, relation.keys()
	   docID=relation['DocID']
	   sense=relation['Sense']
  	   if docID not in relationDict:
		relationDict[docID]={}
           relID=relation['ID']
	   relationDict[docID][relID]={}
	   for i in relation:	
		
		relationDict[docID][relID][i]=relation[i]
	   relType=relation['Type']#Explicit, Implicit,Entrel,AltLex,NoRel
	   connectiveTokens=[]
	   if 'RawText' in relation['Connective']:
	     connectiveTokens=relation['Connective']['RawText'].split()
	   connectiveTokenIDs=relation['Connective']['TokenList']
	   relationDict[docID][relID]['ConnectiveTokens']=connectiveTokens
	   relationDict[docID][relID]['ConnectiveTokenIDs']=connectiveTokenIDs
	   arg1TokenIDs=[]
	   for i in relation['Arg1']['TokenList']:
		arg1TokenIDs.append(i[2])
	   arg2TokenIDs=[]
	   for i in relation['Arg2']['TokenList']:
		arg2TokenIDs.append(i[2])
	   relationDict[docID][relID]['Arg1TokenIDs']=arg1TokenIDs
	   relationDict[docID][relID]['Arg2TokenIDs']=arg2TokenIDs
	return relationDict

def getWordListFromSentence(dictByDocID,docID,sentID):
	words=[]
	for i in dictByDocID[docID][sentID]:
		w=dictByDocID[docID][sentID][i]['word']
		words.append(w)
	return words

def getTokenIDsFromSentence(dictByDocID,docID,sentID):
	tokenIDs=[]
	for i in dictByDocID[docID][sentID]:
		tokenID=dictByDocID[docID][sentID][i]['tokenID']
		tokenIDs.append(tokenID)
	return tokenIDs

def getConnectiveWords(relation,dictByDocID,docID):
	words=[]
	if relation['Type']=='Implicit':
		return []
	wordIDs=[]
	for tokenList in relation['Connective']['TokenList']:
		wordIDs.append(tokenList[4])
	sentID=relation['Connective']['TokenList'][0][3]
	for i in wordIDs:
		words.append(dictByDocID[docID][sentID][i]['word'])
	return words

def getConnectivePOS(relation,dictByDocID,docID):
        words=[]
        if relation['Type']=='Implicit':
                return []
        wordIDs=[]
        for tokenList in relation['Connective']['TokenList']:
                wordIDs.append(tokenList[4])
        sentID=relation['Connective']['TokenList'][0][3]
        for i in wordIDs:
                words.append(dictByDocID[docID][sentID][i]['pos'])
        return words


def getConnectiveWordIDs(relation):
        words=[]
        if relation['Type']=='Implicit':
                return []
        wordIDs=[]
        for tokenList in relation['Connective']['TokenList']:
                wordIDs.append(tokenList[4])
        return wordIDs


def getClauseWordsFromSentence(dictByDocID,docID,sentID,clauseWordIDs):
      
        words=[]
        for i in dictByDocID[docID][sentID]:
	   if i in clauseWordIDs:
                w=dictByDocID[docID][sentID][i]['word']
                words.append(w)
        return words

def getVerbsFromClause(dictByDocID,docID,sentID,clauseWordIDs):
	verbs=[]
	tags=[]
	verbPOS=['VB','VBN','VBD','VBP','VBZ']
	for i in dictByDocID[docID][sentID]:
		if i in clauseWordIDs:
			pos=dictByDocID[docID][sentID][i]['pos']
			if pos in verbPOS:
				verbs.append(dictByDocID[docID][sentID][i]['word'])
				tags.append(dictByDocID[docID][sentID][i]['pos'])
	return (verbs,tags)

def lemma_verb(word, pos='V'):
    lmtzr = WordNetLemmatizer()
    word = word.lower()
    #pos = get_wn_pos(pos)
    #if pos == "":
     #   return word
    word = lmtzr.lemmatize(word, 'V')
    return word

			

def _ps_arg1_clauses(parse_dict, relation, Arg):
    DocID = relation["DocID"]
    Arg_sent_indices = sorted([item[3] for item in relation[Arg]["TokenList"]])
    if len(set(Arg_sent_indices)) != 1:
        return []
    relation_ID = relation["ID"]
    sent_index = Arg_sent_indices[0]
    Arg_list = sorted([item[4] for item in relation[Arg]["TokenList"]])

    sent_length = len(parse_dict[DocID]["sentences"][sent_index]["words"])

    sent_tokens = [(index, parse_dict[DocID]["sentences"][sent_index]["words"][index][0]) for index in range(0, sent_length)]

    # first, use punctuation symbols to split the sentence
    punctuation = "...,:;?!~--"
    #punctuation="...?:;!"
    _clause_indices_list = []#[[(1,"I")..], ..]
    temp = []
    for index, word in sent_tokens:
        if word not in punctuation:
            temp.append((index, word))
        else:
            if temp != []:
                _clause_indices_list.append(temp)
                temp = []
    clause_indices_list = []
    for clause_indices in _clause_indices_list:
        temp = util.list_strip_punctuation(clause_indices)
        if temp != []:
            clause_indices_list.append([item[0] for item in temp])

    # then use SBAR tag in its parse tree to split each part into clauses.
    parse_tree = parse_dict[DocID]["sentences"][sent_index]["parsetree"].strip()
    syntax_tree = Syntax_tree(parse_tree)

    if syntax_tree.tree == None:
	clause_list=[]
	temp=[]
	for clause in _clause_indices_list:
	   for i in clause:
		temp.append(i[0])
	   if temp:
	      clause_list.append((temp,''))
	   temp=[]
        return clause_list
    clause_list = []
    for clause_indices in clause_indices_list:
        clause_tree= parser_util._get_subtree(syntax_tree, clause_indices)
	flag=0
        for node in clause_tree.tree.traverse(strategy="levelorder"):
            if node.name == "SBAR":
                temp1 = [node.index for node in node.get_leaves()]
                temp2 = sorted(list(set(clause_indices) - set(temp1)))

                if temp2 == []:
                    clause_list.append(temp1)
                else:
                    if temp1[0] < temp2 [0]:
                        clause_list.append(temp1)
                        clause_list.append(temp2)
                    else:
                        clause_list.append(temp2)
                        clause_list.append(temp1)


                flag = 1
                break
        if flag == 0:
            clause_list.append(clause_indices)

    conn_token_indices = [item[4] for item in relation["Connective"]["TokenList"]]

    clauses = []# [([1,2,3],yes), ([4, 5],no), ]
    for clause_indices in clause_list:
        clauses.append((clause_indices, ""))
    return clauses

    #gc = Arg_Clauses(relation_ID, Arg, DocID, sent_index, clauses)
    #gc.conn_indices = conn_token_indices
    #gc.conn_head_name = get_conn_name(parse_dict, DocID, sent_index + 1, conn_token_indices) # conn
    #return gc

def _ps_arg2_clauses(parse_dict, relation, Arg):
    DocID = relation["DocID"]
    relation_ID = relation["ID"]
    sent_index = relation[Arg]["TokenList"][0][3]
    sent_length = len(parse_dict[DocID]["sentences"][sent_index]["words"])
    sent_tokens = [(index, parse_dict[DocID]["sentences"][sent_index]["words"][index][0]) for index in range(0, sent_length)]

    # first, split the sentence by the connective and the punctuation symbols
    conn_token_indices = [item[4] for item in relation["Connective"]["TokenList"]]
    punctuation = "...,:;?!~--"
    _clause_indices_list = []#[[(1,"I")..], ..]
    temp = []
    for index, word in sent_tokens:
        if word not in punctuation and index not in conn_token_indices:
            temp.append((index, word))
        else:
            if temp != []:
                _clause_indices_list.append(temp)
                temp = []
    clause_indices_list = []
    for clause_indices in _clause_indices_list:
        temp = util.list_strip_punctuation(clause_indices)
        if temp != []:
            clause_indices_list.append([item[0] for item in temp])

    # then use SBAR tag in its parse tree to split each part into clauses.
    parse_tree = parse_dict[DocID]["sentences"][sent_index]["parsetree"].strip()
    syntax_tree = Syntax_tree(parse_tree)

    if syntax_tree.tree == None:
        return []

    clause_list = []
    for clause_indices in clause_indices_list:
        clause_tree =parser_util._get_subtree(syntax_tree, clause_indices)
        # BFS
        flag = 0
        for node in clause_tree.tree.traverse(strategy="levelorder"):
            if node.name == "SBAR":
                temp1 = [node.index for node in node.get_leaves()]
                temp2 = sorted(list(set(clause_indices) - set(temp1)))

                if temp2 == []:
                    clause_list.append(temp1)
                else:
                    if temp1[0] < temp2 [0]:
                        clause_list.append(temp1)
                        clause_list.append(temp2)
                    else:
                        clause_list.append(temp2)
                        clause_list.append(temp1)

                flag = 1
                break
        if flag == 0:
            clause_list.append(clause_indices)

    # print " ".join([parse_dict[DocID]["sentences"][sent_index]["words"][index][0] for index in range(sent_length)])
    # print clause_list
    # print Arg_list

    clauses = []# [([1,2,3],yes), ([4, 5],no), ]
    for clause_indices in clause_list:
        clauses.append((clause_indices, ""))

    return clauses



#key is 'Arg1','Arg2','Connective'
def getTokenIDsList(relation,key):
	result=[]
        for tokenList in relation[key]['TokenList']: #each token that is part of Arg1 is represented as a list of 5 indices; I just need to take 3rd index (tokenID)
		result.append(tokenList[2])
        return result

#key is 'Arg1','Arg2','Connective'
def getWordIDsList(relation,key):
        result=[]
        for tokenList in relation[key]['TokenList']: #each token that is part of Arg1 is represented as a list of 5 indices; I just need to take 3rd index (tokenID)
                result.append(tokenList[4])
        return result


def getTokenIDsAfterConnective(relation,dictByDocID, docID):
	connSentIDs={}
	connTokenIDs=[]
	connWordIDs=[]
	
	for tokenList in relation['Connective']['TokenList']:
		sentID=tokenList[3]
		connSentIDs[sentID]=1
		connTokenIDs.append(tokenList[2])	
		connWordIDs.append(tokenList[4])
	if len(connSentIDs)>1: #connective spans across more than one sentence
		return []
	tokenIDs=[]
	wordIDs=[]
	flag=0
	if len(connTokenIDs)==1:
		flag=1
	#consecutive connectives; 2 words
	if len(connTokenIDs)==2 and connTokenIDs[-1]-connTokenIDs[0]==1:
		flag=1
	#consecutive connectives; 3 words
        if len(connTokenIDs)==3 and connTokenIDs[1]-connTokenIDs[0]==1 and connTokenIDs[2]-connTokenIDs[1]==1:
                flag=1
	if flag:
		tokenIDAfterConnective=connTokenIDs[-1]+1
		wordIDAfterConnective=connWordIDs[-1]+1
		print  'tokenIDAfterConnective', tokenIDAfterConnective
		for wordID in dictByDocID[docID][sentID]:
		   if wordID>=wordIDAfterConnective:
		   #if tokenList[2]>=tokenIDAfterConnective:
			tokenIDs.append(dictByDocID[docID][sentID][wordID]['tokenID'])
			wordIDs.append(wordID)
	print >>stderr, tokenIDs
	return (tokenIDs,wordIDs)

def getBaselinePSArg2(relation,dictByDocID, docID):
        connSentIDs={}
        connTokenIDs=[]
        connWordIDs=[]

        for tokenList in relation['Connective']['TokenList']:
                sentID=tokenList[3]
                connSentIDs[sentID]=1
                connTokenIDs.append(tokenList[2])
                connWordIDs.append(tokenList[4])
        if len(connSentIDs)>1: #connective spans across more than one sentence
                return []
        tokenIDs=[]
        wordIDs=[]
	argWords=[]
        flag=0
        if len(connTokenIDs)==1:
                flag=1
        #consecutive connectives; 2 words
        if len(connTokenIDs)==2 and connTokenIDs[-1]-connTokenIDs[0]==1:
                flag=1
        #consecutive connectives; 3 words
        if len(connTokenIDs)==3 and connTokenIDs[1]-connTokenIDs[0]==1 and connTokenIDs[2]-connTokenIDs[1]==1:
                flag=1
        if flag:
		for wordID in dictByDocID[docID][sentID]:
			if wordID in connWordIDs:
				pass
			#do not include commas preceding the connective words
			elif wordID==connWordIDs[0]-1 and dictByDocID[docID][sentID][wordID]['word']==',':
				pass
			#do not include commas following the connective words
			elif wordID==connWordIDs[-1]+1 and dictByDocID[docID][sentID][wordID]['word']==',':
				pass
			else:
				tokenIDs.append(dictByDocID[docID][sentID][wordID]['tokenID'])
				wordIDs.append(wordID)
				argWords.append(dictByDocID[docID][sentID][wordID]['word'])
	if argWords and argWords[-1]=='.':
		tokenIDs=tokenIDs[:-1]
		wordIDs=wordIDs[:-1]
		argWords=argWords[:-1]
        #print >>stderr, tokenIDs
        return (tokenIDs,wordIDs)


def removePuncArg2(arg2WordIDs, arg2TokenIDs, dictByDocID, docID,sentID):
	arg2WordIDsNew=[]
	arg2TokenIDsNew=[]
	for i in range(len(arg2WordIDs)):
		wordID=arg2WordIDs[i]
		w=dictByDocID[docID][sentID][wordID]['word']
		if i==0 and w==',':
			pass
		elif i==len(arg2WordIDs)-1:# and w=='.':
			pass
		else:
			arg2WordIDsNew.append(arg2WordIDs[i])
			arg2TokenIDsNew.append(arg2TokenIDs[i])
	return (arg2WordIDsNew, arg2TokenIDsNew)


def getVerbFeatures1(argWords,verbList):
	words=[]
	for w in argWords:
		words.append(w.lower())
	feats=[]
	curFeat=0
	for v in verbList:
		val='NA'
		if v in words:
			val='1'
		feats.append(v+':'+val)
	return feats

	
def get_conn_to_root_path(parse_dict,docID,sentID,conn_indices):
    parse_tree = parse_dict[docID]["sentences"][sentID]["parsetree"].strip()
    syntax_tree = Syntax_tree(parse_tree)
    if syntax_tree.tree == None:
        path = "NONE_TREE"
    else:
        path = ""
        for conn_index in conn_indices:
            conn_node = syntax_tree.get_leaf_node_by_token_index(conn_index)
            t = syntax_tree.get_node_path_to_root(conn_node)
            path += t + "&"
        if path[-1] == "&":
            path = path[:-1]

    return path

def get_conn_to_root_compressed_path(parse_dict,docID,sentID,conn_indices):
    parse_tree = parse_dict[docID]["sentences"][sentID]["parsetree"].strip()
    syntax_tree = Syntax_tree(parse_tree)
    if syntax_tree.tree == None:
        compressed_path = "NONE_TREE"
    else:
        compressed_path = ""
        for conn_index in conn_indices:
            conn_node = syntax_tree.get_leaf_node_by_token_index(conn_index)
	    conn_parent_node = conn_node.up
	    path = syntax_tree.get_node_path_to_root(conn_parent_node)
	    compressed_path += util.get_compressed_path(path) + "&"
            #t = syntax_tree.get_node_path_to_root(conn_node)
            #path += t + "&"
        if compressed_path[-1] == "&":
            compressed_path = compressed_path[:-1]
    return compressed_path

def get_CParent_to_root_path_node_names(parse_dict,docID,sentID,conn_indices):
    parse_tree = parse_dict[docID]["sentences"][sentID]["parsetree"].strip()
    syntax_tree = Syntax_tree(parse_tree)

    if syntax_tree.tree == None:
        path = "NONE_TREE"
    else:
        path = ""
        for conn_index in conn_indices:
            conn_node = syntax_tree.get_leaf_node_by_token_index(conn_index)
            conn_parent_node = conn_node.up
            path += syntax_tree.get_node_path_to_root(conn_parent_node) + "-->"
        if path[-3:] == "-->":
            path = path[:-3]
    return path.split("-->")

def get_conn_connCtx(parse_dict,docID,sentID,conn_indices,conn_words):
    parse_tree = parse_dict[docID]["sentences"][sentID]["parsetree"].strip()
    syntax_tree = Syntax_tree(parse_tree)

    # conn + connCtx
    if syntax_tree.tree == None:
        connCtx = "NONE_TREE"
    else:
        conn_node = syntax_tree.get_self_category_node_by_token_indices(conn_indices)
        connCtx = get_node_Ctx(conn_node, syntax_tree)

    #conn_connCtx = "%s|%s" % (conn_name, connCtx)
    conn_connCtx ='_'.join(conn_words)+'-'+connCtx
    return conn_connCtx


def get_node_Ctx(node, syntax_tree):
    if node == None:
        return "None"
    Ctx = []
    #self
    Ctx.append(node.name)
    #parent
    if node.up == None:
        Ctx.append("NULL")
    else:
        Ctx.append(node.up.name)
    #left
    left_siblings = syntax_tree.get_left_siblings(node)
    if left_siblings == []:
        Ctx.append("NULL")
    else:
        Ctx.append(left_siblings[-1].name)
    #right
    right_siblings = syntax_tree.get_right_siblings(node)
    if right_siblings == []:
        Ctx.append("NULL")
    else:
        Ctx.append(right_siblings[0].name)

    nodeCtx = "-".join(Ctx)
    return nodeCtx

def getClausesForArgument(relation,arg,dictByDocID,docID,sentID,parse_dict):
	clauses=[]
	argWordIDs=[]
	for i in relation[arg]['TokenList']:
		argWordIDs.append(i[4])
	clause=[]
	prev=-1
	for wordID in argWordIDs:
		if wordID-1>1:
			if clause:
				clauses.append(clause)
			clause=[]
		clause.append(wordID)
	return clauses
		
def writeRules(rules,outF,cutoff=5):
	for r in rules:
		if rules[r]>=cutoff:
			outF.write("%s %s\n" % (r.replace(' ','_'), rules[r]))

def getCrossProd(rules1,rules2):
	dict={}
	for r1 in rules1:
		for r2 in rules2:
			c=r1+'-AND-'+r2
			if c not in dict:
				dict[c]=0
			dict[c]+=1
	return dict
			
def get_curr_production_rule(parse_dict,docID,sentID,conn_indices,clause):
    #curr_clause_indices = arg_clauses.clauses[clause_index][0]# ([1,2,3],yes)
    curr_clause_indices = clause
    subtrees = []
    parse_tree = parse_dict[docID]["sentences"][sentID]["parsetree"].strip()
    syntax_tree = Syntax_tree(parse_tree)
    if syntax_tree.tree != None:
        clause_leaves = set([syntax_tree.get_leaf_node_by_token_index(index) for index in curr_clause_indices])
        no_need = []
        for node in syntax_tree.tree.traverse(strategy="levelorder"):
            if node not in no_need:
                if set(node.get_leaves()) <= clause_leaves:
                    subtrees.append(node)
                    no_need.extend(node.get_descendants())

    production_rule = []
    for tree in subtrees:
        for node in tree.traverse(strategy="levelorder"):
            if not node.is_leaf():
                rule = node.name + "-->" + " ".join([child.name for child in node.get_children()])
                production_rule.append(rule)

    return production_rule

def get_curr_production_rules_for_clause(parse_dict,docID,sentID,clause):
    nodes=['S','NP','VP','SBAR','PP','ADJP','ADVP','WHNP']
    curr_clause_indices = clause
    if len(clause)==0:
	return []
    subtrees = []
    parse_tree = parse_dict[docID]["sentences"][sentID]["parsetree"].strip()
    parse_tree=parse_tree[2:-2]
    print >>stderr, 'parse_tree', parse_tree
  #  parse_tree = parse_tree.replace(",", "*COMMA*")
    # parse_tree = parse_tree.replace(":", "*COLON*")
    if not parse_tree:
		return []
    syntax_tree=Tree.fromstring(parse_tree)
    allProductions=syntax_tree.productions()
    print >>stderr, 'Tree'
    print >>stderr, parse_tree
    print >>stderr, '***All productions***'
    for p in allProductions:
	print >>stderr,p.__repr__(),
    print >>stderr, 1
    #parse_tree= Tree(parse_tree, format=1)
    #syntax_tree = Syntax_tree(parse_tree)

    curWord=0
    productions = []
    flag=0
    for i in range (len(allProductions)):
	p=allProductions[i].__repr__()
	pair=p.split('->')
	lhs=pair[0].strip()
	if len(pair[1].strip().split())==1 and lhs not in nodes: #leaf nodes
		w=pair[1].strip()
		if curWord==curr_clause_indices[0]:
			flag=1
			productions.append(p)
			for j in range(0,i):
			   p1=allProductions[i-j-1].__repr__()
		  	   pair1=p1.split('->')
			   #print >>stderr, 'pair1', pair1
			   if pair1[0].strip() in nodes:
				productions=[p1]+productions
				#if curWord==0:
				#	break
			   else:
				break
		elif flag and curWord in curr_clause_indices:
			productions.append(p)
			list1=[]
			for j in range(0,i):
				p1=allProductions[i-j-1].__repr__()
				pair1=p1.split('->')
			#	print >>stderr, 'pair1', pair1
				if pair1[0].strip() in nodes:
					 list1=[p1]+list1
				else:
					productions=productions[:-1]+list1+[p]
					break
			if curWord==curr_clause_indices[-1]:
				flag=0
		curWord+=1
    #print >>stderr, 'Productions', productions
    return productions


def getVerbFeatures(dictByDocID,docID,sentID,clauseWordIDs,verbList):
   (allVerbs,tags)=getVerbsFromClause(dictByDocID,docID,sentID,clauseWordIDs)
   verbs=[]
   for v in allVerbs:
        if v in verbList:
                verbs.append(v)
   if len(verbs)<len(allVerbs):
      print 'Verbs', verbs, len(allVerbs), len(verbs)
   v1=v2=v3='NA'
   if len(verbs):
        v1=verbs[0]
   if len(verbs)>1:
        v2=verbs[1]
   if len(verbs)>2:
        v3=verbs[2]
   return (['verb1:'+v1, 'verb2:'+v2,'verb3:'+v3])

def modifyProductionRules3(productionRules):
	newRules=[]
 	posTags=['NN','NNP','ADJ','VBP','VBD','JJ','JJR','PRP','NNS','NNPS','VBZ','VB','RB','VBN','VBG','VBZ', 'CD','MD','JJS','PRP$']
	for r in productionRules:
	   if len(newRules)>=3:
		break
	   pair=r.split('-->')
	   if pair[0] in posTags:
		newRules.append(pair[0])
	   else:
		newRules.append(r)
	return newRules

def modifyProductionRules2(productionRules):
        newRules=[]
        posTags=['NN','NNP','ADJ','VBP','VBD','JJ','JJR','PRP','NNS','NNPS','VBZ','VB','RB','VBN','VBG','VBZ', 'CD','MD','JJS','PRP$']
        for r in productionRules:
           if len(newRules)>=2:
                break
           pair=r.split('-->')
           if pair[0] in posTags:
                newRules.append(pair[0])
           else:
                newRules.append(r)
        return newRules

def filterProductionRules(productionRules):
	newRules=[]
	posTags=['NN','NNP','ADJ','VBP','VBD','JJ','JJR','PRP','NNS','NNPS','VBZ','VB','RB','VBN','VBG','VBZ', 'CD','JJS','PRP$','-RRB-','DT','-LRB-']
	for r in productionRules:
		pair=r.split('->')
		lhs=pair[0].strip()
		#print >>stderr, 'pair', pair, lhs
		if lhs in posTags and 'said' not in pair[1] and 'says' not in pair[1]:
			print >>stderr,  'pair', pair, lhs, 'Passing'
			pass
		else:
			newRules.append(r)
	return newRules

