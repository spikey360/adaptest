#!/usr/bin/env python

import webapp2
import jinja2
import os
import models.dbhelper as dbhelper
from models.dbhelper import InvalidIdError
from models.objects import Question
from models.objects import Answer
from models.objects import AnsweredQuestion
from models.objects import EstimationCredentials
from google.appengine.api import users
from google.appengine.ext import ndb

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))

class DistributionAnalyzer:
	#TODO must ideally throw an exception for non-existent question
	def analyzeQuestion(self,question):
		answers=[]
		try:
			answers=dbhelper.fetchAnswersOf(question)
		except dbhelper.InvalidIdError:
			raise
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
		return (answers, correctAnswereeThetas, totalAnswereeThetas)
				
		

class PerformEstimation(webapp2.RequestHandler):
	def get(self, q_id):
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		#now the above map gives the p(theta) for the given question
		#need to format data and send it to page
		###############################################
		question=None
		try:
			question=dbhelper.fetchQuestion(int(q_id))
		except InvalidIdError:
			self.response.out.write("No such page") #TODO replace with proper 404 code
			return
		(answers,correctAnswereeThetas,totalAnswereeThetas)=DistributionAnalyzer().analyzeQuestion(question)
		vals={'question':question,'answers':answers,'correctDist':correctAnswereeThetas,'current_user':user}
		template=jinjaEnv.get_template("perform.html")
		self.response.out.write(template.render(vals))


