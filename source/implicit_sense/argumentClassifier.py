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
import regex
from implicit import Clause


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

                relationDocId = relation['DocID'];
                arg1Sentence = Sentence.Sentence.loadFromParser(parses[relationDocId]['sentences'][arg1SentenceNumber]);
                arg2Sentence = Sentence.Sentence.loadFromParser(parses[relationDocId]['sentences'][arg2SentenceNumber]);

                if arg1SentenceNumber == arg2SentenceNumber:
                    f2 = 0;
                elif arg2SentenceNumber - arg1SentenceNumber == 1:
                    self.addTrainingFeatures(relation['Arg1']['RawText'], arg1Sentence.parseTree);
                    self.addTrainingFeatures(relation['Arg2']['RawText'], arg2Sentence.parseTree);
                else:
                    f1 = 0;




    def getClausesFromParseTree(self, parseTree):
        clauses = [];
        parts = parseTree.split("(S")[:];
        for part in parts:
            clause = regex.findall('[A-Z]?[a-z]+', part);
            if clause:
                clauses.append(' '.join(clause));
        return clauses;



    def addTrainingFeatures(self, argumentRawText, sentenceParseTree):
        # Get the clauses from the parseTree
        clauses = self.getClausesFromParseTree(sentenceParseTree);
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
            if clauses[x] in argumentRawText:
                label = 1;

            # Add the featuresDictionary and label to the training set
            featureTuple = (featuresDictionary, label);
            self.trainingSet.append(featureTuple);
        return

    def __init__(self):
        pass

    def classifyText(self, train, test):
        print "In function: classifyText";
        print "Training: " + str(train[0]);
        print "Test: " + str(test[0]);
        classifier = nltk.NaiveBayesClassifier.train(train);
        refsets = collections.defaultdict(set)
        testsets = collections.defaultdict(set)
        truth = set();
        predicted = set();

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
