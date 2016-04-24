#!/usr/bin/python
from sys import argv, exit,stderr
if len(argv)<4:
	print """
	./WritePrepositionJava.py <specsFile> <columnFile> <prepJavaFile>
	<specsFile> contains a list of reserved columns (column number, column name) (all other column names will be generated automatically from columnFile, where column name is before the ':'  featureName:featureValue, e.g. 0 source
	   1 label
	   2 exampleID
	   3 startend
	<columnFile> sample file for input
  
	"""
	exit()

specsF=open(argv[1],'r')
columnF=open(argv[2],'r').readlines()
prepJavaF=open(argv[3],'r').readlines()
specialColumns={}
for l in specsF:
	terms=l.split()
	column=int(terms[0])
	name=terms[1]
	specialColumns[column]=name
columnLine=columnF[0]
columns=columnLine.split()
totColumns=len(columns)
#write new Preposition.java file
i=0
tot=len(prepJavaF)
while i<tot:
	l=prepJavaF[i]
	if l.strip()=='public static final String[][] features=':
	   print l.strip()
	   print '{'
	   featNames=''
	   j=0
	   while j<totColumns:
		if j in specialColumns:
			columnName=specialColumns[j]
		else:
			if ':' not in columns[j]:
				print >>stderr, 'Invalid column', terms[j]
				exit()
			columnName=columns[j].split(':')[0]
		featNames+='{"'+columnName+'","'+str(j)+'"}, '
		j+=1
	   print featNames
	   print '};'
	   i+=3
	else:
		print l,
	i+=1
			
		
	   
	
