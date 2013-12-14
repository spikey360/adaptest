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

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

#HomeHandler
#Handler class for the home page
#Presently, shows and gives link to all questions in the DB
class HomeHandler(webapp2.RequestHandler):
	def get(self):
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
			es=EstimationCredentials()
			es.user=user
			es.estimatedTheta=float(self.request.get('theta'))
			es.put()
			self.response.out.write("Added")

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
('/estim/add',AddQuestion),
('/estim/adduser',AddEstimationCredential),
(r'/estim/perform/(\S+)',PerformEstimation),
(r'/estim/answer/(\S+)',AnswerQuestion),
],
debug=True
)
