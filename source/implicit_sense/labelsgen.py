import json

with open("relations.json") as f:
	content=f.readlines()

data=[]
for entry in content:
	data.append(json.loads(entry))


connectivelabels=dict()
i=1
for entry in data:
	if entry['Type']=='Explicit':
		tmp1=entry['Connective']['CharacterSpanList'][0][0]
		tmp2=entry['DocID']

		connectivelabels[tmp2+'__'+str(tmp1)] =1
	
		



