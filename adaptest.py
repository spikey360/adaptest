#!/usr/bin/env python

import webapp2
import jinja2
import os

from models import User
from models import Question
from models import Answer

from google.appengine.ext import ndb
from google.appengine.api import users

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class HomeHandler(webapp2.RequestHandler):
	def get(self):
		#questions=ndb.gql("SELECT * FROM Question")
		query=Question.query()
		questions=query.fetch()
		vals={'questions':questions}
		template=jinjaEnv.get_template('index.html')
		self.response.out.write(template.render(vals))

class AnswerQuestion(webapp2.RequestHandler):
	def get(self,q_id):
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		query=Question.query(Question.key==ndb.Key('Question',int(q_id)))
		question=None
		answers=[]
		if query.count()==1:
			question=query.get()
			query=Answer.query(Answer.question==ndb.Key('Question',question.key.id()))
			answers=query.fetch()
		else:
			question=Question(question="Could not find this question")
			answers=["..."]
		vals={'question':question,'answers':answers,'current_user':user}
		template=jinjaEnv.get_template('answerQuestion.html')
		self.response.out.write(template.render(vals))

class AddQuestion(webapp2.RequestHandler):
	def get(self):
		vals={}
		user=users.get_current_user()
		if user:
			#some sort of notification about the user who is logged in
			vals['current_user']=user.nickname()
		else:
			self.redirect(users.create_login_url(self.request.uri))
		template=jinjaEnv.get_template('addQuestion.html')
		self.response.out.write(template.render(vals))
	def post(self):
		user=users.get_current_user()
		q=Question()
		q.question=self.request.get('q')
		q.b=0.0
		q.a=1.0
		q.c=0.25
		if user:
			#create/find out the User class
			q.poster=user			
		else:
			self.redirect(users.create_login_url(self.request.uri))
		putQ=None
		try:
			putQ=q.put()
		except TransactionFailedError:
			self.response.out.write("F")
			return
		
		ans=[]
		for i in range(4):
			a=Answer()
			a.answer=self.request.get('a'+str(i+1))
			checked=self.request.get('c'+str(i+1))
			if checked=="true":
				a.correct=True
			else:
				a.correct=False
			a.question=putQ
			ans.append(a)
		try:
			for i in range(4):
				ans[i].put()
			self.response.out.write("S")
		except TransactionFailedError:
			self.response.out.write("F")

app=webapp2.WSGIApplication(
[('/',HomeHandler),
('/estim/add',AddQuestion),
(r'/estim/answer/(\S+)',AnswerQuestion),
],
debug=True
)
