#!/usr/bin/env python

import webapp2
import jinja2
import os
from models.objects import EstimationCredentials
from google.appengine.api import users
from google.appengine.ext import ndb

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))



class CredentialHandler(webapp2.RequestHandler):
	def get(self):
		vals={}
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		else:
			query=EstimationCredentials.query()
			vals['credentials']=query.fetch()
			template=jinjaEnv.get_template('credential.html')
			self.response.out.write(template.render(vals))

class ModifyCredentialHandler(webapp2.RequestHandler):
	def post(self,u_id):
		theta=5.0
		ec=None
		key=int(u_id)
		query=EstimationCredentials.query(EstimationCredentials.key==ndb.Key('EstimationCredentials',key))
		if query.count() == 1:
			ec=query.get()
			theta=ec.estimatedTheta
			if self.request.get("i") == "true":
				#check if incrementable
				if theta+1.0<=10:
					theta=theta+1.0
				else:
					self.response.out.write("F")
					return
			else:
				#check if decrementable
				if theta-1.0>=0:
					theta=theta-1.0
				else:
					self.response.out.write("F")
					return
		else:
			self.response.out.write("F")
			return
		self.setTheta(ec,float(theta))
		self.response.out.write("S")
			
	def setTheta(self, es, theta=5.0):
		es.estimatedTheta=theta
		es.put()

