#!/usr/bin/python
from sys import argv,exit,stderr
import codecs
import json
import func

if len(argv)<3:
        print """
        ./convertOutputToRelation.py <relationsF>  <writeF>
        """
        exit()


relations=argv[1]
writeF=open(argv[2],'w')
relationsF=codecs.open(relations, encoding='utf8')
relations = [json.loads(x) for x in relationsF]

def writeOutputFormat(relations,outF):
        for relation in relations:
                outF.write('%s\n' % json.dumps(relation))

def relationToOutputFormat(relation,outF):
	connectiveTokenIDs=func.getTokenIDsList(relation,'Connective')
        if 'Arg1' in relation:
		arg1TokenIDs=func.getTokenIDsList(relation,'Arg1')
        if 'Arg2' in relation:
		arg2TokenIDs=func.getTokenIDsList(relation,'Arg2')
	if 'Connective' not in relation:
		relation['Connective']={}
	relation['Connective']['TokenList']=connectiveTokenIDs
	if 'Arg1' not in relation:
		relation['Arg1']={}
	relation['Arg1']['TokenList']=arg1TokenIDs
	if 'Arg2' not in relation:
		relation['Arg2']={}
	relation['Arg2']['TokenList']=arg2TokenIDs
	writeOutputFormat([relation], outF)

for relation in relations:
	relationToOutputFormat(relation,writeF)	

	
