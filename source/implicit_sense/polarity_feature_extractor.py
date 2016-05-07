'''
Created on Apr 19, 2016

@author: Xuan Zhang
'''

import util
from parse_util import *
from nltk.stem import WordNetLemmatizer

n_stemmed_word_pos_dict, y_stemmed_word_pos_dict = util.get_MAPA_polarity_dict()
posSet = set()
for wpTuple in n_stemmed_word_pos_dict.keys():
    posSet.add(wpTuple[1])
print "\nPOS-Set:", posSet
negate_words = util.get_negate_word()[0]
wordnet_lemmatizer = WordNetLemmatizer()

def get_polarity_features(relation, parse_dict):
    features = {}
    features_arg1 = get_MPQA_polarity_vec(relation, "Arg1", parse_dict)[0]
    features_arg2 = get_MPQA_polarity_vec(relation, "Arg2", parse_dict)[0]
    
    cross_product_features = util.cross_product_dict(features_arg1, features_arg2)
    
#     for fk in features_arg1.keys():
#         if features_arg1[fk] > 0:
#             features[fk] = features_arg1[fk]
#     
#     for fk in features_arg2.keys():
#         if features_arg2[fk] > 0:
#             features[fk] = features_arg2[fk]

    keyset = set()
    for fk in cross_product_features.keys():
        keyset.add(fk)
        if cross_product_features[fk] > 0:
            features[fk] = cross_product_features[fk]
    
    #print features
    return features, keyset


def get_MPQA_polarity_vec(relation, Arg, parse_dict):
    polarity_cate = ["negatepositive", "positive", "negative", "neutral"]
    subj_cate = ["strongsubj", "weaksubj"]

    polarityDict = {}
    t = 0
    for p in polarity_cate:
        for s in subj_cate:
            polarityDict["%s_%s" % (s, p)] = t
            t += 1

    polarityVec = [0] * len(polarityDict)

    word_list = [word.lower() for word in get_Arg_Words_List(relation, Arg, parse_dict)]
    pos_list = [pos for pos in get_Arg_POS_List(relation, Arg, parse_dict)]
#     print "Words in", Arg, word_list

    features = {}
    for index, (word, pos) in enumerate(zip(word_list, pos_list)):
        subj, polarity = get_word_MPQA_polarity((word, pos))# ('strongsubj', 'positive')
        if polarity in ["NULL", "both"]:
            continue
        # negate positive
        if polarity == "positive" and is_negate_MPQA(index, word_list):
            polarity = "negatepositive"

        subj_polarity = "%s_%s" % (subj, polarity)
        # count or not
        if subj_polarity in polarityDict.keys():
            polarityVec[polarityDict[subj_polarity]] = 1

    for pt in polarityDict.keys():
        features[Arg + '_' + pt] = polarityVec[polarityDict[pt]]
        
    return features, polarityVec


# in:('humor', 'verb') ; out: ('strongsubj', 'positive')
def get_word_MPQA_polarity(word_pos_tuple):
#     n_stemmed_word_pos_dict, y_stemmed_word_pos_dict = util.get_MAPA_polarity_dict()

    word, pennTreePOS = word_pos_tuple
    pos = util.get_MPQA_pos(pennTreePOS)
    word_pos_tuple = (word,pos)

    #Strict matching (match by both word and pos)
    if word_pos_tuple in n_stemmed_word_pos_dict:
        return n_stemmed_word_pos_dict[word_pos_tuple]
    elif (word, "anypos") in n_stemmed_word_pos_dict:
        return n_stemmed_word_pos_dict[(word, "anypos")]

    #Loose matching (match by only word)
#     for wpTuple in n_stemmed_word_pos_dict.keys():
#         if word == wpTuple[0]:
#             return n_stemmed_word_pos_dict[wpTuple]
    
    #Lemmatize word and match again
    wordnet_pos = util.get_wordnet_pos(pennTreePOS)
    if len(wordnet_pos) > 0:
        word = wordnet_lemmatizer.lemmatize(word, wordnet_pos)
        #Loose matching (match by only word)
#         for wpTuple in n_stemmed_word_pos_dict.keys():
#             if word == wpTuple[0]:
#                 return n_stemmed_word_pos_dict[wpTuple]
        
        #Strict matching (match by both word and pos)
        if (word, pos) in n_stemmed_word_pos_dict:
            return n_stemmed_word_pos_dict[(word, pos)]
        elif (word, "anypos") in y_stemmed_word_pos_dict:
            return y_stemmed_word_pos_dict[(word, "anypos")]

    # stems by PorterStemmer 
#     word = util.stem_string(word)
#     if (word, pos) in y_stemmed_word_pos_dict:
#         return y_stemmed_word_pos_dict[(word, pos)]
#     elif (word, "anypos") in y_stemmed_word_pos_dict:
#         return y_stemmed_word_pos_dict[(word, "anypos")]

    # no match
    return ("NULL", "NULL")


def is_negate_MPQA(index, word_list):
#     negate_words = util.get_negate_word()
    prev1 = "NULL"; prev2 = "NULL"; prev3 = "NULL"
    if index - 1 >= 0:
        prev1 = word_list[index - 1]
    if index - 2 >= 0:
        prev2 = word_list[index - 2]
    if index - 3 >= 0:
        prev3 = word_list[index - 3]

    prev_words = [prev1, prev2, prev3]
    
#     prevSet = set(word for word in prev_words)
#     negateSet = set(word for word in negate_words)

    if set(prev_words) & set(negate_words) != set([]):
#     if prevSet & negateSet != set([]):
        return True
    else:
        return False
