import codecs;
import json;
from implicit_args import outputRecord;


class outputGenerator:


    def __init__(self):
        pass

    def generateGoldOutput(self, inputPath):
        print("Reading relations.json");
        trainingData = codecs.open(inputPath + '/relations.json', encoding='utf8');
        relations = [json.loads(x) for x in trainingData];
        print("Done");

        outputFilename = inputPath + "/output.json";

        with open(outputFilename, 'w') as f :#clear the file
            pass;

        for relation in relations:
            connectiveType = relation['Type'];
            if 1:#connectiveType == 'Explicit':
                arg1TokenList = relation['Arg1']['TokenList'];
                arg2TokenList = relation['Arg2']['TokenList'];
                relationDocId = relation['DocID'];
                relationSense = relation['Sense'];
                connectiveTokenList = list(map(lambda tokenList: tokenList[2], relation['Connective']['TokenList']))
                arg1TokenListFinal = map(lambda tokenList: tokenList[2], arg1TokenList) ;
                arg2TokenListFinal = map(lambda tokenList: tokenList[2], arg2TokenList) ;


                with open(outputFilename, 'a+') as f:
                        output =  outputRecord.OutputRecord.loadFromParameters(relationDocId, relationSense, connectiveType, connectiveTokenList, arg1TokenListFinal, arg2TokenListFinal);
                        formattedOutput = output.getFormattedOutput();
                        json.dump(formattedOutput , f);
                        f.write("\n");


    def generateRelations(self, inputPath, connectiveTypeFilter = "Implicit"):
        print("Reading relations.json");
        trainingData = codecs.open(inputPath + '/relations.json', encoding='utf8');
        relations = [json.loads(x) for x in trainingData];
        print("Done");

        outputFilename = inputPath + "/outputRelations.json";

        with open(outputFilename, 'w') as f :#clear the file
            pass;

        for relation in relations:
            connectiveType = relation['Type'];
            if connectiveType == connectiveTypeFilter:
                with open(outputFilename, 'a+') as f:
                        json.dump(relation , f);
                        f.write("\n");


