import webapp2
import jinja2
import os
import math
import models.dbhelper as dbhelper
from models.objects import Question
from models.dbhelper import InvalidIdError
from handlers.performestimation import DistributionAnalyzer
from google.appengine.ext import ndb
import logging

answers=None
correct_distribution=None
total_distribution=None
question=None

start_a=0.0
end_a=1.0
start_b=0.0
end_b=10.0
#interval periods, increases/decreases precision of calculation
interval_a=0.1
interval_b=0.1

def calculateP(theta,a,b,c):
	k=-a*(theta-b)
	#logging.info('k=%s'%k)
	P=c+(1.0-c)/(1.0+math.exp(k))
	return P

def calculateKhiTerm(totalAttemptees,theta,observedP,a,b,c):
	P=calculateP(theta,a,b,c)
	Q=1.0-P
	khi=totalAttemptees*math.pow((observedP-P),2)/(P*Q)
	return khi

def calculateKhiSquare(a,b,c):
	
	khiSquare=0.0
	for (x,y) in correct_distribution.items():
		#x=theta, y=p(theta)
		khiSquare=khiSquare+calculateKhiTerm(total_distribution[x],x,y,a,b,c)
	return khiSquare

def calculateParameters():
	global start_a, end_a, start_b, end_b, interval_a, interval_b
	min_a=start_a
	min_b=start_b
	a=start_a
	b=start_b
	c=0.25
	min_yet=math.sqrt(calculateKhiSquare(a,b,c))
	steps_a=(end_a-start_a)/interval_a
	steps_b=(end_b-start_b)/interval_b
	for i in range(int(steps_a)):
		b=0.0
		for j in range(int(steps_b)):
			khi=math.sqrt(calculateKhiSquare(a,b,c))
			if khi<min_yet:
				min_yet=khi
				min_a=a
				min_b=b
			b+=interval_b
		a+=interval_a
	return (min_a,min_b,c)

class GetKhi(webapp2.RequestHandler):
	def get(self,q_id):
		global answers,correct_distribution,total_distribution
		q_key=int(q_id)
		c=0.25 #will have to be made flexible
		calc_a=calc_b=calc_c=0.0
		try:
			question=dbhelper.fetchQuestion(q_key)
			(answers,correct_distribution,total_distribution)=DistributionAnalyzer().analyzeQuestion(question)
			(calc_a,calc_b,calc_c)=calculateParameters()
			question.a=calc_a
			question.b=calc_b
			question.c=calc_c
		except InvalidIdError:
			self.response.out.write("F") #a 404 page should not be given here
			return
		if question is not None:
			question.put()
		self.response.out.write("%f,%f,%f"%(calc_a,calc_b,calc_c))

def calculateItemInformation(a,b,c,theta):
	p=calculateP(theta,a,b,c)
	q=1.0-p
	z=p-c
	m=1.0-c
	#if m == 0:
	#	print ">>>>>>>>>>",a,b,c,theta
	i=a*a*z*z*q/(m*m*p)
	return i

def calculateMLE(presentTheta,user):
	#Maximum Likelihood Estimation
	precision=0.1
	#iterate as many times unless theta_cap becomes less than or equal to precision
	allFaced=dbhelper.fetchAllQuestionsParamsTestModule(user)
	theta_cap=presentTheta
	se_now=0.0
	while True:
		num=0
		denom=0
		for (a,b,c,u) in allFaced:
			print ">>>>",theta_cap,a,b,c
			p=calculateP(theta_cap,a,b,c)
			#q=1.0-p
			num+=(a)*(u-p)
			denom+=calculateItemInformation(a,b,c,theta_cap)
		print ">>",num,denom
		del_theta=num/denom
		print ">",del_theta
		theta_cap+=del_theta
		se_now=1/math.sqrt(denom)
		#if se_now>se:
		#	#increasing se, divergent, exit
		#	print "SE:",se
		#	break
		#else:
		#	se=se_now
		if del_theta<=precision:
			print "SE:",se_now
			break
	return (theta_cap,se_now)


