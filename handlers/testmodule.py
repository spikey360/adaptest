#!/usr/bin/env python

import webapp2
import jinja2
import os
import time
import logging
import math
import globals

#import everthing :P cuz soon , we are gonna need more than a few of the dbhelper functions 
from models.dbhelper import *
from google.appengine.api import users
from computation import calculateP, calculateMLE

class InvalidTimeLeftError(Exception):
	def __init__(self,timeLeft):
		self.timeLeft=timeLeft
	def __str__(self):
		return str(self.timeLeft)


jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))

#####################################################################

	
	

#####################################################################

def calculateNatureOfNextQuestion(lastTwo_bool,infl1_bool,infl2_bool):
	#returns tougherQuestion, easierQuestion, maxInfoQuestion
	askTough=False
	
	if lastTwo_bool[0] and lastTwo_bool[1]:
		#trend is, user tends to give correct answer, requires tougher question
		askTough=True
	if not lastTwo_bool[0] and not lastTwo_bool[1]:
		#trend is, user tends to give wrong answer, requires easier
		askTough=False
	if not lastTwo_bool[0] and lastTwo_bool[1]:
		#user has hit inflexion, if 1 is hit, then this is 2
		if infl1_bool:
			infl2_bool=True
		else:
			infl1_bool=True
			askTough=True
	if lastTwo_bool[0] and not lastTwo_bool[1]:
		if infl1_bool:
			infl2_bool=True
		else:
			infl1_bool=True
			askTough=False
	#now, decide the nature of question
	if infl2_bool:
		return (globals.maxInfoQuestion,infl1_bool,infl2_bool)
	elif askTough:
		return (globals.tougherQuestion,infl1_bool,infl2_bool)
	#if incorrect answer/pass, ask an easier question till you get a correct answer
	else:
		return (globals.easierQuestion,infl1_bool,infl2_bool)
	
def getFirstQuestion(global_state,user):
	qs=fetchMoreDifficultQuestion(5.0,user)
	userState=global_state
	userState.theta=qs.b
	userState.put()
	return qs

def getNextQuestion(global_state,user):

	#get the list of all questions faced
	allFaced=fetchAllQuestionsParamsTestModule(user)
	userState=fetchGlobal(user)
	allFacedCount=len(allFaced)
	print allFaced
	#get the last two questions, observe the trend
	if allFacedCount>=2:
		(a1,b1,c1,sec_last)=allFaced[len(allFaced)-2]
		(a2,b2,c2,last)=allFaced[len(allFaced)-1]
	else:
		#faced only 1 question till now
		(a1,b1,c1,sec_last)=allFaced[len(allFaced)-1]
		(a2,b2,c2,last)=allFaced[len(allFaced)-1]
		#filling with duplicate values
		
	lasts=[]
	
	
	if sec_last==globals.correctAnswer:
		lasts.append(True)
	else:
		lasts.append(False)
	if last==globals.correctAnswer:
		lasts.append(True)
	else:
		lasts.append(False)
		
	print lasts
	#calculate the nature of next question
	#choose next question according to nature
	(nextNature,inf1,inf2)=calculateNatureOfNextQuestion(lasts,userState.inflexion_1,userState.inflexion_2)
	userState.inflexion_1=inf1
	userState.inflexion_2=inf2
	qs=None
	if nextNature==globals.tougherQuestion:
		qs=fetchMoreDifficultQuestion(userState.theta,user)
		print "Asking tougher"
		userState.theta=qs.b
	if nextNature==globals.easierQuestion:
		qs=fetchLessDifficultQuestion(userState.theta,user)
		print "Asking easier"
		userState.theta=qs.b
	if nextNature==globals.maxInfoQuestion:
		b_mle=calculateMLE(userState.theta,user)
		userState.theta=b_mle
		qs=fetchMostInformativeQuestion(userState,user)
		print "Asking max info"
		# test is finished
		userState.isTestFinished=True
	#the latest(maximum possible) theta estimation, according to correctness of last answer
	
	#at the end, save user state
	userState.put()
	return qs
	
class TestModule(webapp2.RequestHandler):
	def post(self,q_id):
		#required only for taking answers
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		a_id=self.request.get('answer')
		question=None
		answer=None
		try:
			question=fetchQuestion(int(q_id))
			answer=getAnswer(int(a_id))
		except dbhelper.InvalidIdError:
			self.response.out.write("F")
			return
		if answer is not None:
			result=insertQuestionAnswered(user,question.key,answer.key,evaluation=True)
			self.response.out.write(result)
		else:
			#invalid answer given
			self.response.out.write("F")
			
			
		#decide if data is sufficient to end test
		return
	def get(self):
		#required for getting question, options and time
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		userState=fetchGlobal(user)
		#see if test finished or not, in which case, printout score
		if userState.isTestFinished:
			#throw score
			score=calculateMLE(userState.theta,user)
			vals={'score':score}
			template=jinjaEnv.get_template('score.html')
			self.response.out.write(template.render(vals))
			#return
			return
		allFaced=fetchAllQuestionsParamsTestModule(user)
		question=None
		print "faced",len(allFaced)
		if len(allFaced)<1:
			#throw a median question
			question=getFirstQuestion(userState,user)
		else:
			question=getNextQuestion(userState,user)
		try:
			answers=fetchAnswersOf(question)
		except InvalidIdError:
			question=Question(question="Could not find this question")
		vals={'question':question,'answers':answers,'current_user':user,'evaluation':True}
		template=jinjaEnv.get_template('answerQuestion.html')
		self.response.out.write(template.render(vals))
		
			
			
			
		

