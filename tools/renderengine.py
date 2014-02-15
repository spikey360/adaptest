import os
import cStringIO
import jinja2
import logging
from google.appengine.ext import ndb
from google.appengine.api import memcache

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))


def renderQuestion(vals):
	template=jinjaEnv.get_template('answerQuestion.html')
	output=cStringIO.StringIO()
	output.write(template.render(vals))
	return output.getvalue()
	
def getRenderedQuestion(qid,vals):
	data=memcache.get('%d_rQuestion'%qid)
	if data is not None:
		return data
	else:
		renderQuestion(vals)
		data=renderQuestion(vals)
		if not memcache.add('%d_rQuestion'%qid,data,60*5): #5 minute cache
			logging.error("Could not add rendering %d to memcache"%qid)
		return data

