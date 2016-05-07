import ParsedInput
import os
import nltk
from nltk.tree import *

execfile("labelsgen.py")

def current_to_root(index, ptree):
	leaf=ptree
	path=ptree.leaf_treeposition(index)
	for ind in path[0:(len(path)-1)]:
		leaf=leaf[ind]
	label=''
	for ind in path[0:(len(path)-1)]:
		label=leaf.parent().label()+'_'+label		
		leaf=leaf.parent()
	
	return label

listfiles=os.listdir('raw/')
labels=0
allTrainData=[]
filesProcessed = 0
maxFilesToProcess = 10

for x in listfiles:
	#Load the data
	if(filesProcessed > maxFilesToProcess):
		break
	filesProcessed = filesProcessed + 1
	print filesProcessed
	print x
	#print 'enter load..'
	try:
		parsedData =  ParsedInput.ParsedInput.parseFromFile('parses.json', x)

	except:
		print x
		continue
	#print 'exit load'
	
	tagdata=[]
	current=''
	prev=''

	allsentences=parsedData.sentences
	counter=0
	for sentence in allsentences:
		current=''
		prev=''
		pt=sentence.parseTree
        #Convert to an actual tree as a list
		ptree=ParentedTree.fromstring(pt)
		if len(ptree[0])<1:
			continue
		for counter,next in enumerate(sentence.words):
			if prev!='':
				label = x+'__'+str(current.characterOffsetBegin)
				if label in connectivelabels:
					labels=1
				else:
					labels=0
				crp=current_to_root((counter-1),ptree)
				#print counter-1,current.actualWord
				tagdata=[current.partOfSpeech, prev.actualWord+'_'+current.actualWord, prev.partOfSpeech, prev.partOfSpeech+'_'+current.partOfSpeech, current.actualWord+'_'+next.actualWord, next.partOfSpeech, current.partOfSpeech+'_'+next.partOfSpeech, crp, labels]
				allTrainData.append(tagdata)
				
			prev=current
			current=next
			#if labels==1:
				#print x
				#print tagdata


import json

filename=open("allTrainData","w")

encoded=json.dumps(allTrainData)

filename.write(encoded)


'''
FOR READING THE SAVED FILE, USE:

import json

filename=open("allTrainData","r")
encoded=filename.read()
allTrainData=json.loads(encoded)

'''

