import webapp2
import model_objects
import unittest

class UnitTestingHandler(webapp2.RequestHandler):
	def get(self):
		suite = unittest.TestLoader().loadTestsFromTestCase(model_objects.QuestionAnswerTest)
		self.response.out.write("Unit testing<br>")
		k=unittest.TextTestRunner(verbosity=3).run(suite)
		self.response.out.write("Failures : %d<br>Errors : %d"%(len(k.failures),len(k.errors)))
