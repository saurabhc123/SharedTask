from Word import Word


class Sentence:

    def __init__(self, dependencies, words, parseTree):
        self.dependencies = dependencies
        self.words = words
        self.parseTree = parseTree


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