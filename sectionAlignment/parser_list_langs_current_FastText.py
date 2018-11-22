#By Diego Saez based on:  https://github.com/mediawiki-utilities/python-mwxml/blob/master/ipython/labs_example.ipynb


#Considering just the articles that are in the 6 languages (articlesInSixLang.p)
#computes a weigthed(tfidf) section embbed 
#config
dumpDate = '20180801'

#call parser
import mwxml
import glob
import re
import json
import sys
import pandas as pd
from fastText_multilingual.fasttext import FastVector
import numpy as np
from collections import Counter
import csv

def fasttextDistanceTfIdf(weightedTfIdf,vectorsLang):
    '''
	weightedTfIdf: tfidf document description
	vectorsLang: fasttext
    '''
    secVector  = sum([weight * vectorsLang[word] for word,weight in weightedTfIdf.items() if word in vectorsLang]) # / len(weightedTfIdf)
    return secVector

def tfIdf(tf,df,dl,N):
    ''' TfIdf Normalized by doc lenght
        tfs: term frec
        df: doc frec
        dl: doc Lenght (number of words in the document)
        N: number of documents'''
    tfIDF = dict([( word,(freq/dl)* np.log(N/df[word]) ) for word,freq in tf.items()])  
    return tfIDF

sections_RE = re.compile(r'(^|[^=])==([^=\n\r]+)==([^=]|$)')
links_RE = re.compile(r"\[\[(.+?)\]\]")

def extract_sections(text):
 for m in sections_RE.finditer(text):
  yield [m.start(),m.end(),m.group(2).strip()]

def extract_links(text):
 for m in links_RE.finditer(text):
  yield [m.group(1).split('|')[0].strip()]

#Working with a sample of documents, to make output memory friendly
for lang in  ['ja','ar','en','fr', 'es', 'ru']: 
	df = pd.read_pickle('articlesInSixLang.p').reset_index()
	wikidatadict = df[df.wiki ==lang][['q','page']].set_index('page').to_dict()['q']
	del(df) #save memory
	print(lang)
	paths = glob.glob('/mnt/data/xmldatadumps/public/%swiki/%s/%swiki-%s-pages-meta-current*.xml*.bz2' % (lang,dumpDate,lang,dumpDate))
	if len(paths) > 1: #remove the single file when have, keep it for small wikis that came all togheter in one file
		paths.remove('/mnt/data/xmldatadumps/public/%swiki/%s/%swiki-%s-pages-meta-current.xml.bz2' % (lang,dumpDate,lang,dumpDate))

	print(paths)
	lang_dictionary = FastVector(vector_file='fastText_multilingual/vectors/wiki.%s.vec' % lang)
	if lang != 'en':
		lang_dictionary.apply_transform('fastText_multilingual/my_alingments/apply_in_%s_to_en.txt' % lang)

	def process_dump(dump, path):
		for page in dump:
			if int(page.namespace) == 0:  #if int(page.id) in pagesIds:
				if page.title in wikidatadict:
				#try:
					for revision in page: 
						pass #pass all , go to the last revision
					text =  revision.text
					sections = list(extract_sections(text) or "")
					N = len(sections)
					sectionContent = {}
					for n,sec  in enumerate(sections):
						if n+1 < len(sections):
							secText = text[sections[n][1]:sections[n+1][0]]
						else:
							secText = text[sections[n][1]:] #for the last sextion
						#print(sec)
						sectionContent[sections[n][2]] = Counter(secText.lower().split())
					idf = []
					[idf.extend(words.keys()) for sec,words in sectionContent.items()]
					idf = Counter(idf)
					weigthed = {}
					for sec,content in sectionContent.items():
						tfIdfSec = tfIdf(content,idf,sum(content.values()),N)
						weigthed[sec] = fasttextDistanceTfIdf(tfIdfSec,lang_dictionary)
			
					yield wikidatadict[page.title], weigthed
				#except:
					#pass

	f = open('multiLanguageFromDumpsFastextarticlesInSixLang/sections-articles_%s.json' % lang,'w')
#	writer =  csv.writer(f,delimiter='\t')
	for result in mwxml.map(process_dump, paths, threads = 168):
		try:
			q = result[0]
			secs = result[1]
			for sec,vector in secs.items():
				if not isinstance(vector,int):
					f.write(json.dumps([q,sec,vector.tolist()])+'\n')
		except Exception as e:
    			print('error: ',e)
