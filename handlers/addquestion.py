#!/usr/bin/env python

import webapp2
import jinja2
import os
from models import Question
from models import Answer
from google.appengine.api import users

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))

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
		#get the key of the question
		q.question=self.request.get('q')
		#initialize a, b, c
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
		for i in range(4): #four answers at present
			a=Answer()
			#get the numbered variable which hold the flag of it being correct
			a.answer=self.request.get('a'+str(i+1))
			checked=self.request.get('c'+str(i+1))
			if checked=="true": #check for correctness, set by true
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


