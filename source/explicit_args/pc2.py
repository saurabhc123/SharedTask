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
import time
from model_trainer.NT_arg_extractor.constituent import Constituent
from connective import Connective
from model_trainer.NT_arg_extractor.feature_functions \
  import all_features as _constituent_feat_func
from example import Example
import util
import argparse
import pickle
import sys
def get_conn_to_root_path(parse_dict, DocID, sent_index, conn_indices):
    parse_tree = parse_dict[DocID]["sentences"][sent_index]["parsetree"].strip()
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

def _get_constituents(parse_dict, connective):
    DocID = connective.DocID
    sent_index = connective.sent_index
    parse_tree = parse_dict[DocID]["sentences"][sent_index]["parsetree"].strip()
    syntax_tree = Syntax_tree(parse_tree)
    if syntax_tree.tree == None:
        print "No Syntax Tree";
        return []

    conn_indices = connective.token_indices
    constituent_nodes = []
    if len(conn_indices) == 1:# like and or so...
        conn_node = syntax_tree.get_leaf_node_by_token_index(conn_indices[0]).up
    else:
        conn_node = syntax_tree.get_common_ancestor_by_token_indices(conn_indices)
        conn_leaves = set([syntax_tree.get_leaf_node_by_token_index(conn_index) for conn_index in conn_indices])
        children = conn_node.get_children()
        for child in children:
            leaves = set(child.get_leaves())
            if conn_leaves & leaves == set([]):
                constituent_nodes.append(child)

    curr = conn_node
    while not curr.is_root():
        constituent_nodes.extend(syntax_tree.get_siblings(curr))
        curr = curr.up

    # obtain the Constituent object according to the node.
    constituents = []
    for node in constituent_nodes:
        cons = Constituent(syntax_tree, node)
        cons.connective = connective
        constituents.append(cons)
    if len(constituents) == 0:
     print "Number of Constituents is 0";
    return constituents

#observedArray = [];
def test_maxent(algorithms, train, test, flag, modelFileName):
     observedArray = [];
     '''
     train = [
      (dict(a=1,b=2,c=3), 'y'),
      (dict(a=3,b=6,c=1), 'x'),
      (dict(a=1,b=1,c=0), 'y'),
      (dict(a=7,b=1,c=1), 'x'),
      (dict(a=0,b=1,c=1), 'y'),
      (dict(a=8,b=0,c=1), 'y'),
      (dict(a=0,b=1,c=0), 'x'),
      (dict(a=0,b=0,c=0), 'x'),
      (dict(a=0,b=1,c=1), 'y')]

     test = [
     (dict(a=1,b=0,c=1)), # unseen
     (dict(a=5,b=0,c=0)), # unseen
     (dict(a=0,b=1,c=1)), # seen 3 times, labels=y,y,x
     (dict(a=0,b=1,c=0)), # seen 1 time, label=x
     ]
     '''
     classifiers = {}
     algorithm = 'GIS'
     p = 0.0;
     r = 0.0;
     f = 0.0;
     #classifiers[algorithm] = nltk.MaxentClassifier.train(train, algorithm, trace=0, max_iter=20)
     if os.path.isfile(modelFileName):
      print "Model Exists";
      with open(modelFileName, "r") as filename:
       arg1Model = pickle.load(filename)
       classifiers['IIS'] = arg1Model;
     else:
      print "No Model Exists";
      if flag == 0:
       classifiers[algorithm] = nltk.MaxentClassifier.train(train, algorithm, trace=0, max_iter=15)
      else:
       classifiers[algorithm] = nltk.MaxentClassifier.train(train, algorithm, trace=0, max_iter=50)
     for algorithm, classifier in classifiers.items():
         refsets = collections.defaultdict(set)
         testsets = collections.defaultdict(set)

	 count = 0;
         for i, (feats, label) in enumerate(test):
          count = count + 1;
          refsets[label].add(i)
          observed = classifier.classify(feats)
          testsets[observed].add(i)
	  observedArray.append(observed);
         ''' 
         if flag == 1: 
          p = p + (precision(refsets['null'], testsets['null']) + precision(refsets['arg1'], testsets['arg1']) + precision(refsets['arg2'], testsets['arg2']))/3;
          r = r + (recall(refsets['null'], testsets['null']) + recall(refsets['arg1'], testsets['arg1']) + recall(refsets['arg2'], testsets['arg2']))/3;
          f = f + (f_measure(refsets['null'], testsets['null']) + f_measure(refsets['arg1'], testsets['arg1']) + f_measure(refsets['arg2'], testsets['arg2']))/3;
          
         print "Precision: ", p;
         print "Recall: ", r;
         print "F-measure: ", f;
         '''
     #return classifiers
     #print "Most Informative Features: " + str(classifier.show_most_informative_features(5));
     return observedArray; 

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
trSet = [];
testSet = [];
testSetLabels = [];
bigDiction = dict();
obigDiction = dict();
featForConnTr = dict();
featForConnTs = dict();
filenameSentenceSentTokenTr = dict();
filenameSentenceSentTokenTs = dict();
def prepRel(inFile, outFile):
 pdtb_file = codecs.open(inFile+'/relations.json', encoding='utf8');
 relations = [json.loads(x) for x in pdtb_file];
 orel = []
 countSS = 0;
 with open(outFile, 'w') as f:
  for relation in relations:
   cType = relation['Type'];
   if cType == 'Explicit':
    arg1_sentence_number = relation['Arg1']['TokenList'][0][3];
    arg2_sentence_number = relation['Arg2']['TokenList'][0][3];
    if arg1_sentence_number == arg2_sentence_number:
     countSS = countSS + 1;
     orel.append(relation);
     json.dump(relation, f)
     f.write("\n");


 #with open(outFile, 'w') as f:
 #    json.dump(orel, f)

dictByDocID={};
def makeDictByDocID(parseDict):
 tokenID=0
 dictByDocID={}
 for docID in parseDict:
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
    #dictByDocID[docID][sentenceID][wordID]['word']=w
    dictByDocID[docID][sentenceID][wordID]['pos']=pos
    dictByDocID[docID][sentenceID][wordID]['tokenID']=tokenID
    tokenID+=1
   sentenceID+=1
 return dictByDocID

relToConn = dict();
def readInput(inputFilenamePath, inputParse, trainOrTest):
 featForConn = dict();
 #Read relations.json
 if trainOrTest == "test":
  #pdtb_file = codecs.open(inputFilenamePath+'/relations_from_connective_output.json', encoding='utf8');
  pdtb_file = codecs.open(inputFilenamePath, encoding='utf8');
 else:
  pdtb_file = codecs.open(inputFilenamePath+'/relations.json', encoding='utf8');
 relations = [json.loads(x) for x in pdtb_file];
 #/sys.stderr.write("Len of Relations: " + str(len(relations)));
 #Read parses.json 
 if trainOrTest == "test":
  parse_file = codecs.open(inputParse, encoding='utf8');
 else:
  parse_file = codecs.open(inputFilenamePath+'/parses.json', encoding='utf8')
 en_parse_dict = json.load(parse_file)
 #makeDictByDocID(en_parse_dict);

 with open('/home/VTNLPS16/SharedTask/source/tempR.json', 'w') as q:
  json.dump(relations, q);
 counter = 0;
 flag = 0;
 featureSet = [];
 labelSet = [];
 #trainingSet = [];
 #testSet = [];
 countOfExplicit = 0;
 #bigDiction = dict();
 bigDictionIndex = 0;
 countExcept = 0;
 for relation in relations:
  try: 
   cType = relation['Type']; 
   label = "";
   if cType == 'Explicit':
    if trainOrTest == 'train':
     countOfExplicit = countOfExplicit + 1;
     arg1_sentence_number = relation['Arg1']['TokenList'][0][3];
     arg2_sentence_number = relation['Arg2']['TokenList'][0][3];   
     if arg1_sentence_number == arg2_sentence_number:
      label = 'SS';
     else:
      label = 'PS'; 

    #Arg1 Token List Generation
     arg1TokenList = [];
     arg1STokenList = [];
     for a1i in enumerate(relation['Arg1']['TokenList']):
     #print str(a1i);
     #print "Arg 1: " + str(a1i[1][2]);
      arg1TokenList.append(a1i[1][2]);
      arg1STokenList.append(a1i[1][4]);
   
    #Arg1 Token List Generation
     arg2TokenList = [];
     arg2STokenList = [];
     for a2i in enumerate(relation['Arg2']['TokenList']):
      arg2TokenList.append(a2i[1][2]);
      arg2STokenList.append(a2i[1][4]);

   #print "Relation Number " + str(counter) + " has explicit connective with connective word being : '" + relation['Connective']['RawText'] + "'";
   relation_DocID = relation['DocID'];
   parseJSON_sentence_number = relation['Connective']['TokenList'][0][3];
   connectiveWordID = relation['Connective']['TokenList'][0][4];
   #print "Sentence Number: " + str(parseJSON_sentence_number);
   #print "Connective Word ID: " + str(connectiveWordID);
   fileName = str(relation['DocID']);
   relID = str(relation['ID']);
   #if trainOrTest == 'test':
   # relToConn[relID] = connectiveWordID;
   #Parses.json object for that relation
   parseObject = en_parse_dict[relation_DocID]['sentences'][parseJSON_sentence_number];
   connectiveWordIDs = [];
   
   #print "Number of Connectives: " + str(len(relation['Connective']['TokenList']));
   for i in range(len(relation['Connective']['TokenList'])):
    connectiveWordIDs.append(relation['Connective']['TokenList'][i][4]);
 
   if trainOrTest == 'test':
    relToConn[relID] = connectiveWordIDs; 
   
   #print "Connective Words: " + str(connectiveWordIDs); 
   connectiveWords = []
   for i in range(len(connectiveWordIDs)):
    connectiveWords.append(parseObject['words'][connectiveWordIDs[i]][0]);
  
   #print "Connective Words: " + str(connectiveWordIDs); 
   #connectiveWord = parseObject['words'][connectiveWordID][0];
   #print "connectiveWord: " + str(parseObject['words']);
   #bigDictionaryKey = str(relation_DocID)+"_"+str(parseJSON_sentence_number)+"_"+str(connectiveWordID);
  
   #Building Feature Set
   features = dict();

   #Feature 1: Connective String
   #connectiveWord = str(parseObject['words'][connectiveWordID][0]);
   #features['f1'] = connectiveWord; 
   #features.append(connectiveWord);

   strConnectiveWords = ' '.join(connectiveWords);
   features['f1'] = strConnectiveWords;
  
   #Feature 2: Position of Connective
   connectivePosition = ''
   nonConn = "false";
   if len(connectiveWordIDs) > 1:
    if connectiveWordIDs[-1] - connectiveWordIDs[0] > len(connectiveWordIDs) - 1:
     connectivePosition = 'middle';
     nonConn = "true";
    else:
     firstConnWord = connectiveWordIDs[0];
   else:
    firstConnWord = connectiveWordIDs[0];
  
   if nonConn == "false": 
    lengthOfSentence = len(parseObject['words']);
    if connectiveWordID == 0:
     connectivePosition = 'start';
    elif connectiveWordID == (lengthOfSentence - 1):
     connectivePosition = 'end';
    else:
     connectivePosition = 'middle'; 
  
   features['f2'] = connectivePosition;
   #features.append(connectivePosition);
  
   #Feature 3: POS of Connective
   connectivePOSs = []
   for i in range(len(connectiveWordIDs)):
    connectivePOSs.append(str(parseObject['words'][connectiveWordIDs[i]][1]['PartOfSpeech']));
   features['f3'] = ' '.join(connectivePOSs);


    #connectiveWordID is the first connective
   connectiveWordID = connectiveWordIDs[0];
   
   #Feature 4, 5, 6 & 7: prev_1
   prev_1 = '';
   prev_1_POS = '';
   if connectiveWordID > 0:
    prev_1 = str(parseObject['words'][connectiveWordID - 1][0]);
    prev_1_POS = str(parseObject['words'][connectiveWordID - 1][1]['PartOfSpeech']);
  
   features['f4'] = prev_1;
   #features.append(prev_1);
   features['f5'] = prev_1_POS;
   #features.append(prev_1_POS);

   #prev_1_plus_C = prev_1 + "_" + connectiveWord;
   prev_1_plus_C = prev_1 + "_" + ' '.join(connectiveWords); 
   features['f6'] = prev_1_plus_C;
   #features.append(prev_1_plus_C);
   
   #prev_1_POS_plus_C_POS = prev_1_POS + "_" + connectivePOS;
   prev_1_POS_plus_C_POS = prev_1_POS + "_" + ' '.join(connectivePOSs);
   features['f7'] = prev_1_POS_plus_C_POS;
   #features.append(prev_1_POS_plus_C_POS);

   #Feature 8, 9, 10, & 11: prev_2
   prev_2 = '';
   prev_2_POS = '';
   if connectiveWordID > 1:  
    prev_2 = str(parseObject['words'][connectiveWordID - 2][0]);
    prev_2_POS = str(parseObject['words'][connectiveWordID - 2][1]['PartOfSpeech']);
 
   features['f8'] = prev_2;
   #features.append(prev_2);
   features['f9'] = prev_2_POS;
   #features.append(prev_2_POS);
   
   prev_2_plus_C = prev_2 + "_" + ' '.join(connectiveWords);
   #prev_2_plus_C = prev_2 + "_" + connectiveWord;
   features['f10'] = prev_2_plus_C;
   #features.append(prev_2_plus_C);
   
   prev_2_POS_plus_C_POS =  prev_2_POS + "_" + ' '.join(connectivePOSs);
   #prev_2_POS_plus_C_POS = prev_2_POS + "_" + connectivePOS;
   features['f11'] = prev_2_POS_plus_C_POS;
   #features.append(prev_2_POS_plus_C_POS);

   
   #Feature 12: C_POS + next_1_POS
   next_1_POS = '';
   if connectiveWordID <= len(parseObject['words'])-2:
    next_1_POS = str(parseObject['words'][connectiveWordID + 1][1]['PartOfSpeech']);

   C_POS_plus_next_1_POS = ' '.join(connectivePOSs) + "_" + next_1_POS;
   #C_POS_plus_next_1_POS = connectivePOS + "_" + next_1_POS;
   features['f12'] = C_POS_plus_next_1_POS;
   #features.append(C_POS_plus_next_1_POS);

   #Feature 13: next_2
   next_2 = '';
   if connectiveWordID <= len(parseObject['words'])-3:
     next_2 = str(parseObject['words'][connectiveWordID + 2][0]);

   features['f13'] = next_2;
   #features.append(next_2);

   #Feature 14: path from C to root

   pt = parseObject['parsetree'];
   #print pt;   
   ptree = ParentedTree.fromstring(pt);
   #print ptree;
   crp = "";
   crp = get_conn_to_root_path(en_parse_dict, relation_DocID, parseJSON_sentence_number, connectiveWordIDs);
   
   features['f14'] = crp;
   #features.append(crp);
   #featForConn[(relation_DocID, parseJSON_sentence_number, tuple(connectiveWordIDs))] = features;
  except:
   #exc_type, exc_obj, exc_tb = sys.exc_info()
   #fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
   #print(exc_type, fname, exc_tb.tb_lineno) 
   #sys.stderr.write( exc_tb.tb_lineno);
   #raise 
   countExcept = countExcept + 1;
   continue;
  if(trainOrTest == 'test'):
    arg1TokenList = [];
    arg2TokenList = [];
    arg1STokenList = [];
    arg2STokenList = [];
    bigDiction[bigDictionIndex] = (features, label, relation_DocID, parseJSON_sentence_number, connectiveWordIDs, strConnectiveWords, arg1TokenList, arg2TokenList, arg1STokenList, arg2STokenList, relID);
    #featForConn[(relation_DocID, parseJSON_sentence_number, connectiveWordIDs)] = features;
    featForConnTs[(relation_DocID, parseJSON_sentence_number, tuple(connectiveWordIDs))] = features;
    bigDictionIndex = bigDictionIndex + 1;
     
  if(trainOrTest == 'train'):
    obigDiction[bigDictionIndex] = (features, label, relation_DocID, parseJSON_sentence_number, connectiveWordIDs, strConnectiveWords, arg1TokenList, arg2TokenList, arg1STokenList, arg2STokenList, relID);
    featForConnTr[(relation_DocID, parseJSON_sentence_number, tuple(connectiveWordIDs))] = features;
    bigDictionIndex = bigDictionIndex + 1;
    trainingSet.append((features, label));
  else:
    testSet.append((features, label));
    #testSet.append(features); 

   #trainingSet.append((features, label));
   #featureSet.append(features);
   #labelSet.append(label);
  counter = counter + 1;
  #raise ValueError("Omitted: ", countExcept);
 #print "Number of Explicit Relations: " + str(countOfExplicit);
 #num_folds = 10
 #cv = cross_validation.KFold(len(trainingSet), n_folds=10, indices=True, shuffle=False, random_state=None)
 sys.stderr.write("Number Input: " + str(len(relations)) + ", Number Omitted: " + str(countExcept));
def classifyText(train, test):
 #print "In function: classifyText";
 #print "Training: " + str(train[0]);
 #print "Test: " + str(test[0]);
 classifier = nltk.NaiveBayesClassifier.train(train);
 #accuracy = nltk.classify.util.accuracy(classifier, test);
 #print 'accuracy:', nltk.classify.util.accuracy(classifier, trainingSet[testcv[0]:testcv[len(testcv)-1]])
 refsets = collections.defaultdict(set)
 testsets = collections.defaultdict(set)
 truth = set();
 predicted = set();
 for i, (feats, label) in enumerate(test):
  refsets[label].add(i)
  observed = classifier.classify(feats)
  testsets[observed].add(i)

 '''
 p = (precision(refsets['PS'], testsets['PS']) + precision(refsets['SS'], testsets['SS']))/2;
 r = (recall(refsets['PS'], testsets['PS']) + recall(refsets['SS'], testsets['SS']))/2;
 f = (f_measure(refsets['PS'], testsets['PS']) + f_measure(refsets['SS'], testsets['SS']))/2;

 print "Accuracy: ", accuracy;
 print "Precision: ", p;
 print "Recall: ", r;
 print "F-measure: ", f;
 '''
def readParseJson():
 #print("In function: readParseJson");
 
 #Read relations.json
 pdtb_file = codecs.open('/home/development/data/conll16st-en-01-12-16-train/relations.json', encoding='utf8');
 relations = [json.loads(x) for x in pdtb_file]; 
 #print("Done");

 #Read parses.json
 listfiles=os.listdir('/home/development/data/conll16st-en-01-12-16-train/raw/');
 for x in listfiles:
  try:
   parsedData =  ParsedInput.ParsedInput.parseFromFile('/home/development/data/conll16st-en-01-12-16-train/parses.json', x)
  except:
   print "Error Reading: " + x;
   break

dictDocumentToken = dict();
allTokenDict = dict();
sentToDocToken = dict();
filenameSentenceSentToken = dict();
conn_category = dict();
dictSentenceToken = dict();
def preprocessing2(inputFilenamePath):
 dict = {}
 file = open(inputFilenamePath);
 lines = [line.strip() for line in file.readlines()]
 for line in lines:
  list = line.split("#")
  conn = list[0].strip()
  category = list[1].strip()
  conn_category[conn] = category

def preprocessing(inputFilenamePath):
 parse_file = codecs.open(inputFilenamePath, encoding='ascii')
 en_parse_dict = json.load(parse_file)
 
 for filename, sentenceObject in en_parse_dict.iteritems():
  sentenceNumber = 0;
  i = 0;
  for sentenceArray in en_parse_dict[filename]['sentences']:
   wordsInSentence = sentenceArray['words'];
   #i = 1;
   wordArray = [];
   j = 0;
   k = 0;
   sentWordArray = []
   for word in wordsInSentence:
    rawWord = word[0];
    #if rawWord != ".":  
     #print "Word: " + str(word[0]) + " has id: " + str(i);
    wordArray.append(i);
    sentWordArray.append(k);
    allTokenDict[i] = rawWord;
    filenameSentenceSentToken[((filename, sentenceNumber, j))] = word[1]['PartOfSpeech'];
    sentToDocToken[(filename, sentenceNumber, j)] = i; 
    i = i + 1;
    j = j + 1;
    k = k + 1;
   dictSentenceToken[(filename, sentenceNumber)] = sentWordArray;
   dictDocumentToken[(filename, sentenceNumber)] = wordArray;
   #print "Number of Words in Sentence: " + str(len(wordArray)) + " with i = " + str(i);
   sentenceNumber = sentenceNumber + 1;  
 
 #print "Dictionary: " + str(allTokenDict); 

psRelations = []
ssRelations = []
def splitSSandPS(inputFilenamePath, trainOrTest, observedArray):
 if trainOrTest == "train":
  parse_file = codecs.open(inputFilenamePath+'/parses.json', encoding='ascii');
 else:
  parse_file = codecs.open(inputFilenamePath, encoding='ascii');
 en_parse_dict = json.load(parse_file);
 dictByDocID = makeDictByDocID(en_parse_dict);

 '''
 i = 0;
 ss_array = [];
 ps_array = [];
 currDict = dict();
 if trainOrTest == 'train':
  currDict = obigDiction;
 else:
  currDict = bigDiction;
 for prediction in observedArray:
  if prediction == 'PS':
   #ps_array.append(bigDiction[i]);
   ps_array.append(currDict[i]);
   psRelations.append(currDict[i][10]);
  elif prediction == 'SS':
   #ss_array.append(bigDiction[i]);
   ss_array.append(currDict[i]);
   ssRelations.append(currDict[i][10]);
  i = i + 1;
   
 print "Size of Entire Dictionary: " + str(len(bigDiction));
 print "Size of PS Dictionary: " + str(len(ps_array));
 print "Size of SS Dictionary: " + str(len(ss_array));
 return ss_array, ps_array, en_parse_dict;
 '''

 ss_array = [];
 ps_array = [];
 if trainOrTest == 'train':
  for index in range(len(obigDiction)):
   de = obigDiction[index];
  #for de in obigDiction:
   label = de[1];
   if label == 'PS':
    ps_array.append(de);
   elif label == 'SS':
    ss_array.append(de);
 elif trainOrTest == 'test':
  i = 0;
  for prediction in observedArray:
   if prediction == 'PS':
    if bigDiction[i][3] == 0:
     ss_array.append(bigDiction[i]);
     ssRelations.append(bigDiction[i][10]); 
    else:
     ps_array.append(bigDiction[i]);
     psRelations.append(bigDiction[i][10]);
   elif prediction == 'SS':
    ss_array.append(bigDiction[i]);
    ssRelations.append(bigDiction[i][10]);
   i = i + 1;
 '''
 with open('ssRelation.txt', 'w') as p:
  for value in sorted(ssRelations):
   p.write("Relation: " + str(value));
   p.write("\n");

 with open('psRelation.txt', 'w') as p:
  for value in sorted(psRelations):
   p.write("Relation: " + str(value));
   p.write("\n");
 '''
 print "Size of OA: " + str(len(observedArray));
 print "Size of PS Dictionary: " + str(len(ps_array));
 print "Size of SS Dictionary: " + str(len(ss_array)); 
 return ss_array, ps_array, en_parse_dict, dictByDocID;

import model_trainer.NT_arg_extractor.NT_dict_util as dict_util;
allRelationIDs = [];
paraRelIDs = []
def SS_parallel_not_parallel(inFile, trainOrTest, oa):
 ss_array, ps_array, parse_dict, dictByDocID = splitSSandPS(inFile, trainOrTest, oa);
 SS_conns_parallel_list = [];
 SS_conns_not_parallel_list = [];
 for dictEntry in ss_array:
  conn_indices = dictEntry[4];
  parallel = False;
  if len(conn_indices) > 1:
   for i in range(len(conn_indices)):
    if i + 1 < len(conn_indices) and conn_indices[i+1] - conn_indices[i] > 1:
     parallel = True
  if parallel:
   SS_conns_parallel_list.append(dictEntry);
   if trainOrTest == 'test':
    paraRelIDs.append(dictEntry[10]);
  else:
   SS_conns_not_parallel_list.append(dictEntry);


 #Convert into connectives
 connectives = [];
 i = 0;
 cnrel = [];
 for dictEntry in SS_conns_not_parallel_list:
  connective = Connective(dictEntry[2], dictEntry[3], dictEntry[4], dictEntry[5]);
  connective.relation_ID = dictEntry[10];
  if trainOrTest == 'test':
   allRelationIDs.append(dictEntry[10]);
   cnrel.append(dictEntry[10]);
  if trainOrTest == 'train':
   connective.Arg1_token_indices = dictEntry[8];
   connective.Arg2_token_indices = dictEntry[9];
  i = i + 1;
  connectives.append(connective);
 print "conn rel: " + str(len(cnrel));
 print "distinct conn rel: " + str(len(set(cnrel))); 
 to_file = '/home/development/code/explicit_args/constituent_feature.txt'
 trSet = [];
 tSet = [];
 #Extract constituents
 count1 = 0;
 count2 = 0;
 count3 = 0;

 totalConst = [];
 for curr_index, connective in enumerate(connectives):
  #totalConst.append(connective);
  sentenceIndexForConstituents = connective.sent_index;
  #arg1TL = SS_conns_not_parallel_list[sentenceIndexForConstituents];
  #print "arg1TL: " + str(arg1TL);
  constituents = _get_constituents(parse_dict, connective)

  constituents = sorted(constituents, key=lambda constituent: constituent.indices[0]) 
  #print "Connective: " + str(connective);
  #print "Constituents: " + str(constituents);
  #for i, constituent in enumerate(constituents):
  # extract features for each constituent
  example_list = [];
  i = 0;
  
  consrel = []; 
  for i, constituent in enumerate(constituents):
   consrel.append(constituent.connective.relation_ID);
   totalConst.append(constituent);
   feature = dict();
   label = "null";
   #print "Constituent Node: " + str(constituent.node);
   #print "Const Connective: " + str(constituent.connective);
   #print "Const Indices: " + str(constituent.indices);
   #print "Constituent Indices: " + " ".join([str(t) for t in constituent.get_indices()]);
   if trainOrTest == 'train':
    constIndices = set(constituent.get_indices());
    arg1OrigSet = set(connective.Arg1_token_indices);
    arg2OrigSet = set(connective.Arg2_token_indices);  

    if constIndices.issubset(arg1OrigSet):
     label = "arg1";
     count1= count1 + 1;
    elif constIndices.issubset(arg2OrigSet):
     label = "arg2";
     count2 = count2 + 1;
    else:
     label = "null";
     count3 = count3 + 1;
 
   syntax_tree = constituent.syntax_tree
   #conn_category = Connectives_dict().conn_category
   connective = constituent.connective
   conn_indices = connective.token_indices
   DocID = connective.DocID
   sent_index = connective.sent_index
   conn_node = dict_util.get_conn_node(syntax_tree, conn_indices)
   
   CON_POS = "";
   CON_POS = dict_util.get_CON_POS(parse_dict, DocID, sent_index, conn_indices)
   feature['f0'] = CON_POS
   #print "f0: ", feature['f0']
   NT_prev_curr_Path = "";
   NT_prev_curr_Path = dict_util.get_NT_prev_curr_Path(i, constituents)
   feature['f1'] = NT_prev_curr_Path
   #print "f1: ", feature['f1']
   CParent_to_root_path = "";
   CParent_to_root_path = dict_util.get_CParent_to_root_path(parse_dict, DocID, sent_index, conn_indices)
   feature['f2'] = CParent_to_root_path
   #print "f2: ", feature['f2']
   self_category = "";
   self_category = dict_util.get_self_category(parse_dict, DocID, sent_index, conn_indices)
   feature['f3'] = self_category
   #print "f3: ", feature['f3']
   CParent_to_root_path_node_names = "";
   CParent_to_root_path_node_names = dict_util.get_CParent_to_root_path_node_names(parse_dict, DocID, sent_index, conn_indices)
   feature['f4'] = str(CParent_to_root_path_node_names)  
   #print "f4: ", feature['f4']
   left_sibling_category = ""
   left_sibling_category = dict_util.get_left_sibling_category(parse_dict, DocID, sent_index, conn_indices)
   feature['f5'] = left_sibling_category
   #print "f5: ", feature['f5']
   NT_to_root_path = ""
   NT_to_root_path = dict_util.get_NT_to_root_path(constituent)
   feature['f6'] = NT_to_root_path
   #print "f6: ", feature['f6']
   conn_parent_categoryCtx = ""
   conn_parent_categoryCtx = dict_util.get_conn_parent_categoryCtx(parse_dict, DocID, sent_index, conn_indices)
   feature['f7'] = conn_parent_categoryCtx
   #print "f7: ", feature['f7']
   parent_category = ""
   parent_category = dict_util.get_parent_category(parse_dict, DocID, sent_index, conn_indices)
   feature['f8'] = parent_category
   #print "f8: ", feature['f8']
   conn_rightSiblingCtx = ""
   conn_rightSiblingCtx = dict_util.get_conn_rightSiblingCtx(parse_dict, DocID, sent_index, conn_indices)
   feature['f9'] = conn_rightSiblingCtx
   #print "f9: ", feature['f9']
   CON_Str = ""
   CON_Str = dict_util.get_CON_Str(parse_dict, DocID, sent_index, conn_indices)
   feature['f10'] = CON_Str
   #print "f10: ", feature['f10']
   CON_LStr = ""
   CON_LStr = CON_Str.lower()
   feature['f11'] = CON_LStr
   #print "f11: ", feature['f11']
   CON_Cat = "";
   if conn_category.has_key(connective.name):
    CON_Cat = conn_category[connective.name]
   feature['f12'] = CON_Cat;
   #print "f12: ", feature['f12']
   CON_iRSib = ""
   CON_iRSib = dict_util.get_CON_iRSib(syntax_tree,conn_node)
   feature['f13'] = CON_iRSib
   #print "f13: ", feature['f13']
   NT_Ctx = ""
   NT_Ctx = dict_util.get_NT_Ctx(constituent)
   feature['f14'] = NT_Ctx
   #print "f14: ", feature['f14']
   CON_NT_Path = ""
   CON_NT_Path = dict_util.get_CON_NT_Path(conn_node, constituent)
   feature['f15'] = CON_NT_Path
   #print "f15: ", feature['f15']
   CON_NT_Path_iLsib = CON_iLSib = dict_util.get_CON_iLSib(syntax_tree,conn_node)
   if CON_iLSib > 1:
    CON_NT_Path_iLsib = CON_NT_Path + ":>1"
   else:
    CON_NT_Path_iLsib = CON_NT_Path + ":<=1"
   feature['f16'] = CON_NT_Path_iLsib
   #print "f16: ", feature['f16']
   '''
   CON_Cat = "";
   if conn_category.has_key(connective.name):
    CON_Cat = conn_category[connective.name]
   feature['f0'] = CON_Cat;

   CON_Str = dict_util.get_CON_Str(parse_dict, DocID, sent_index, conn_indices)
   feature['f1'] = CON_Str;
   
   #print "CON_Str: " + str(CON_Str);
   CON_LStr = CON_Str.lower()
   feature['f2'] = CON_LStr;
   
   #print "CON_LStr: " + str(CON_LStr);
   CON_iLSib = dict_util.get_CON_iLSib(syntax_tree,conn_node)
   feature['f3'] = CON_iLSib;
   #print "CON_iLSib: " + str(CON_iLSib);
   CON_iRSib = dict_util.get_CON_iRSib(syntax_tree,conn_node)
   feature['f4'] = CON_iRSib;
   #print "CON_iRSib: " + str(CON_iRSib);
   NT_Ctx = dict_util.get_NT_Ctx(constituent)
   feature['f5'] = NT_Ctx;
   #print "NT_Ctx: " + str(NT_Ctx);
   CON_NT_Path = dict_util.get_CON_NT_Path(conn_node, constituent)
   feature['f6'] = CON_NT_Path;
   #print "CON_NT_Path: " + str(CON_NT_Path);
   #CON_NT_Position = dict_util.get_CON_NT_Position(conn_node, constituent)
   CON_NT_Position = "neither";
   constIndices = set(constituent.get_indices());
   if max(constIndices) < conn_indices[0]:
    CON_NT_Position = "left";
   if min(constIndices) > conn_indices[-1]:
    CON_NT_Position = "right"; 
   feature['f7'] = CON_NT_Position;
   #print "CON_NT_POSITION: " + str(CON_NT_Position);
   if conn_category.has_key(CON_LStr):
    CON_Cat = conn_category[CON_LStr];
   else:
    CON_Cat = "";
   feature['f8'] = CON_Cat;

   if CON_iLSib > 1:
    CON_NT_Path_iLsib = CON_NT_Path + ":>1"
   else:
    CON_NT_Path_iLsib = CON_NT_Path + ":<=1"
   feature['f8'] = CON_NT_Path_iLsib;
   '''
   ''' 
   feature['f10']  = dictByDocID[DocID][sent_index][constituent.get_indices()[0]]['pos']
   feature['f11']  = dictByDocID[DocID][sent_index][constituent.get_indices()[-1]]['pos']
   feature['f12']  = 'NA';

   if i <> 0:
    prevConstituent = constituents[i-1];
    prevDoc = prevConstituent.connective.DocID;
    prevSI = prevConstituent.connective.sent_index;
    feature['f12'] = dictByDocID[prevDoc][prevSI][constituent.get_indices()[-1]]['pos'];

   feature['f13'] = 'NA';
   if i <> len(constituents)-1:
    nextConstituent = constituents[i+1];
    nextDoc = nextConstituent.connective.DocID;
    nextSI = nextConstituent.connective.sent_index;
    feature['f13'] = dictByDocID[nextDoc][nextSI][constituent.get_indices()[0]]['pos'];
  
   feature['f14'] = 'NA';
   feature['f14'] = dictByDocID[DocID][sent_index][constituent.get_indices()[0]]['word'];
   feature['f15'] = 'NA';
   if i <> 0:
    prevConstituent = constituents[i-1];
    prevDoc = prevConstituent.connective.DocID;
    prevSI = prevConstituent.connective.sent_index;
    feature['f15'] = dictByDocID[prevDoc][prevSI][constituent.get_indices()[-1]]['word'];
 
   feature['16'] = feature['f15'] + "_" + feature['f14'];
   feature['f17'] = 'NA';
   lastCurr = dictByDocID[DocID][sent_index][constituent.get_indices()[-1]]['word'];
   if i <> len(constituents)-1:
    nextConstituent = constituents[i+1];
    nextDoc = nextConstituent.connective.DocID;
    nextSI = nextConstituent.connective.sent_index;
    feature['f17'] = dictByDocID[nextDoc][nextSI][constituent.get_indices()[0]]['word'];

   feature['17'] = lastCurr + "_" + feature['f17'];
   '''
   '''  
   if trainOrTest == 'train': 
    feats = featForConnTr[(DocID, sent_index, tuple(conn_indices))];
   else:
    feats = featForConnTs[(DocID, sent_index, tuple(conn_indices))];
   feature['f9'] = feats['f3'];
   #featForConn[(relation_DocID, parseJSON_sentence_number, connectiveWordIDs)] = features;
   feature['f10']  = dictByDocID[DocID][sent_index][constituent.get_indices()[0]]['pos']
   feature['f11']  = dictByDocID[DocID][sent_index][constituent.get_indices()[-1]]['pos']
   feature['f12']  = 'NA';
   #feature['f13'] = 'NA';
   if i <> 0:
    prevConstituent = constituents[i-1];
    prevDoc = prevConstituent.connective.DocID;
    prevSI = prevConstituent.connective.sent_index;
    feature['f12'] = dictByDocID[prevDoc][prevSI][constituent.get_indices()[-1]]['pos'];

   feature['f13'] = 'NA';
   if i <> len(constituents)-1: 
    nextConstituent = constituents[i+1];
    nextDoc = nextConstituent.connective.DocID;
    nextSI = nextConstituent.connective.sent_index;
    feature['f13'] = dictByDocID[nextDoc][nextSI][constituent.get_indices()[0]]['pos'];
   
   feature['f14'] = 'NA';
   feature['f14'] = dictByDocID[DocID][sent_index][constituent.get_indices()[0]]['word'];
   feature['f15'] = 'NA';
   if i <> 0:
    prevConstituent = constituents[i-1];
    prevDoc = prevConstituent.connective.DocID;
    prevSI = prevConstituent.connective.sent_index;
    feature['f15'] = dictByDocID[prevDoc][prevSI][constituent.get_indices()[-1]]['word'];
  
   feature['16'] = feature['f15'] + "_" + feature['f14'];
   feature['f17'] = 'NA';
   lastCurr = dictByDocID[DocID][sent_index][constituent.get_indices()[-1]]['word'];
   if i <> len(constituents)-1:
    nextConstituent = constituents[i+1];
    nextDoc = nextConstituent.connective.DocID;
    nextSI = nextConstituent.connective.sent_index;
    feature['f17'] = dictByDocID[nextDoc][nextSI][constituent.get_indices()[0]]['word']; 
  
   feature['17'] = lastCurr + "_" + feature['f17']; 
   #print "Feature 17: " + str(feature['f17']);
   '''

   if(trainOrTest == 'train'):
    trSet.append((feature, label));
   else:
    tSet.append((feature, label));
 
 print "constituent rel: " + str(len(consrel));
 print "constituent unique rel: " + str(len(set(consrel)));

 if(trainOrTest == 'train'):
  return totalConst, trSet, SS_conns_parallel_list, SS_conns_not_parallel_list, parse_dict, ps_array;
 else: 
  return totalConst, tSet, SS_conns_parallel_list, SS_conns_not_parallel_list, parse_dict, ps_array;

entryDict = dict();
import re;
def ssOrPS(inputFilenamePath):
 parse_file = codecs.open(inputFilenamePath+'/parses.json', encoding='utf8');
 en_parse_dict = json.load(parse_file);
 i = 0;
 with open('/home/development/code/explicit_args/output_dev.json', 'w') as f:
  i = -1;
  for prediction in observedArray:
   i = i + 1;
   filename = bigDiction[i][2];
   sentenceNumber = int(bigDiction[i][3]) + 1;
   connWordIDs = bigDiction[i][4];
   wordList = dictDocumentToken[(filename, sentenceNumber)]; 
   #print "Key: " + str("("+str(filename)+","+str(sentenceNumber)+")");
   #print "Value: " + str(wordList);
   connectiveTokenList = connWordIDs;
   connectiveWordNumberArray = [];
   #print "Raw Text: " + str(bigDiction[i][5]);
   if prediction == 'PS':
    '''
    arg1TokenList = dictDocumentToken[(filename, sentenceNumber-1)];
    print "Arg1TokenList: " + str(arg1TokenList);
    connectiveSentenceSet = set(dictDocumentToken[(filename, sentenceNumber)]);
    connectiveWordNumber = connWordID + dictDocumentToken[(filename, sentenceNumber)][0];
    #connectiveWordSet = set([connWordID]);
    connectiveWordSet = set([connectiveWordNumber]);
    print "Arg2ConnectiveSentenceSet: " + str(connectiveSentenceSet);
    print "Arg2ConnectiveWordSet: " + str(connectiveWordSet);
    arg2TokenListSet = connectiveSentenceSet - connectiveWordSet;
    arg2TokenList = list(arg2TokenListSet);
    '''
   elif prediction == 'SS':
    for connID in connWordIDs:
     connectiveWordNumberArray.append(wordList[connID]);
    
    arg1TokenList = [];
    arg2TokenList = [];
    for j in range(len(connWordIDs)):
     if j + 1 < len(connWordIDs) and connWordIDs[j+1] - connWordIDs[j] > 1:
      parallel = True;
     else:
      for index, value in enumerate(wordList):
       if value < connectiveWordNumberArray[0]:
        #if index == 0:
        #print "First Index String: " + str(allTokenDict[value]);
        #if str(allTokenDict[value]).isalnum():
         #arg1TokenList.append(value);
        #else:
         arg1TokenList.append(value); 
       elif value > connectiveWordNumberArray[len(connectiveWordNumberArray)-1]:
        #if index == len(wordList)-1:
         #print "Last Index String: " + str(allTokenDict[value]);
         #if str(allTokenDict[value]).isalnum():
          #arg2TokenList.append(value);
        #else:
         arg2TokenList.append(value);
    
    if len(arg1TokenList) <> 0:
     arg1_fe = arg1TokenList[0];
     arg1_le = arg1TokenList[-1];
     if str(allTokenDict[arg1_fe]).isalnum() == False:
      arg1TokenList.remove(arg1_fe);
     if str(allTokenDict[arg1_le]).isalnum() == False:
      if len(arg1TokenList) <> 0:
       arg1TokenList.remove(arg1_le);
   
    if len(arg2TokenList) <> 0:
     arg2_fe = arg2TokenList[0];
     arg2_le = arg2TokenList[-1];  
     if str(allTokenDict[arg2_fe]).isalnum() == False:
      arg2TokenList.remove(arg2_fe);
     if str(allTokenDict[arg2_le]).isalnum() == False:
      if len(arg2TokenList) <> 0:
       arg2TokenList.remove(arg2_le); 

    #if str(allTokenDict[arg1_fe]).isalnum() == False:
    # arg1TokenList.remove(arg1_fe);
    #if str(allTokenDict[arg1_le]).isalnum() == False:
    # arg1TokenList.remove(arg1_le);
    #if str(allTokenDict[arg2_fe]).isalnum() == False:
    # arg2TokenList.remove(arg2_fe);
    #if str(allTokenDict[arg2_le]).isalnum() == False:
    # arg2TokenList.remove(arg2_le);

    entryDict['DocID'] = str(filename);
    entryDict['Arg1'] = dict({"TokenList":arg1TokenList});
    entryDict['Arg2'] = dict({"TokenList":arg2TokenList});
    entryDict['Connective'] = dict({"TokenList":connectiveWordNumberArray});
    entryDict['Sense'] = ["Expansion.Conjunction"];
    entryDict['Type'] = 'Explicit';
   
    json.dump(entryDict, f)
    f.write("\n");
   
    orig1 = "";
    for l in bigDiction[i][6]:
     orig1 = orig1 + " " + allTokenDict[l];
   
    sentStr = "";
    for j in arg1TokenList:
     sentStr = sentStr + " " + allTokenDict[j];

    orig2 = "";
    for m in bigDiction[i][7]:
     orig2 = orig2 + " " + allTokenDict[m];

    sentStr2 = "";
    for k in arg2TokenList:
     sentStr2 = sentStr2 + " " + allTokenDict[k];
 
  '''
    connSentence = dictDocumentToken[(filename, sentenceNumber)];
    print "Sentence Index: " + str(connSentence);
    print "Connective Words: " + str(connWordIDs);
    arg1TokenList = [];
    arg2TokenList = [];
    wordInSentenceIndex = 0;
    for word in connSentence:
     if(wordInSentenceIndex < connWordIDs[0]):
      arg1TokenList.append(word);
     elif (wordInSentenceIndex > connWordIDs[-1]):
      arg2TokenList.append(word);
     elif (wordInSentenceIndex >= connWordIDs[0]) && (wordInSentenceIndex <= connWordIDs[-1]):
       
     else:
      connectiveWordNumber = connWordIDs[0] + wordInSentenceIndex; 
     wordInSentenceIndex = wordInSentenceIndex + 1;
     
   entryDict['DocID'] = str(filename);
   entryDict['Arg1'] = dict({"TokenList":arg1TokenList});
   entryDict['Arg2'] = dict({"TokenList":arg2TokenList});
   entryDict['Connective'] = dict({"TokenList":[connectiveWordNumber]});
   entryDict['Sense'] = ["Expansion.Conjunction"];
   entryDict['Type'] = 'Explicit';
 
   json.dump(entryDict, f)
   f.write("\n");
  '''
   #i = i + 1;
  '''
   print "SSorPS: " + str(prediction);
   print "Connective ID: " + str(connWordID);
   print "Arg 1: " + str(arg1TokenList);
   sentStr = "";
   for j in arg1TokenList:
    sentStr = sentStr + " " + allTokenDict[j];
   print "Arg 1 String: " + sentStr;
   print "Arg 2: " + str(arg2TokenList);
   sentStr2 = "";
   for k in arg2TokenList:
    sentStr2 = sentStr2 + " " + allTokenDict[k];
   print "Arg 2 String: " + sentStr2;
  '''
from syntax_tree import Syntax_tree;
def ssArgumentExt(inputFilenamePath):
 parse_file = codecs.open(inputFilenamePath+'/parses.json', encoding='utf8');
 en_parse_dict = json.load(parse_file);
 i = 0;
 for prediction in observedArray:
  filename = bigDiction[i][2];
  sentenceNumber = int(bigDiction[i+1][3]) + 1;
  connWordID = int(bigDiction[i][4]);
  parse_tree = en_parse_dict[filename]["sentences"][sentenceNumber]["parsetree"].strip();
  syntax_tree = Syntax_tree(parse_tree)
  if syntax_tree.tree == None:
   return []
  #Get Connective Indices
  conn_indices = [connWordID];
  constituent_nodes = [];
  if len(conn_indices) == 1:# like and or so...
        conn_node = syntax_tree.get_leaf_node_by_token_index(conn_indices[0]).up
  else:
        conn_node = syntax_tree.get_common_ancestor_by_token_indices(conn_indices)
        conn_leaves = set([syntax_tree.get_leaf_node_by_token_index(conn_index) for conn_index in conn_indices])
        children = conn_node.get_children()
        for child in children:
            leaves = set(child.get_leaves())
            if conn_leaves & leaves == set([]):
                constituent_nodes.append(child)
  
  curr = conn_node
  while not curr.is_root():
   constituent_nodes.extend(syntax_tree.get_siblings(curr))
   curr = curr.up

  # obtain the Constituent object according to the node.
  constituents = []
  for node in constituent_nodes:
   cons = Constituent(syntax_tree, node)
   #print "Object Type: " + str(cons.type());
   #print "Object Dir: " + str(cons.dir());
   #print "Object id: " + str(cons.id());
   #print "cons: " + str(cons.connective);
   connective = Connective(filename, sentenceNumber, conn_indices, "text");
   cons.connective = connective
   constituents.append(cons)
  i = i + 1;
 #return constituents

def assignSSandPS(inputFilenamePath): 
 #Read parses.json
 parse_file = codecs.open(inputFilenamePath+'/parses.json', encoding='utf8')
 en_parse_dict = json.load(parse_file)
 #parseObject = en_parse_dict[relation_DocID]['sentences'][parseJSON_sentence_number];
 #connectiveWord = parseObject['words'][connectiveWordID][0];
 i = 0;
 fileTokenCount = dict();
 for x in observedArray:
  prediction = x;
  #bigDiction[bigDictionIndex] = (features, label, str(relation_DocID), str(parseJSON_sentence_number), str(connectiveWordID));
  filenameID = bigDiction[i][2];
 
  if filenameID not in fileTokenCount: 
  #if (fileTokenCount.get(str(filenameID), default=None)) == 'None':
   fileTokenCount[filenameID] = 0;
 
  connectiveWordID = int(bigDiction[i][4]);
  if prediction == 'SS':
   sentenceNumber = int(bigDiction[i][3]);
   parseObject = en_parse_dict[filenameID]['sentences'][sentenceNumber];
   words = parseObject['words'];
   sentenceCount = int(len(words));
   

   dependencies = parseObject['dependencies'];
   sentenceWordCount = int(len(dependencies));
   currWordCount = fileTokenCount[filenameID];
   arg1 = [];
   arg2 = [];
   wordInSentenceIndex = 0;
   for wordObject in words:
   #for wordObject in dependencies:
    if(wordInSentenceIndex < connectiveWordID):
     arg1.append(currWordCount);
    elif (wordInSentenceIndex > connectiveWordID):
     arg2.append(currWordCount);
    
    wordInSentenceIndex = wordInSentenceIndex + 1;
    currWordCount = currWordCount + 1;
  else:
   #Arg1
   arg1SentenceNumber = int(bigDiction[i][3]) - 1 - 1;
   parseObject = en_parse_dict[filenameID]['sentences'][sentenceNumber];
   words = parseObject['words'];
   currWordCount = fileTokenCount[filenameID];
   arg1 = [];
   arg2 = [];
   for wordObject in words:
    arg1.append(currWordCount);
    currWordCount = currWordCount + 1;
   #Arg2
   arg2SentenceNumber = int(bigDiction[i][3]) - 1; 
   parseObject = en_parse_dict[filenameID]['sentences'][sentenceNumber];
   words = parseObject['words'];
   wordInSentenceIndex = 0;
   for wordObject in words:
    if (wordInSentenceIndex != connectiveWordID):
     arg2.append(currWordCount);
    
   
  #print "connectiveWordID: " + str(connectiveWordID); 
  #print "Arg 1: " + str(arg1);
  #print "Arg 2: " + str(arg2);
  
  #fileTokenCount[filenameID] = fileTokenCount[filenameID] + sentenceWordCount; 
  fileTokenCount[filenameID] = fileTokenCount[filenameID] + sentenceCount;
  i = i + 1;

def merge_NT_Arg(Arg_list, parse_dict, DocID, sent_index):
    punctuation = """!"#&'*+,-..../:;<=>?@[\]^_`|~""" + "``" + "''"
    if len(Arg_list) <= 1:
        return Arg_list
    temp = []
    # scan the missing parts, if it is the punctuation, then make up
    for i, item in enumerate(Arg_list):
        if i <= len(Arg_list) - 2:
            temp.append(item)
            next_item = Arg_list[i + 1]
            if next_item - item > 1:
                flag = 1
                for j in range(item + 1, next_item):
                    if parse_dict[DocID]["sentences"][sent_index]["words"][j][0] not in punctuation:
                        flag = 0
                        break
                if flag == 1:# make up
                    temp += range(item + 1, next_item)
    temp.append(Arg_list[-1])

    Arg = [(index, parse_dict[DocID]["sentences"][sent_index]["words"][index][0]) for index in temp]
    # remove the leading or tailing punctuations
    Arg = util.list_strip_punctuation(Arg)

    Arg = [item[0] for item in Arg]

    return Arg

mergeSSrelations = [];
#notInRelationCount = 0;
#inRelationCount = 0;
nullArgs = [];
def mergeSS(constituents, predictedArray, conns_list, parse_dict):
 notInRelationCount = 0;
 inRelationCount = 0;
 print "Size of Conns_list: " + str(len(conns_list));
 cl = [];
 for cl_entry in conns_list:
  cl.append(cl_entry[10]);
 print "Number of Conn Relations: " + str(len(cl));
 print "Number of Distinct Conn Relations: " + str(len(set(cl)));
 #print "Size of Conns_list: " + str(len(set(conns_list.keys()))); 
 #relation_dict = {};
 relation_dict = dict();
 for constituent, predicted in zip(constituents, predictedArray):
  relation_ID = constituent.connective.relation_ID;
  mergeSSrelations.append(relation_ID);
  constituent_indices = constituent.indices;
  if relation_dict.has_key(relation_ID):
   currArray = relation_dict[relation_ID];
   relation_dict[relation_ID].extend([(constituent_indices, predicted)]);
   inRelationCount = inRelationCount + 1;
  else:
   relation_dict[relation_ID] = [(constituent_indices, predicted)]
   notInRelationCount = notInRelationCount + 1;
  '''
  if relation_ID not in relation_dict:
   relation_dict[relation_ID] = [(constituent_indices, predicted)]
   notInRelationCount = notInRelationCount + 1;
  else:
   relation_dict[relation_ID].append((constituent_indices, predicted))
   inRelationCount = inRelationCount + 1;
  '''
 print "Number of SS Relations: " + str(len(mergeSSrelations));
 print "Number of Unique SS Relations: " + str(len(set(mergeSSrelations))); 
 print "NotInRelationCount: " + str(notInRelationCount);
 print "InRelationCount: " + str(inRelationCount);
 print "Size of Relation Dict: " + str(len(relation_dict));
 for relation_ID in relation_dict.keys():
  list = relation_dict[relation_ID]
  Arg1_list = []
  Arg2_list = []
  #null_list = []
  for span, label in list:
   if label == "arg1":
    Arg1_list.extend(span)
   if label == "arg2":
    Arg2_list.extend(span)
   #if label == "null":
   # null_list.extend(span)

  Arg1_list = sorted([int(item) for item in Arg1_list])
  Arg2_list = sorted([int(item) for item in Arg2_list])
  #null_list = sorted([int(item) for item in null_list])
  relation_dict[relation_ID] = (Arg1_list, Arg2_list)
 
 print "Size of Relation Dict After Creating Arg List: " + str(len(relation_dict));
 temp = []
 source = "SS"
 index = 0;
 print "Conns_list: " + str(len(conns_list));
 countZ = 0;
 countNotZ = 0;
 relIDZ = [];
 relNonKey = [];
 for i, dictEntry in enumerate(conns_list):
  DocID = dictEntry[2];
  sent_index = dictEntry[3];
  conn_indices = dictEntry[4]; 
  relID = dictEntry[10];
  #DocID, sent_index, conn_indices = conn
  if relation_dict.has_key(relID):
   Arg1_list, Arg2_list = relation_dict[relID]
   Arg1_list = merge_NT_Arg(Arg1_list, parse_dict, DocID, sent_index)
   Arg2_list = merge_NT_Arg(Arg2_list, parse_dict, DocID, sent_index)
   #null_list = merge_NT_Arg(null_list, parse_dict, DocID, sent_index)
   if Arg1_list != [] and Arg2_list != []:
    countNotZ = countNotZ + 1;
    temp.append((source, DocID, sent_index, conn_indices, Arg1_list, Arg2_list, relID))
   else:
    #print "Filename For Zero: " + str(DocID);
    #print "Sent Index For Zero: " + str(sent_index);
    #print "Conn Index For Zero: " + str(conn_indices);
    #print "Word List: " + str(dictSentenceToken[(DocID, sent_index)]);
    #countZ = countZ + 1;
    '''
    relIDZ.append(relID);
   
    countZ = countZ + 1;
    
    arg1TokenList = [];
    arg2TokenList = [];
    wordList = dictSentenceToken[(DocID, sent_index)];
    for index, value in enumerate(wordList):
     if value < conn_indices[0]:
      arg1TokenList.append(value);
     elif value > conn_indices[-1]:
      arg2TokenList.append(value);
    #temp.append((source, DocID, sent_index, conn_indices, Arg1_list, Arg2_list, relID))
    print "Conn Indices: " + str(conn_indices)
    print "Zero Arg1: " + str(arg1TokenList);
    print "Zero Arg2: " + str(arg2TokenList);

    #if len(arg1TokenList) != 0 or len(arg2TokenList) != 0:
    # print "Add to temp";
    # temp.append((source, DocID, sent_index, conn_indices, arg1TokenList, arg2TokenList, relID));
    if arg1TokenList != [] and arg2TokenList != []:
     temp.append((source, DocID, sent_index, conn_indices, arg1TokenList, arg2TokenList, relID));
     print "Add to temp";
    else:
     print "Don't add to temp";
    '''
    '''
    arg1Null = [];
    arg2Null = [];
    for nullE in null_list:
     if nullE < conn_indices[0]:
      arg1Null.append(nullE);
     elif nullE > conn_indices[-1]:
      arg2Null.append(nullE);
    '''
    #print "Arg 1 Null: " + str(arg1Null);
    #print "Arg 2 Null: " + str(arg2Null);
    #temp.append((source, DocID, sent_index, conn_indices, arg1Null, arg2Null));
    #nullArgs.append((DocID, relID, sent_index, conn_indices));
    pass;
  else:
   relNonKey.append(relID);
  index = index + 1;
 print "Count Z: " + str(countZ);
 print "Count Not Z: " + str(countNotZ);
 print "Size of temp: " + str(len(temp));
 print "RelID Z: " + str(sorted(relIDZ));
 print "RelNonKey: " + str(sorted(relNonKey));
 print "Size of Non Key: " + str(len(relNonKey));
 return temp

def get_doc_offset(parse_dict, DocID, sent_index, list):
    offset = 0
    #print "Sent Index: " + str(sent_index);
    for i in range(sent_index):
        #print "i: " + str(i);
        #print "Number of Sentences: " + str(len(parse_dict[DocID]["sentences"]));
        #print "Number of Words: " + str(len(parse_dict[DocID]["sentences"][i]["words"]));
        offset += len(parse_dict[DocID]["sentences"][i]["words"])
    temp = []
    for item in list:
        temp.append(item + offset)
    return temp

relToConn2 = dict();
def printToFile(relFile, outFile, temp, parse_dict, ps_array):
 index = 0;
 
 with open(relFile, 'wb') as f:
  print "Size of SS Entries: " + str(len(temp));
  for data in temp:
   dictEntry = dict();
   relID = index;
   docID = data[1];
   sent_index = data[2];
   entryDict = str(docID);
   dictEntry['DocID'] = str(docID);
   dictEntry['ID'] = str(data[6]);
   arg1 = get_doc_offset(parse_dict, docID, data[2],data[4]);
   arg1Final = [];
   elementI = 0
   for arg1e in arg1:
    arg1Final.append([0, 0, arg1e, sent_index, data[4][elementI]]);
    elementI = elementI + 1;
   dictEntry['Arg1'] = dict({"TokenList":arg1Final}); 
   arg2 = get_doc_offset(parse_dict, docID, data[2],data[5]);
   arg2Final = [];
   elementI = 0
   for arg2e in arg2:
    arg2Final.append([0, 0, arg2e, sent_index, data[5][elementI]]);
    elementI = elementI + 1;
   dictEntry['Arg2'] = dict({"TokenList":arg2Final});
   conn_indices = get_doc_offset(parse_dict, docID, data[2],data[3]);
   connFinal = [];
   elementI = 0
   for connI in conn_indices:
    connFinal.append([0, 0, connI, sent_index, data[3][elementI]]);
    elementI = elementI + 1;
   dictEntry['Connective'] = dict({"TokenList":connFinal});
   dictEntry['Sense'] = ["Expansion.Conjunction"];
   dictEntry['Type'] = 'Explicit';
   dictEntry['Arg1Pos'] = 'SS';
   relToConn2[str(data[6])] = data[3];
   json.dump(dictEntry, f)
   f.write("\n");
 ''' 
 with open('/home/development/code/explicit_args/conn.txt', 'w') as t:
  for data in temp:
   docID = data[1];
   conn_indices = get_doc_offset(parse_dict, docID, data[2],data[3]);
   t.write(str(conn_indices));
   t.write("\n");
 '''
 ''' 
 with open(outFile, 'w') as f:
  index = 0;
  for data in temp:
   dictEntry = dict();
   relID = index;
   docID = data[1];
   entryDict = str(docID);
     
   dictEntry['DocID'] = str(docID);
   arg1 = get_doc_offset(parse_dict, docID, data[2],data[4]);
   dictEntry['Arg1'] = dict({"TokenList":arg1}); 
   arg2 = get_doc_offset(parse_dict, docID, data[2],data[5]);
   dictEntry['Arg2'] = dict({"TokenList":arg2});
   conn_indices = []
   for h in data[3]:
    conn_indices.append(sentToDocToken[(docID, data[2], h)]);
   #conn_indices = get_doc_offset(parse_dict, docID, data[2],data[3]);
   #print "Conn SentToDocToken: " + str(conn_indices);
   dictEntry['Connective'] = dict({"TokenList":conn_indices});
   dictEntry['Sense'] = ["Expansion.Conjunction"];
   dictEntry['Type'] = 'Explicit';
   #dictEntry['Arg1Pos'] = 'SS'; 
   conn_indices = get_doc_offset(parse_dict, docID, data[2],data[3]);
   #print "Conn From Offset: " + str(conn_indices);
   json.dump(dictEntry, f)
   f.write("\n");
 
 with open(outFile, 'a') as f:
  index = 0;
  for ps_entry in ps_array:
   dictEntry = dict();
   filename = ps_entry[2];
   #dictEntry['DocID'] = str(ps_entry[2]);
   sent_index = ps_entry[3];
   relID = ps_entry[10];
   arg1DocIndex = [];
   arg2DocIndex = [];
   arg1SentIndex = [];
   arg2SentIndex = [];

   arg2SentIndex = dictSentenceToken[(filename, sent_index)];
   arg2DocIndex = dictDocumentToken[(filename, sent_index)];
   if sent_index-1 >= 0:
    arg1DocIndex = dictDocumentToken[(filename, sent_index-1)];
    arg1SentIndex = dictSentenceToken[(filename, sent_index-1)];
    #arg1DocIndex = dictDocumentToken[(filename, sent_index - 2)];

   arg1Final = [];
   for x,y in zip(arg1SentIndex, arg1DocIndex):
    arg1Final.append([0, 0, y, sent_index - 1, x]);

   arg2Final = [];
   for a,b in zip(arg2SentIndex, arg2DocIndex):
    arg2Final.append([0, 0, b, sent_index, a]);

   conn_indices = [];
   for e in ps_entry[4]:
    conn_indices.append(e);
   conn_indices_final = get_doc_offset(parse_dict, filename, sent_index, conn_indices);
   connFinal = [];
   elementI = 0
   for connI in conn_indices_final:
    connFinal.append([0, 0, connI, sent_index, conn_indices[elementI]]);
    elementI = elementI + 1;
   dictEntry['DocID'] = str(filename);
   dictEntry['ID'] = str(relID);
   dictEntry['Arg1'] = dict({"TokenList":arg1DocIndex});
   dictEntry['Arg2'] = dict({"TokenList":arg2DocIndex});
   dictEntry['Connective'] = dict({"TokenList":conn_indices_final});
   #dictEntry['Connective'] = dict({"TokenList":conn_indices});
   dictEntry['Sense'] = ["Expansion.Conjunction"];
   dictEntry['Type'] = 'Explicit';
   dictEntry['Arg1Pos'] = 'PS';

   #print "Relation Value for Conn For Rel: " + str(relID) + " with value: " + str(relToConn[relID]);
   #print "Value I'm printing: " + str(conn_indices);

   json.dump(dictEntry, f)
   f.write("\n");
   '''
 #print "Dict Sentence: " + str(dictSentenceToken);
 #print "Dict Document: " + str(dictDocumentToken);

 with open(relFile, 'ab') as p:
  print "Size of PS Entries: " + str(len(ps_array));
  for ps_entry in ps_array:
   dictEntry = dict();
   filename = ps_entry[2];
   #dictEntry['DocID'] = str(ps_entry[2]);
   sent_index = ps_entry[3];
   relID = ps_entry[10];
   arg1DocIndex = [];
   arg2DocIndex = [];
   arg1SentIndex = [];
   arg2SentIndex = [];

   arg2SentIndex = dictSentenceToken[(filename, sent_index)];
   arg2DocIndex = dictDocumentToken[(filename, sent_index)];
   if sent_index-1 >= 0:
    arg1DocIndex = dictDocumentToken[(filename, sent_index-1)];
    arg1SentIndex = dictSentenceToken[(filename, sent_index-1)];
    #arg1DocIndex = dictDocumentToken[(filename, sent_index - 2)];

   arg1Final = [];
   for x,y in zip(arg1SentIndex, arg1DocIndex):
    arg1Final.append([0, 0, y, sent_index - 1, x]);

   arg2Final = [];
   for a,b in zip(arg2SentIndex, arg2DocIndex):
    arg2Final.append([0, 0, b, sent_index, a]);

   conn_indices = [];
   for e in ps_entry[4]:
    conn_indices.append(e);
   conn_indices_final = get_doc_offset(parse_dict, filename, sent_index, conn_indices);
   connFinal = [];
   elementI = 0
   for connI in conn_indices_final:
    connFinal.append([0, 0, connI, sent_index, conn_indices[elementI]]);
    elementI = elementI + 1;
   dictEntry['DocID'] = str(filename);
   dictEntry['ID'] = str(relID);
   dictEntry['Arg1'] = dict({"TokenList":arg1Final});
   dictEntry['Arg2'] = dict({"TokenList":arg2Final});
   dictEntry['Connective'] = dict({"TokenList":connFinal});
   #dictEntry['Connective'] = dict({"TokenList":conn_indices});
   dictEntry['Sense'] = ["Expansion.Conjunction"];
   dictEntry['Type'] = 'Explicit';
   dictEntry['Arg1Pos'] = 'PS';
   relToConn2[str(relID)] = conn_indices;
   json.dump(dictEntry, p)
   p.write("\n");

if __name__ == '__main__':
 parser = argparse.ArgumentParser(description="The explicit sense classifier")
 parser.add_argument('relationsfile', help='Path to relations.json')
 parser.add_argument('parsesfile', help='Path to parses.json')
 parser.add_argument('modeldir', help='Path to pre-trained classifier model directory')
 parser.add_argument('outputdir', help='Directory for saving output files: relations-explicit-sense.json and scorer-format output file')
 args = parser.parse_args()
 testRelationFilePath = args.relationsfile;
 testParseFilePath = args.parsesfile;
 updatedRelationsFile = args.outputdir;

 start_time = time.time();
 #prepRel('/home/development/code/explicit_args/conll16st/tutorial/conll16st-en-01-12-16-trial', '/home/development/code/explicit_args/conll16st/tutorial/conll16st-en-01-12-16-trial/ss_relations.json')
 #prepRel('/home/development/code/explicit_args/conll16st/tutorial/conll16st-en-01-12-16-trial', '/home/development/code/explicit_args/conll16st/tutorial/conll16st-en-01-12-16-trial/ss_relations.json')
 #prepRel('/home/development/code/explicit_args/arijit_rel', '/home/development/code/explicit_args/ss_relations.json') 
 #prepRel('/home/development/data/conll16st-en-01-12-16-dev', '/home/development/code/explicit_args/dev_rel.json')
 
 #readInput('/home/development/data/conll16st-en-01-12-16-train','','train');
 #readInput('/home/development/code/explicit_args/conll16st/tutorial/conll16st-en-01-12-16-trial','','train');
 #print "Training Set: ", trainingSet;
 readInput(testRelationFilePath, testParseFilePath, 'test');
 #readInput('/home/development/code/connective_explicit/connectiveclassifierfinal', 'test');
 #readInput('/home/development/data/conll16st-en-01-12-16-dev', 'test');
 #readInput('/home/development/code/explicit_args/conll16st/tutorial/conll16st-en-01-12-16-trial', 'test');
 print "Size of Test Set: ", str(len(testSet)); 
 #sys.stderr.write("with Test Set Size: " + str(len(testSet)) );
 #classifyText(trainingSet, testSet);

 
 oa = test_maxent(nltk.classify.MaxentClassifier.ALGORITHMS, trainingSet, testSet, 0, 'explicit_args/arg1PosModel_15'); 
 #print "Size of Observed Array: " + str(len(oa));
 #sys.stderr.write("with Test Set Size: " + str(len(oa)) );
 
 preprocessing(testParseFilePath);
 #preprocessing('/home/development/code/connective_explicit/connectiveclassifierfinal/');
 #preprocessing('/home/development/data/conll16st-en-01-12-16-dev');
 #sys.stderr.write("with Test Set Size: " + str(len(oa)) );
 
 preprocessing2('explicit_args/connective-category.txt');
 #preprocessing('/home/development/code/explicit_args/conll16st/tutorial/conll16st-en-01-12-16-trial');
 #ssOrPS('/home/development/data/conll16st-en-01-12-16-dev');
 #sys.stderr.write("with Test Set Size: " + str(len(oa)) );
 #Training Set: Constituent
 #trConn, trSet, SS_conns_parallel_list, SS_conns_not_parallel_list, parse_dict, ps_array = SS_parallel_not_parallel('/home/development/data/conll16st-en-01-12-16-train', 'train', []);
 #trConn, trSet, SS_conns_parallel_list, SS_conns_not_parallel_list, parse_dict, ps_array = SS_parallel_not_parallel('/home/development/code/explicit_args/conll16st/tutorial/conll16st-en-01-12-16-trial', 'train', []); 
 #Test Set: Constituent
 #SS_parallel_not_parallel('/home/development/data/conll16st-en-01-12-16-dev', 'test');
 #tSet = SS_parallel_not_parallel('/home/development/code/explicit_args/conll16st/tutorial/conll16st-en-01-12-16-trial', 'test'); 
 #tConn, tSet, SS_conns_parallel_list, SS_conns_not_parallel_list, parse_dict, ps_array = SS_parallel_not_parallel('/home/development/data/conll16st-en-01-12-16-dev', 'test', oa);
 tConn, tSet, SS_conns_parallel_list, SS_conns_not_parallel_list, parse_dict, ps_array = SS_parallel_not_parallel(testParseFilePath, 'test', oa);
 #tConn, tSet, SS_conns_parallel_list, SS_conns_not_parallel_list, parse_dict, ps_array = SS_parallel_not_parallel('/home/development/code/connective_explicit/connectiveclassifierfinal', 'test', oa);
 #sys.stderr.write("with Test Set Size: " + str(len(oa)) + " and size of non parallel: " + str(len(SS_conns_not_parallel_list)));
 
 print "Size of relationIDs: " + str(len(allRelationIDs));
 print "Size of distinct relationIDs: " + str(len(set(allRelationIDs)));
 print "Size of SS_conns_not_parallel_list: " + str(len(SS_conns_not_parallel_list));
 print "Size of SS_conns_parallel_list: " + str(len(SS_conns_parallel_list));
 #print "SS Parallel Size: " + str(len(SS_conns_parallel_list));
 #print "SS Not Parallel Size: " + str(len(SS_conns_not_parallel_list));
 #print "tConn: " + str(len(tConn));
 #print "tSet: " + str(len(tSet));
 #print "Size of PS: " + str(len(ps_array));
 #tConn, tSet, SS_conns_parallel_list, SS_conns_not_parallel_list, parse_dict = SS_parallel_not_parallel('/home/development/code/explicit_args/conll16st/tutorial/conll16st-en-01-12-16-trial', 'test', oa);
 predictedArray = test_maxent(nltk.classify.MaxentClassifier.ALGORITHMS, trSet, tSet, 1, 'explicit_args/constClassModel_50');
 print "Size of Predicted Array: " + str(len(predictedArray));
 temp = mergeSS(tConn, predictedArray, SS_conns_not_parallel_list, parse_dict);
 print "Size of Temp: " + str(len(temp));
 scorerFile = '/home/development/code/explicit_args/final_scorer_file.json';
 printToFile(updatedRelationsFile, scorerFile, temp, parse_dict, ps_array);
 #printToFile('/home/development/code/explicit_args/ss_dev_out.json', temp, parse_dict, ps_array); 
 
 #test_maxent(nltk.classify.MaxentClassifier.ALGORITHMS, trainingSet, testSet);
 #splitSSandPS('/home/development/code/explicit_args/conll16st/tutorial/conll16st-en-01-12-16-trial');
 #SS_parallel_not_parallel();
 #ssOrPS('/home/development/code/explicit_args/conll16st/tutorial/conll16st-en-01-12-16-trial');
 #assignSSandPS('/home/development/data/conll16st-en-01-12-16-dev');
 #ssArgumentExt('/home/development/code/explicit_args/conll16st/tutorial/conll16st-en-01-12-16-trial');
 #print "All Relation IDs: " + str(sorted(allRelationIDs));
 #print "All Relation IDs: " + str(len(set(allRelationIDs)));
 #print "Parallel Relation IDs: " + str(sorted(paraRelIDs));
 #print "Size of MergeSS Relations IDs: " + str(len(mergeSSrelations));
 #print "MergeSS Relation IDs: " + str(sorted(mergeSSrelations));
 #diffRel = set(allRelationIDs) - mergeSSrelations;
 #print "Different in Relations Minus MergeSS: " + str(sorted(diffRel));
 #diffSS = mergeSSrelations - set(allRelationIDs)
 #print "Different in MergeSS Minus Relations: " + str(sorted(diffSS)); 
 #diff = set(sorted(relToConn.keys())) - set(relToConn2.keys());
 #print "Difference In Dictionaries: " + str(sorted(diff)); 
 #sys.stderr.write("Size of SS " + str(len(temp)) + ", Size of PS: " + str(len(ps_array)) ); 
 print "Done with Execution Time: " + str((time.time() - start_time));

'''
def getTrainingModel(train, flag):
 #classifier = nltk.NaiveBayesClassifier.train(train);
 algorithm = 'IIS';
 if flag == 0:
  print "Max Iter: 15";
  classifier = nltk.MaxentClassifier.train(train, algorithm, trace=0, max_iter=15)
 else:
  print "Max Iter: 50";
  classifier = nltk.MaxentClassifier.train(train, algorithm, trace=0, max_iter=50)
 return classifier;

import pickle
if __name__ == '__main__':
 start_time = time.time();

 print "Training Position Classifier";
 readInput('/home/development/data/conll16st-en-01-12-16-train','', 'train');
 print "Done reading Input";
 arg1PosModel = getTrainingModel(trainingSet, 0);
 print "Done training position";
 f = open('/home/development/code/explicit_args/arg1PosModel_15', 'wb')
 pickle.dump(arg1PosModel, f)
 print "Done writing training position classifier";

 #Training Set: Constituent
 print "Training constituent classifier";
 trConn, trSet, SS_conns_parallel_list, SS_conns_not_parallel_list, parse_dict, ps_array = SS_parallel_not_parallel('/home/development/data/conll16st-en-01-12-16-train', 'train', []);
 print "Done reading input";
 constClassModel = getTrainingModel(trSet, 1);
 print "Done training classifier";
 f = open('/home/development/code/explicit_args/constClassModel_50', 'wb')
 pickle.dump(constClassModel, f) 
 print "Done printing training constituent classifier"; 
 print "Done with Execution Time: " + str((time.time() - start_time));
'''
