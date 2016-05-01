from Word import Word
import regex as re;


class Sentence:

    def __init__(self, dependencies, words, parseTree):
        self.dependencies = dependencies
        self.words = words
        self.parseTree = parseTree

    def __init__(self, dependencies, words, parseTree, startTokenIndex, endTokenIndex, docId):
        self.dependencies = dependencies
        self.words = words
        self.parseTree = parseTree
        self.startTokenIndex = startTokenIndex;
        self.endTokenIndex = endTokenIndex;
        self.docId = docId;

    @classmethod
    def loadFromParser(self, parsedSentence):
        #Read the parseTree
        parseTree = parsedSentence['parsetree']
        #Read the Dependencies
        dependencies = parsedSentence['dependencies']
        #Read the Words
        wordsInJson = parsedSentence['words']
        words = map(lambda w : Word.loadFromParser(w), wordsInJson)
        return self(dependencies, words, parseTree)


    @classmethod
    def loadFromParser(self, parsedSentence, tokenCountBeforeThisSentence = 0, docId = 0):
        #Read the parseTree
        parseTree = parsedSentence['parsetree']
        #Read the Dependencies
        dependencies = parsedSentence['dependencies']
        #Read the Words
        wordsInJson = parsedSentence['words']
        words = map(lambda w : Word.loadFromParser(w), wordsInJson)
        startIndex = 0;
        if tokenCountBeforeThisSentence != 0:
            startIndex = tokenCountBeforeThisSentence + 1;
        return self(dependencies, words, parseTree, startIndex, startIndex + len(words) - 1, docId)



    def getSubSequenceTokenIndexes(self, subsequence):
        tokenIndexes = [];
        subsequenceWords = re.findall(r'\w+', subsequence.containedClause);
        subsequenceLength = len(subsequenceWords);

        if subsequenceLength == 0:
            return tokenIndexes;

        wordCount = len(self.words);
        #If the subsequence has only one word, return the first word.
        if subsequenceLength == 1:
            index = 0;
            for word in self.words:
                if subsequenceWords[0] in word.actualWord:
                    tokenIndexes.append(index + self.startTokenIndex);
                index += 1
        elif subsequenceLength == 2:#If the subsequence has more than one word, but less than 3, match on the first and second word
            index = 0;
            for word in self.words:
                if subsequenceWords[0] in word.actualWord:
                    if subsequenceWords[1] in self.words[index + 1].actualWord:
                        tokenIndexes.append(index + self.startTokenIndex);
                        tokenIndexes.append(index + 1 + self.startTokenIndex);
                index += 1
        elif subsequenceLength == 3:#If the subsequence has more than 2 words but less than 4, match on the first three words
            index = 0;
            for word in self.words:
                if subsequenceWords[0] in word.actualWord:
                    if subsequenceWords[1] in self.words[index + 1].actualWord:
                        if subsequenceWords[2] in self.words[index + 2].actualWord:
                            tokenIndexes.append(index + self.startTokenIndex);
                            tokenIndexes.append(index + 1 + self.startTokenIndex);
                            tokenIndexes.append(index + 2 + self.startTokenIndex);
                index += 1
        else:#If the subsequence has more than 3 words, match on first 2 and last 2
            index = 0;
            for word in self.words:
                if subsequenceWords[0] in word.actualWord:
                    if subsequenceWords[1] in self.words[index + 1].actualWord:
                        if subsequenceWords[subsequenceLength - 1] in self.words[index + subsequenceLength - 1].actualWord:
                            if subsequenceWords[subsequenceLength - 2] in self.words[index + subsequenceLength - 2].actualWord:
                                for indexIterator in range(0,subsequenceLength):
                                    tokenIndexes.append(index + indexIterator + self.startTokenIndex);
                index += 1


        return tokenIndexes;

    def getWordsList(self):
        return map(lambda w : (w.actualWord, w.partOfSpeech), self.words);
