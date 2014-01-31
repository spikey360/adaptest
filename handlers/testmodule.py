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
from computation import calculateP

class InvalidTimeLeftError(Exception):
	def __init__(self,timeLeft):
		self.timeLeft=timeLeft
	def __str__(self):
		return str(self.timeLeft)


jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))

def evalFirstQuestion(u,timeLeft,c):
	#worst naive algo i could come up with in a jiffy to test the rest with summation 
	#ajust this tempTheta with the b value of the question and try and give one with b=~4-6
	if timeLeft<0 or timeLeft>30:
		raise InvalidTimeLeftError(timeLeft)
	tempTheta=2.5
	if(u==globals.incorrectAnswer):
		#time is not taken into consideration if answer is wrong
		tempTheta=tempTheta/2
	else:
		#time is considered a lot of question is passed, guessing is considered if timeTaken < 10 sec
		#else only solve time is taken :)
		if (u==globals.passAnswer):
		#pass
			#best case 1.15x
			#worst case 1.05x
			tempTheta=tempTheta*( timeLeft/300+1.05)
		else:
		#correct
			if timeLeft>=18:
				#best case 1.40
				#worst case 1.20
				tempTheta=tempTheta*(-timeLeft/60+1.7)
			else:
				#best case 1.40
				#worst case 1.20
				tempTheta=tempTheta*(timeLeft/90+1.2)
	#logging.info('tempTheta=%s'%tempTheta)
	return tempTheta

def evalNextQuestion(u,user,previousTheta):
	#part of the formula is taken from Pg 85 and part developed by me and used some part of st. line eqn
	#estimate the user's theta and get the next question based on this theta
	
	#very fancy way to do 'do-while' loop in python, but i dont complain if it gets the job done
	#get the question params
	params=fetchAllQuestionsParamsTestModule(user)
	theta_S=previousTheta
	while True:
		#time.sleep(1) #since db operations are going to happen its beneficial to give waste some time here #not worth it
		theta_S_1=getNewTheta(params,previousTheta)
		if math.fabs(theta_S_1-theta_S) <=0.2:
			break
		else:
			theta_S=theta_S_1
	return theta_S

def getNewTheta(params,theta_S):
	sumNumerator=0
	sumDenominator=0.00000001	#just incase the for loop does not get executed!

	for param in params:
		(a,b,c,u)=param
		P=float(calculateP(theta_S,a,b,c))
		Q=1-P
		sumNumerator=sumNumerator+a*(u-P)
		sumDenominator=sumDenominator+(a*a)*P*Q
	theta_S1=theta_S+(sumNumerator/sumDenominator)
	
	return theta_S1


def getNextQuestion(self, timeAnswerWasPostedToServer, givenAnswerID, currentUser):
	#get the currentUser global instances
	currentUserGlobals=fetchGlobal(currentUser)
	TotalQuestions=int(currentUserGlobals.TotalQuestions)
	TotalQuestions=TotalQuestions-1
	questionTimerEnd=int(float(currentUserGlobals.questionTimerEnd))
	timeRemaining=-int(float(timeAnswerWasPostedToServer))+questionTimerEnd
	#u is the score given to the user, 1 if the answer is correct , 0 if its incorrect and 0.33 if passed :)
	u=globals.incorrectAnswer
	if givenAnswerID == '':
		u=globals.passAnswer
	else:
		CorrectAnswer=isCorrectAnswer(int(givenAnswerID))
		if CorrectAnswer:
			u=globals.correctAnswer
	update_or_Insert_QuestionTestModule(currentUserGlobals.questionNumberToGive,givenAnswerID,currentUser,u)
	#if int(currentUserGlobals.TotalQuestions) == 10:
	#	logging.info('\ntempTheta for question: %s'%currentUserGlobals.TotalQuestions)
	#	nextTheta=evalFirstQuestion(u,timeRemaining,0.25)
	#else:
	#	logging.info('\nStd. Calculation for question: %s'%currentUserGlobals.TotalQuestions)
	#	nextTheta=evalNextQuestion(u,currentUser,float(currentUserGlobals.theta))
	#logging.info('\nnextTheta=%s\n'%nextTheta)
	#if nextTheta and current theta is same, terminate and display present theta as score
	###########################################################
	b=fetchQuestion(int(currentUserGlobals.questionNumberToGive)).b
	askTough=False
	#if last answer was correct and we have not hit inflexion_1, ask a tougher
	if u==globals.correctAnswer and currentUserGlobals.inflexion_1==False
		askTough=True
	#if last answer was incorrect and we have not hit inflexion_1, hit inflexion_1, ask an easier
	elif u==globals.incorrectAnswer or u==globals.passAnswer and currentUserGlobals.inflexion_1=False
		askTough=False
		currentUserGlobals.inflexion_1=True
	#if last answer was correct and we have hit inflexion_1, hit inflexion_2, prepare for maximum information question
	elif u==globals.correctAnswer and currentUserGlobals.inflexion_1=True
		currentUserGlobals.inflexion_2=True
	#if last answer was incorrect and we have hit inflexion_1, ask an easier
	elif u==globals.incorrectAnswer or u==globals.passAnswer and currentUserGlobals.inflexion_1=True
		currentUserGlobals.inflexion_2=True
	
	next=None
	#the algorithm should go like this
	#if correct answer, ask a tougher question
	if currentUserGlobals.inflexion_2:
		currentUserGlobals.questionNumberToGive=fetchMostInformative(b,user)
	elif askTough:
		difficult=fetchMoreDifficultQuestion(b,currentUser)
		#next=fetchQuestion(difficult) #TODO
		currentUserGlobals.questionNumberToGive=str(difficult)
	#if incorrect answer/pass, ask an easier question till you get a correct answer
	else:
		easier=fetchMoreDifficultQuestion(b,currentUser,easier=True)
		#next=fetchQuestion(difficult) #TODO
		currentUserGlobals.questionNumberToGive=str(easier)
	currentUserGlobals.put() #make the data persistent with a db write
	#as soon as we get the correct answer, calc theta using evalNextQuestion
	#then we keep giving those questions which give maxiumum information for the person
	#we continue giving until the 'confidence interval' is lower than a predef value
	
	if nextTheta <0 or nextTheta>10:
		vals={'message':'Your test has ended!<br>Result :<h1>Inconclusive</h1><br><br><form id="myForm" action="/" method="GET"><input type="submit" value="Goto Home"></form>'}
		templateMessage=jinjaEnv.get_template('message.html')
		self.response.out.write(templateMessage.render(vals))
		return
	time.sleep(1)
	q=fetchMoreDifficultQuestion(nextTheta,currentUser)
	logging.info('\nq=%s\n'%q)
	if q == False:
		vals={'message':'Sorry, Database is out of Questions!<br>Kindly press Take Test Button to redo the test!!!<br><br><form id="myForm" action="/" method="GET"><input type="submit" value="Goto Home"></form>'}
		templateMessage=jinjaEnv.get_template('message.html')
		self.response.out.write(templateMessage.render(vals))
	else:
		questionTimerEnd=round(time.time()+32.5)
		update_or_Insert(currentUser, str(TotalQuestions), str(q), str(questionTimerEnd),nextTheta)
		time.sleep(1.5)
		self.redirect("/test")
	return


class TestModule(webapp2.RequestHandler):
	def post(self):
		timeAnswerWasPosted=time.time()
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		getNextQuestion(self, timeAnswerWasPosted, self.request.get('option'), user)
	def get(self):
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		currUser=fetchGlobal(user)
		questionNumberToGive=currUser.questionNumberToGive
		TotalQuestions=int(currUser.TotalQuestions)
		questionTimerEnd=currUser.questionTimerEnd
		if TotalQuestions>0:
			questionNumber=10-TotalQuestions
			question=fetchQuestion(int((questionNumberToGive)))
			answers=fetchAnswersOf(question)
			qNo=str(questionNumber+1)
			vals={'title':qNo,'endTime':questionTimerEnd,'question':question.question,'answers':answers,'questionID':questionNumberToGive,'current_user':user}
			template=jinjaEnv.get_template('testQuestion.html')
			self.response.out.write(template.render(vals))
		else:
			vals={'message':'You Have finished giving the test.<br>Score :<h1>%s</h1><br>Press Take Test Button to redo the test!!!<br><br><form id="myForm" action="/" method="GET"><input type="submit" value="Goto Home"></form>'%(currUser.theta)}
			template=jinjaEnv.get_template('message.html')
			self.response.out.write(template.render(vals))
