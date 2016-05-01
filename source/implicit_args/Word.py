

class Word:


    def __init__(self, actualWord , partOfSpeech, characterOffsetBegin, characterOffsetEnd, linkers):
        self.actualWord = actualWord
        self.partOfSpeech = partOfSpeech
        self.characterOffsetBegin = characterOffsetBegin
        self.characterOffsetEnd = characterOffsetEnd
        self.linkers = linkers


    def __init__(self, actualWord , partOfSpeech):
        self.actualWord = actualWord
        self.partOfSpeech = partOfSpeech


    @classmethod
    def loadFromParser(self , parsedWord):
        actualWord = parsedWord[0]
        partOfSpeech = parsedWord[1]['PartOfSpeech']
        #characterOffsetEnd = parsedWord[1]['CharacterOffsetEnd']
        #characterOffsetBegin = parsedWord[1]['CharacterOffsetBegin']
        #linkers = parsedWord[1]['Linkers']
        return self(actualWord, partOfSpeech)
