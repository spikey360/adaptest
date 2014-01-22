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

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))

def evalFirstQuestion(u,timeLeft,c):
	#worst naive algo i could come up with in a jiffy to test the rest with summation 
	#ajust this tempTheta with the b value of the question and try and give one with b=~4-6
	tempTheta=2.5
	if(u==0):
		#time is not taken into consideration if answer is wrong
		tempTheta=tempTheta/2
	else:
		#time is considered a lot of question is passed, guessing is considered if timeTaken < 5sec
		#else only solve time is taken :)
		if math.fabs(0.33-u)<=0.01:
		#pass
			#best case 1.15x
			#worst case 1.05x
			tempTheta=tempTheta*( timeLeft/300+1.05)
		else:
		#correct
			if timeLeft>20:
				#best case 1.43
				#worst case 1.31
				tempTheta=tempTheta*(timeLeft*0.12/9+1.03)
			else:
				#best case 1.4
				#worst case 1.30
				tempTheta=tempTheta*(timeLeft/200+1.3)
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
		theta_S_1=getNewTheta(params,previousTheta)
		if math.fabs(theta_S_1-theta_S) <=0.2:
			break
		else:
			theta_S=theta_S_1
	return theta_S

def getNewTheta(params,theta_S):
	sumNumerator=0
	sumDenominator=0
	for x in range(0, int(len(params)/4)):
		P=float(calculateP(theta_S,params[x*4],params[x*4+1],params[x*4+2]))
		sumNumerator=sumNumerator-params[x*4]*(params[x*4+3]-P)
		sumDenominator=sumDenominator+(params[x*4]*params[x*4])*P*(1-P)
	theta_S1=theta_S+(sumNumerator/sumDenominator)
	return theta_S1


def getNextQuestion(self, timeAnswerWasPostedToServer, givenAnswerID, currentUser):
	#get the currentUser global instances
	currentUserGlobals=fetchGlobal(currentUser)
	#questionID=int(currentUserGlobals.questionNumberToGive)
	TotalQuestions=int(currentUserGlobals.TotalQuestions)
	TotalQuestions=TotalQuestions-1
	questionTimerEnd=int(float(currentUserGlobals.questionTimerEnd))
	timeRemaining=-int(float(timeAnswerWasPostedToServer))+questionTimerEnd
	#u is the score given to the user, 1 if the answer is correct , 0 if its incorrect and 0.33 if passed :)
	u=0.0
	if givenAnswerID == '':
		u=0.33
	else:
		CorrectAnswer=isCorrectAnswer(int(givenAnswerID))
		if CorrectAnswer:
			u=1.0
	update_or_Insert_QuestionTestModule(currentUserGlobals.questionNumberToGive,givenAnswerID,currentUser,u)
	if currentUserGlobals.questionNumberToGive == globals.firstQuestion:
		logging.info("tempTheta for first question")
		nextTheta=evalFirstQuestion(u,timeRemaining,0.25)
	else:
		logging.info("Not first question, so std. calc")
		nextTheta=evalNextQuestion(u,currentUser,float(currentUserGlobals.theta))
	
	logging.info('\nnextTheta=%s\n'%nextTheta)
	
	q=fetchMoreDifficultQuestion(nextTheta)
	
	logging.info('\nq=%s\n'%q)
	
	questionTimerEnd=round(time.time()+32.5)
	update_or_Insert(currentUser, str(TotalQuestions), str(q), str(questionTimerEnd),nextTheta)
	time.sleep(1)
	self.redirect("/test")
	#theta_S_1=theta_S
	#while True:
		#P=float(calculateP(theta_S,a,b,c))
		#P=getStLineP(theta_S,b,c)
		#logging.info('P=%s'%P)
		#original theta_S_1=theta_S+((-a*(u-P))/((a*a)*P*(1-P)))
		#if P==1:
		#	P=0.99
		#elif P==0:
		#	P=0.01
		#theta_S_1=theta_S+0.90*((-a*(u-P))/((a*a)*P*(1-P)))+0.10*float(timeRemaining)
		
		#http://en.wikipedia.org/wiki/Item_response_theory#cite_ref-19
		#dino=(a*a)*((P-c)*(P-c)*(1-P))/((1-c)*(1-c)*P)
		
		#theta_S_1=theta_S+(a*(u-P)/dino)
		#logging.info('%s theta_S[%s] theta_S1[%s]'%(k,theta_S,theta_S_1))
		#k=k+1
		#if math.fabs(theta_S_1-theta_S) <=10.1:
		#	break
		#else:
		#	theta_S=theta_S_1
		#	time.sleep(2)
	
	
	#time.sleep( 2 )
	#self.redirect("/test")
	return


class TestModule(webapp2.RequestHandler):
	def post(self):
		timeAnswerWasPosted=time.time()
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		getNextQuestion(self, timeAnswerWasPosted, self.request.get('option'), user)
		self.redirect("/test")
	def get(self):
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		currUser=fetchGlobal(user)
		questionNumberToGive=currUser.questionNumberToGive
		TotalQuestions=int(currUser.TotalQuestions)
		questionTimerEnd=currUser.questionTimerEnd
		if TotalQuestions>0:
			#get the question and the answer from the db here, according to the question id :)
			questionNumber=10-TotalQuestions
			question=fetchQuestion(int((questionNumberToGive)))
			answers=fetchAnswersOf(question)
			qNo=str(questionNumber+1)
			vals={'title':qNo,'endTime':questionTimerEnd,'question':question.question,'answers':answers,'questionID':questionNumberToGive,'current_user':user}
			template=jinjaEnv.get_template('testQuestion.html')
			self.response.out.write(template.render(vals))
		else:
			htmlSnippet='<form id="myForm" action="/" method="GET"><input type="submit" value="Goto Home"></form>'
			self.response.write("You Have finished giving the test, kindly press Take Test Button to redo the test!!!<br><br>%s"%htmlSnippet)
