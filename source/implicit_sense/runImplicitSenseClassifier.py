import senseClassifier
import Sentence



if __name__ == '__main__':
     print ("Hello World");
     senseClassifierInstance = senseClassifier.senseClassifier();


     senseClassifierInstance.readInput('../data/conll16st-en-01-12-16-train', 'train');
     #print "Training Set: ", trainingSet;
     senseClassifierInstance.readInput('../data/conll16st-en-01-12-16-dev', 'test');
     #print "Test Set: ", testSet;
     senseClassifierInstance.classifyText(senseClassifierInstance.trainingSet, senseClassifierInstance.testSet);

     #Classifiers.test_maxent(nltk.classify.MaxentClassifier.ALGORITHMS, trainingSet, testSet);
     print "Done";

