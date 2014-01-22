#!/usr/bin/env python

import webapp2
import jinja2
import os
from google.appengine.api import users
from models.objects import Question

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))

class PerformanceHandler(webapp2.RequestHandler):
	def get(self):
		#We are using a NoSQL DB so will be refraining fom writing GQL
		#query for all Question objects in DB
		user=users.get_current_user()
		query=Question.query()
		#fetch them
		questions=query.fetch()
		#Values we will be passing to the view (of MVC)
		vals={'current_user':user,'questions':questions}
		#get the page template suitable for this page
		template=jinjaEnv.get_template('performance.html')
		#render the values into the template and put it in the output stream of the RequestHandler
		self.response.out.write(template.render(vals))

