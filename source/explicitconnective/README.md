To run evaluation, just run evaluate_connective_classifier_maxent.py from the command line:

python  evaluate_connective_classifier_maxent.py 

Make sure parses.json for the data you want to test on is in the same folder.

The code should write the scorer-format output file and relations.json file for the next component in the same folder. 


Running with parameters would be something like this.

python evaluate_connective_classifier_maxent.py ../../input/parses.json savedClassifier0414maxentGIStraintestconnonly.json connectivelist ../../output/explicitconnective


