#!/usr/bin/env python

from objects import *
from google.appengine.ext import ndb
import handlers.globals
#import handlers.computation
import logging

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
	faced_question_keys=AnsweredQuestion.query(ndb.AND(AnsweredQuestion.user==user,AnsweredQuestion.evaluation==True), projection=[AnsweredQuestion.question]).fetch() #FIXME pick up the questions themselves, instead of keys
	all_question_keys=Question.query().fetch()
	#not_faced_keys=[nf for nf in all_question_keys not in faced_question_keys]
	
	#faced_list=[]
	#for aq in faced:
	#	faced_list.append(Question.query(Question.key==aq.question))
	#faced_questions=set(faced_list)
	#all_questions=set(Question.query().fetch())
	#remaining_questions=all_questions.difference(faced_questions)
	#remaining=list(remaining_questions)
	#calculate item information for each of those questions, with theta from userState
	maxI=0
	maxQ=None
	for q in all_question_keys:
		if q not in faced_question_keys:
			question=Question.query(Question.key==q.key).get() #FIXME too many db reads
			i=handlers.computation.calculateItemInformation(question.a,question.b,question.c,userState.theta)
			if i> maxI:
				maxQ=question
	#sort descending, throw the first question
	if maxQ != None:
		return maxQ
	else:
		raise NoMoreQuestionError(userState.theta)

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
		instance.inflexion_1=False # first time
		instance.inflexion_2=False # neither of them are activated
		instance.isTestFinished=False
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

