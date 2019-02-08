from bottle import route, run, template
import SecRec

@route('/<lang>/<title>')
def index(lang,title):
    print(lang,title)
    recs = SecRec.getRecs(title,lang)
    return template('{{name}}', name=recs)

run(host='0.0.0.0',port=80)
