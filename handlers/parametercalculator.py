import webapp2
import logging
import handlers.computation as computation
import models.dbhelper as dbhelper
from handlers.performestimation import DistributionAnalyzer
from models.dbhelper import InvalidIdError
from models.objects import Question
from google.appengine.api import taskqueue
from google.appengine.ext import ndb


class ParameterCalculatorHandler(webapp2.RequestHandler):
	def addTasks(self):
		all_questions=Question.query().fetch()
		for question in all_questions:
			taskqueue.add(queue_name='estimatorQueue',url='/estim/admin/tasks/calculateparams',params={'qid':str(question.key.id())})
		
	def get(self):
		self.addTasks()
		self.response.out.write("Added tasks to queue")
	def post(self):
		self.addTasks()
		self.response.out.write("Added task to queue")

class ParameterCalculatorWorker(webapp2.RequestHandler):
	def post(self):
		q_id=self.request.get('qid')
		q_key=int(q_id)
		computation.question=None
		try:
			computation.question=dbhelper.fetchQuestion(q_key)
		except InvalidIdError:
			logging.info("Invalid question %s"%q_id)
			return
		(computation.answers,computation.correct_distribution,computation.total_distribution)=DistributionAnalyzer().analyzeQuestion(computation.question)
		def worker():
			logging.info("Started parameter calculator task for %s"%q_id)
			calc_a=calc_b=calc_c=0.0
			(calc_a,calc_b,calc_c)=computation.calculateParameters()
			computation.question.a=calc_a
			computation.question.b=calc_b
			computation.question.c=calc_c
			computation.question.put()
		ndb.transaction(worker)

