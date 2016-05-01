import codecs
import json

import Sentence


class ParsedInput:

    def __init__(self, parsedDictionary):
        self.documents = {};
        for key in parsedDictionary:
            docId = key
            sentences = parsedDictionary[key]['sentences']
            #self.sentences = map(lambda s: Sentence.Sentence.loadFromParser(s), sentences)
            sentenceList = [];
            tokenCount = 0;
            for sentence in sentences:
                newSentence = Sentence.Sentence.loadFromParser(sentence, tokenCount, docId);
                tokenCount = newSentence.endTokenIndex;
                sentenceList.append(newSentence);
            self.documents[key] = sentenceList

    @classmethod
    def parseFromFile(self, sourceFile):
        parse_file = codecs.open(sourceFile , encoding='utf8')
        parsedDictionary = json.load(parse_file)
        return self(parsedDictionary)