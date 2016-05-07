import json
import codecs
import Sentence


class ParsedInput:

    def __init__(self, parsedDictionary, docId):
        sentences = parsedDictionary[docId]['sentences']
        self.sentences = map(lambda s: Sentence.Sentence.loadFromParser(s), sentences)

    @classmethod
    def parseFromFile(self, fileToParse , docId):
        parserFileContents = codecs.open(fileToParse, encoding='utf8')
        parsedFileDictionary = json.load(parserFileContents)
        assert isinstance(parsedFileDictionary, object)
        return self(parsedFileDictionary, docId)