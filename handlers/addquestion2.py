#!/usr/bin/env python

import webapp2
import jinja2
import os
from models.objects import Question
from models.objects import Answer
from google.appengine.api import users
from random import randint

from testmodule import *

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))

class AddQuestion2(webapp2.RequestHandler):
	def get(self):
		for x in range(0, 110):
			user=users.get_current_user()
			q=Question()
			#get the key of the question
			q.question='Question Number %d ?'%(x+1)
			#initialize a, b, c
			
			#q.a an important parameter
			#q.a=1.0 Rasch Case
			q.a=randint(50,200)/100.0 # this is real case, should be properly estimated
			q.b=(x+1)/10.0
			q.c=0.25
			if user:
				#create/find out the User class
				q.poster=user
			else:
				self.redirect(users.create_login_url(self.request.uri))
			putQ=None
			try:
				putQ=q.put()
				self.response.out.write("S")
			except TransactionFailedError:
				self.response.out.write("F")
			ans=[]
			#currentAnswer can also be randomised atm, its always the first one
			#currentAnswer=randint(0,3)
			currentAnswer=0
			for i in range(4): #four answers at present
				a=Answer()
				#get the numbered variable which hold the flag of it being correct
				a.answer='Option %d-%d'%(x+1,i+1)
				if i==currentAnswer: #check for correctness, set by true
					a.correct=True
				else:
					a.correct=False
				a.question=putQ
				ans.append(a)
			try:
				putQ=q.put()
				for i in range(4):
					ans[i].put()
				self.response.out.write("S")
			except TransactionFailedError:
				self.response.out.write("F")
		
		#temp test for score :P
		#user=users.get_current_user()
		#DisplayResultPg85(self,getThetaResult(user))