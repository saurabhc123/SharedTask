#coding:utf-8
from util import singleton
import util, config

@singleton
class Implicit_arg1_dict():
    def __init__(self):

        self.dict_curr_production_rule = \
            util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_PRODUCTION_RULE)

        self.dict_prev_curr_production_rule = \
            util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_PREV_CURR_PRODUCTION_RULE)

        self.dict_prev_curr_CP_production_rule = \
            util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_PREV_CURR_CP_PRODUCTION_RULE)

        self.dict_curr_next_CP_production_rule = \
            util.load_dict_from_file(config.IMPLICIT_ARG1_DICT_CURR_NEXT_CP_PRODUCTION_RULE)










