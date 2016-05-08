#!/usr/bin/python
from sys import argv,exit,stderr
#def is_ascii(s):
 #   return all(ord(c) < 128 for c in s)

def is_ascii(c):
    if ord(c)>=128:
        print >>stderr, c
    return ord(c) < 128

f=open(argv[1],'r')
new=''
for l in f:
   new=''
   for c in l:
        if is_ascii(c):
                new=new+c
        else:
                new=new+'_'
   print new,
