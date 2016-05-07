'''
Created on Apr 19, 2016

@author: Xuan Zhang
'''

def get_Arg_Words_List(relation, Arg, parse_dict):
    words = []
    DocID = relation["DocID"]
    Arg_TokenList = get_Arg_TokenList(relation, Arg)
    for sent_index, word_index in Arg_TokenList:
        word = parse_dict[DocID]["sentences"][sent_index]["words"][word_index][0]
        words.append(word)
    return words

#['NN', 'VERB', '''']
def get_Arg_POS_List(relation, Arg, parse_dict):
    pos = []
    DocID = relation["DocID"]
    Arg_TokenList = get_Arg_TokenList(relation, Arg)
    for sent_index, word_index in Arg_TokenList:
        pos_tag = parse_dict[DocID]["sentences"][sent_index]["words"][word_index][1]["PartOfSpeech"]
        pos.append(pos_tag)
    return pos

def get_Arg_TokenList(relation, Arg):
    return [(item[3], item[4]) for item in relation[Arg]["TokenList"]]