import nltk


class Classifiers:

    def test_maxent(algorithms, train, test):
         print train[0];
         print test[0];
         #train = [(dict(a=1, b=2, c=3), 'x')];
         #test = [(dict(a=1, b=2, c=3))];

         maxentClassifiers = {}
         algorithm = 'IIS'
         print algorithm;
         maxentClassifiers[algorithm] = nltk.MaxentClassifier.train(train, algorithm, trace=0, max_iter=1000)
         print "Hello";
         for algorithm, classifier in maxentClassifiers.items():
             for featureset in test:
                 pdist = classifier.prob_classify(featureset)
             print

         return maxentClassifiers