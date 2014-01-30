import unittest
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import testbed
from models.objects import *
from models.dbhelper import *

class QuestionAnswerTest(unittest.TestCase):
	def setUp(self):
		self.testbed=testbed.Testbed()
		self.testbed.activate()
		self.testbed.init_datastore_v3_stub()
		self.testbed.init_user_stub()
	def tearDown(self):
		self.testbed.deactivate()
	
	def test_insertQuestion(self):
		question=Question()
		question.question="Hello World"
		question.a=1.0
		question.b=5.0
		question.c=0.25
		poster=users.get_current_user()
		question.put()
		
		self.assertEqual(1,len(Question.query().fetch()))

	def test_fetchQuestion(self):
		question=Question()
		question.question="Hello World"
		question.a=1.0
		question.b=5.0
		question.c=0.25
		poster=users.get_current_user()
		question.put()
		
		q=fetchQuestion(question.key.id())
		self.assertEqual(question,q)
		
		self.assertRaises(InvalidIdError,fetchQuestion,123)
	
	def test_fetchAnswers(self):
		question=Question()
		question.question="Hello World"
		question.a=1.0
		question.b=5.0
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
		a4.correct=True
		a1.correct=a2.correct=a3.correct=False
		a1.put()
		a2.put()
		a3.put()
		a_key=a4.put()
		a4_ret=getAnswer(a_key.id())
		self.assertEqual(a4,a4_ret)
		answers_ret=fetchAnswers(q_key.id())
		self.assertEqual(4,len(answers_ret))
		self.assertEqual(4,len(fetchAnswersOf(question)))
		self.assertEqual(a3,getAnswer(a3.key.id()))
		self.assertEqual(True,isCorrectAnswer(a_key.id()))
		self.assertEqual(False,isCorrectAnswer(a2.key.id()))
		self.assertRaises(InvalidIdError,getAnswer,123)
		self.assertRaises(InvalidIdError,fetchAnswers,123)
	
	def test_global(self):
		user=users.get_current_user()
		gi=globalInstances()
		gi.examinee=user
		gi.TotalQuestions="Random string"
		gi.questionNumberToGive="Random String 2"
		gi.questionTimerEnd="Random String 3"
		gi.theta=3.141592653
		gi.put()
		self.assertEquals(gi,fetchGlobal(user))
		self.assertIsNone(fetchGlobal(None))
	
	def test_answeredQuestion(self):
		question=Question()
		question.question="Hello World"
		question.a=1.0
		question.b=5.0
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
		a4.correct=True
		a1.correct=a2.correct=a3.correct=False
		a1.put()
		a2.put()
		a3.put()
		a_key=a4.put()
		########################
		user=users.get_current_user()
		ret=insertQuestionAnswered(user,q_key,a_key)
		self.assertEquals('S',ret)
		ret=insertQuestionAnswered(user,q_key,a_key)
		self.assertEquals('R',ret)
		query=AnsweredQuestion.query().fetch()
		self.assertEquals(1,len(query))
		ret=update_or_Insert_QuestionTestModule(str(q_key.id()),str(a_key.id()),user,1.0)
		self.assertEquals('S',ret)
		update_or_Insert_QuestionTestModule(str(q_key.id()),str(a_key.id()),user,1.0)
		query=AnsweredQuestion.query().fetch()
		self.assertEquals(2,len(query))
		ret=fetchAllQuestionsParamsTestModule(user)
		self.assertEquals(0,len(ret)) #count<2
		self.assertTrue(AlreadyMarked(user,q_key))
		clearUserTestAnswers(user)
		self.assertFalse(AlreadyMarked(user,q_key))

