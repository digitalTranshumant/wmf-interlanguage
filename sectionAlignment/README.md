== Pipeline ==

== Preparation ==
00 DownloadDependencies.ipynb
01 WikidataSqlToHive.ipybn: Get Wikidata Information from SQL replicas
02 my_alingments: Create Fasttext_multilingual alingments based on Wikidata # stat1005:alignment/fastText_multilingual

=== Data Extraction ===
03 parser_list_langs_current.py: Extract Section information from the dumps.
04 parser_list_langs_current_FastText.py.py: Convert section in Aligned FastText vectors
05 removeDuplicates.sh: data cleaning

===  Preprocessing ===
06 preProcessJustSec.py: get subsample of the output parser_list_langs_current.py
07 preProcessSecLinks.py: get subsample of the output parser_list_langs_current.py
08 preProcessSecPos.py: get subsample of the output parser_list_langs_current.py
09 SectionCharacterization.ipynb: get vertical sections stats (no parallel)
10 SecCharacterizationToPandas.ipynb: Take section Characterization and transform in pickle

=== Getting Similarities ===

11 PairOfLangs-JustSections-FinalExperiments-CoOcurrenceCount-Pandas.py: count number of coOccurences
12 CoOcurrencesToTfIdf.ipynb: Add tfidf weights to the CoOcurrenceCount
13 computeLinksPairDistance.ipynb: compute Link similarities
14 computeFasttextContentDistance.ipybn: compute distance between section content
15 SectionFasttextDistance.ipynb: Get distance between embeddings of section titles (no content), based on the pre-trained fasttext alingment
16: SectionFasttextDistance-my_alingments.ipynb: same than 12, but with the alingments generated in 02


=== Build Ground Truth ===
17 GetGoogleTranslations.ipynb

=== Experiments ===

18 SectionAligmentClassifier.ipynb: Train and test models

== Adding New languages ==

18 SectionAligmentClassifierPlusNew.ipynb: Execute the model in languages without Ground Truth 

