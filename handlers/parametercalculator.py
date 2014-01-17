import webapp2
import logging
import handlers.computation as computation
import models.dbhelper as dbhelper
from models.dbhelper import InvalidIdError
from google.appengine.api import taskqueue
from google.appengine.ext import ndb


class ParameterCalculatorHandler(webapp2.RequestHandler):
	def get(self):
		#self.response.out.write("POST with qid to start task")
		q_id=self.request.get('qid')
		taskqueue.add(url='/estim/admin/tasks/calculateparams',params={'qid':q_id})
		self.response.out.write("Added task to queue")
	def post(self):
		q_id=self.request.get('qid')
		taskqueue.add(url='/estim/admin/tasks/calculateparams',params={'qid':q_id})
		self.response.out.write("Added task to queue")

class ParameterCalculatorWorker(webapp2.RequestHandler):
	def post(self):
		q_id=self.request.get('qid')
		q_key=int(q_id)
		question=None
		try:
			question=dbhelper.fetchQuestion(q_key)
		except InvalidIdError:
			logging.info("Invalid question %s"%q_id)
			return
		def worker():
			logging.info("Started parameter calculator task for %s"%q_id)
			calc_a=calc_b=calc_c=0.0
			(calc_a,calc_b,calc_c)=computation.calculateParameters()
			question.a=calc_a
			question.b=calc_b
			question.c=calc_c
			question.put()
		ndb.transaction(worker)

