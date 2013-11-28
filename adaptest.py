#!/usr/bin/env python

import webapp2
import jinja2
import os

from models import Question
from models import Answer

from google.appengine.ext import ndb

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class User(ndb.Model):
	user=ndb.UserProperty()
	uname=ndb.StringProperty()
	pwd=ndb.StringProperty()

class HomeHandler(webapp2.RequestHandler):
	def get(self):
		users=ndb.gql("SELECT * FROM User")
		vals={'users':users}
		template=jinjaEnv.get_template('index.html')
		self.response.out.write(template.render(vals))
class AddQuestion(webapp2.RequestHandler):
	def get(self):
		vals={}
		template=jinjaEnv.get_template('addQuestion.html')
		self.response.out.write(template.render(vals))
	def post(self):
		q=Question()
		q.question=self.request.get('q')
		q.b=0.0
		q.a=1.0
		q.c=0.25
		try:
			q.put()
		except TransactionFailedError:
			self.response.out.write("F")
		
		ans=[Answer()]*4
		for i in range(4):
			#ans[i]=Answer()
			ans[i].answer=self.request.get('a'+str(i))
			ans[i].question=q.key().id_or_name()
		try:
			for i in range(4):
				ans[i].put()
			self.response.out.write("S")
		except TransactionFailedError:
			self.response.out.write("F")

app=webapp2.WSGIApplication(
[('/',HomeHandler),
('/estim/add',AddQuestion),
],
debug=True
)
