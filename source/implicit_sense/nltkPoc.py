import nltk
import implicit.inputStatistics
from implicit import argumentClassifier


def gender_features(word):
    return {'last_letter': word[-1], 'jeeper':word[1]}


from nltk.corpus import names


def statisticsTest():
    inputStatisticsInstance = implicit.inputStatistics.inputStatistics();
    inputStatisticsInstance.generateSentenceStatistics('../data/conll16st-en-01-12-16-train');
    inputStatisticsInstance.generateSentenceStatistics('../data/conll16st-en-01-12-16-dev');

def TestClauses():
    parseTree = "( (S (NP (NNP Kemper) (NNP Financial) (NNPS Services) (NNP Inc.)) (, ,) (S (VP (VBG charging) (SBAR (IN that) (S (NP (NN program) (NN trading)) (VP (VBZ is) (VP (VBG ruining) (NP (DT the) (NN stock) (NN market)))))))) (, ,) (VP (VBD cut) (PRT (RP off)) (NP (CD four) (JJ big) (NNP Wall) (NNP Street) (NNS firms)) (PP (IN from) (S (VP (VBG doing) (NP (NP (DT any)) (PP (IN of) (NP (PRP$ its) (NN stock-trading) (NN business)))))))) (. .)) )";
    parseTree1 = "(S(CLAUSE(VP(VP they/PRP were/VBD delivered/VBN promptly/RB) and/CC(VP a/DT very/RB))(NP (NP good/JJ value/NN) and/CC (NP excellent/NN)))(CLAUSE(VP all/DT)(NP (NP around/IN (NP slipper/NN)) (NP with/IN (NP traction/NN))))  ./.)";
    parseTree2 = "( (S (NP (NP (DT The) (NNP Kemper) (NNP Corp.) (NN unit)) (CC and) (NP (JJ other) (NNS critics))) (VP (VBP complain) (SBAR (IN that) (S (NP (NN program) (NN trading)) (VP (VP (VBZ causes) (NP (NP (JJ wild) (NNS swings)) (PP (PP (IN in) (NP (NN stock) (NNS prices))) (, ,) (PP (JJ such) (IN as) (PP (IN on) (NP (NNP Tuesday)))) (CC and) (PP (IN on) (NP (NP (NNP Oct.) (CD 13)) (CC and) (CD 16)))))) (, ,) (CC and) (VP (VBZ has) (VP (VBN increased) (NP (NP (NNS chances)) (PP (IN for) (NP (NN market) (NNS crashes)))))))))) (. .)) )( (S (PP (IN Over) (NP (DT the) (JJ past) (CD nine) (NNS months))) (, ,) (NP (NP (JJ several) (NNS firms)) (, ,) (PP (VBG including) (NP (NP (NN discount) (NN broker) (NNP Charles) (NNP Schwab) (CC &) (NNP Co.)) (CC and) (NP (NP (NNP Sears) (, ,) (NNP Roebuck) (CC &) (NNP Co.) (POS 's)) (NNP Dean) (NNP Witter) (NNP Reynolds) (NNP Inc.) (NN unit)))) (, ,)) (VP (VBP have) (VP (VBN attacked) (NP (NN program) (NN trading)) (PP (IN as) (NP (DT a) (JJ major) (NN market) (NN evil))))) (. .)) )";
    # argumentClassifierInstance = implicit.argumentClassifier.argumentClassifier();
    # clauses = argumentClassifierInstance.getClausesFromParseTree(parseTree2);
    # print clauses

def nltkTest():
    labeled_names = ([(name, 'male') for name in names.words('male.txt')] +
                     [(name, 'female') for name in names.words('female.txt')])
    import random
    random.shuffle(labeled_names)
    featuresets = [(gender_features(n), gender) for (n, gender) in labeled_names]
    train_set, test_set = featuresets[500:], featuresets[:500]
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    val = classifier.classify(gender_features('Neo'))
    print val

def argumentClassifierTest():
    argumentClassifierInstance = argumentClassifier.argumentClassifier();
    argumentClassifierInstance.generateTrainingData('../data/conll16st-en-01-12-16-dev')
    argumentClassifierInstance.classifyText(argumentClassifierInstance.trainingSet, argumentClassifierInstance.trainingSet);

argumentClassifierTest();
#statisticsTest();
# TestClauses();
# nltkTest()


