'''
Created on Apr 19, 2016

@author: Xuan Zhang
'''

def get_feature_by_list(list):
    feat_dict = {}
    for index, item in enumerate(list):
        if item != 0:
            feat_dict[index+1] = item
    return feat_dict