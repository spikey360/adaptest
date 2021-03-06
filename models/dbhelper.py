#!/usr/bin/env python

from objects import *
from google.appengine.ext import ndb
import handlers.globals
#import handlers.computation
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

class NoMoreQuestionError(Exception):
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
	#TODO: bounds on the maximum number of questions to fetch
	query=Question.query(Question.b>=b).order(Question.b)
	return query.fetch()

def fetchMoreDifficultQuestion(b,user):
	query=fetchMoreDifficultQuestions(b)
	for question in query:
		if AlreadyMarked(user,question.key) == False:
			return question
	raise NoMoreQuestionError(b)

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
	query=Question.query(Question.b<=b)
	return query.order(-Question.b).fetch()

def fetchLessDifficultQuestion(b,user):
	query=fetchLessDifficultQuestions(b)
	for question in query:
		if AlreadyMarked(user,question.key) == False:
			return question
	raise NoMoreQuestionError(b)

def fetchMostInformativeQuestion(userState,user):
	#return fetchMoreDifficultQuestion(5.0,user) #TODO implement this to find the question with maximum information
	#get all questions user has not answered yet
	faced_question_keys=AnsweredQuestion.query(ndb.AND(AnsweredQuestion.user==user,AnsweredQuestion.evaluation==True), projection=[AnsweredQuestion.question]).fetch()
	#pick only the questions, drop them into an array
	fqk=[]
	for m in faced_question_keys:
		fqk.append(m.question)
	all_question_keys=Question.query().fetch()
	#calculate item information for each of those questions, with theta from userState
	maxI=0
	maxQ=None
	for q in all_question_keys:
		if q.key not in fqk:
			question=Question.query(Question.key==q.key).get() #FIXME too many db reads
			i=handlers.computation.calculateItemInformation(question.a,question.b,question.c,userState.theta)
			if i> maxI:
				maxQ=question
				maxI=i
	#sort descending, throw the first question
	if maxQ != None:
		return maxQ
	else:
		raise NoMoreQuestionError(userState.theta)

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
		
def initiateUserState(user):
	query=globalInstances.query(globalInstances.examinee==user)
	if query.count()==0:
		# Globals for the currentUser does not exist, so create a new one :)
		instance=globalInstances()
		instance.examinee=user
		instance.theta=5.0
		instance.inflexion_1=False # first time
		instance.inflexion_2=False # neither of them are activated
		instance.isTestFinished=False
		instance.durationInSeconds=3600
		instance.put()
	return

def fetchGlobal(user):
	#fetches all globals for the user in, latest first
	query=globalInstances.query(globalInstances.examinee==user).order(globalInstances.start)
	if query.count()>=1:
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
	query=AnsweredQuestion.query(ndb.AND(AnsweredQuestion.user==user,AnsweredQuestion.evaluation==True)).order(AnsweredQuestion.time)
	params=[]
	if query.count()>=2:	#the user must answer atleast 2 questions :)
		for instance in query:
			currentQuestion=instance.question
			question=fetchQuestion(currentQuestion.id())
			a=(question.a)
			b=(question.b)
			c=(question.c)
			u=handlers.globals.incorrectAnswer
			if instance.answer==getPassedAnswer():
				u=handlers.globals.passAnswer
			elif isCorrectAnswer(instance.answer.id()):
				u=handlers.globals.correctAnswer
			params.append((a,b,c,u))
	else:

		return params
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

