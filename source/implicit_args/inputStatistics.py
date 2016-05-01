import codecs
import json
# import ParsedInput
# import scikit-learn


class inputStatistics:

    def generateSentenceStatistics(self, inputFilenamePath):
        print("In function: readInput");
        # Read relations.json
        print("Reading relations.json");
        pdtb_file = codecs.open(inputFilenamePath + '/relations.json', encoding='utf8');
        relations = [json.loads(x) for x in pdtb_file];
        print ("Done");

        sameSentence = 0;
        differentSentence = 0;
        countOfConnectiveType = 0;
        subsequentSentence = 0;
        for relation in relations:
            cType = relation['Type'];

            if cType == 'Implicit':
                countOfConnectiveType = countOfConnectiveType + 1;
                arg1SentenceNumber = relation['Arg1']['TokenList'][0][3];
                arg2SentenceNumber = relation['Arg2']['TokenList'][0][3];

                if arg1SentenceNumber == arg2SentenceNumber:
                    sameSentence = sameSentence + 1;
                elif arg2SentenceNumber - arg1SentenceNumber == 1:
                    subsequentSentence = subsequentSentence + 1;
                else:
                    differentSentence = differentSentence + 1;
        print "Number of Implicit Relations: " + str(countOfConnectiveType);
        print "Same sentence count: " + str(sameSentence) + "("+ str((sameSentence*100)/countOfConnectiveType) + "%)";
        print "Subsequent sentence count: " + str(subsequentSentence)+ "("+ str((subsequentSentence*100)/countOfConnectiveType) + "%)";
        print "Different sentence count: " + str(differentSentence)+ "("+ str((differentSentence*100)/countOfConnectiveType) + "%)";


    def __init__(self):
        pass

