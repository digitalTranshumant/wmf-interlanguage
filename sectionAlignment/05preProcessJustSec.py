import json
import os
import gzip



for lang in os.listdir('multiLanguageFromDumps'):
	print(lang.strip('.gz'))
	output = {}
	c = 0
	with gzip.open('multiLanguageFromDumps/%s' % lang) as f:
		for l in f:
			c+=1
			if c%1000000==0: print(c)
			tmp = json.loads(l.decode())
			output[tmp[1]] = list(tmp[2].keys())
		with open('multiLanguageFromDumpsSec/%s' % lang.strip('.gz'),'w') as o:
			json.dump(output,o)
