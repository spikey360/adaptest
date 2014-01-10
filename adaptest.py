#!/usr/bin/env python

import webapp2
import jinja2
import os

import handlers.homehandler
import handlers.performancehandler
import handlers.answerquestion

from models import User
from models import Question
from models import Answer
from models import AnsweredQuestion
from models import EstimationCredentials

from google.appengine.ext import ndb
from google.appengine.api import users

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))



######################
HomeHandler=handlers.homehandler.HomeHandler
PerformanceHandler=handlers.performancehandler.PerformanceHandler
AnswerQuestion=handlers.answerquestion.AnswerQuestion
######################



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

class PerformEstimation(webapp2.RequestHandler):
	def get(self, q_id):
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		query=Question.query(Question.key==ndb.Key('Question',int(q_id)))
		question=None
		answers=[]
		if query.count()==1:
			question=query.get()
			query=Answer.query(Answer.question==ndb.Key('Question',question.key.id()))
			answers=query.fetch()
		else:
			question=Question(question="Could not find this question")
			answers=["..."]
		#TODO must check answers size
		
		
		correctAnswereeThetas={}
		totalAnswereeThetas={}
		#initialize all possible estimation thetas
		for j in range(0,10,1):
			correctAnswereeThetas[float(j)]=0.0
			totalAnswereeThetas[float(j)]=0.0
		
		for answer in answers:
			#find number of people who gave this answer, make it distinct for user, meaning only one answer by a given user will be tabulated
			query=AnsweredQuestion.query(AnsweredQuestion.answer==ndb.Key('Answer',answer.key.id()),projection=[AnsweredQuestion.user],distinct=True)
			givenAnswers=query.fetch() #who are the people who answered this question?
			for givenAnswer in givenAnswers:
				who=EstimationCredentials.query(EstimationCredentials.user==givenAnswer.user)
				#TODO check if there is only one credential(not implemented just now)
				#find theta of this person
				theta=who.get().estimatedTheta
				totalAnswereeThetas[theta]=totalAnswereeThetas[theta]+1.0
				if answer.correct:
				#increment the specific estimatedTheta counter by 1
					correctAnswereeThetas[theta]=correctAnswereeThetas[theta]+1.0
				
		#normalize correctAnswerrThetas
		for j in range(0,10,1):
			if totalAnswereeThetas[float(j)]!=0: #ensures we don't divide by zero
				correctAnswereeThetas[float(j)]=correctAnswereeThetas[float(j)]/totalAnswereeThetas[float(j)]
				
			#now the above map gives the p(theta) for the given question
		#need to format data and send it to page
		vals={'question':question,'answers':answers,'correctDist':correctAnswereeThetas,'current_user':user}
		template=jinjaEnv.get_template("perform.html")
		self.response.out.write(template.render(vals))

app=webapp2.WSGIApplication(
[('/',HomeHandler),
('/estim/admin/add',AddQuestion),
#('/estim/adduser',AddEstimationCredential), #not needed from user side
(r'/estim/admin/perform/(\S+)',PerformEstimation),
('/estim/admin/performance',PerformanceHandler),
(r'/estim/answer/(\S+)',AnswerQuestion),
],
debug=True
)
