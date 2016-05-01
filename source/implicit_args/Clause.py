from nltk.stem.wordnet import WordNetLemmatizer
from syntax_tree import Syntax_tree
import implicit_arg1_dict;
import util
from implicit_arg1_dict import Implicit_arg1_dict

class Clause:

    def __init__(self, containedClause, sentence):
        self.containedClause = containedClause
        self.words = sentence.getWordsList();
        self.parseTree = sentence.parseTree

    # def __init__(self, containedClause, parseTree):
    #     self.containedClause = containedClause
    #     self.parseTree = parseTree

    def getFeatures(self, previousClause, nextClause, argumentType):
        """

        :rtype:Dictionary
        """
        if(argumentType in "Arg1"):
            f = self.getArgument1Features(previousClause, nextClause);
        else:
            f = self.getArgument2Features(previousClause, nextClause);
        return f;

    def getArgument1Features(self, previousClause, nextClause):
        """

        :rtype:Dictionary
        """
        f ={};


        currentClauseTokenCount = len(self.containedClause);
        if self.containedClause:

            f['currFirstTerm'] =   self.words[self.containedClause[0]][0];
            f['currLastTerm'] =  self.words[self.containedClause[currentClauseTokenCount - 1]][0];
        else:
            f['currFirstTerm'] =  '';
            f['currLastTerm'] = '';

        prevLastTerm = '';
        previousProductionRules = ''
        if previousClause:
            previousClauseTokenCount = len(previousClause);
            prevLastTerm = self.words[previousClause[previousClauseTokenCount - 1]][0];
            f["prevLastTerm"] = prevLastTerm
            previousProductionRules = self.getProductionRules(previousClause);
        else:
            f["prevLastTerm"] = prevLastTerm;


        currentProductionRules = self.getProductionRules(self.containedClause);
        crossProductOfPrevCurrProductionRules = self.getPrevCurrCPProductionRule(currentProductionRules, previousProductionRules);
        cpF = self.get_prev_curr_CP_production_rule_feature(crossProductOfPrevCurrProductionRules);
        f['crossProductOfPrevCurrProductionRules'] = cpF
        f['clauseWordCount'] = currentClauseTokenCount;

        return f;

    def getArgument2Features(self, previousClause, nextClause):
        """

        :rtype:Dictionary
        """
        f ={};

        currFirstTerm = '';
        currLastTerm = ''
        positionInSentence = 'middle'
        currentClauseTokenCount = len(self.containedClause);
        if self.containedClause:

            f['currFirstTerm'] =  currFirstTerm = self.words[self.containedClause[0]][0];
            f['currLastTerm'] = currLastTerm = self.words[self.containedClause[currentClauseTokenCount - 1]][0];
        else:
            f['currFirstTerm'] =  '';
            f['currLastTerm'] = '';

        prevLastTerm = '';
        previousProductionRules = ''
        if previousClause:
            previousClauseTokenCount = len(previousClause);
            prevLastTerm = self.words[previousClause[previousClauseTokenCount - 1]][0];
            f["prevLastTerm"] = prevLastTerm
            previousProductionRules = self.getProductionRules(previousClause);
        else:
            f["prevLastTerm"] = prevLastTerm;
            positionInSentence = 'start'

        nextFirstTerm = '';
        if nextClause:
            nextFirstTerm = self.words[nextClause[0]][0];
        else:
            f['nextFirstTerm'] = nextFirstTerm;
            positionInSentence = 'end'

        if not nextClause:
            if not previousClause:
                positionInSentence = 'whole';

        f["prevLastTermcurrFirstTerm"]= prevLastTerm + currFirstTerm;
        f["currLastTermnextFirstTerm"] = currLastTerm + nextFirstTerm;
        f['positionInSentence'] = positionInSentence;
        lowercasedVerbsStruct = self.getLowerCasedVerbsStruct(self.containedClause, self.words);
        clauseVerbs = '_'.join( map(lambda verbsStruct : verbsStruct[0], lowercasedVerbsStruct));
        lemmatizedVerbs = '_'.join( map(lambda verbsStruct : verbsStruct[1], lowercasedVerbsStruct))
        f['lowercasedVerbs'] = clauseVerbs;
        f['lemmatizedVerbs'] = lemmatizedVerbs;
        currentProductionRules = self.getProductionRules(self.containedClause);
        crossProductOfPrevCurrProductionRules = self.getPrevCurrCPProductionRule(currentProductionRules, previousProductionRules);
        cpF = self.get_prev_curr_CP_production_rule_feature(crossProductOfPrevCurrProductionRules);
        f['crossProductOfPrevCurrProductionRules'] = cpF
        f['clauseWordCount'] = currentClauseTokenCount;

        return f;

    def get_prev_curr_CP_production_rule_feature(self, prev_curr_CP_production_rule):
        # load dict
        dict_prev_curr_CP_production_rule = Implicit_arg1_dict().dict_prev_curr_CP_production_rule


        return  util.get_feature_by_feat_list(dict_prev_curr_CP_production_rule, prev_curr_CP_production_rule)

    def getProductionRules(self, clause):
        curr_clause_indices = clause# ([1,2,3],yes)

        subtrees = []
        parse_tree = self.parseTree
        syntax_tree = Syntax_tree(parse_tree)
        if syntax_tree.tree != None:
            clause_leaves = set([syntax_tree.get_leaf_node_by_token_index(index) for index in curr_clause_indices])
            no_need = []
            for node in syntax_tree.tree.traverse(strategy="levelorder"):
                if node not in no_need:
                    if set(node.get_leaves()) <= clause_leaves:
                        subtrees.append(node)
                        no_need.extend(node.get_descendants())

        production_rule = []
        for tree in subtrees:
            for node in tree.traverse(strategy="levelorder"):
                if not node.is_leaf():
                    rule = node.name + "-->" + " ".join([child.name for child in node.get_children()])
                    production_rule.append(rule)

        return production_rule

    def getPrevCurrCPProductionRule(self, curr_production_rule, prev_production_rule):
        if not prev_production_rule:
            return curr_production_rule

        CP_production_rule = []
        for curr_rule in curr_production_rule:
            for prev_rule in prev_production_rule:
                CP_production_rule.append("%s|%s" % (prev_rule, curr_rule))

        return CP_production_rule

    def getLowerCasedVerbsStruct(self, wordIndices, words):
        verb_pos = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]

        verbs = []
        lmtzr = WordNetLemmatizer();
        for index in wordIndices:
            word = words[index][0];
            pos = words[index][1];
            if pos in verb_pos:
                lowercasedWord = word.lower();
                verbs.append((lowercasedWord, lmtzr.lemmatize(lowercasedWord, "v")))
        return verbs



