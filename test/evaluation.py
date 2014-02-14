import unittest
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import testbed
from models.objects import *
from models.dbhelper import *
from handlers.testmodule import *
from handlers.globals import *

def generate_AnsweredQuestion(thetaNow,user,correct=True,gradient=0.2):
	u=correctAnswer
	#generating a question with a greater than known b
	question=Question()
	question.question="Hello World"
	question.a=1.0
	if correct:
		question.b=thetaNow+gradient
	else:
		question.b=thetaNow-gradient
	question.c=0.25
	poster=users.get_current_user()
	q_key=question.put()
	a1=Answer()
	a2=Answer()
	a3=Answer()
	a4=Answer()
	a1.question=a2.question=a3.question=a4.question=q_key
	a1.answer="a1"
	a2.answer="a2"
	a3.answer="a3"
	a4.answer="a4"
	#all answers initially incorrect
	a1.correct=a2.correct=a3.correct=a4.correct=False
	if correct:
		#last one is correct, user always chooses last one
		a4.correct=True
	else:
		#first one is correct, user always chooses last one, AnsweredQuestion is thus incorrect
		a1.correct=True
		u=incorrectAnswer
	a1.put()
	a2.put()
	a3.put()
	a_key=a4.put()
	update_or_Insert_QuestionTestModule(str(q_key.id()),str(a_key.id()),user,u)

class EvaluationTest(unittest.TestCase):
	def setUp(self):
		self.testbed=testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_user_stub()		
	def tearDown(self):
		self.testbed.deactivate()
			
	def test_is_theta_increasing(self):
		states=[correctAnswer]
		user=users.get_current_user()
		for state in states:
			thetaNow=evalFirstQuestion(state,15,0.25)
			while thetaNow<=10.0:
				#insert a correct AnsweredQuestion in user's name
				generate_AnsweredQuestion(thetaNow,user,correct=True)
				###
				nextTheta=evalNextQuestion(state,user,thetaNow)
				self.assertGreaterEqual(nextTheta,thetaNow)
				thetaNow=nextTheta
				
				
	
	def test_is_theta_decreasing(self):
		states=[incorrectAnswer]
		user=users.get_current_user()
		for state in states:
			thetaNow=evalFirstQuestion(state,15,0.25)
			while thetaNow>=0.0:
				#insert a correct AnsweredQuestion in user's name
				generate_AnsweredQuestion(thetaNow,user,correct=False)
				###
				nextTheta=evalNextQuestion(state,user,thetaNow)
				self.assertLessEqual(nextTheta,thetaNow)
				thetaNow=nextTheta
		
	def test_is_honouring_limits(self):
		states={incorrectAnswer,correctAnswer,passAnswer}
		for state in states:
			for t in range(30):
				tempTheta=evalFirstQuestion(state,t,0.25)
				self.assertLessEqual(tempTheta,10.0)
				self.assertGreaterEqual(tempTheta,0.0)
		
	def test_is_honouring_time(self):
		states={incorrectAnswer,correctAnswer,passAnswer}
		for state in states:
			for t in range(31):
				tempTheta=evalFirstQuestion(state,t,0.25)
				self.assertIsNotNone(tempTheta)
			for t in range(-10000,0):
				self.assertRaises(InvalidTimeLeftError,evalFirstQuestion,state,t,0.25)
			for t in range(31,10000):
				self.assertRaises(InvalidTimeLeftError,evalFirstQuestion,state,t,0.25)
	
	def test_nature_of_next_question(self):
		inflexion_1=False
		inflexion_2=False
		lastCorrect=True
		#2 correct
		(nature,inflexion_1,inflexion_2)=calculateNatureOfNextQuestion(lastCorrect,inflexion_1,inflexion_2)
		self.assertEquals(tougherQuestion,nature)
		(nature,inflexion_1,inflexion_2)=calculateNatureOfNextQuestion(lastCorrect,inflexion_1,inflexion_2)
		self.assertEquals(tougherQuestion,nature)
		#1 wrong
		lastCorrect=False
		(nature,inflexion_1,inflexion_2)=calculateNatureOfNextQuestion(lastCorrect,inflexion_1,inflexion_2)
		self.assertEquals(easierQuestion,nature)
		#1 correct
		lastCorrect=True
		(nature,inflexion_1,inflexion_2)=calculateNatureOfNextQuestion(lastCorrect,inflexion_1,inflexion_2)
		self.assertEquals(maxInfoQuestion,nature)
		#is maxInfoQuestion
		
		inflexion_1=False
		inflexion_2=False
		lastCorrect=False
		
		#3 wrong
		(nature,inflexion_1,inflexion_2)=calculateNatureOfNextQuestion(lastCorrect,inflexion_1,inflexion_2)
		self.assertEquals(easierQuestion,nature)
		(nature,inflexion_1,inflexion_2)=calculateNatureOfNextQuestion(lastCorrect,inflexion_1,inflexion_2)
		self.assertEquals(easierQuestion,nature)
		(nature,inflexion_1,inflexion_2)=calculateNatureOfNextQuestion(lastCorrect,inflexion_1,inflexion_2)
		self.assertEquals(easierQuestion,nature)
		#2 correct
		lastCorrect=True
		(nature,inflexion_1,inflexion_2)=calculateNatureOfNextQuestion(lastCorrect,inflexion_1,inflexion_2)
		self.assertEquals(tougherQuestion,nature)
		(nature,inflexion_1,inflexion_2)=calculateNatureOfNextQuestion(lastCorrect,inflexion_1,inflexion_2)
		self.assertEquals(tougherQuestion,nature)
		#1 wrong
		lastCorrect=False
		(nature,inflexion_1,inflexion_2)=calculateNatureOfNextQuestion(lastCorrect,inflexion_1,inflexion_2)
		self.assertEquals(maxInfoQuestion,nature)
				

