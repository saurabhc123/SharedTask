class Clause:

    def __init__(self, containedClause):
        self.containedClause = containedClause

    def getFeatures(self, previousClause, nextClause):
        """

        :rtype:Dictionary
        """
        f ={};

        currFirstTerm = '';
        currLastTerm = ''
        positionInSentence = 'middle'
        if self.containedClause:
            currentClauseWords = self.containedClause.split(" ")[:];
            f['currFirstTerm'] =  currFirstTerm = currentClauseWords[0];
            f['currLastTerm'] = currLastTerm = currentClauseWords[len(currentClauseWords) - 1];
        else:
            f['currFirstTerm'] =  '';
            f['currLastTerm'] = '';

        prevLastTerm = '';
        if previousClause:
            prevClauseWords =  previousClause.split(" ")[:];
            prevLastTerm = prevClauseWords[len(prevClauseWords) - 1]
            f["prevLastTerm"] = prevLastTerm
        else:
            f["prevLastTerm"] = prevLastTerm;
            positionInSentence = 'start'

        nextFirstTerm = '';
        if nextClause:
            nextClauseWords = nextClause.split(" ")[:];
            nextFirstTerm = nextClauseWords[len(nextClauseWords) - 1]
        else:
            f['nextFirstTerm'] = nextFirstTerm;
            positionInSentence = 'end'

        if not nextClause:
            if not previousClause:
                positionInSentence = 'whole';

        f["prevLastTermcurrFirstTerm"]= prevLastTerm + currFirstTerm;
        f["currLastTermnextFirstTerm"] = currLastTerm + nextFirstTerm;
        f['positionInSentence'] = positionInSentence;

        return f;