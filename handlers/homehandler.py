#!/usr/bin/env python

import webapp2
import jinja2
import os
import time
import globals


from models.objects import *
from models.dbhelper import *
from google.appengine.api import users

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))

#HomeHandler
#Handler class for the home page
#Presently, shows and gives link to all questions in the DB

def createDummyAnswer():
	query=Answer.query(Answer.answer=='~pass~')
	if query.count()>=1:
		return#do nothing cuz dummy answer present
	else:
		instance=Answer()
		instance.answer='~pass~'
		try:
			#write it to DB
			instance.put() 
			return
		except TransactionFailedError: #some bug here
			return 'F'
	return



class HomeHandler(webapp2.RequestHandler):
	def __init__(self,request,response):
		self.initialize(request,response)
	def get(self):
		#force the use to Login
		createDummyAnswer()
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		#We are using a NoSQL DB so will be refraining fom writing GQL
		#query for all Question objects in DB
		query=Question.query()
		#fetch them
		questions=query.fetch()
		#Values we will be passing to the view (of MVC)
		vals={'questions':questions}
		#get the page template suitable for this page
		template=jinjaEnv.get_template('index.html')
		#render the values into the template and put it in the output stream of the RequestHandler
		self.response.out.write(template.render(vals))
		
	def post(self):
		#just reset the globals for the currentUser in the DB
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		else:
			clearUserTestAnswers(user)
			time.sleep(0.75)
			firstQuestion=fetchMoreDifficultQuestion(2.45,user)
			#update_or_Insert(user,str(10), str(globals.firstQuestion) ,str(round(time.time()+30.5)),1.0)
			update_or_Insert(user,str(10), str(firstQuestion) ,str(round(time.time()+30.5)),2.5)
		time.sleep( 2 )
		self.redirect("/test")
	
	

