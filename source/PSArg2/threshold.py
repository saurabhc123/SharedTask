#!/usr/bin/python
from sys import argv,exit,stderr
f=open(argv[1],'r')
th=float(argv[2])
for l in f:
	terms=l.split()
	pred=terms[2]
	score=float(terms[-2])
	if '=1' in pred and score<th:
		pred='prediction=0'
	print terms[0],terms[1],pred, ' '.join(terms[3:])
