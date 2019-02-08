
# coding: utf-8

# # Section Recommendation / Inter-lingual approach
# 
# This notebook implements section recommendation based on the Section Aligments. 
# Given an article in language a target language T, though Wikidata retrieves the section of the same in article in other languages, and provides a recommendations.

# In[1]:


import pandas as pd
import requests
import re

#Config
suportedLangs = ['fr','en','es','ja','ar','ru']


# In[2]:


#Loads alignments 

import os 
rec = {}
for f in os.listdir('recSheetsTSV/'):
    lang1 = f[0:2]
    lang2 = f[6:8]
    rec[lang1] = rec.get(lang1,{})
    rec[lang1][lang2] = pd.read_csv('recSheetsTSV/'+f,sep='\t')
    rec[lang1][lang2].set_index('secFrom',inplace=True)
    


# In[43]:


#This function is for the aligment API, I don't use in the recommendations
def getAlignment(lang1,lang2,sec):  
    df = rec[lang1][lang2]
    tmp = df[df.index ==sec][['langTo','prob']]
    return list(zip(tmp['langTo'],tmp['prob']))


# In[81]:


## Section parser
#sections_RE = re.compile(r'(^|[^=])==([^=\n\r]+)==([^=]|$)') #I've used this expression in the paper
#but it doesn't get subsections, now, changing for a more general one
sections_RE = re.compile(r'==([^=\n\r]+)==')
def extract_sections(text):
    for m in sections_RE.finditer(text):
        #yield m.group(2).strip() #this is for the old regular expression
        yield m.group(1).strip()
        
#Get articles
def getContent(title,lang):
    url = "https://%s.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&formatversion=2&titles=%s" % (lang,title)
    response = requests.get(url)
    content = response.json()['query']['pages'][0]['revisions'][0]['content']
    return content

def getPages(title,lang,target=suportedLangs):
    """
    title: page title in target language
    lang: target language
    target: List of Pages 
    returns a dictionary 'x_wiki':x_title
    """
    response= requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&sites=%swiki&titles=%s&props=sitelinks&format=json" % (lang,title))
    output ={}
    assert list(response.json()['entities'].values())[0]['sitelinks'], "Oh no! This assertion failed!"
    links = list(response.json()['entities'].values())[0]['sitelinks']
    for t in target:
        if t+'wiki' in links:
            output[t] = links[t+'wiki' ]['title']
        
    return output

def getSectionsOnline(title,lang):
    #This function gets the sections directly from the 
    #mediawikiparser
    #For offline use list(extract_sections(getContent(page,l)))
    response = requests.get("https://%s.wikipedia.org/w/api.php?action=parse&page=%s&format=json" % (lang,title))
    r = response.json()
    return [s['line'] for s in r['parse']['sections']]

def getAllLangs(title,lang,online=False,giveTitles=False): #offline, meaning not using the mediawiki parser, is 3 times faster
    """
    title: page title in target language
    lang: target language
    returns a dictionary 'x_wiki':list_of_sections_in_x 
    """
    titles ={}
    secs = {}
    for l,page in getPages(title,lang).items():
        titles[l] = page
        #print(l,page)
        if online:
            secs[l] = getSectionsOnline(page,l)
        else:
            secs[l]  = list(extract_sections(getContent(page,l)))
    if giveTitles:
        return secs,titles
    else:
        return secs

# In[82]:


import networkx as nx
import json

#For each section in language X, we have N possible mappings with certain probability. 
#Ex: 'Vida temprana' in Spanish maps to 'Early Life,p=0.9','Early Years,p=.8','References,p=0.3' in English
#Given two languages X and Y, we want to find the most similar clusters considering the mapped sections
def getMostSimilarClusters(c1,c2): 
    """
    c1: dictionary of sections in language 1 (allready mapped to target language) with a giving probability
    c2: dictionary of sections in language 2 (allready mapped to target languages) with a giving probability
    """
    G = nx.Graph()
    mostSimilar = []
    for pos1,dict_1 in enumerate(c1):
        for pos2,dict_2 in enumerate(c2):
            dot_product = sum(dict_1[key]*dict_2.get(key, 0) for key in dict_1)
            G.add_edge((1,pos1),(2,pos2))
            G[(1,pos1)][(2,pos2)]['w'] = dot_product
    for a, b, data in sorted(G.edges(data=True), key=lambda x: x[2]['w'],reverse=True):
        try:
            G.remove_node(a)
            G.remove_node(b)   
            sortedNodes  = sorted([a,b])
            mostSimilar.append((sortedNodes[0][1],sortedNodes[1][1]))
        except:
            pass #one of the nodes was already paried
    return mostSimilar

#Given a template dictionary of sections c1
#and another dictionary of sections c2
#update  probabilities on c1 based on information c2
def updateClusterWeights(c1,c2): #c1 is the template to be updated
    """
    c1: dictionary of sections in language 1 (allready mapped to target language) with a giving probability
    c2: dictionary of sections in language 2 (allready mapped to target languages) with a giving probability
    """
    for s1,s2 in getMostSimilarClusters(c1,c2):
        for s in c1[s1].keys() & c2[s2].keys():
            c1[s1][s] = c1[s1][s] + c2[s2][s]
    return c1
        


# In[5]:


def getRecs(title,TargetLang,blind=False,verbose=False,giveTitles=False):
    '''
    title: Article to get recommendations (ex:'Quilombo')
    TargetLang: Language of the article (ex:'en')
    verbose: return explanations
    '''
    #load translations
    global rec
    # get sections in all Languages
    if giveTitles:
        secs,titles = getAllLangs(title,TargetLang,giveTitles=giveTitles)
    else:
        secs = getAllLangs(title,TargetLang)
    # get a list of the sources languages
    sourceLangs = set(secs.keys()) - {TargetLang}
    #count amount of sections in the target language
    lenTarget = len(secs[TargetLang])
    #count the number of sections in each source lang, produce a tuple (SecCount,Lang)
    lenSources = [(len(s),l) for l,s in secs.items() if l != TargetLang]
    #use the language with more sections as template
    templateLang = max(lenSources)[1]
    secsMapped = {}
    #For all source languages S, take all sections in S and map to the target languge T, with it's probability
    for lang in sourceLangs:
        df = rec[lang][TargetLang]
        secsMapped[lang] = []
        for sec in secs[lang]:
            tmp = df[df.index ==sec][['langTo','prob']]
            secsMapped[lang].append(dict(zip(tmp.langTo,tmp.prob)))
    #Use the language with more sections as template
    templateRec = secsMapped[templateLang]
    #Update the template using the remaining languages
    for lang in sourceLangs:
        if lang != templateLang:
            templateRec = updateClusterWeights(templateRec,secsMapped[lang])
    finalRecs = []
    for cluster in templateRec:
        if cluster: #check cluster is not empty
            candidates = [recTuple[0] for recTuple in sorted(cluster.items(),  key=lambda x: x[1],reverse=True)][:3]
            if not blind:
                if not (set(candidates) & set(secs[TargetLang])):
                    finalRecs.append(candidates[0])
            else:
                    finalRecs.append(candidates[0])

    if verbose:
        output = {}
        output['context'] = {}
        output['Recommendations'] = json.dumps(list(set(finalRecs)))
        output['context']['CurrentSections'] = secs[TargetLang]
        #create a copy of sections
        otherLangs = secs.copy()
        del(otherLangs[TargetLang])
        output['context']['SectionsInOtherLanguages'] = otherLangs
        if giveTitles:
            del(titles[TargetLang])
            output['context']['titles'] = titles
            
    else:
        output = json.dumps(list(set(finalRecs)))
    return output



