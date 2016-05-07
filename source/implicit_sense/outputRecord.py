class OutputRecord:

    def __init__(self, docId , sense, type, connective, arg1TokenList, arg2TokenList):
        self.docId = docId
        self.sense = sense
        self.type = type
        self.connective = connective
        self.arg1TokenList = arg1TokenList
        self.arg2TokenList = arg2TokenList

    @classmethod
    def loadFromParameters(self, docId, sense, type, connective, arg1TokenList, arg2TokenList):
        return self(docId , sense, type, connective, arg1TokenList, arg2TokenList)


    def getFormattedOutput(self):
            entryDict = {};
            entryDict['DocID'] = str(self.docId);
            entryDict['Arg1'] = dict({"TokenList":self.arg1TokenList});
            entryDict['Arg2'] = dict({"TokenList":self.arg2TokenList});
            entryDict['Connective'] = dict({"TokenList":self.connective});
            entryDict['Sense'] = self.sense;
            entryDict['Type'] = self.type;
            return entryDict;

