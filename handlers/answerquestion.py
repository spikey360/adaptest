#!/usr/bin/env python

import webapp2
import jinja2
import os
from models.objects import Question
from models.objects import Answer
from models.objects import AnsweredQuestion
from models.objects import EstimationCredentials
from models import dbhelper
from google.appengine.ext import ndb
from google.appengine.api import users

from models.dbhelper import insertQuestionAnswered

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))

def createDefaultCredential(user, theta=5.0):
	es=None
	query=EstimationCredentials.query(EstimationCredentials.user==user)
	if query.count()==1:
		#already exists, return
		return
	else:
		es=EstimationCredentials()
		es.user=user
	es.estimatedTheta=theta
	es.put()
	return

#AnswerQuestion
#Handler class for the page where the user can answer from mutiple choices
#Presently, does just that
class AnswerQuestion(webapp2.RequestHandler):
	#overriding the function which would be executed for a GET request
	def get(self,q_id):
		#get the current user
		user=users.get_current_user()
		if not user:	#if user object is None i.e. No user can be determined
			#redirect to the user authentication page
			self.redirect(users.create_login_url(self.request.uri))
		question=None
		answers=[]
		try:
			question=dbhelper.fetchQuestion(int(q_id))
			answers=dbhelper.fetchAnswersOf(question)
		except dbhelper.InvalidIdError:
			question=Question(question="Could not find this question") #should ideally redirect to 404 page
		#Values to pass to the View component
		vals={'question':question,'answers':answers,'current_user':user}
		#render to the template
		template=jinjaEnv.get_template('answerQuestion.html')
		#write it to the handler's output stream
		self.response.out.write(template.render(vals))
		return
		
	#overriding the function to be executed for a POST request
	def post(self, q_id):
		#TODO check if the question has already been answered by the user, if so, do not post the new answer
		#get the current user, this is important if we are to take an answer for this question
		
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		#ensure that credential to answer exists
		createDefaultCredential(user)
		#initialize a new AnsweredQuestion
		#aq=AnsweredQuestion()
		#get the id of the Answer which has been selected
		a_id=self.request.get('answer')
		question=None
		answer=None
		try:
			question=dbhelper.fetchQuestion(int(q_id))
			answer=dbhelper.getAnswer(int(a_id))
		except dbhelper.InvalidIdError:
			self.response.out.write("F")
			return
		if answer is not None:
			#then a valid answer has been given for some question
			#aq.user=user.user_id() #put the user name
			#aq.answer=query.get().key #the key id of the answer that has been given by him
			#try:
			#	aq.put() #write it to DB
			#	self.response.out.write("S") #write a flag indicating success
			#except TransactionFailedError: #some bug here
			#	self.response.out.write("F")
			result=insertQuestionAnswered(user,question.key,answer.key)
			self.response.out.write(result)
			
		else:
			#invalid answer given
			self.response.out.write("F")
		