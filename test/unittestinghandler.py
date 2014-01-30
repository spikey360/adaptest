import webapp2
import model_objects
import evaluation
import unittest

class UnitTestingHandler(webapp2.RequestHandler):
	def get(self):
		suite = unittest.TestLoader().loadTestsFromTestCase(model_objects.QuestionAnswerTest)
		self.response.out.write("Unit testing model_objects<br>")
		k=unittest.TextTestRunner(verbosity=3).run(suite)
		self.response.out.write("Failures : %d<br>Errors : %d"%(len(k.failures),len(k.errors)))
		suite = unittest.TestLoader().loadTestsFromTestCase(evaluation.EvaluationTest)
		self.response.out.write("<hr>")
		self.response.out.write("Unit testing evaluation<br>")
		k=unittest.TextTestRunner(verbosity=3).run(suite)
		self.response.out.write("Failures : %d<br>Errors : %d"%(len(k.failures),len(k.errors)))
