import webapp2
import jinja2
import os
import math
import models.dbhelper as dbhelper
from models.objects import Question
from models.dbhelper import InvalidIdError
from handlers.performestimation import DistributionAnalyzer
from google.appengine.ext import ndb

def calculateP(theta,a,b,c):
	k=-a*(theta-b)
	P=c+(1.0-c)/(1.0+math.exp(k))
	return P

def calculateKhiTerm(totalAttemptees,theta,observedP,a,b,c):
	P=calculateP(theta,a,b,c)
	Q=1.0-P
	khi=totalAttemptees*math.pow((observedP-P),2)/(P*Q)
	return khi

def calculateKhiSquare(q_key,a,b,c):
	question=None
	try:
		question=dbhelper.fetchQuestion(q_key)
	except InvalidIdError:
		raise
	(answers,correct_distribution,total_distribution)=DistributionAnalyzer().analyzeQuestion(question)
	khiSquare=0.0
	for (x,y) in correct_distribution.items():
		#x=theta, y=p(theta)
		khiSquare=khiSquare+calculateKhiTerm(total_distribution[x],x,y,a,b,c)
	return khiSquare

class GetKhi(webapp2.RequestHandler):
	def get(self,q_id):
		q_key=int(q_id)
		a=float(self.request.get('a'))
		b=float(self.request.get('b'))
		c=0.25 #will have to be made flexible
		ks=0.0
		try:
			ks=calculateKhiSquare(int(q_id),a,b,c)
		except InvalidIdError:
			self.response.out.write("F") #a 404 page should not be given here
		self.response.out.write("%f"%ks)
