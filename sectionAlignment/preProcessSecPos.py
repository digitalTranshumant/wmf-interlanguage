import json
import os
import gzip
import pandas as pd
import csv


for lang in os.listdir('multiLanguageFromDumps'):
 print(lang.strip('.gz'))
 langCode = lang[-7:-5]
 df = pd.read_csv('wikidataSixLang.csv.gz',sep='\t',header=None).rename(columns={0:'q',1:'wiki',2:'page'})
 wikidatadict = df[df.wiki ==langCode][['q','page']].set_index('page').to_dict()['q']
 del(df) #save memory
 output = open('multiLanguageFromDumpsSecPos/%scsv' % lang[:-4],'w')
 writer =  csv.writer(output,delimiter='\t')
 c = 0
 with open('multiLanguageFromDumps/%s' % lang) as f:		
  for l in f:
   c+=1
   if c%1000000==0: print(c)
   tmp = json.loads(l)
   pageWikidata = wikidatadict.get(tmp[1],False)
   print
   if pageWikidata:
    for sec,data in tmp[2].items():
      writer.writerow([pageWikidata,sec, data['pos']])
 output.close()
