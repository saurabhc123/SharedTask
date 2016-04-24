
import json
import sys
import explicitconnective.evaluate_connective_classifier_maxent

class DiscourseParser(object):

    def __init__(self):
        pass

    output_relations_file_name = "explicit_connective_relations.json"

    def run_connective_classifier(self, input_parses_file, output_path):
        output_relations_file = output_path + self.output_relations_file_name
        explicitconnective.evaluate_connective_classifier_maxent.main(input_parses_file, output_relations_file)

    def parse_doc(self, doc, doc_id):
        output = []
        num_sentences = len(doc['sentences'])
        token_id = 0
        for i in range(num_sentences-1):
            sentence1 = doc['sentences'][i]
            len_sentence1 = len(sentence1['words'])
            token_id += len_sentence1
            sentence2 = doc['sentences'][i+1]
            len_sentence2 = len(sentence2['words'])

            relation = {}
            relation['DocID'] = doc_id
            relation['Arg1'] = {}
            relation['Arg1']['TokenList'] = range((token_id - len_sentence1), token_id - 1)
            relation['Arg2'] = {}
            relation['Arg2']['TokenList'] = range(token_id, (token_id + len_sentence2) - 1)
            relation['Type'] = 'Implicit'
            relation['Sense'] = ['Expansion.Conjunction']
            relation['Connective'] = {}
            relation['Connective']['TokenList'] = []
            output.append(relation)
        return output



if __name__ == '__main__':
    input_parses_file = sys.argv[1]
    output_dir = sys.argv[2]
    parser = DiscourseParser()
    parser.run_connective_classifier(input_parses_file, output_dir)

