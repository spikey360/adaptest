#!/usr/bin/env python

from models.objects import Question
from models.objects import Answer
from models.objects import globalInstances
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
	return None

def fetchLessDifficultQuestions(b):
	return None

def isCorrectAnswer(a_id):
	query=Answer.query(Answer.key==ndb.Key('Answer',a_id))
	if query.count() == 1:
		return query.get().correct
	else:
		raise InvalidIdError(a_id)
		
def update_or_Insert(userId, currQuestion, questionNumber, timer):
	query=globalInstances.query(globalInstances.examinee==userId)
	if query.count()>=1:	# time for update
		for currentUser in query:
			currentUser.TotalQuestions=currQuestion
			currentUser.questionNumberToGive=questionNumber
			currentUser.questionTimerEnd=timer
			currentUser.put()
	else:	# create a new one :)
		instance=globalInstances()
		instance.examinee=userId
		instance.TotalQuestions=currQuestion
		instance.questionNumberToGive=questionNumber
		instance.questionTimerEnd=timer
		instance.put()
	return

def fetchGlobal(userId):
	query=globalInstances.query(globalInstances.examinee==userId)
	if query.count()==1:
		return query.get()
	else:
		raise InvalidIdError(q_id)
