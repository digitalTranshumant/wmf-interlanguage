#By Diego Saez based on:  https://github.com/mediawiki-utilities/python-mwxml/blob/master/ipython/labs_example.ipynb
#config
dumpDate = '20180801'

#Get list of articles
#f = open('articles_to_wikiproject.txt')
#pagesIds = {}
#for l in f:	
# try:
#  pagesIds[int(l.split()[0])] = ''
# except:
#  pass
#f.close()

#call parser
import mwxml
import glob
import re
import json
import sys
import pandas as pd
import os

directory ='multiLanguageFromDumps'
if not os.path.exists(directory):
    os.makedirs(directory)


sections_RE = re.compile(r'(^|[^=])==([^=\n\r]+)==([^=]|$)')
links_RE = re.compile(r"\[\[(.+?)\]\]")


def extract_sections(text):
 for m in sections_RE.finditer(text):
  yield [m.start(),m.end(),m.group(2).strip()]

def extract_links(text):
 for m in links_RE.finditer(text):
  yield [m.group(1).split('|')[0].strip()]


for lang in ['ja','ar','en','fr', 'es', 'ru']: 
	## This is for getting the Wikidata Id for each page, not used in this case. 
	#df = pd.read_csv('wikidataSixLang.csv.gz',sep='\t',header=None).rename(columns={0:'q',1:'wiki',2:'page'}) 
	#wikidatadict = df[df.wiki ==lang][['q','page']].set_index('page').to_dict()['q']
	#del(df) #save memory
	print(lang)
	paths = glob.glob('/mnt/data/xmldatadumps/public/%swiki/%s/%swiki-%s-pages-meta-current*.xml*.bz2' % (lang,dumpDate,lang,dumpDate))
	if len(paths) > 1: #remove the single file when have, keep it for small wikis that came all togheter in one file
		paths.remove('/mnt/data/xmldatadumps/public/%swiki/%s/%swiki-%s-pages-meta-current.xml.bz2' % (lang,dumpDate,lang,dumpDate))

	print(paths)

	def process_dump(dump, path):
		for page in dump:
			if int(page.namespace) == 0:  #if int(page.id) in pagesIds:
				try:
					for revision in page: pass #pass all , go to the last revision
					text =  revision.text
					sections = list(extract_sections(text) or "")
					output = {}
					for n,sec  in enumerate(sections):
						if n+1 < len(sections):
							secText = text[sections[n][1]:sections[n+1][0]]
						else:
							secText = text[sections[n][1]:] #for the last sextion
						links = list(extract_links(secText))
						links = [wikidatadict.get(link[0],'-1') for link in links]
						output[sections[n][2]] = {'links':links,'size':len(secText),'pos':n+1}
					yield page.id,page.title, output
				except:
					pass

	f = open('multiLanguageFromDumps/sections-articles_%s.json' % lang,'w')
	for result in mwxml.map(process_dump, paths, threads = 168):
	    f.write(json.dumps(result)+'\n')
