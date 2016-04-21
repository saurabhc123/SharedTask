import codecs
import json
import os
import pickle as pkl
import sys
import argparse
import nltk
from nltk.tree import *


class ExplicitConnectiveClassifier:
    # ================================  DEFINE ALL FUNCTIONS ====================================================================
    def __init__(self):
        pass


    def readInput(self, inputFilenamePath):

        # Read parses.json
        print ("    Reading parses.json");
        parse_file = codecs.open(inputFilenamePath, encoding='utf8')
        en_parse_dict = json.load(parse_file)
        print ("    Done");
        return en_parse_dict

    def self_category(self, index, ptree):
        leaf = ptree
        path = ptree.leaf_treeposition(index)
        for ind in path[0:(len(path) - 1)]:
            leaf = leaf[ind]
        label = ''
        label = leaf.parent().label()

        return label

    def parent_category(self, index, ptree):
        leaf = ptree
        path = ptree.leaf_treeposition(index)
        for ind in path[0:(len(path) - 1)]:
            leaf = leaf[ind]
        label = ''
        label = leaf.parent().parent().label()

        return label

    def right_sibling(self, index, ptree):
        leaf = ptree
        path = ptree.leaf_treeposition(index)
        for ind in path[0:(len(path) - 1)]:
            leaf = leaf[ind]
        label = ''
        label = leaf.parent().parent()[-1].label()

        return label

    def left_sibling(self, index, ptree):
        leaf = ptree
        path = ptree.leaf_treeposition(index)
        for ind in path[0:(len(path) - 1)]:
            leaf = leaf[ind]
        label = ''
        label = leaf.parent().parent()[0].label()

        return label

    def right_sibling_n(self, index, ptree):
        leaf = ptree
        path = ptree.leaf_treeposition(index)
        for ind in path[0:(len(path) - 1)]:
            leaf = leaf[ind]
        label = ''
        label = leaf.parent()[-1].label()

        return label

    def left_sibling_n(self, index, ptree):
        leaf = ptree
        path = ptree.leaf_treeposition(index)
        for ind in path[0:(len(path) - 1)]:
            leaf = leaf[ind]
        label = ''
        label = leaf.parent()[0].label()

        return label

    def current_to_root(self, index, ptree):
        leaf = ptree
        path = ptree.leaf_treeposition(index)
        for ind in path[0:(len(path) - 1)]:
            leaf = leaf[ind]
        label = ''
        for ind in path[0:(len(path) - 1)]:
            label = leaf.parent().label() + '_' + label
            leaf = leaf.parent()

        return label

    def parent_category_linked(self, index, ptree):
        leaf = ptree
        path = ptree.leaf_treeposition(index)
        for ind in path[0:(len(path) - 1)]:
            leaf = leaf[ind]
        label = ''
        label = leaf.parent().parent().label()
        for i in leaf.parent():
            label = label + '_' + i.label()

        label = label + '_' + leaf.parent().label()

        return label

    def right_category_linked(self, index, ptree):
        leaf = ptree
        path = ptree.leaf_treeposition(index)
        for ind in path[0:(len(path) - 1)]:
            leaf = leaf[ind]
        label = ''
        label = leaf.parent().label()
        for i in leaf.parent()[-1]:
            label = label + '_' + i.label()

        label = label + '_' + leaf.label()

        return label


    def gen_features(self , input_file_path, connectivefile):
        allDevData = []
        identifierdev = []
        parsefiles = self.readInput(input_file_path)
        nc_id = ''
        c_id = ''
        pc_id = ''
        file_count = 0
        filename = open(connectivefile, "r")
        encoded = filename.read()
        connectivelist = json.loads(encoded)
        filename.close()
        connectivelist = list(set(connectivelist))

        for key, value in parsefiles.iteritems():
            # Load the data
            if file_count % 10 == 0:
                print "    " + str(file_count) + " files processed..."
            file_count += 1
            tagdata = []
            current = ''
            prev = ''
            tokenid = -1
            sentid = -1
            allsentences = value['sentences']
            counter = 0
            lpind = 0
            for sentence in allsentences:
                sentid = sentid + 1
                current = ''
                prev = ''
                pt = sentence['parsetree']
                ptree = ParentedTree.fromstring(pt)
                if len(ptree[0]) < 1:
                    lpind = 1
                else:
                    lpind = 0
                for counter, next in enumerate(sentence['words']):
                    p_multi_ind = 0
                    c_multi_ind = 0
                    p_multi_ind_th = 0
                    c_multi_th = 0
                    # print next[0]
                    tokenid = tokenid + 1
                    if prev != '':

                        if counter == 2:
                            pwlabels = 'dummy'
                            if (prev[0] in connectivelist) or (prev[0] + ' ' + current[0] in connectivelist) or (
                                                prev[0] + ' ' + current[0] + ' ' + next[0] in connectivelist):

                                if prev[0] + ' ' + current[0] in connectivelist:
                                    prev[0] = prev[0] + ' ' + current[0]
                                    p_multi_ind = 1
                                    p_multi_ind_th = 0
                                elif prev[0] + ' ' + current[0] + ' ' + next[0] in connectivelist:
                                    prev[0] = prev[0] + ' ' + current[0] + ' ' + next[0]
                                    p_multi_ind_th = 1
                                    p_multi_ind = 0
                                else:
                                    p_multi_ind = 0
                                    p_multi_ind_th = 0

                                if lpind == 0:
                                    crp = self.current_to_root((counter - 2), ptree)
                                    self_cat = self.self_category((counter - 2), ptree)
                                    parent_cat = self.parent_category((counter - 2), ptree)
                                    left_sib = self.left_sibling((counter - 2), ptree)
                                    right_sib = self.right_sibling((counter - 2), ptree)
                                    parent_cat_link = self.parent_category_linked((counter - 2), ptree)
                                    right_cat_link = self.parent_category_linked((counter - 2), ptree)
                                    left_sib_n = self.left_sibling_n((counter - 2), ptree)
                                    right_sib_n = self.right_sibling_n((counter - 2), ptree)
                                else:
                                    crp = '0'
                                    self_cat = '0'
                                    parent_cat = '0'
                                    left_sib = '0'
                                    right_sib = '0'
                                    parent_cat_link = '0'
                                    right_cat_link = '0'

                                    left_sib_n = '0'
                                    right_sib_n = '0'

                                tagdata = {0: prev[1]['PartOfSpeech'], 1: '_' + prev[0], 2: '_',
                                           3: '_' + prev[1]['PartOfSpeech'], 4: prev[0] + '_' + current[0],
                                           5: current[1]['PartOfSpeech'],
                                           6: prev[1]['PartOfSpeech'] + '_' + current[1]['PartOfSpeech'], 7: crp,
                                           8: prev[0], 9: self_cat, 10: left_sib_n, 11: right_sib_n, 12: parent_cat,
                                           13: self_cat + '_' + left_sib_n, 14: self_cat + '_' + right_sib_n,
                                           15: self_cat + '_' + parent_cat, 16: left_sib_n + '_' + right_sib_n,
                                           17: left_sib_n + '_' + parent_cat, 18: right_sib_n + '_' + parent_cat,
                                           19: right_cat_link, 20: parent_cat_link}
                                allDevData.append((tagdata, pwlabels))
                                if p_multi_ind == 1:
                                    identifierdev.append(
                                        {'docID': key, 'tokenId': [tokenid - 2, tokenid - 1], 'sentid': sentid,
                                         'senttokenid': [counter - 2, counter - 1],
                                         'characterOffsetBegin': prev[1]['CharacterOffsetBegin'],
                                         'characterOffsetEnd': prev[1]['CharacterOffsetEnd'], 'word': prev[0]})
                                elif p_multi_ind_th == 1:
                                    identifierdev.append(
                                        {'docID': key, 'tokenId': [tokenid - 2, tokenid - 1, tokenid], 'sentid': sentid,
                                         'senttokenid': [counter - 2, counter - 1, counter],
                                         'characterOffsetBegin': prev[1]['CharacterOffsetBegin'],
                                         'characterOffsetEnd': prev[1]['CharacterOffsetEnd'], 'word': prev[0]})
                                else:
                                    identifierdev.append({'docID': key, 'tokenId': [tokenid - 2], 'sentid': sentid,
                                                          'senttokenid': [counter - 2],
                                                          'characterOffsetBegin': prev[1]['CharacterOffsetBegin'],
                                                          'characterOffsetEnd': prev[1]['CharacterOffsetEnd'],
                                                          'word': prev[0]})

                        labels = 'dummy'

                        if lpind == 0:
                            crp = self.current_to_root((counter - 1), ptree)
                            self_cat = self.self_category((counter - 1), ptree)
                            parent_cat = self.parent_category((counter - 1), ptree)
                            left_sib = self.left_sibling((counter - 1), ptree)
                            right_sib = self.right_sibling((counter - 1), ptree)
                            parent_cat_link = self.parent_category_linked((counter - 1), ptree)
                            right_cat_link = self.parent_category_linked((counter - 1), ptree)

                            left_sib_n = self.left_sibling_n((counter - 1), ptree)
                            right_sib_n = self.right_sibling_n((counter - 1), ptree)

                        else:
                            crp = 0
                            self_cat = 0
                            parent_cat = 0
                            left_sib = 0
                            right_sib = 0
                            parent_cat_link = 0
                            right_cat_link = 0

                            left_sib_n = 0
                            right_sib_n = 0

                        # TOP PAPER with modified sibling feature
                        if (counter + 1) < len(sentence['words']):
                            if current[0] + ' ' + next[0] + ' ' + sentence['words'][counter + 1][0] in connectivelist:
                                current[0] = current[0] + ' ' + next[0] + ' ' + sentence['words'][counter + 1][0]
                                c_multi_th = 1
                                c_multi_ind = 0

                        if (current[0] in connectivelist) or (current[0] + ' ' + next[0] in connectivelist) or (
                            c_multi_th == 1):

                            if current[0] + ' ' + next[0] in connectivelist:
                                current[0] = current[0] + ' ' + next[0]
                                c_multi_ind = 1
                            # c_multi_th=0
                            else:
                                c_multi_ind = 0
                            # c_multi_th=0



                            tagdata = {0: current[1]['PartOfSpeech'], 1: prev[0] + '_' + current[0],
                                       2: prev[1]['PartOfSpeech'],
                                       3: prev[1]['PartOfSpeech'] + '_' + current[1]['PartOfSpeech'],
                                       4: current[0] + '_' + next[0], 5: next[1]['PartOfSpeech'],
                                       6: current[1]['PartOfSpeech'] + '_' + next[1]['PartOfSpeech'], 7: crp,
                                       8: current[0], 9: self_cat, 10: left_sib_n, 11: right_sib_n, 12: parent_cat,
                                       13: self_cat + '_' + left_sib_n, 14: self_cat + '_' + right_sib_n,
                                       15: self_cat + '_' + parent_cat, 16: left_sib_n + '_' + right_sib_n,
                                       17: left_sib_n + '_' + parent_cat, 18: right_sib_n + '_' + parent_cat,
                                       19: right_cat_link, 20: parent_cat_link}

                            allDevData.append((tagdata, labels))
                            if c_multi_ind == 1:
                                identifierdev.append({'docID': key, 'tokenId': [tokenid - 1, tokenid], 'sentid': sentid,
                                                      'senttokenid': [counter - 1, counter],
                                                      'characterOffsetBegin': current[1]['CharacterOffsetBegin'],
                                                      'characterOffsetEnd': current[1]['CharacterOffsetEnd'],
                                                      'word': current[0]})
                            elif c_multi_th == 1:
                                identifierdev.append(
                                    {'docID': key, 'tokenId': [tokenid - 1, tokenid, tokenid + 1], 'sentid': sentid,
                                     'senttokenid': [counter - 1, counter, counter + 1],
                                     'characterOffsetBegin': current[1]['CharacterOffsetBegin'],
                                     'characterOffsetEnd': current[1]['CharacterOffsetEnd'], 'word': current[0]})
                            else:
                                identifierdev.append({'docID': key, 'tokenId': [tokenid - 1], 'sentid': sentid,
                                                      'senttokenid': [counter - 1],
                                                      'characterOffsetBegin': current[1]['CharacterOffsetBegin'],
                                                      'characterOffsetEnd': current[1]['CharacterOffsetEnd'],
                                                      'word': current[0]})

                    prev = current
                    current = next

                if next[0] in connectivelist:

                    if lpind == 0:
                        crp = self.current_to_root((counter), ptree)
                        self_cat = self.self_category((counter), ptree)
                        parent_cat = self.parent_category((counter), ptree)
                        left_sib = self.left_sibling((counter), ptree)
                        right_sib = self.right_sibling((counter), ptree)
                        parent_cat_link = self.parent_category_linked((counter), ptree)
                        right_cat_link = self.parent_category_linked((counter), ptree)

                        left_sib_n = self.left_sibling_n((counter), ptree)
                        right_sib_n = self.right_sibling_n((counter), ptree)
                    else:
                        crp = '0'
                        self_cat = '0'
                        parent_cat = '0'
                        left_sib = '0'
                        right_sib = '0'
                        parent_cat_link = '0'
                        right_cat_link = '0'

                        left_sib_n = '0'
                        right_sib_n = '0'
                    tagdata = {0: next[1]['PartOfSpeech'], 1: current[0] + '_' + next[0], 2: current[1]['PartOfSpeech'],
                               3: current[1]['PartOfSpeech'] + '_' + next[1]['PartOfSpeech'], 4: next[0] + '_', 5: '_',
                               6: next[1]['PartOfSpeech'] + '_', 7: crp, 8: next[0], 9: self_cat, 10: left_sib_n,
                               11: right_sib_n, 12: parent_cat, 13: self_cat + '_' + left_sib_n,
                               14: self_cat + '_' + right_sib_n, 15: self_cat + '_' + parent_cat,
                               16: left_sib_n + '_' + right_sib_n, 17: left_sib_n + '_' + parent_cat,
                               18: right_sib_n + '_' + parent_cat, 19: right_cat_link, 20: parent_cat_link}

                    allDevData.append((tagdata, labels))

                    identifierdev.append(
                        {'docID': key, 'tokenId': [tokenid], 'sentid': sentid, 'senttokenid': [counter],
                         'characterOffsetBegin': current[1]['CharacterOffsetBegin'],
                         'characterOffsetEnd': current[1]['CharacterOffsetEnd'], 'word': current[0]})
        print "    " + str(file_count) + " files processed..."
        return (allDevData, identifierdev)


# ===================================================================================================================================

    def main(self, input_path, model_path, connective_file_name, outputfolder):
        parsefile = input_path + "/parses.json"
        modelfile = model_path + "/explicitconnective/savedClassifier0414maxentGIStraintestconnonly.json"
        connective_file = model_path + "/explicitconnective/" + connective_file_name

        print "Loading Pre-trained Model..."
        print " "
        with open(modelfile, "r") as filename:
            classifiers = pkl.load(filename)

        print "Loading Data and generating features..."
        explicitConnectiveInstance = ExplicitConnectiveClassifier()
        allDevData, identifierdev = explicitConnectiveInstance.gen_features(parsefile, connective_file)

        test = []
        testind = []
        test_conn_cnt = 0
        for index, row in enumerate(allDevData):
            test_conn_cnt = test_conn_cnt + 1
            test.append((row[0], bool(row[1])))
            testind.append(identifierdev[index])
            # print len(test)

        print "Finished Loading Data..."

        # print "Training..."
        # classifiers=test_maxent(nltk.classify.MaxentClassifier.ALGORITHMS)
        print " "
        print "Testing..."
        testclassifier = classifiers['GIS']

        # ------Predict using best parameters ----------------
        finaloutput = []
        bestth = 4  # Emperically determined

        for algorithm, classifier in classifiers.items():
            for index, featureset in enumerate(test):
                if index % 500 == 0:
                    print "    " + str(index) + " cases processed..."
                pdist = classifier.prob_classify(featureset[0])
                if pdist.prob(1) > (float(bestth) / 10):
                    finaloutput.append(testind[index])

        print "    " + str(index) + " cases processed..."
        print " "
        print "Generating File for Scorer and Relations.json for next component..."
        scorerfile = []
        relationsfile = []
        for fincount, output in enumerate(finaloutput):
            docid = output['docID']
            '''
                if docid==previd:
                    tokenlist.append(output['tokenId']-1)
                else:
                '''
            scorerfile.append(
                {'Arg1': {'TokenList': []}, 'Arg2': {'TokenList': []}, 'Connective': {'TokenList': output['tokenId']},
                 'DocID': docid, 'Sense': [' '], 'Type': 'Explicit'})
            tokenlist = []
            for cnt, tid in enumerate(output['tokenId']):
                tokenlist.append([0, 0, tid, output['sentid'], output['senttokenid'][cnt]])

            relationsfile.append(
                {'DocID': docid, 'Arg1': {'CharacterSpanList': [[' ']], 'RawText': ' ', 'TokenList': [[' ']]},
                 'Arg2': {'CharacterSpanList': [[' ']], 'RawText': u' ', 'TokenList': [[' ']]},
                 'Connective': {'CharacterSpanList': [[0, 0]], 'RawText': ' ', 'TokenList': tokenlist}, 'Sense': [' '],
                 'Type': 'Explicit', 'ID': fincount})

        print "    Writing Scorer-Format Output File to scorerfileconnectiveoutput.json..."
        import json
        filename = open(outputfolder + "/scorerfileconnectiveoutput.json", "w")
        for line in scorerfile:
            print>> filename, json.dumps(line)
        filename.close()

        print "    Writing Relations File to relations_from_connective_output.json..."
        filename = open(outputfolder + "/relations_from_connective_output.json", "w")
        for line in relationsfile:
            print>> filename, json.dumps(line)
        filename.close()

        print " "
        print "All Executions Successfull..."


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Run a pre-trained connective classifier detection module")
    parser.add_argument('parsefile', help='Path to parses.json')
    parser.add_argument('modelfile', help='Path to pretrained classifier model file')
    parser.add_argument('connectivelist', help='Path to connectivelist')
    parser.add_argument('outputfolder',
                        help='Folder for saving output files: relations_from_connective_output.json and scorer-format output file')
    args = parser.parse_args()

    if len(sys.argv) < 3:
        print "Please Specify Proper Arguments:"
        print "parsefile : default parses.json"
        print "modelfile : default savedClassifier0414maxentGIStraintestconnonly.json"
        print "connectivelist : default connectivelist"
        print "outputfolder : default . (current folder)"
        print "Thus, the default command to run would be:"
        print "    python evaluate_connective_classifier_maxent.py parses.json savedClassifier0414maxentGIStraintestconnonly.json connectivelist ."
        sys.exit(1)

    main(args.parsefile, args.modelfile, args.connectivelist, args.outputfolder)
