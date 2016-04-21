import json
import codecs
from pprint import pprint
import os
import ParsedInput

def readParseJson():
 parse_file = codecs.open('/Users/Prashant/Documents/NLP_ST/conll16st/tutorial/conll16st-en-01-12-16-trial/parses.json', encoding='utf8')
 en_parse_dict = json.load(parse_file)

 listOfAllFiles=os.listdir('raw/');
 for x in listfiles:
  try:
   parsedData =  ParsedInput.ParsedInput.parseFromFile('parses.json', x)
  except:
   print x
   break
   
 #print en_parse_dict[en_doc_id]['sentences'][15]['parsetree']
 #pprint(en_parse_dict);

if __name__ == '__main__':
 print ("Hello World");
 readParseJson();
