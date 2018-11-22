# Pipeline

## Preparation 

00 DownloadDependencies.ipynb <br>
01 WikidataSqlToHive.ipybn: Get Wikidata Information from SQL replicas <br>
02 my_alingments: Create Fasttext_multilingual alingments based on Wikidata <br>

## Data Extraction 
03 parser_list_langs_current.py: Extract Section information from the dumps. <br>
04 parser_list_langs_current_FastText.py.py: Convert section in Aligned FastText vectors <br>
 <br>
##  Preprocessing 
05 preProcessJustSec.py: get subsample of the output parser_list_langs_current.py <br>
06 preProcessSecLinks.py: get subsample of the output parser_list_langs_current.py <br>
07 preProcessSecPos.py: get subsample of the output parser_list_langs_current.py <br>
08 SectionCharacterization.ipynb: get vertical sections stats (no parallel) <br>
09 SecCharacterizationToPandas.ipynb: Take section Characterization and transform in pickle <br>

## Getting Similarities 

10 PairOfLangs-JustSections-FinalExperiments-CoOcurrenceCount-Pandas.py: count number of coOccurences  <br>
11 CoOcurrencesToTfIdf.ipynb: Add tfidf weights to the CoOcurrenceCount  <br>
12 computeLinksPairDistance.ipynb: compute Link similarities <br> 
13 computeFasttextContentDistance.ipybn: compute distance between section content <br>
14 SectionFasttextDistance.ipynb: Get distance between embeddings of section titles (no content), based on the pre-trained fasttext alingment  <br>
15: SectionFasttextDistance-my_alingments.ipynb: same than 12, but with the alingments generated in 02  <br>


## Build Ground Truth 
16 GetGoogleTranslations.ipynb <br>

## Experiments 

17 SectionAligmentClassifier.ipynb: Train and test Alignment Classifer <br>
18 SynonymClassifierExperiments.ipynb: Train and test Synonym Classifier<br>

## Adding New languages 

19 SectionAligmentClassifierPlusNew.ipynb: Execute the model in languages without Ground Truth 
