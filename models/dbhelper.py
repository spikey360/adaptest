#!/usr/bin/env python

from models.objects import *
from google.appengine.ext import ndb

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

def fetchMoreDifficultQuestion(b):
	query=fetchMoreDifficultQuestions(b)
	for question in query:
		return question.key.id()
	return false

def fetchLessDifficultQuestions(b):
	query=Question.query(Question.b<=b)
	return query.fetch()

def isCorrectAnswer(a_id):
	query=Answer.query(Answer.key==ndb.Key('Answer',a_id))
	if query.count() == 1:
		return query.get().correct
	else:
		raise InvalidIdError(a_id)
		
def update_or_Insert(user, currQuestion, questionNumber, timer, currentTheta):
	query=globalInstances.query(globalInstances.examinee==user)
	
	if query.count()>=1:	# time for update
		for currentUser in query:
			currentUser.TotalQuestions=currQuestion
			currentUser.questionNumberToGive=questionNumber
			currentUser.questionTimerEnd=timer
			currentUser.theta=currentTheta
			currentUser.put()
	else:
		# Globals for the currentUser does not exist, so create a new one :)
		instance=globalInstances()
		instance.examinee=user
		instance.TotalQuestions=currQuestion
		instance.questionNumberToGive=questionNumber
		instance.questionTimerEnd=timer
		instance.theta=currentTheta
		instance.put()
	return

def fetchGlobal(user):
	#fetches all globals for the currentUser logged in/giving the test
	query=globalInstances.query(globalInstances.examinee==user)
	if query.count()==1:
		return query.get()
	else:
		raise InvalidIdError(q_id)
		
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
		question=fetchQuestion(int(q_id_str))
		answer=getAnswer(int(a_id_str))
	except InvalidIdError:
		raise
	return insertQuestionAnswered(user,question.key,answer.key,evaluation=True)
	
def fetchAllQuestionsParamsTestModule(user):
	#query=AnsweredQuestionTestModule.query(AnsweredQuestionTestModule.examinee==user)
	query=AnsweredQuestion.query(ndb.AND(AnsweredQuestion.user==user,AnsweredQuestion.evaluation==True))
	params=[]
	if query.count()>=2:	#the user must answer atleast 2 questions :)
		for instance in query:
			currentQuestion=instance.question
			question=fetchQuestion(int(currentQuestion))
			a=(question.a)
			b=(question.b)
			c=(question.c)
			params.append(a)
			params.append(b)
			params.append(c)
			params.append(instance.u)
	else:
		return false
	return params
