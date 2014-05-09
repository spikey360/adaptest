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
		user=users.get_current_user()
		DisplayResultPg85(self,getThetaResult(user))