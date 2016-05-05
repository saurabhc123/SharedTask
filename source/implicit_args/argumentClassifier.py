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
import os.path
import pickle as pkl
import time

class argumentClassifier:
    arg1TrainingSet = [];
    arg2TrainingSet = [];
    modelPath = "implicit_args"
    arg1ModelFile = modelPath + "/arg1model.model"
    arg2ModelFile = modelPath + "/arg2model.model"
    input_relations_file = ''
    input_parses_file = ''

    def generateTrainingData(self, training_parses_file, training_relations_file):

        print("Reading relations.json");
        trainingData = codecs.open(training_relations_file, encoding='utf8');
        relations = [json.loads(x) for x in trainingData];
        print("Done");

        # Read parses.json
        print ("Reading parses.json");
        if os.path.isfile(training_parses_file):
            print "Training parses file found"
        parse_file = codecs.open(training_parses_file, encoding='utf8')

        parses = json.load(parse_file)
        print ("Done");

        self.input_parses_file = training_parses_file
        self.input_relations_file = training_relations_file

        for relation in relations:
            connectiveType = relation['Type'];
            if connectiveType == 'Implicit':
                arg1SentenceNumber = relation['Arg1']['TokenList'][0][3];
                arg2SentenceNumber = relation['Arg2']['TokenList'][0][3];

                relationDocId = relation['DocID'];
                arg1Sentence = Sentence.Sentence.loadFromParser(parses[relationDocId]['sentences'][arg1SentenceNumber]);
                arg2Sentence = Sentence.Sentence.loadFromParser(parses[relationDocId]['sentences'][arg2SentenceNumber]);

                if arg1SentenceNumber == arg2SentenceNumber:
                    f2 = 0;
                elif arg2SentenceNumber - arg1SentenceNumber == 1:
                    arg1TokenList = map(lambda token: token[4], relation['Arg1']['TokenList']);
                    arg2TokenList = map(lambda token: token[4], relation['Arg2']['TokenList']);
                    self.addTrainingFeatures(arg1TokenList, parses, relation, 'Arg1', arg1Sentence, "Arg1");
                    self.addTrainingFeatures(arg2TokenList, parses, relation, 'Arg2', arg2Sentence, "Arg2");
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
        punctuation = """!"#&'*+-..../:;<=>?@[\]^_`|~""" + "``" + "''"
        i = 0
        while i < len(list) and list[i][1] in punctuation + "-LCB--LRB-":
            i += 1
        if i == len(list):
            return []

        j = len(list) - 1
        while j >= 0 and list[j][1] in punctuation + "-RRB--RCB-":
            j -= 1

        return list[i: j + 1]

    def _get_subtree(self, syntax_tree, clause_indices):
        copy_tree = copy.deepcopy(syntax_tree)

        for index, leaf in enumerate(copy_tree.tree.get_leaves()):
            leaf.add_feature("index", index)

        clause_nodes = []
        for index in clause_indices:
            node = copy_tree.get_leaf_node_by_token_index(index)
            clause_nodes.append(node)

        for node in copy_tree.tree.traverse(strategy="levelorder"):
            node_leaves = node.get_leaves()
            if set(node_leaves) & set(clause_nodes) == set([]):
                node.detach()
        return copy_tree

    def getClausesRefinedOld(self, parse_dict, relations, Arg):
        relation = relations;
        DocID = relation["DocID"]
        Arg_sent_indices = sorted([item[3] for item in relation[Arg]["TokenList"]])
        if len(set(Arg_sent_indices)) != 1:
            return []
        relation_ID = relation["ID"]
        sent_index = Arg_sent_indices[0]
        Arg_list = sorted([item[4] for item in relation[Arg]["TokenList"]])
        relationsOutputTokenList = [(index, relation[Arg]["TokenList"][index][2]) for index in range(0, len(Arg_list))]

        sent_length = len(parse_dict[DocID]["sentences"][sent_index]["words"])

        # sent_indices = sorted(list(set(range(0, sent_length)) - set(conn_token_indices)))
        sent_tokens = [(index, parse_dict[DocID]["sentences"][sent_index]["words"][index][0]) for index in
                       range(0, sent_length)]

        # first, use punctuation symbols to split the sentence
        punctuation = "...,:;?!~--"
        _clause_indices_list = []  # [[(1,"I")..], ..]
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
            # print "****" , clause_indices;
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
            clause_tree = self._get_subtree(syntax_tree, clause_indices)
            flag = 0
            for node in clause_tree.tree.traverse(strategy="levelorder"):
                if node.name == "SBAR":
                    temp1 = [node.index for node in node.get_leaves()]
                    temp2 = sorted(list(set(clause_indices) - set(temp1)))

                    if temp2 == []:
                        clause_list.append(temp1)
                    else:
                        if temp1[0] < temp2[0]:
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

        clauses = []  # [([1,2,3],yes), ([4, 5],no), ]
        for clause_indices in clause_list:
            clauses.append(clause_indices)

        return clauses;

    def getClausesRefined(self, parseTree, wordsParam):

        if not parseTree:
            return []

        # first, use punctuation symbols to split the sentence
        punctuation = "...,:;?!~--"
        _clause_indices_list = []  # [[(1,"I")..], ..]
        temp = []
        words = map(lambda word: word.actualWord, wordsParam);
        sent_tokens = words;

        index = 0;
        for word in sent_tokens:
            if word not in punctuation:
                temp.append((index, word))
            else:
                if temp != []:
                    temp.append((index, word))
                    _clause_indices_list.append(temp)
                    temp = []
            index += 1;
        clause_indices_list = []
        for clause_words in _clause_indices_list:
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
            # print "####" , clause_words;
            # clause_tree = self._get_subtree(syntax_tree, clause_words)
            clause_word_indices = map(lambda w: w[0], clause_words);
            clause_tree = self._get_subtree(syntax_tree, clause_word_indices)

            flag = 0
            for node in clause_tree.tree.traverse(strategy="levelorder"):
                if node.name == "SBAR":
                    temp1 = [node.index for node in node.get_leaves()]
                    temp2 = sorted(list(set(clause_word_indices) - set(temp1)))

                    if temp2 == []:
                        clause_list.append(temp1)
                    else:
                        if temp1[0] < temp2[0]:
                            clause_list.append(temp1)
                            clause_list.append(temp2)
                        else:
                            clause_list.append(temp2)
                            clause_list.append(temp1)

                    flag = 1
                    break
            if flag == 0:
                # clause_list.append(clause_words[0])
                clause_list.append(clause_word_indices)

        # clauseSentences = [];
        # for clauseWordList in clause_list:
        #     clauseSentence = "";
        #     wordDelimiter = " ";
        #     for index in clauseWordList:
        #         clauseSentence += words[index] + wordDelimiter;
        #     clauseSentences.append(clauseSentence);
        # clauseWordsWithPos  = map(lambda clauseIndex: (wordsParam[clauseIndex], wordsParam[clauseIndex]) , clause_list);
        return clause_list;

    def addTrainingFeatures(self, argumentOutputTokens, parse_dict, relations, Arg, argSentence, argType):
        # Get the clauses from the parseTree
        clauses = self.getClausesRefinedOld(parse_dict, relations, Arg);
        clauseWords = argSentence.getWordsList();
        # clauses1= self.getClausesRefined(argSentence.parseTree, argSentence.getWordsList());
        clausesCount = len(clauses);
        # For each clause
        for x in range(0, clausesCount):
            # Get the previous and next clause for itself.
            # Get the featuresDictionary for the clause
            featuresDictionary = {};
            previousClause = "";
            nextClause = "";
            if x == 0:  # The previous clause will be empty for the first clause
                if clausesCount > 1:
                    nextClause = clauses[x + 1];
                clause = Clause.Clause(clauses[x], argSentence);
                featuresDictionary = clause.getFeatures(previousClause, nextClause, argType);
            elif x == clausesCount - 1:
                previousClause = clauses[x - 1];
                clause = Clause.Clause(clauses[x], argSentence);
                featuresDictionary = clause.getFeatures(previousClause, nextClause, argType);
            else:  # The next clause will be empty for the last clause
                previousClause = clauses[x - 1];
                nextClause = clauses[x + 1];
                clause = Clause.Clause(clauses[x], argSentence);
                featuresDictionary = clause.getFeatures(previousClause, nextClause, argType);
            label = 0;
            if self.compare_intersect(clauses[x], argumentOutputTokens):
                label = 1;
            else:
                label = 0;

            # Add the featuresDictionary and label to the training set
            featureTuple = (featuresDictionary, label);
            if (argType in "Arg1"):
                self.arg1TrainingSet.append(featureTuple);
            else:
                self.arg2TrainingSet.append(featureTuple);
        return

    def compare_intersect(self, x, y):
        result = frozenset(x).intersection(y)
        return result == frozenset(x);

    def __init__(self, input_relations_file, input_parses_file):
        self.input_parses_file = input_parses_file
        self.input_relations_file = input_relations_file
        pass

    def getPredictedTokenListForSentence(self, argumentSentence, classifier, argType):
        parseTree = argumentSentence.parseTree;
        # words = argumentSentence.getWordsList();
        words = argumentSentence.words
        punctuation = "...,:;?!~--"
        # argumentClauses = self.getClausesRefinedOld1(parse_dict, relations, Arg);
        argumentClauses = self.getClausesRefined(parseTree, words);
        words = map(lambda word: (word.actualWord, word.partOfSpeech), argumentSentence.words)
        clausesCount = len(argumentClauses);
        argumentTokenList = [];
        # For each clause
        for x in range(0, clausesCount):
            # Get the previous and next clause for itself.
            # Get the featuresDictionary for the clause
            featuresDictionary = {};
            previousClause = "";
            nextClause = "";
            if x == 0:  # The previous clause will be empty for the first clause
                if clausesCount > 1:
                    nextClause = argumentClauses[x + 1];
                #Clean the clause of unwanted characters
                clauseLength = len(argumentClauses[x]);
                if( clauseLength > 2):
                    #Check last two indexes
                    if(argumentClauses[x][clauseLength - 1] - argumentClauses[x][clauseLength - 2] > 1):
                        #pop the last one if the difference is more than 1
                        argumentClauses[x].pop(-1);
                clause = Clause.Clause(argumentClauses[x], argumentSentence);
                featuresDictionary = clause.getFeatures(previousClause, nextClause, argType);
            elif x == clausesCount - 1:
                previousClause = argumentClauses[x - 1];
                clause = Clause.Clause(argumentClauses[x], argumentSentence);
                featuresDictionary = clause.getFeatures(previousClause, nextClause, argType);
            else:  # The next clause will be empty for the last clause
                previousClause = argumentClauses[x - 1];
                nextClause = argumentClauses[x + 1];
                clause = Clause.Clause(argumentClauses[x], argumentSentence);
                featuresDictionary = clause.getFeatures(previousClause, nextClause, argType);
            if classifier.classify(featuresDictionary):
                relevantTokens = map(lambda outputTokenIndex: argumentSentence.startTokenIndex + outputTokenIndex,
                                     argumentClauses[x]);
                #Include the intermediary tokens if subsequent clauses are being added.
                if argumentTokenList:
                    tokenListLength = len(argumentTokenList);
                    diff =  argumentClauses[x][0] + argumentSentence.startTokenIndex - argumentTokenList[tokenListLength - 1];
                    if(diff > 1 and diff < 3):
                        argumentTokenList.append(argumentTokenList[tokenListLength - 1] + 1)
                argumentTokenList.extend(relevantTokens);


        # if argumentTokenList:
        #     try:
        #         argumentTokenListLength = len(argumentTokenList)
        #         lastToken = words[argumentTokenListLength + 1][0]
        #         # ww = map(lambda tokenIndex: words[argumentSentence.startTokenIndex - tokenIndex][0],
        #         #             argumentTokenList)
        #         # print ww;
        #         print "Found last token" , lastToken;
        #         if lastToken in punctuation:
        #             print "Popped last token" , lastToken;
        #             argumentTokenList.pop(-1);
        #     except:
        #         print("Index out of range: For words and tokens", len(argumentTokenList), len(words))


        return argumentTokenList;

    def getTrainingModel(self, train):
        # classifier = nltk.NaiveBayesClassifier.train(train);
        algorithm = 'IIS';
        classifier = nltk.MaxentClassifier.train(train, algorithm, trace=0, max_iter=100)
        return classifier;

    def do_models_exist(self):
        if os.path.isfile(self.arg1ModelFile) and os.path.isfile(self.arg2ModelFile):
            return 1
        return 0

    def get_arg1_model(self):
        #Load Arg1 model
        if os.path.isfile(self.arg1ModelFile):
            with open(self.arg1ModelFile, "r") as filename:
                arg1Model = pkl.load(filename)
                #If it exists, return it.
                return arg1Model

        #else create it
        arg1Model = self.getTrainingModel(self.arg1TrainingSet)
        f = open(self.arg1ModelFile, 'wb')
        pkl.dump(arg1Model, f)
        f.close()
        return arg1Model

    def get_arg2_model(self):
        #Load Arg2 model
        if os.path.isfile(self.arg2ModelFile):
            with open(self.arg2ModelFile, "r") as filename:
                arg2Model = pkl.load(filename)
                #If it exists, return it.
                return arg2Model

        #else create it
        arg2Model = self.getTrainingModel(self.arg1TrainingSet)
        f = open(self.arg2ModelFile, 'wb')
        pkl.dump(arg2Model, f)
        f.close()
        return arg2Model

    def performClassificationOnTest1(self, arg1Classifier, arg2Classifier, outputFilename):
        correctArg1Predictions = 0;
        wrongArg1Predictions = 0;
        punctuation = "...,:;?!~--"
        testData = codecs.open(self.input_relations_file, encoding='utf8');
        relations = [json.loads(x) for x in testData];

        # parse_file = codecs.open(inputPath + '/parses.json', encoding='utf8')
        # parses = json.load(parse_file)
        comparisonFileName = outputFilename + "-comparison.json";

        with open(outputFilename, 'w') as f:
            t = 1;

        with open(comparisonFileName, 'w') as f:
            t = 1;

        parsedData = ParsedInput.ParsedInput.parseFromFile(self.input_parses_file)

        parse_file = codecs.open(self.input_parses_file, encoding='utf8')
        parses = json.load(parse_file)

        arg1TokenList = [];
        arg2TokenList = [];
        for relation in relations:
            connectiveType = relation['Type'];
            connective = relation['Connective']
            id = relation["ID"]
            if connectiveType != 'Implicit':
                # continue;
                relationSense = relation['Sense']
                arg1TokenList = list(
                    map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg1']['TokenList']));
                arg2TokenList = list(
                    map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg2']['TokenList']));
                relationDocId = relation['DocID'];
            if connectiveType == 'Implicit':
                arg1SentenceNumber = relation['Arg1']['TokenList'][0][3];
                arg2SentenceNumber = relation['Arg2']['TokenList'][0][3];
                relationDocId = relation['DocID'];
                relationSense = relation['Sense'];
                arg1Sentence = parsedData.documents[relationDocId][arg1SentenceNumber];
                arg2Sentence = parsedData.documents[relationDocId][arg2SentenceNumber];
                relationArgument1 = relation['Arg1']['RawText'];
                relationArgument2 = relation['Arg2']['RawText'];

                if arg1SentenceNumber == arg2SentenceNumber:
                    f2 = 0;
                    arg1TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList),
                                             relation['Arg1']['TokenList']));
                    arg2TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList),
                                             relation['Arg2']['TokenList']));
                elif arg2SentenceNumber - arg1SentenceNumber == 1:
                    arg1TokenList = self.getPredictedTokenListForSentence(arg1Sentence, arg1Classifier, "Arg1");
                    arg2TokenList = self.getPredictedTokenListForSentence(arg2Sentence, arg2Classifier, "Arg2");
                    # arg1TokenList = self.getPredictedTokenListForSentence(arg1Sentence.parseTree,  parses, relation, 'Arg1', classifier);
                    # arg2TokenList = self.getPredictedTokenListForSentence(arg2Sentence,  parses, relation, 'Arg2', classifier);
                    # arg1TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg1']['TokenList']));
                    # arg2TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg2']['TokenList']));



                    # ----------------------- Uncomment the below to do comparisons.
                    arg1WordList = map(
                        lambda tokenIndex: arg1Sentence.words[tokenIndex - arg1Sentence.startTokenIndex].actualWord,
                        arg1TokenList)
                    arg2WordList = map(
                        lambda tokenIndex: arg2Sentence.words[tokenIndex - arg2Sentence.startTokenIndex].actualWord,
                        arg2TokenList)
                    relationArg1TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList),
                                                     relation['Arg1']['TokenList']));
                    relationArg2TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList),
                                                     relation['Arg2']['TokenList']));


                    if len(arg1WordList) == 0:
                        arg1WordList = map(lambda word: word.actualWord, arg1Sentence.words)


                    if len(arg2WordList) == 0:
                        arg2WordList = map(lambda word: word.actualWord, arg2Sentence.words)

                    if arg1WordList:
                        if (arg1WordList[len(arg1WordList) - 1]) in punctuation:
                            arg1WordList.pop(-1);

                    if arg2WordList:
                        if (arg2WordList[len(arg2WordList) - 1]) in punctuation:
                            arg2WordList.pop(-1);



                    matchFound = ''

                    with open(comparisonFileName, 'a+') as f:
                        try:
                            if len(arg1WordList) != len(relationArg1TokenList):
                                matchFound = "Arg1 match not found" , id
                                json.dump(matchFound, f);
                                f.write("\n");
                                f.write(" ".join(arg1WordList));
                                f.write("\n");
                                arg1TokenListGold = map(lambda tokenIndex: arg1Sentence.words[
                                    tokenIndex - arg1Sentence.startTokenIndex].actualWord, relationArg1TokenList)
                                f.write(" ".join(arg1TokenListGold));
                                f.write("\n\n");

                            if len(arg2WordList) == len(relationArg2TokenList):
                                matchFound = "Arg2 match found"
                            else:
                                matchFound = "Arg2 match not found" , id
                                json.dump(matchFound, f);
                                f.write("\n");
                                f.write(" ".join(arg2WordList));
                                f.write("\n");
                                arg2TokenListGold = map(lambda tokenIndex: arg2Sentence.words[
                                    tokenIndex - arg2Sentence.startTokenIndex].actualWord, relationArg2TokenList)
                                f.write(" ".join(arg2TokenListGold));
                                f.write("\n\n");


                        except:
                            print("Index out of range: Relation1", relationArg1TokenList)
                            print("Index out of range: Relation2", relationArg2TokenList)









                            # with open(outputFilename, 'a+') as f:
                            #     output =  outputRecord.OutputRecord.loadFromParameters(relationDocId, relationSense, connectiveType, connectiveTokenList, arg1TokenList, arg2TokenList);
                            #     formattedOutput = output.getFormattedOutput();
                            #     json.dump(formattedOutput , f);
                            #     f.write("\n");

    def performClassificationOnTest(self, arg1Classifier, arg2Classifier, outputFilename):

        testData = codecs.open(self.input_relations_file, encoding='utf8');
        relations = [json.loads(x) for x in testData];

        punctuation = "...,:;?!~--"

        with open(outputFilename, 'w') as f:
            t = 1;

        parsedData = ParsedInput.ParsedInput.parseFromFile(self.input_parses_file)

        arg1TokenList = [];
        arg2TokenList = [];

        for relation in relations:
            connectiveType = relation['Type'];
            arg1RelationsTokenList = relation['Arg1']['TokenList'];
            arg2RelationsTokenList = relation['Arg2']['TokenList'];
            arg1SentenceNumber = relation['Arg1']['TokenList'][0][3];
            arg2SentenceNumber = relation['Arg2']['TokenList'][0][3];
            relationDocId = relation['DocID'];
            relationSense = relation['Sense'];
            if 'RawText' in relation['Arg1']:
                arg1RawText = relation['Arg1']['RawText']
            else:
                arg1RawText = ''

            if 'RawText' in relation['Arg2']:
                arg2RawText = relation['Arg2']['RawText']
            else:
                arg2RawText = ''

            connective = relation['Connective']
            id = relation['ID']
            if connectiveType != 'Implicit':
                arg1TokenList = list(
                    map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg1']['TokenList']));
                arg2TokenList = list(
                    map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg2']['TokenList']));

            if connectiveType == 'Implicit':
                arg1Sentence = parsedData.documents[relationDocId][arg1SentenceNumber];
                arg2Sentence = parsedData.documents[relationDocId][arg2SentenceNumber];

                if arg1SentenceNumber == arg2SentenceNumber:
                    f2 = 0;
                    arg1TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList),
                                             relation['Arg1']['TokenList']));
                    arg2TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList),
                                             relation['Arg2']['TokenList']));
                elif arg2SentenceNumber - arg1SentenceNumber == 1:
                    arg1TokenList = self.getPredictedTokenListForSentence(arg1Sentence, arg1Classifier, "Arg1");
                    arg2TokenList = self.getPredictedTokenListForSentence(arg2Sentence, arg2Classifier, "Arg2");
                    # arg1TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg1']['TokenList']));
                    # arg2TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg2']['TokenList']));

                    arg1WordList = map(
                            lambda tokenIndex: arg1Sentence.words[tokenIndex - arg1Sentence.startTokenIndex].actualWord,
                            arg1TokenList)
                    arg2WordList = map(
                                lambda tokenIndex: arg2Sentence.words[tokenIndex - arg2Sentence.startTokenIndex].actualWord,
                                arg2TokenList)



                    if len(arg1TokenList) == 0:
                        arg1WordList = map(lambda word: word.actualWord, arg1Sentence.words)

                    if len(arg2TokenList) == 0:
                        arg2WordList = map(lambda word: word.actualWord, arg2Sentence.words)

                    if arg1WordList:
                        if (arg1WordList[len(arg1WordList) - 1]) in punctuation:
                            arg1WordList.pop(-1);
                            if len(arg1TokenList) != 0:
                                arg1TokenList.pop(-1);

                    if arg2WordList:
                        if (arg2WordList[len(arg2WordList) - 1]) in punctuation:
                            arg2WordList.pop(-1);
                            if len(arg2TokenList) != 0:
                                arg2TokenList.pop(-1);

                    if len(arg1TokenList) == 0:
                        for i in range(arg1Sentence.startTokenIndex , arg1Sentence.startTokenIndex + len(arg1WordList), 1):
                            arg1TokenList.append(i);

                    if len(arg2TokenList) == 0:
                        for i in range(arg2Sentence.startTokenIndex , arg2Sentence.startTokenIndex + len(arg2WordList), 1):
                            arg2TokenList.append(i);

                arg1RelationsTokenList = []
                arg2RelationsTokenList = []

                for argToken in arg1TokenList:
                    arg1RelationsTokenList.append([0, 0, argToken, arg1SentenceNumber, argToken - arg1Sentence.startTokenIndex]);
                for argToken in arg2TokenList:
                    arg2RelationsTokenList.append([0, 0, argToken, arg2SentenceNumber, argToken - arg2Sentence.startTokenIndex]);

                arg1RawText = "".join([('' if word in punctuation else ' ')+word for word in arg1WordList])
                arg2RawText = "".join([('' if word in punctuation else ' ')+word for word in arg2WordList])

            with open(outputFilename, 'a+') as f:
                output = outputRecord.OutputRecord.loadFromParameters(relationDocId, relationSense, connectiveType,
                                                                      connective, arg1RelationsTokenList,
                                                                      arg2RelationsTokenList, id);
                formattedOutput = output.getFormattedOutputForRelations(arg1RawText,arg2RawText);
                json.dump(formattedOutput, f, sort_keys=True);
                f.write("\n");

    def performClassificationOnTestOld(self, arg1Classifier, arg2Classifier, outputFilename):
        correctArg1Predictions = 0;
        wrongArg1Predictions = 0;

        testData = codecs.open(self.input_relations_file, encoding='utf8');
        relations = [json.loads(x) for x in testData];

        punctuation = "...,:;?!~--"
        # parse_file = codecs.open(inputPath + '/parses.json', encoding='utf8')
        # parses = json.load(parse_file)
        comparisonFileName = outputFilename + "-comparison.json";

        with open(outputFilename, 'w') as f:
            t = 1;

        parsedData = ParsedInput.ParsedInput.parseFromFile(self.input_parses_file)

        arg1TokenList = [];
        arg2TokenList = [];
        for relation in relations:
            connectiveType = relation['Type'];
            if connectiveType != 'Implicit':
                # continue;
                relationSense = relation['Sense']
                arg1TokenList = list(
                    map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg1']['TokenList']));
                arg2TokenList = list(
                    map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg2']['TokenList']));
                connectiveTokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList),
                                               relation['Connective']['TokenList']))
                relationDocId = relation['DocID'];
            if connectiveType == 'Implicit':
                arg1SentenceNumber = relation['Arg1']['TokenList'][0][3];
                arg2SentenceNumber = relation['Arg2']['TokenList'][0][3];
                relationDocId = relation['DocID'];
                relationSense = relation['Sense'];
                connectiveTokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList),
                                               relation['Connective']['TokenList']))
                arg1Sentence = parsedData.documents[relationDocId][arg1SentenceNumber];
                arg2Sentence = parsedData.documents[relationDocId][arg2SentenceNumber];
                relationArgument1 = relation['Arg1']['RawText'];
                relationArgument2 = relation['Arg2']['RawText'];

                if arg1SentenceNumber == arg2SentenceNumber:
                    f2 = 0;
                    arg1TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList),
                                             relation['Arg1']['TokenList']));
                    arg2TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList),
                                             relation['Arg2']['TokenList']));
                elif arg2SentenceNumber - arg1SentenceNumber == 1:
                    arg1TokenList = self.getPredictedTokenListForSentence(arg1Sentence, arg1Classifier, "Arg1");
                    arg2TokenList = self.getPredictedTokenListForSentence(arg2Sentence, arg2Classifier, "Arg2");
                    # arg1TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg1']['TokenList']));
                    # arg2TokenList = list(map(lambda tokenList: self.generateTokenListForOutput(tokenList), relation['Arg2']['TokenList']));

                    arg1WordList = map(
                            lambda tokenIndex: arg1Sentence.words[tokenIndex - arg1Sentence.startTokenIndex].actualWord,
                            arg1TokenList)
                    arg2WordList = map(
                                lambda tokenIndex: arg2Sentence.words[tokenIndex - arg2Sentence.startTokenIndex].actualWord,
                                arg2TokenList)

                    if arg1WordList:
                        if (arg1WordList[len(arg1WordList) - 1]) in punctuation:
                            arg1TokenList.pop(-1);

                    if arg2WordList:
                        if (arg2WordList[len(arg2WordList) - 1]) in punctuation:
                            arg2TokenList.pop(-1);





            with open(outputFilename, 'a+') as f:
                output = outputRecord.OutputRecord.loadFromParameters(relationDocId, relationSense, connectiveType,
                                                                      connectiveTokenList, arg1TokenList,
                                                                      arg2TokenList);
                formattedOutput = output.getFormattedOutput();
                json.dump(formattedOutput, f);
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

def extract_implicit_arguments(input_relations_file, input_parses_file, output_relations_file):
    """

    Args:
        input_relations_file:
        input_parses_file:
        output_relations_file:
    """
    argumentClassifierInstance = argumentClassifier(input_relations_file, input_parses_file);
    print "Loading the models for implicit arguments..." + (time.strftime("%I:%M:%S"))
    if not argumentClassifierInstance.do_models_exist():
        print "Pre-trained models for implicit arguments not found"
        exit();
    else:
        print "Pre-trained models for implicit arguments found..."
    trainedArg1Model = argumentClassifierInstance.get_arg1_model()
    trainedArg2Model = argumentClassifierInstance.get_arg2_model()
    print "Making predictions now for implicit arguments..." + (time.strftime("%I:%M:%S"))
    argumentClassifierInstance.performClassificationOnTest(trainedArg1Model, trainedArg2Model, output_relations_file)
