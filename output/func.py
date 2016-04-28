


import json
import codecs






def getTokenIDsList(relation,key):
	result=[]
        for tokenList in relation[key]['TokenList']: #each token that is part of Arg1 is represented as a list of 5 indices; I just need to take 3rd index (tokenID)
		result.append(tokenList[2])
        return result
