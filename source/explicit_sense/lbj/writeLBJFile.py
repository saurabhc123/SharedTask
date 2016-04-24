#!/usr/bin/python
from sys import argv, exit, stderr
if len(argv) < 4:
	print """
	./writeLBJFile.py <lbjF> <columnFile> <startColumn> 
	<lbjF> e.g. prepositionLearner.lbj
	<columnFile> e.g. for each column in column (starting with startColumn, get featureList (featureName before ':')
	<startColumn> feature names will be collected starting with this column
	e.g. if startColumn=4, columns 0, 1 ,2 , 3 will be skipped
	Create .lbj file with a definition for using 'discrete%' expression for each feature in the featureListF; include all the features into 'using' expression
	"""
	exit()

lbjF=open(argv[1],'r').readlines()
columnFile=open(argv[2],'r').readlines()
terms=columnFile[0].split()
startColumn=int(argv[3])
feats=[]
tot=len(terms)
for i in range(startColumn, tot):
	if ':' not in terms[i]:
		print >>stderr, 'Invalid column', terms[i]
		exit()
	feats.append(terms[i].split(':',1)[0])
tot=len(lbjF)
i=0
flag=1
while i < tot:
	l=lbjF[i]
	if 'discrete%' in l:
		i+=4
		if flag:
			flag=0
			for feat in feats:
			   print "discrete%% %s(Preposition p) <-\n{" % feat
			   print '   if ((p.getFeature("%s")).endsWith("NA")==false)' % feat
			   print '      sense p.getFeature("%s");\n}' % feat
	elif l.strip()=='using':
		print l,
		print '\t',
		for j in range(len(feats)):
			feat=feats[j]
			if j!=len(feats)-1:
			   print feat+',',
			else:
				print feat
		i+=1			  

	else:
		print l,
	i+=1
