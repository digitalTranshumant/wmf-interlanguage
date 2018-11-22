== Pipeline == <br>

== Preparation == <br>

00 DownloadDependencies.ipynb <br>
01 WikidataSqlToHive.ipybn: Get Wikidata Information from SQL replicas <br>
02 my_alingments: Create Fasttext_multilingual alingments based on Wikidata <br>

=== Data Extraction === <br>

03 parser_list_langs_current.py: Extract Section information from the dumps. <br>
04 parser_list_langs_current_FastText.py.py: Convert section in Aligned FastText vectors <br>
05 removeDuplicates.sh: data cleaning <br>
 <br>
===  Preprocessing === <br>
06 preProcessJustSec.py: get subsample of the output parser_list_langs_current.py <br>
07 preProcessSecLinks.py: get subsample of the output parser_list_langs_current.py <br>
08 preProcessSecPos.py: get subsample of the output parser_list_langs_current.py <br>
09 SectionCharacterization.ipynb: get vertical sections stats (no parallel) <br>
10 SecCharacterizationToPandas.ipynb: Take section Characterization and transform in pickle <br>

=== Getting Similarities ===

11 PairOfLangs-JustSections-FinalExperiments-CoOcurrenceCount-Pandas.py: count number of coOccurences  <br>
12 CoOcurrencesToTfIdf.ipynb: Add tfidf weights to the CoOcurrenceCount  <br>
13 computeLinksPairDistance.ipynb: compute Link similarities <br> 
14 computeFasttextContentDistance.ipybn: compute distance between section content <br>
15 SectionFasttextDistance.ipynb: Get distance between embeddings of section titles (no content), based on the pre-trained fasttext alingment  <br>
16: SectionFasttextDistance-my_alingments.ipynb: same than 12, but with the alingments generated in 02  <br>


=== Build Ground Truth ===
17 GetGoogleTranslations.ipynb <br>

=== Experiments ===

18 SectionAligmentClassifier.ipynb: Train and test Alignment Classifer <br>
19 SynonymClassifierExperiments.ipynb: Train and test Synonym Classifier<br>

== Adding New languages ==<br>

20 SectionAligmentClassifierPlusNew.ipynb: Execute the model in languages without Ground Truth  <br>

