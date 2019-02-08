from bottle import route, run, template,request,static_file
import SecRecV3 as SecRec
import json
import requests
import mysql.connector as mariadb

f = open('server.log','a',buffering=1)
mariadb_connection = mariadb.connect(user='app', password='pool', database='app')
cursor = mariadb_connection.cursor() 

# create TABLE evaluation (    ip VARCHAR(100),    article VARCHAR(200) ,    lang VARCHAR(40),    section VARCHAR(40),    evaluation VARCHAR(40), ts TIMESTAMP );


#Sec Rec API
@route('/API/recommendation/<lang>/<title>')
def APIRecs(lang,title):
	userIp = request.environ.get('REMOTE_ADDR')
	verbose = request.query.verbose or True
	blind = request.query.blid or False
	f.write('SecRec %s %s %s \n' % (userIp,lang,title))
	if lang not in SecRec.suportedLangs:
		error = {'error':'%s is not supported; supported languages are: %s' % (lang,','.join(SecRec.suportedLangs))}
		return error
	try:
		recs = SecRec.getRecs(title,lang,blind=blind,verbose=verbose)
		return template('{{name}}', name=recs)
	except:
		error = {'error':'%s not found, please try with another article' % title}
		return error
	

@route('/API/alignment/<lang1>/<lang2>/<section>')
def APIAlignment(lang1,lang2,section):
	userIp = request.environ.get('REMOTE_ADDR')
	f.write('Alignment %s %s %s %s \n' % (userIp,lang1,lang2,section))
	if lang1 not in SecRec.suportedLangs:
		error = {'error':'%s is not supported; supported languages are: %s' % (lang1,','.join(SecRec.suportedLangs))}
		return error
	if lang2 not in SecRec.suportedLangs:
		error = {'error':'%s is not supported; supported languages are: %s' % (lang2,','.join(SecRec.suportedLangs))}
		return error
	recs = SecRec.getAlignment(lang1,lang2,section)	
	return template('{{name}}', name=recs)


@route('/static/<filename>')
def server_static(filename):
	return static_file(filename, root='.')

@route('/')
def index():
	title = request.query.title or 'Quilombo'
	lang = request.query.lang or 'en'
	userIp = request.environ.get('REMOTE_ADDR')
	f.write('Demopage %s %s %s \n' % (userIp,lang,title))
	if lang not in SecRec.suportedLangs:
		text = '%s is not supported; supported languages are: %s' 
	else:

		try:
			response = requests.get("https://%s.wikipedia.org/api/rest_v1/page/summary/%s" % (lang,title))
			r = response.json()
			text = r['extract_html'] 
			image =  r['thumbnail']['source']
			recs = SecRec.getRecs(title,lang,blind=False,verbose=True,giveTitles=True)
			secRec = eval(recs['Recommendations'])
			currentSec = recs['context']['CurrentSections']
			numPerLang = {}
			langtitles = recs['context']['titles']
			for l, s in  recs['context']['SectionsInOtherLanguages'].items():
				numPerLang[l] = len(s)

		except:
			text = 'Article not found, please try another article'
			secRec = []
			image = ''
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
				<form action="/">

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

					<img src="{{image}}" ALIGN="left"> {{!text}} 
				<br>
				%if secRec: 
				<a href='https://{{lang}}.wikipedia.org/w/index.php?title={{title}}&action=edit' target='_blank'> Go to Wikipedia and edit this article </a>
				%end
				</div>

				<div class="col-sm">

				<b>Recommended sections:</b>
				<ul>
				<form action="/evaluated/{{lang}}/{{title}}/">


					  % for item in secRec:
					    <li><b>{{item}}</b>   <input type="radio" name="{{item}}" value="good" > Good  <input type="radio" name="{{item}}" value="fair"> Fair   <input type="radio" name="{{item}}" value="bad"> Bad </li>
					  % end
					 %if secRec:
					 <input type="submit" value="Evaluate"> <br>
					 %end
					 %if not secRec:
					 We can't provide section recommendations for this article.  This might be because the current article is the one with more complete set of sections among all the supported languages or we don't have good quality alignments for the remaining sections.
					 %end
					  </form> 

					</ul>
					<b>Number of sections in other languages:</b>
					<ul>
					  % for l,n in numPerLang.items():
					    <li><b> {{l}}:</b> {{n}}  <a href="https://{{l}}.wikipedia.org/wiki/{{langtitles[l]}}">{{langtitles[l]}}</a></li>
					  % end
					</ul>
					<b>Current sections and subsections in this article are:</b>
					<ul>
					 <li>	{{currentSec}} </li>
					</ul>

				</div>
			    </div>
	

			   </div>

			</body>
			</html>
			''', text=text,image=image,title=title,lang=lang,secRec=secRec,currentSec=currentSec,numPerLang=numPerLang,langtitles=langtitles)


### Evaluated
@route('/evaluated/<lang>/<title>/')
def evaluated(lang,title):
	userIp = request.environ.get('REMOTE_ADDR')
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
				<form action="/">

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



run(host='0.0.0.0',port=80)
