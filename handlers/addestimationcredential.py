#!/usr/bin/env python

import webapp2
import jinja2
import os

from models import User
from models import Question
from models import Answer
from models import AnsweredQuestion
from models import EstimationCredentials

from google.appengine.ext import ndb
from google.appengine.api import users

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))



class AddEstimationCredential(webapp2.RequestHandler):
	def get(self):
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		else:
			#template=jinjaEnv.get_template('credential.html')
			#self.response.out.write(template.render(vals))
			self.createDefault(user,float(self.request.get('theta')))
			self.response.out.write("Added")
			
	def post(self):
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		else:
			self.createDefault(user,float(self.request.get('theta')))
			self.response.out.write("Added")
			
	def createDefault(self, user, theta=5.0):
		es=None
		query=EstimationCredentials.query(EstimationCredentials.user==user)
		if query.count()==1:
			es=query.get()
		else:
			es=EstimationCredentials()
			es.user=user
		es.estimatedTheta=theta
		es.put()


