#This is the same than PairOfLangs-JustSections-FinalExperiments.py
#But instead of retreive the top N most similar,  returns all  courrencies count
import pandas as pd
import networkx as nx
import json
from collections import Counter
import gzip
import json
import itertools
import networkx as nx
from functools import reduce

#Parameters 
##define languages
langs=['es','en','ar','ja','fr','ru']


il = pd.read_csv('wikidataSixLang.csv.gz',sep='\t',header=None)
il = il.rename(columns={0:'wikidata',1:'lang',2:'page_title'})
selectedLanguages = il[il['lang'].isin(langs)]
del il #free memory

while langs:
	targetLang = langs.pop()
	targetData = selectedLanguages[selectedLanguages['lang'] == targetLang]
	targetData.set_index('wikidata',inplace=True)
	sectionsTargetAll = []
	c =0
	sectionsTarget = {}
	with open('../gap/multiLanguageFromDumpsSec/sections-articles_%s.json' % targetLang) as f: 
	    sectionsTarget = json.load(f)
	    

	# Selecting articles in one language
	for lang in langs:
	    print(lang)
	    secondLang =  selectedLanguages[selectedLanguages['lang'] ==lang]
	    secondLang.set_index('wikidata',inplace=True)
	    allSelected = pd.concat([targetData, secondLang.add_suffix('_second')], axis=1, join='inner')

	    titles_second = dict.fromkeys(allSelected.page_title_second.unique())
	    with open('../gap/multiLanguageFromDumpsSec/sections-articles_%s.json' % lang) as f: 
                sectionsSecond = json.load(f)

	    
	    print('Proccesing')
	    allCombinations= allSelected.apply(lambda data: itertools.product(sectionsTarget.get(data['page_title'],[]),sectionsSecond.get(data['page_title_second'],[])),axis=1)
	    pairs = [item for sublist in allCombinations for item in sublist] 

	    coOcurrences = pd.DataFrame.from_dict(Counter(pairs), orient='index').reset_index()
	    coOcurrences = coOcurrences.rename(columns={'index':'pair', 0:'count'})
	    coOcurrences[[targetLang,lang]] = pd.DataFrame(coOcurrences.pair.tolist(), index= coOcurrences.index)

	    del(coOcurrences['pair'])
	    coOcurrences.to_pickle('resultsMapping-CoOcurrenceCountPandas/mapping_%s_%s.p' % (targetLang,lang))
	    del(coOcurrences)






