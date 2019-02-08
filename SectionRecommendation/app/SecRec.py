
# coding: utf-8

# In[1]:


import pandas as pd
import requests


# In[60]:


#Config
suportedLangs = ['fr','en','es','ja','ar','ru']


# In[473]:


import re
sections_RE = re.compile(r'(^|[^=])==([^=\n\r]+)==([^=]|$)')
def extract_sections(text):
    for m in sections_RE.finditer(text):
        yield m.group(2).strip()
        
def getContent(title,lang):
    url = "https://%s.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&formatversion=2&titles=%s" % (lang,title)
    response = requests.get(url)
    content = response.json()['query']['pages'][0]['revisions'][0]['content']
    return content

def getPages(title,lang,target=suportedLangs):
    response= requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&sites=%swiki&titles=%s&props=sitelinks&format=json" % (lang,title))
    output ={}
    assert list(response.json()['entities'].values())[0]['sitelinks'], "Oh no! This assertion failed!"
    links = list(response.json()['entities'].values())[0]['sitelinks']
    for t in target:
        if t+'wiki' in links:
            output[t] = links[t+'wiki' ]['title']
        
    return output

def getAllLangs(title,lang):
    secs = {}
    for l,page in getPages(title,lang).items():
        print(l,page)
        secs[l]  = list(extract_sections(getContent(page,l)))
    return secs


# In[470]:


#Load recsheet
import os 
rec = {}
for f in os.listdir('recSheetsTSV/'):
    lang1 = f[0:2]
    lang2 = f[6:8]
    rec[lang1] = rec.get(lang1,{})
    rec[lang1][lang2] = pd.read_csv('recSheetsTSV/'+f,sep='\t')
    rec[lang1][lang2].set_index('secFrom',inplace=True)

#syn = {}
#for f in os.listdir('synonymPredict/'):
#    lang1 = f[0:2]
#    syn[lang1] =  pd.read_csv('synonymPredict/'+f,sep='\t')


# In[442]:


import networkx as nx
import json
def getMostSimilarClusters(c1,c2):
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

def updateClusterWeights(c1,c2): #c1 is the template to be updated
    for s1,s2 in getMostSimilarClusters(c1,c2):
        for s in c1[s1].keys() & c2[s2].keys():
            c1[s1][s] = c1[s1][s] + c2[s2][s]
    return c1
        


# In[471]:


def getRecs(title,TargetLang):
    #load translations
    global rec
    # get sections in all Languages
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
    for lang in sourceLangs:
        df = rec[lang][TargetLang]
        secsMapped[lang] = []
        for sec in secs[lang]:
            tmp = df[df.index ==sec][['langTo','prob']]
            secsMapped[lang].append(dict(zip(tmp.langTo,tmp.prob)))
    templateRec = secsMapped[templateLang]
    for lang in sourceLangs:
        if lang != templateLang:
            templateRec = updateClusterWeights(templateRec,secsMapped[lang])
    finalRecs = []
    for cluster in templateRec:
        if cluster: #check cluster is not empty
            candidates = [recTuple[0] for recTuple in sorted(cluster.items(),  key=lambda x: x[1],reverse=True)][:3]
            if not (set(candidates) & set(secs[TargetLang])):
                finalRecs.append(candidates[0])
    return json.dumps(list(set(finalRecs)))


# In[481]:



