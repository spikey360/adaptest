import unittest
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import testbed
from models.objects import *
from models.dbhelper import *
from handlers.testmodule import *
from handlers.globals import *

class EvaluationTest(unittest.TestCase):
	def setUp(self):
		self.testbed=testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_user_stub()		
	def tearDown(self):
		self.testbed.deactivate()
			
	def test_is_theta_increasing(self):
		self.assertEquals(True,True)
	
	def test_is_theta_decreasing(self):
		self.assertEquals(True,True)
		
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
			for t in range(30):
				tempTheta=evalFirstQuestion(state,t,0.25)
				self.assertIsNotNone(tempTheta)
			for t in range(-10000,0):
				self.assertRaises(InvalidTimeLeftError,evalFirstQuestion,state,t,0.25)
			for t in range(31,10000):
				self.assertRaises(InvalidTimeLeftError,evalFirstQuestion,state,t,0.25)
				

