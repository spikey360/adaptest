#!/usr/bin/env python

from models.objects import Question
from models.objects import Answer
from models.objects import globalInstances
from models.objects import AnsweredQuestion
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
	query=Question.query(Question.b>=b)
	return query.fetch()

def fetchLessDifficultQuestions(b):
	query=Question.query(Question.b<=b)
	return query.fetch()

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
		
def insertQuestionAnswered(user,questionId,answerId):
	aq=AnsweredQuestion()
	#get the id of the Answer which has been selected
	#query=AnsweredQuestion.query(ndb.AND(AnsweredQuestion.user==userId,AnsweredQuestion.key==ndb.Key('Answer',int(answerId))))
	query=AnsweredQuestion.query(ndb.AND(AnsweredQuestion.user==user,AnsweredQuestion.question==questionId))
	if query.count()>=1:
		#answer already given!
		#self.response.out.write("F")
		return 'R' #for trying to 'R'eanswer
	else:
		#then a valid answer has been given for some question
		aq.user=user
		aq.question=questionId
		aq.answer=answerId
		try:
			aq.put() #write it to DB
			#self.response.out.write("S") #write a flag indicating success
			return 'S'
		except TransactionFailedError: #some bug here
			#self.response.out.write("F")
			return 'F'
	return


