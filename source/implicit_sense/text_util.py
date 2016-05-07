'''
Created on Apr 19, 2016

@author: Xuan Zhang
'''

from tools.PorterStemmer import PorterStemmer
import os
from nltk.corpus import wordnet

def stem_string(line):
    if line == "":
        return ""
    p = PorterStemmer()
    word = ""
    output = ""
    for c in line:
        if c.isalpha():
            word += c.lower()
        else:
            if word:
                output += p.stem(word, 0,len(word)-1)
                word = ''
            output += c.lower()
    if word:
        output += p.stem(word, 0,len(word)-1)
    return output

def get_negate_word():
    fin = open(os.getcwd() + os.sep + "dict" + os.sep + "negate_word")
    negate = []
    negate_stem = []
    for line in fin:
        word = line.strip()
        negate.append(word)
        negate_stem.append(stem_string(word))
    return negate, negate_stem

def get_MAPA_polarity_dict():
        n_stemmed_word_pos_dict = {}
        y_stemmed_word_pos_dict = {}

        fin = open(os.getcwd() + os.sep + "dict" + os.sep + "MPQA_Subjectivity_Lexicon.txt")
        for line in fin:
            line = line.strip()
            if line == "":
                continue

            # if it has two polarities, choose the previous one
            _type, _, _word, _pos, _stemmed, _polarity = line.split(" ")[:6]

            type = _type.split("=")[-1]
            word = _word.split("=")[-1]
            pos = _pos.split("=")[-1]
            stemmed = _stemmed.split("=")[-1]
            polarity = _polarity.split("=")[-1]

            if stemmed == "n":
                n_stemmed_word_pos_dict[(word, pos)] = (type, polarity)
            if stemmed == "y":
                y_stemmed_word_pos_dict[(word, pos)] = (type, polarity)

        return n_stemmed_word_pos_dict, y_stemmed_word_pos_dict
    
def cross_product_list(list1, list2):
    t = []
    for i in list1:
        for j in list2:
            t.append(i * j)
    return t

def cross_product_dict(dict1, dict2):
    result = {}
    for i in dict1.keys():
        for j in dict2.keys():
            result[i + '_' + j] = dict1[i] * dict2[j]
    return result

def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return ''

def get_MPQA_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return 'adj'
    elif treebank_tag.startswith('V'):
        return 'verb'
    elif treebank_tag.startswith('N'):
        return 'noun'
    elif treebank_tag.startswith('R'):
        return 'adverb'
    else:
        return ''
