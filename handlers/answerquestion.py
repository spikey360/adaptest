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
		#We are looking for that question which the user is interested in answering
		query=Question.query(Question.key==ndb.Key('Question',int(q_id))) #the question has an id q_id, which has been obtained from uri
		question=None
		answers=[]
		if query.count()==1: #got only one question
			question=query.get()
			#run a query for those Answers which belong to this question
			query=Answer.query(Answer.question==ndb.Key('Question',question.key.id()))
			answers=query.fetch()
		else: #found more than 1 question
			#put some dummy but descriptive value for question and answer
			question=Question(question="Could not find this question")
			answers=["..."]
		#Values to pass to the View component
		vals={'question':question,'answers':answers,'current_user':user}
		#render to the template
		template=jinjaEnv.get_template('answerQuestion.html')
		#write it to the handler's output stream
		self.response.out.write(template.render(vals))
		
	#overriding the function to be executed for a POST request
	def post(self, q_id):
		#TODO check if the question has already been answered by the user, if so, do not post the new answer
		#q_id not used though
		#get the current user, this is important if we are to take an answer for this question
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		#ensure that credential to answer exists
		createDefaultCredential(user)
		#initialize a new AnsweredQuestion
		aq=AnsweredQuestion()
		#get the id of the Answer which has been selected
		a_id=self.request.get('answer')
		query=Answer.query(Answer.key==ndb.Key('Answer',int(a_id)))
		if query.count()==1:
			#then a valid answer has been given for some question
			aq.user=user #put the user name
			aq.answer=query.get().key #the key id of the answer that has been given by him
			try:
				aq.put() #write it to DB
				self.response.out.write("S") #write a flag indicating success
			except TransactionFailedError: #some bug here
				self.response.out.write("F")
		else:
			#invalid answer given
			self.response.out.write("F")

