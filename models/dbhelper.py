#!/usr/bin/env python

import handlers.globals

from objects import *
from google.appengine.ext import ndb
import logging
import jinja2
import os
import random
import time


jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))

class InvalidIdError(Exception):
	def __init__(self,q_id):
		self.q_id=q_id
	def __str__(self):
		return str(self.q_id)

def fetchQuestion(q_id):
	#fetch it
	query=Question.query(Question.key==ndb.Key('Question',q_id))
	if query.count()==1:
		return query.get()
	else:
		raise InvalidIdError(q_id)

def getAnswer(a_id):
	#fetch it
	query=Answer.query(Answer.key==ndb.Key('Answer',a_id))
	if query.count()==1:
		return query.get()
	else:
		raise InvalidIdError(a_id)

def getPassedAnswer():
	#fetch it
	query=Answer.query(Answer.answer=='~pass~')
	if query.count()==1:
		return query.get()
	#else:
	#	raise InvalidIdError(a_id)
	

def fetchAnswers(q_id):
	question=None
	try:
		question=fetchQuestion(q_id)
	except InvalidIdError:
		raise
	answers=[]
	query=Answer.query(Answer.question==ndb.Key('Question',question.key.id()))
	answers=query.fetch()
	return answers

def fetchAnswersOf(Question):
	try:
		return fetchAnswers(Question.key.id())
	except InvalidIdError:
		raise

def fetchMoreDifficultQuestions(b):
	query=Question.query(Question.b>=b).order(Question.b)
	return query.fetch()

def fetchMoreDifficultQuestion(b,user):
	query=fetchMoreDifficultQuestions(b)
	for question in query:
		if AlreadyMarked(user,question.key) == False:
			return question.key.id()
	return False

def AlreadyMarked(user,question_key):
	query=AnsweredQuestion.query(ndb.AND(AnsweredQuestion.user==user,AnsweredQuestion.question==question_key,AnsweredQuestion.evaluation==True))
	if query.count()==1:	#the user has already answered the given question
		return True
	else:
		return False

def clearUserTestAnswers(user):
	delete_keys = AnsweredQuestion.query(ndb.AND(AnsweredQuestion.user==user,AnsweredQuestion.evaluation==True)).fetch(keys_only=True)
	ndb.delete_multi(delete_keys)
	return

def fetchLessDifficultQuestions(b):
	query=Question.query(Question.b<=b).order(-Question.b)
	return query.fetch()

def fetchLessDifficultQuestion(b,user):
	query=fetchLessDifficultQuestions(b)
	for question in query:
		if AlreadyMarked(user,question.key) == False:
			return question.key.id()
	return False

def isCorrectAnswer(a_id):
	query=Answer.query(Answer.key==ndb.Key('Answer',a_id))
	if query.count() == 1:
		return query.get().correct
	else:
		raise InvalidIdError(a_id)

def isPassedAnswer(a_id):
	query=Answer.query(Answer.key==ndb.Key('Answer',a_id))
	if query.count() == 1:
		if query.get().answer=='~pass~':
			return True
		else:
			return False
	else:
		raise InvalidIdError(a_id)
		
def update_or_Insert(user, currQuestion, questionNumber, timer, currentTheta, pastAnswer = 'correct'):
	query=globalInstances.query(globalInstances.examinee==user)
	
	if query.count()>=1:	# time for update
		for currentUser in query:
			currentUser.TotalQuestions=currQuestion
			currentUser.questionNumberToGive=questionNumber
			currentUser.questionTimerEnd=timer
			currentUser.theta=currentTheta
			currentUser.pastAnswer=pastAnswer
			currentUser.put()
	else:
		# Globals for the currentUser does not exist, so create a new one :)
		instance=globalInstances()
		instance.examinee=user
		instance.TotalQuestions=currQuestion
		instance.questionNumberToGive=questionNumber
		instance.questionTimerEnd=timer
		instance.theta=currentTheta
		instance.pastAnswer=pastAnswer
		instance.put()
	return

def fetchGlobal(user):
	#fetches all globals for the currentUser logged in/giving the test
	query=globalInstances.query(globalInstances.examinee==user)
	if query.count()==1:
		return query.get()
	else:
		return None
		
def insertQuestionAnswered(user,questionId,answerId,evaluation=False):
	aq=AnsweredQuestion()
	query=AnsweredQuestion.query(ndb.AND(AnsweredQuestion.user==user,AnsweredQuestion.question==questionId,AnsweredQuestion.evaluation==evaluation))
	if query.count()>=1:
		#this means that the user has already answered the question with questionID, stop hem
		return 'R' #for trying to 'R'eanswer
	else:
		#then a valid answer has been given for some question
		aq.user=user
		aq.question=questionId
		aq.answer=answerId
		aq.evaluation=evaluation
		try:
			#write it to DB
			aq.put() 
			return 'S'
		except TransactionFailedError: #some bug here
			return 'F'
	return
	
def update_or_Insert_QuestionTestModule(q_id_str,a_id_str,user,u):
	#StringProperty,StringProperty,UserProperty,dontcare
	question=None
	answer=None
	try:
		if a_id_str=='':
			answer=getPassedAnswer()
		else:
			answer=getAnswer(int(a_id_str))
		question=fetchQuestion(int(q_id_str))
	except InvalidIdError:
		raise
	return insertQuestionAnswered(user,question.key,answer.key,evaluation=True)
	
def fetchAllQuestionsParamsTestModule(user):
	query=AnsweredQuestion.query(ndb.AND(AnsweredQuestion.user==user,AnsweredQuestion.evaluation==True))
	params=[]
	#this variable limits the number of times this loop will execute, which is 10secs tops (minus the time required for executing the other commands).
	limiter=0
	while True:
		limiter=limiter+1
		if(limiter>1000):
			break
		if query.count()>=10:	#the user must answer atleast 2 questions :)
			for instance in query:
				currentQuestion=instance.question
				question=fetchQuestion(currentQuestion.id())
				a=1.0
				b=(question.b)
				c=(question.c)
				params.append(a)
				params.append(b)
				params.append(c)
				u=handlers.globals.incorrectAnswer
				if isPassedAnswer(instance.answer.id()):
					logging.info("pass answer here!")
					u=handlers.globals.passAnswer
				elif isCorrectAnswer(instance.answer.id()):
					#logging.info("%s|%s"%(instance.answer,getPassedAnswer().answer))
					u=handlers.globals.correctAnswer
				params.append(u)
			return params
		time.sleep(0.01)
	return params
	
def getSetting(prop_str):
	query=Setting.query(Setting.prop==prop_str)
	return query.get()

def updateOrInsertScores(user, upperBound=11, lowerBound=-1):
	query=ExamineeScores.query(ExamineeScores.examinee==user)
	
	if query.count()>=1:	# time for update
		for currentUser in query:
			if upperBound != 11:
				currentUser.upperBoundTheta=upperBound
			if lowerBound != -1:
				currentUser.lowerBoundTheta=lowerBound
			currentUser.put()
	else:
		# Scores for the currentUser does not exist, so create a new one :)
		instance=ExamineeScores()
		instance.examinee=user
		if upperBound == 11:
			instance.upperBoundTheta=0
		else:
			instance.upperBoundTheta=upperBound
		if lowerBound == -1:
			instance.lowerBoundTheta=0
		else:
			instance.lowerBoundTheta=lowerBound
		instance.put()
	return

def ScoresIsAcceptable(user):
	query=ExamineeScores.query(ExamineeScores.examinee==user)
	if query.count()>=1:	# time for update
		for currentUser in query:
			if identicalTo(currentUser.lowerBoundTheta,currentUser.upperBoundTheta,1.5):
				return True
			return False
	else:
		return False

def ReturnScores(user):
	query=ExamineeScores.query(ExamineeScores.examinee==user)
	if query.count()>=1:	# time for update
		for currentUser in query:
			str='The Score is [%s,%s]'%(currentUser.lowerBoundTheta,currentUser.upperBoundTheta)
			return str
		return 'Scores Not Found'
	else:
		return 'Scores Not Found'