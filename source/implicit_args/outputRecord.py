class OutputRecord:


    def __init__(self, docId , sense, type, connective, arg1TokenList, arg2TokenList, id):
        self.docId = docId
        self.sense = sense
        self.type = type
        self.connective = connective
        self.arg1TokenList = arg1TokenList
        self.arg2TokenList = arg2TokenList
        self.id = id


    @classmethod
    def loadFromParameters(self, docId, sense, type, connective, arg1TokenList, arg2TokenList, id):
        return self(docId , sense, type, connective, arg1TokenList, arg2TokenList, id)


    def getFormattedOutput(self):
            entryDict = {};
            entryDict['DocID'] = str(self.docId);
            entryDict['Arg1'] = dict({"TokenList":self.arg1TokenList});
            entryDict['Arg2'] = dict({"TokenList":self.arg2TokenList});
            entryDict['Connective'] = self.connective;
            entryDict['Sense'] = self.sense;
            entryDict['Type'] = self.type;
            entryDict['ID'] = self.id
            return entryDict;

    def getFormattedOutputForRelations(self, arg1RawText, arg2RawText):
            entryDict = {};
            entryDict['Arg1'] = dict({"CharacterSpanList": [], "RawText": arg1RawText, "TokenList":self.arg1TokenList});
            entryDict['Arg2'] = dict({"CharacterSpanList": [], "RawText": arg2RawText, "TokenList":self.arg2TokenList});
            entryDict['DocID'] = self.docId;
            entryDict['Connective'] = self.connective;
            entryDict['ID'] = self.id;
            entryDict['Sense'] = self.sense;
            entryDict['Type'] = self.type;
            return entryDict;

    def getFormattedDebugOutput(self):
            entryDict = {};
            entryDict['Arg1'] = self.arg1TokenList;
            entryDict['Arg2'] = self.arg2TokenList;
            entryDict['Type'] = self.type;
            return entryDict;