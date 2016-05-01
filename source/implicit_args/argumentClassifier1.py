import codecs
import json
# import ParsedInput
import nltk
# import scikit-learn
import nltk.metrics
import Sentence
import regex
from implicit_args import Clause
from implicit_args import outputRecord
import ParsedInput
from syntax_tree import Syntax_tree
import copy


class argumentClassifier:
    trainingSet = [];
    testSet = [];

    def generateTrainingData(self, inputPath):
        print("Reading relations.json");
        trainingData = codecs.open(inputPath + '/relations.json', encoding='utf8');
        relations = [json.loads(x) for x in trainingData];
        print("Done");

        # Read parses.json
        print ("Reading parses.json");
        parse_file = codecs.open(inputPath + '/parses.json', encoding='utf8')
        parses = json.load(parse_file)
        print ("Done");

        for relation in relations:
            connectiveType = relation['Type'];
            if connectiveType == 'Implicit':
                arg1SentenceNumber = relation['Arg1']['TokenList'][0][3];
                arg2SentenceNumber = relation['Arg2']['TokenList'][0][3];
                print arg1SentenceNumber
                relationDocId = relation['DocID'];
                arg1Sentence = Sentence.Sentence.loadFromParser(parses[relationDocId]['sentences'][arg1SentenceNumber]);
                arg2Sentence = Sentence.Sentence.loadFromParser(parses[relationDocId]['sentences'][arg2SentenceNumber]);

                if arg1SentenceNumber == arg2SentenceNumber:
                    f2 = 0;
                elif arg2SentenceNumber - arg1SentenceNumber == 1:
                    arg1Words = map(lambda w : w[0], parses[relationDocId]["sentences"][arg1SentenceNumber]["words"])
                    arg2Words = map(lambda w : w[0], parses[relationDocId]["sentences"][arg1SentenceNumber]["words"])
                    self.addTrainingFeatures(arg1Sentence.parseTree, arg1Words, relation['Arg1']["RawText"]);
                    self.addTrainingFeatures(arg2Sentence.parseTree, arg2Words, relation['Arg2']["RawText"]);
                    #self.addTrainingFeatures(arg1Sentence.parseTree, arg1Sentence.getWordsList(), relation['Arg1']["RawText"]);
                    #self.addTrainingFeatures(arg2Sentence.parseTree, arg2Sentence.getWordsList(), relation['Arg2']["RawText"]);

                else:
                    f1 = 0;




    def getClausesFromParseTree(self, parseTree):
        clauses = [];
        parts = parseTree.split("(SBAR")[:];
        for part in parts:
            clause = regex.findall('[A-Z]?[a-z]+', part);
            if clause:
                clauses.append(Clause.Clause(' '.join(clause), part));
        return clauses;

    def list_strip_punctuation(self, list):
        punctuation = """!"#&'*+,-..../:;<=>?@[\]^_`|~""" + "``" + "''"
        i = 0
        while i < len(list) and list[i][1] in punctuation + "-LCB--LRB-":
            print list[i -1][1]
            i += 1
        if i == len(list):
            return []

        j = len(list) - 1
        while j >= 0 and list[j][1] in punctuation + "-RRB--RCB-":
            j -= 1

        return list[i: j+1]

    def getSubtree(self, syntax_tree, clause_indices):
        copy_tree = copy.deepcopy(syntax_tree)

        for index, leaf in enumerate(copy_tree.tree.get_leaves()):
            leaf.add_feature("index",index)

        clause_nodes = []
        for index in clause_indices:
            node = copy_tree.get_leaf_node_by_token_index(index)
            clause_nodes.append(node)

        for node in copy_tree.tree.traverse(strategy="levelorder"):
            node_leaves = node.get_leaves()
            if set(node_leaves) & set(clause_nodes) == set([]):
                node.detach()
        return copy_tree

    def getClausesRefined1(self, parse_dict, relations, Arg):
        relation = relations;
        DocID = relation["DocID"]
        Arg_sent_indices = sorted([item[3] for item in relation[Arg]["TokenList"]])
        if len(set(Arg_sent_indices)) != 1:
            return []
        relation_ID = relation["ID"]
        sent_index = Arg_sent_indices[0]
        Arg_list = sorted([item[4] for item in relation[Arg]["TokenList"]])

        sent_length = len(parse_dict[DocID]["sentences"][sent_index]["words"])

        # sent_indices = sorted(list(set(range(0, sent_length)) - set(conn_token_indices)))
        sent_tokens = [(index, parse_dict[DocID]["sentences"][sent_index]["words"][index][0]) for index in range(0, sent_length)]

        # first, use punctuation symbols to split the sentence
        punctuation = "...,:;?!~--"
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
            temp = self.list_strip_punctuation(clause_indices)
            if temp != []:
                clause_indices_list.append([item[0] for item in temp])

        # then use SBAR tag in its parse tree to split each part into clauses.
        parse_tree = parse_dict[DocID]["sentences"][sent_index]["parsetree"].strip()
        syntax_tree = Syntax_tree(parse_tree)

        if syntax_tree.tree == None:
            return []

        clause_list = []
        for clause_indices in clause_indices_list:
            clause_tree = self.getSubtree(syntax_tree, clause_indices)
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

        conn_token_indices = [item[4] for item in relation["Connective"]["TokenList"]]

        clauses = []# [([1,2,3],yes), ([4, 5],no), ]
        for clause_indices in clause_list:
            clauses.append(clause_indices)


        #clauseSentences = list(map(lambda clauseIndex: parse_dict[DocID]["sentences"][sent_index][clauseIndex], clauses));

        clauseSentences = [];
        for clauseIndex in clauses:
            clauseSentence = "";
            wordDelimiter = " ";
            for index in clauseIndex:
                word = parse_dict[DocID]["sentences"][sent_index]["words"][index][0];
                clauseSentence += word + wordDelimiter;
            clauseSentences.append(clauseSentence);

        return clauseSentences;

    def getClausesRefined(self, parseTree, words):

        if not parseTree:
            return []


        # first, use punctuation symbols to split the sentence
        punctuation = "...,:;?!~--"
        _clause_indices_list = []#[[(1,"I")..], ..]
        temp = []
        sent_tokens = words;
        index = 0;
        for word in sent_tokens:
            if word not in punctuation:
                temp.append((index,word))
            else:
                if temp != []:
                    _clause_indices_list.append(temp)
                    temp = []
            index += 1;
        clause_indices_list = []
        for clause_words in _clause_indices_list:
            print clause_words;
            temp = self.list_strip_punctuation(clause_words)
            if temp != []:
                clause_indices_list.append([item for item in temp])

        # then use SBAR tag in its parse tree to split each part into clauses.
        parse_tree = parseTree
        syntax_tree = Syntax_tree(parse_tree)

        if syntax_tree.tree == None:
            return []

        clause_list = []
        for clause_words in clause_indices_list:
            clause_tree = self.getSubtree(syntax_tree, clause_words)
            flag = 0
            for node in clause_tree.tree.traverse(strategy="levelorder"):
                if node.name == "SBAR":
                    temp1 = [node.index for node in node.get_leaves()]
                    temp2 = sorted(list(set(clause_words) - set(temp1)))

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
                clause_list.append(clause_words)

        clauseSentences = [];
        for clauseWordList in clause_list:
            clauseSentence = "";
            wordDelimiter = " ";
            for word in clauseWordList:
                clauseSentence += word[1] + wordDelimiter;
            clauseSentences.append(clauseSentence);

        return clauseSentences;

    def matchPartialStrings(self, a, b):
        return sum(map(lambda (x, y): 0 if x == y else 1, zip(a, b))) < 2;

    def addTrainingFeatures(self, parseTree, words, argumentRawText):
        # Get the clauses from the parseTree
        clauses= self.getClausesRefined(parseTree, words);
        clausesCount = len(clauses);
        # For each clause
        for x in range(0, clausesCount):
            # Get the previous and next clause for itself.
            # Get the featuresDictionary for the clause
            featuresDictionary = {};
            previousClause = "";
            nextClause = "";
            if x == 0 :  # The previous clause will be empty for the first clause
                if clausesCount > 1:
                    nextClause = clauses[x + 1];
                clause = Clause.Clause(clauses[x]);
                featuresDictionary = clause.getFeatures(previousClause, nextClause);
            elif x == clausesCount - 1:
                previousClause = clauses[x - 1];
                clause = Clause.Clause(clauses[x]);
                featuresDictionary = clause.getFeatures(previousClause, nextClause);
            else:  # The next clause will be empty for the last clause
                previousClause = clauses[x - 1];
                nextClause = clauses[x + 1];
                clause = Clause.Clause(clauses[x]);
                featuresDictionary = clause.getFeatures(previousClause, nextClause);
            label = 0;
            if clauses[x].strip() in argumentRawText:
            #if self.matchPartialStrings(clauses[x].strip(), argumentRawText):
                label = 1;
            else:
                label = 0;

            # Add the featuresDictionary and label to the training set
            featureTuple = (featuresDictionary, label);
            self.trainingSet.append(featureTuple);
        return

    def __init__(self):
        pass

    def getPredictedTokenListForSentence(self,parseTree, words, argumentSentence, classifier):
        argumentClauses = self.getClausesRefined(parseTree, words);
        clausesCount = len(argumentClauses);
        argumentTokenList = [];
        # For each clause
        for x in range(0, clausesCount):
            # Get the previous and next clause for itself.
            # Get the featuresDictionary for the clause
            featuresDictionary = {};
            previousClause = "";
            nextClause = "";
            if x == 0 :  # The previous clause will be empty for the first clause
                if clausesCount > 1:
                    nextClause = argumentClauses[x + 1];
                clause = Clause.Clause(argumentClauses[x]);
                featuresDictionary = clause.getFeatures(previousClause, nextClause);
            elif x == clausesCount - 1:
                previousClause = argumentClauses[x - 1];
                clause = Clause.Clause(argumentClauses[x]);
                featuresDictionary = clause.getFeatures(previousClause, nextClause);
            else:  # The next clause will be empty for the last clause
                previousClause = argumentClauses[x - 1];
                nextClause = argumentClauses[x + 1];
                clause = Clause.Clause(argumentClauses[x]);
                featuresDictionary = clause.getFeatures(previousClause, nextClause);
            if classifier.classify(featuresDictionary):
                argumentTokenList.extend(argumentSentence.getSubSequenceTokenIndexes(clause));
        return argumentTokenList;

    def getTrainingModel(self, train):
        #classifier = nltk.NaiveBayesClassifier.train(train);
        algorithm = 'IIS';
        classifier = nltk.MaxentClassifier.train(train, algorithm, trace=0, max_iter=100)
        return classifier;

    def performClassificationOnTest(self, classifier, inputPath):
        correctArg1Predictions = 0;
        wrongArg1Predictions = 0;



        testData = codecs.open(inputPath + '/relations.json', encoding='utf8');
        relations = [json.loads(x) for x in testData];

        # parse_file = codecs.open(inputPath + '/parses.json', encoding='utf8')
        # parses = json.load(parse_file)
        outputFilename = inputPath + "/output.json";

        with open(outputFilename, 'w') as f:
            t =1;

        parsedData =  ParsedInput.ParsedInput.parseFromFile(inputPath)

        parse_file = codecs.open(inputPath + '/parses.json', encoding='utf8')
        parses = json.load(parse_file)


        arg1TokenList = [];
        arg2TokenList = [];
        for relation in relations:
            connectiveType = relation['Type'];
            if connectiveType != 'Implicit':
                continue;
                relationSense = relation['Sense']
                arg1TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg1']['TokenList']));
                arg2TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg2']['TokenList']));
                connectiveTokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Connective']['TokenList']))
                relationDocId = relation['DocID'];
            if connectiveType == 'Implicit':
                arg1SentenceNumber = relation['Arg1']['TokenList'][0][3];
                print arg1SentenceNumber;
                arg2SentenceNumber = relation['Arg2']['TokenList'][0][3];
                relationDocId = relation['DocID'];
                relationSense = relation['Sense'];
                connectiveTokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Connective']['TokenList']))
                arg1Sentence = parsedData.documents[relationDocId][arg1SentenceNumber];
                arg2Sentence = parsedData.documents[relationDocId][arg2SentenceNumber];
                relationArgument1 = relation['Arg1']['RawText'];
                relationArgument2 = relation['Arg2']['RawText'];


                if arg1SentenceNumber == arg2SentenceNumber:
                    f2 = 0;
                    arg1TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg1']['TokenList']));
                    arg2TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg2']['TokenList']));
                elif arg2SentenceNumber - arg1SentenceNumber == 1:
                    arg1TokenList = self.getPredictedTokenListForSentence(arg1Sentence.parseTree, arg1Sentence.getWordsList(), arg1Sentence, classifier);
                    arg2TokenList = self.getPredictedTokenListForSentence(arg2Sentence.parseTree, arg2Sentence.getWordsList(), arg2Sentence, classifier);
                    #arg1TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg1']['TokenList']));
                    #arg2TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg2']['TokenList']));


            with open(outputFilename, 'a+') as f:
                output =  outputRecord.OutputRecord.loadFromParameters(relationDocId, relationSense, connectiveType, connectiveTokenList, arg1TokenList, arg2TokenList);
                formattedOutput = output.getFormattedOutput();
                json.dump(formattedOutput , f);
                f.write("\n");

    def performClassificationOnTestOld(self, classifier, inputPath):
        correctArg1Predictions = 0;
        wrongArg1Predictions = 0;



        testData = codecs.open(inputPath + '/relations.json', encoding='utf8');
        relations = [json.loads(x) for x in testData];

        # parse_file = codecs.open(inputPath + '/parses.json', encoding='utf8')
        # parses = json.load(parse_file)
        outputFilename = inputPath + "/output.json";

        with open(outputFilename, 'w') as f:
            t =1;

        parsedData =  ParsedInput.ParsedInput.parseFromFile(inputPath)

        arg1TokenList = [];
        arg2TokenList = [];
        for relation in relations:
            connectiveType = relation['Type'];
            if connectiveType != 'Implicit':
                continue;
                relationSense = relation['Sense']
                arg1TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg1']['TokenList']));
                arg2TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg2']['TokenList']));
                connectiveTokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Connective']['TokenList']))
                relationDocId = relation['DocID'];
            if connectiveType == 'Implicit':
                arg1SentenceNumber = relation['Arg1']['TokenList'][0][3];
                arg2SentenceNumber = relation['Arg2']['TokenList'][0][3];
                relationDocId = relation['DocID'];
                relationSense = relation['Sense'];
                connectiveTokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Connective']['TokenList']))
                arg1Sentence = parsedData.documents[relationDocId][arg1SentenceNumber];
                arg2Sentence = parsedData.documents[relationDocId][arg2SentenceNumber];
                relationArgument1 = relation['Arg1']['RawText'];
                relationArgument2 = relation['Arg2']['RawText'];


                if arg1SentenceNumber == arg2SentenceNumber:
                    f2 = 0;
                    arg1TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg1']['TokenList']));
                    arg2TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg2']['TokenList']));
                elif arg2SentenceNumber - arg1SentenceNumber == 1:
                    arg1TokenList = self.getPredictedTokenListForSentence(arg1Sentence, classifier);
                    arg2TokenList = self.getPredictedTokenListForSentence(arg2Sentence, classifier);
                    #arg1TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg1']['TokenList']));
                    #arg2TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg2']['TokenList']));


            with open(outputFilename, 'a+') as f:
                output =  outputRecord.OutputRecord.loadFromParameters(relationDocId, relationSense, connectiveType, connectiveTokenList, arg1TokenList, arg2TokenList);
                formattedOutput = output.getFormattedOutput();
                json.dump(formattedOutput , f);
                f.write("\n");


    def generateTokenListForOutput(self, tokenList):
        if tokenList:
            if len(tokenList) > 2:
                finalTokenList = tokenList[2];
                return finalTokenList;
        return;

    def classifyBasedOnTrainingSet(self, train, test):
        print "In function: classifyText";
        print "Training: " + str(train[0]);
        print "Test: " + str(test[0]);
        algorithm = 'IIS';
        classifier = nltk.MaxentClassifier.train(train, algorithm, trace=0, max_iter=100)



        correctPredictions = 0;
        wrongPredictions = 0;

        for i, (feats, label) in enumerate(test):
            observed = classifier.classify(feats)
            # print "Label:", label , "Observed" , observed;
            if label == observed:
                correctPredictions = correctPredictions + 1;
            else:
                wrongPredictions = wrongPredictions + 1;

        accuracy = (correctPredictions * 100) / (correctPredictions + wrongPredictions);

        print "Accuracy: ", accuracy;
