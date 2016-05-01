import codecs
import json
# import ParsedInput
import nltk
import collections
# import scikit-learn
from sklearn import cross_validation
import nltk.metrics
import Sentence


class senseClassifier:
    trainingSet = [];
    testSet = [];

    def readInput(self, inputFilenamePath, trainOrTest):
        print("In function: readInput");
        # Read relations.json
        print("Reading relations.json");
        pdtb_file = codecs.open(inputFilenamePath + '/relations.json', encoding='utf8');
        relations = [json.loads(x) for x in pdtb_file];
        print("Done");

        # Read parses.json
        print ("Reading parses.json");
        parse_file = codecs.open(inputFilenamePath + '/parses.json', encoding='utf8')
        en_parse_dict = json.load(parse_file)
        print ("Done");

        counter = 0;
        flag = 0;
        featureSet = [];
        labelSet = [];
        # trainingSet = [];
        # testSet = [];
        countOfImplicit = 0;
        for relation in relations:
            cType = relation['Type'];
            if cType == 'Implicit':
                countOfImplicit = countOfImplicit + 1;
                parseJSON_sentence_number = relation['Arg2']['TokenList'][0][3];
                relation_DocID = relation['DocID'];
                #Parses.json object for that relation
                #sentence = en_parse_dict[relation_DocID]['sentences'][parseJSON_sentence_number];
                sentence = Sentence.Sentence.loadFromParser(en_parse_dict[relation_DocID]['sentences'][parseJSON_sentence_number]);
                senseLabel = relation['Sense'][0];

                # Building Feature Set
                features = [];

                # Feature 1: First word, just for testing.
                firstWord = sentence.words[0].actualWord;
                features.append(firstWord);

                tup1 = ();
                t = self.getImplicitSenseFeatures(firstWord, senseLabel)
                if (trainOrTest == 'train'):
                    self.trainingSet.append(t);
                else:
                    self.testSet.append(t);

                featureSet.append(features);
                labelSet.append(senseLabel);
        counter = counter + 1;
        print "Number of Explicit Relations: " + str(countOfImplicit);
        # print "Size of Feature Set: " + str(len(featureSet));
        # print "Size of Label Set: " + str(len(labelSet));
        print "Size of Training Set: " + str(len(self.trainingSet));
        num_folds = 10
        # cv = cross_validation.KFold(len(trainingSet), n_folds=10, indices=True, shuffle=False, random_state=None)
        cv = cross_validation.KFold(len(self.trainingSet), n_folds=num_folds, shuffle=True, random_state=None);
        accuracy = 0.0;
        p = 0.0;
        r = 0.0;
        f = 0.0;

        p1 = 0.0;
        r1 = 0.0;
        f1 = 0.0;



    def __init__(self):
        pass

    def getImplicitSenseFeatures(self, connectiveWordID, label):
        f = {'firstWord': connectiveWordID}
        t = (f, label);
        return t

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
            #print "Label:", label , "Observed" , observed;
            if label == observed:
                correctPredictions = correctPredictions + 1;
            else:
                wrongPredictions = wrongPredictions + 1;

        accuracy = (correctPredictions * 100) / (correctPredictions + wrongPredictions);

        print "Accuracy: ", accuracy;
