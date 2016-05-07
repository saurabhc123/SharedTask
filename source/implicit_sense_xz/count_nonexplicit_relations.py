'''
Created on Apr 30, 2016

@author: Xuan Zhang
'''
from sys import argv,exit
import json
import codecs

if len(argv)<2:
    print """
    ./count_nonexplicit_relations.py <relationFilePath>    
    """
    exit()

relationFilePath =argv[1]
 
print("In function: readInput");
#Read relations.json
print("Reading relations.json");
pdtb_file = codecs.open(relationFilePath, encoding='utf8');
relations = [json.loads(x) for x in pdtb_file];
print("Done");

countOfNonExplicit = 0;
for relation in relations:
    cType = relation['Type']; 
    if not cType == 'Explicit':
        countOfNonExplicit += 1

print "\nNumber of Non-Explicit Relations: " + str(countOfNonExplicit);