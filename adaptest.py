#!/usr/bin/env python

import webapp2
import jinja2
import os

import models

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class HomeHandler(webapp2.RequestHandler):
	def get(self):
		vals={}
		template=jinjaEnv.get_template('index.html')
		self.response.out.write(template.render(vals))
		

app=webapp2.WSGIApplication(
[('/',HomeHandler)],
debug=True
)
