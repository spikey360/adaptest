import webapp2
import jinja2
import os
import math
from models.objects import Question
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

class GetKhi(webapp2.RequestHandler):
	def get(self,q_id):
		q_key=int(q_id)
		a=float(self.request.get('a'))
		b=float(self.request.get('b'))
		c=0.25 #will have to be made flexible
		query=Question.query(Question.key==ndb.Key('Question',q_key))
		if query.count() !=1:
			self.response.out.write("F")
			return
		(question,answers,correct_distribution,total_distribution)=DistributionAnalyzer().analyzeQuestion(q_key)
		khiSquare=0.0
		for (x,y) in correct_distribution.items():
			#x=theta, y=p(theta)
			khiSquare=khiSquare+calculateKhiTerm(total_distribution[x],x,y,a,b,c)
		self.response.out.write("%f"%khiSquare)
