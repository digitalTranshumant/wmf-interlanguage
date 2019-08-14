from bottle import route, run, template,request,static_file,response,Bottle
import bottle
import SecRecV4 as SecRec
import json
import requests
import mysql.connector as mariadb

f = open('server.log','a',buffering=1)
supportedLangs = ['en','es','fr','ru','ja','ar']


# create TABLE evaluation (    ip VARCHAR(100),    article VARCHAR(200) ,    lang VARCHAR(40),    section VARCHAR(40),    evaluation VARCHAR(40), ts TIMESTAMP );

# create TABLE evaluationGeneral (    ip VARCHAR(100),    article VARCHAR(200) ,    lang VARCHAR(40),    Q1 VARCHAR(40),    Q2 VARCHAR(40), Q3 VARCHAR(40),Q4 VARCHAR(40),Q5 VARCHAR(40),ts TIMESTAMP );

app = Bottle()

#Sec Rec API
@app.route('/API/recommendation/<lang>/<title>')
def APIRecs(lang,title):
	userIp = request.environ.get('HTTP_X_FORWARDED_FOR')
	verbose = request.query.verbose or False
	if verbose == 'False':
		verbose = False
	blind = request.query.blind or True
	if blind == 'False':
		blind = False
	f.write('SecRec %s %s %s \n' % (userIp,lang,title))
	if lang not in SecRec.suportedLangs:
		error = {'error':'%s is not supported; supported languages are: %s' % (lang,','.join(SecRec.suportedLangs))}
		return error
	try:
		recs = SecRec.getRecs2(title,lang,blind=blind,verbose=verbose)
		print(json.dumps(recs))
		return recs
	except:
		error = {'error':'%s not found, please try with another article' % title}
		return error
	

@app.route('/API/alignment/<lang1>/<lang2>/<section>')
def APIAlignment(lang1,lang2,section):
	print('hola')
	userIp = request.environ.get('HTTP_X_FORWARDED_FOR')
	print(section)
	f.write('Alignment %s %s %s %s \n' % (userIp,lang1,lang2,section))
	if lang1 not in SecRec.suportedLangs:
		error = {'error':'%s is not supported; supported languages are: %s' % (lang1,','.join(SecRec.suportedLangs))}
		return error
	if lang2 not in SecRec.suportedLangs:
		error = {'error':'%s is not supported; supported languages are: %s' % (lang2,','.join(SecRec.suportedLangs))}
		return error
	recs = SecRec.getAlignment(lang1,lang2,section)	
	response.content_type = 'application/json'
	return json.dumps(recs)

@app.route('/static/<filename>')
def server_static(filename):
	return static_file(filename, root='.')

@app.route('/v1')
def indexv1():
	title = request.query.title or 'Quilombo'
	lang = request.query.lang or 'en'
	print(request.environ)
	userIp = request.environ.get('HTTP_X_FORWARDED_FOR')
	f.write('Demopage %s %s %s \n' % (userIp,lang,title))
	if lang not in SecRec.suportedLangs:
		text = '%s is not supported; supported languages are: %s' 
	else:

		try:
			response = requests.get("https://%s.wikipedia.org/api/rest_v1/page/summary/%s" % (lang,title))
			r = response.json()
			text = r['extract_html'] 
			image =  r.get('thumbnail', {}).get('source','')
			recs = SecRec.getRecs2(title,lang,blind=False,verbose=True,giveTitles=True)
			secRec = recs['Recommendations']
			currentSec = recs['context']['CurrentSections']
			numPerLang = {}
			langtitles = recs['context']['titles']
			for l, s in  recs['context']['SectionsInOtherLanguages'].items():
				numPerLang[l] = len(s)

		except:
			try:    #this try is in case that SecRec.getRecs fails, but there is still a pagepreview
				response = requests.get("https://%s.wikipedia.org/api/rest_v1/page/summary/%s" % (lang,title))
				r = response.json()
				text = r['extract_html']
				image =  r.get('thumbnail', {}).get('source','')
			except:
				text = 'Article not found, please try another article'
				image = ''
			recs = {'context':{'usedMoreLike':''}}
			secRec = []
			currentSec = ''
			langtitles = {}
			numPerLang = {}
	return template('''  

			<!DOCTYPE html>
			<html>
			<head>

			  <title>Section Recommendation Demo</title>
			  <link href="/static/bootstrap.min.css" rel="stylesheet">
			<style>
				body {
				    background-color: #EAECF0 !important;
				}

				header, main, footer {
				    margin: 10px 0 30px;
				}

				header .project-name {
				    font-size: 1.5em;
				}

				footer {
				    margin-top: 100px;
				}

								
				.main-content {
				    background-color: white;
				    padding: 15px;
				}

			p {
			  text-align: justify;
			  text-justify: inter-word;
			}
			</style>


			</head>


			<body>
			  <div class="container">
  			   <div class="row"> <h1> Section Recommendation Demo  </h1> </div>


			   <div class="row">  
				<form action="/v1">

				Wiki: 
				  <select name="lang" value="{{lang}}">
				    <option value="en" selected ></option>
				    <option value="ar">ar.wikipedia</option>
				    <option value="en">en.wikipedia</option>
				    <option value="es">es.wikipedia</option>
				    <option value="fr">fr.wikipedia</option>
				    <option value="ja">ja.wikipedia</option>
				    <option value="ru">ru.wikipedia</option>
				  </select>
				Article: <input type="text" name="title" value="{{title}}">
				 <input type="submit" value="Try Another Article"> <br>
							</form>  
			   </div>
			
			   <div class="row justify-content-md-center">
   				
				<div class="col-lg">
  			  	         <h3> {{title}} - {{lang}}.wikipedia.org </h3>  
					 <b> Article Summary: </b> <br>

					<img style="margin: 0px 15px 5px 0px" src="{{image}}" ALIGN="left"> {{!text}} 
				<br>
				%if secRec: 
				<a href='https://{{lang}}.wikipedia.org/w/index.php?title={{title}}&action=edit' target='_blank'> Go to Wikipedia and edit this article </a>
				%end
				</div>

				<div class="col-sm">

				<b>Recommended sections:</b>
				<ul><table>
				<form action="/evaluated/{{lang}}/{{title}}/">
					


					  % for item in secRec:
					     <tr> <td ><li><b>{{item}}</b> </li></td><td>  <input type="radio" name="{{item}}" value="good" > Good  </td><td><input type="radio" name="{{item}}" value="redundant"> Redundant   </td><td><input type="radio" name="{{item}}" value="NotRelated"> Not Related </td></tr>
					  % end
				</table></ul>
					 %if secRec:
					 <input type="submit" value="Evaluate"> <br>
					 %end
					 %if not secRec:
					 We can't provide section recommendations for this article.  This might be because the current article is the one with more complete set of sections among all the supported languages or we don't have good quality alignments for the remaining sections.
					 %end
					  </form> 

					</ul>
					<b>Number of sections in other languages:</b>
					%if useMoreLike:
					<br>We couldn't find sections to recommend in any of the supported languages. This page might be an <a href="https://en.wikipedia.org/wiki/Wikipedia:Stub"> Stub</a>. To provide recommendations we have used similar pages:	<br> 
					%end
					<ul>
					  % if not numPerLang:
						<li> These article does not exists in any of the other supported languages </li>
					  %end
					  % for l,n in numPerLang.items():
					    <li><b> {{l}}:</b> {{n}}  <a href="https://{{l}}.wikipedia.org/wiki/{{langtitles[l]}}">{{langtitles[l]}}</a></li>
					  % end
					</ul>
					<b>Current sections and subsections in this article are:</b>
					<ul>
					  %if currentSec and not useMoreLike:
					 <li>{{currentSec}} </li>
					 %end	
					  %if not currentSec:
					 <li>The current article has no sections yet. </li>
					 %end
					</ul>

				</div>
			    </div>
	

			   </div>

			</body>
			</html>
			''', text=text,image=image,title=title,lang=lang,secRec=secRec,currentSec=currentSec,numPerLang=numPerLang,langtitles=langtitles,useMoreLike=recs['context']['usedMoreLike'])


### Evaluated
@app.route('/evaluated/<lang>/<title>/')
def evaluated(lang,title):
	mariadb_connection = mariadb.connect(user='app', password='pool', database='app')
	cursor = mariadb_connection.cursor() 
	userIp = request.environ.get('HTTP_X_FORWARDED_FOR')
	evaluations = dict(request.query.decode())
	for sec,value in evaluations.items():
		cursor.execute("INSERT INTO evaluation (ip,article,lang,section,evaluation) VALUES ('%s','%s','%s','%s','%s')" % (userIp,title,lang,sec,value))
	mariadb_connection.commit() 

	return template('''  

			<!DOCTYPE html>
			<html>
			<head>

			  <title>Section Recommendation Demo</title>
			  <link href="/static/bootstrap.min.css" rel="stylesheet">
			<style>
				body {
				    background-color: #EAECF0 !important;
				}

				header, main, footer {
				    margin: 10px 0 30px;
				}

				header .project-name {
				    font-size: 1.5em;
				}

				footer {
				    margin-top: 100px;
				}

								
				.main-content {
				    background-color: white;
				    padding: 15px;
				}

			p {
			  text-align: justify;
			  text-justify: inter-word;
			}
			</style>


			</head>


			<body>
			  <div class="container">
  			   <div class="row"> <h1> Section Recommendation Demo  </h1> </div>
			   <div class="row justify-content-md-center">
			   Thanks for your feedback. Please select another article. <br>
				
			   </div>


			   <div class="row">  
				<form action="/v1">

				Wiki: 
				  <select name="lang">
				    <option value="en" selected ></option>
				    <option value="ar">ar.wikipedia</option>
				    <option value="en">en.wikipedia</option>
				    <option value="es">es.wikipedia</option>
				    <option value="fr">fr.wikipedia</option>
				    <option value="ja">ja.wikipedia</option>
				    <option value="ru">ru.wikipedia</option>
				  </select>
				Article: <input type="text" name="title" value="">
				 <input type="submit" value="Try Another Article"> <br>
							</form>  
			   </div>

			   </div>


			</body>
			</html> ''')


## sandbox

@app.route('/')
def index():
	try:
		evaluations = dict(request.query.decode())
		if evaluations.get('GenerateRandom',False):
			lang = request.query.lang or 'en'
			title = SecRec.getArticleWithRec(lang)
		else:
			lang = request.query.lang or 'en'
			title = request.query.title or SecRec.getArticleWithRec(lang)

		print(title,lang)
		userIp = request.environ.get('HTTP_X_FORWARDED_FOR')
		f.write('Demopage %s %s %s \n' % (userIp,lang,title))
		if evaluations:
			mariadb_connection = mariadb.connect(user='app', password='pool', database='app')
			titleEval = evaluations.get('title')
			langEval = evaluations.get('lang')
			Q1 = evaluations.get('Q1','No Reponse')
			Q2 = evaluations.get('Q2','No Reponse')
			Q3 = evaluations.get('Q3','No Reponse')
			Q4 = evaluations.get('Q4','No Reponse')
			Q5 = evaluations.get('Q5','No Reponse')
			print('values:',userIp, titleEval, langEval,Q1,Q2,Q3,Q4,Q5)
			cmd = "INSERT INTO evaluationGeneral (ip,article,lang,Q1,Q2,Q3,Q4,Q5) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')" % (userIp, titleEval, langEval,Q1,Q2,Q3,Q4,Q5)
			print(cmd)
			cursor = mariadb_connection.cursor() 
			cursor.execute(cmd)
			mariadb_connection.commit() 
			cursor.close()
			mariadb_connection.close()

		if lang not in SecRec.suportedLangs:
			text = '%s is not supported; supported languages are: %s' 
		else:

			try:
				response = requests.get("https://%s.wikipedia.org/api/rest_v1/page/summary/%s" % (lang,title))
				r = response.json()
				text = r['extract_html'] 
				image =  r.get('thumbnail', {}).get('source','')
				recs = SecRec.getRecs2(title,lang,blind=False,verbose=True,giveTitles=True)
				secRec = recs['Recommendations']
				currentSec = recs['context']['CurrentSections']
				numPerLang = {}
				langtitles = recs['context']['titles']
				for l, s in  recs['context']['SectionsInOtherLanguages'].items():
					numPerLang[l] = len(s)

			except:
				try:    #this try is in case that SecRec.getRecs fails, but there is still a pagepreview
					response = requests.get("https://%s.wikipedia.org/api/rest_v1/page/summary/%s" % (lang,title))
					r = response.json()
					text = r['extract_html'] 
					image =  r.get('thumbnail', {}).get('source','')
				except:
					text = 'Article not found, please try another article'
					image = ''
				recs = {'context':{'usedMoreLike':''}}
				secRec = []
				currentSec = ''
				langtitles = {}
				numPerLang = {}
		return template('''  

				<!DOCTYPE html>
				<html>
				<head>

				  <title>Section Recommendation Demo</title>
				  <link href="/static/bootstrap.min.css" rel="stylesheet">
				<style>
					body {
					    background-color: #EAECF0 !important;
					}

					header, main, footer {
					    margin: 10px 0 30px;
					}

					header .project-name {
					    font-size: 1.5em;
					}

					footer {
					    margin-top: 100px;
					}

								
					.main-content {
					    background-color: white;
					    padding: 15px;
					}

				p {
				  text-align: justify;
				  text-justify: inter-word;
				}
				</style>


				</head>

				<body>
				  <div class="container">

				   <div class="row" style="border-style:solid">  
					<form action="/">
				<table >
					 <tr> <td >Wiki:  </td><td style="margin:5px">
					  <select name="lang" value="{{lang}}">
					    <option value="en" selected ></option>
					    <option value="ar">ar.wikipedia</option>
					    <option value="en" selected="selected">en.wikipedia</option>
					    <option value="es">es.wikipedia</option>
					    <option value="fr">fr.wikipedia</option>
					    <option value="ja">ja.wikipedia</option>
					    <option value="ru">ru.wikipedia</option>
					  </select> <br></td> 
			
					 <td >Article:</td><td> <input type="text" name="title" value="{{title}}"> <br> </td> 
					 <td><input type="submit" value="Get recommendations"> <br></td> </tr>
								</form>  
				</table>

				   </div>
			
				   <div class="row justify-content-md-center">
	   				
					<div class="col-lg">
	  			  	         <h3> {{title}} - {{lang}}.wikipedia.org </h3>  
						 <b> Article Summary: </b> <br>


						<img style="margin: 0px 15px 5px 0px" src="{{image}}" ALIGN="left"> {{!text[:-4]}} 
	<a href='https://{{lang}}.wikipedia.org/w/index.php?title={{title}}' target='_blank'> View on Wikipedia</a> </p>


					<b>Current sections and subsections in this article are:</b>
					<ul>
					%if currentSec and not useMoreLike:
						%for current in currentSec:
						<li>{{current}} </li>
						%end
					%end	
					%if not currentSec:
					<li>The current article has no sections yet. </li>
					%end
					</ul>


					</div>

					<div class="col-sm">

						<h3>Recommended sections:</h3>
						<form action="/">
						<ul>
						% for item in secRec:
							<li><b>{{item}}</b> </li>				
						%end
						</ul>



						 %if secRec:

						<b> Most or all of the recommended sections.. </b>
						<ol>
						<li>  Are relevant to the topic of this article </li>
						<input type="radio" name="Q1" value="agree" > Agree <input type="radio" name="Q1" value="disagree" > Disagree
						<li> Are important for this article to have</li>
						<input type="radio" name="Q2" value="agree" > Agree <input type="radio" name="Q2" value="disagree" > Disagree
						<li> Are redundant or conflict with the existing sections in the article</li>
						<input type="radio" name="Q3" value="agree" > Agree <input type="radio" name="Q3" value="disagree" > Disagree
						<li> Are redundant or conflict with other recommended sections</li>
						<input type="radio" name="Q4" value="agree" > Agree <input type="radio" name="Q4" value="disagree" > Disagree
						</ol>
						<ul>
						<li> <b> If I were expanding this article, I would find these recommendations useful </b></li>
						<input type="radio" name="Q5" value="agree" > Agree <input type="radio" name="Q5" value="disagree" > Disagree <br>
						 <input type="submit" value="Submit Ratings"> <br>
						 %end
						 %if not secRec:
						 We can't provide section recommendations for this article.  This might be because the current article is the one with more complete set of sections among all the supported languages, please select another article.
						 %end
	   					 <input type="hidden" name="title" value="{{title}}" />
	   					 <input type="hidden" name="lang" value="{{lang}}" />
	   					 <input type="hidden" name="GenerateRandom" value="yes" />
						  </form> 
						<form action="/"> <input type="submit" value="Skip Article"> <br>
						</ul>
	<b> Provide additional feedback </b> <br>
	<p>If you would like to provide additional feedback on
	these recommendations, please do so on the <a href='https://meta.wikimedia.org/wiki/Research_talk:Expanding_Wikipedia_articles_across_languages/Inter_language_approach/Feedback' target="_blank">talk page</a>. </p>
	<p>If you paste the template below with your feedback, it
	will help us understand your comments better.</p>

	{{'{{'}}Section_recommendation_feedback <br>
	|lang={{lang}}<br>
	|article={{title}}<br>
	|link=https://secrec.wmflabs.org/?lang={{lang}}&title={{title}}<br>
	% for n,item in enumerate(secRec):
	|section{{n+1}}={{item}}<br>				
	%end
	{{'}}'}}				</div>
				    </div>
	

				   </div>

				</body>
				</html>
				''', text=text,image=image,title=title,lang=lang,secRec=secRec,currentSec=currentSec,numPerLang=numPerLang,langtitles=langtitles,useMoreLike=recs['context']['usedMoreLike'])

	except Exception as e: 
		print('error - reloading',e)
		index()

@app.route("/test/:category/:category2", method=["GET","POST"])
def admin(category,category2):
    try:
        return category+category2
    except Exception(e):
        print ("e:"+str(e))





run(app,host='0.0.0.0',port=80,server='tornado',reloader=True,interval=3,quiet=False,debug=True)
