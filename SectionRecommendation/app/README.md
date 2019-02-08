# Section Recommendation app and API

An online demo app can be found in: http://secrec.wmflabs.org


Alignment API example: https://secrec.wmflabs.org/API/alignment/es/en/Historia

Recommendation API example: https://secrec.wmflabs.org/API/recommendation/en/Quilombo?verbose=False&blind=False

Where the parameters are:
* lang: One of the six supported languages [ar,en,es,fr,en,ru]
* title: Is an existing article on the target language.
* verbose: {False,True} When True, provide contextual information about recommendations
* blind: {False,True}  When True, gives recommendations without considering the existing sections on the current article. When False, return just potential missing sections



test.py: is the bottle file containing the web server

SecRecV3.py: is the main file containing Sec. Rec. modules (is a .py version, from the notebook version ../SecRec.ipynb)

recSheetsTSV: is a folder containing the section alignments produced in the root folder of this repo.
