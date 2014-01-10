#!/usr/bin/env python

import webapp2
import jinja2
import os

import handlers.homehandler
import handlers.performancehandler
import handlers.answerquestion
import handlers.addquestion
import handlers.addestimationcredential
import handlers.performestimation

from models import User
from models import Question
from models import Answer
from models import AnsweredQuestion
from models import EstimationCredentials

from google.appengine.ext import ndb
from google.appengine.api import users

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))



######################
HomeHandler=handlers.homehandler.HomeHandler
PerformanceHandler=handlers.performancehandler.PerformanceHandler
AnswerQuestion=handlers.answerquestion.AnswerQuestion
AddQuestion=handlers.addquestion.AddQuestion
AddEstimationCredential=handlers.addestimationcredential.AddEstimationCredential
PerformEstimation=handlers.performestimation.PerformEstimation
######################

app=webapp2.WSGIApplication(
[('/',HomeHandler),
('/estim/admin/add',AddQuestion),
#('/estim/adduser',AddEstimationCredential), #not needed from user side
(r'/estim/admin/perform/(\S+)',PerformEstimation),
('/estim/admin/performance',PerformanceHandler),
(r'/estim/answer/(\S+)',AnswerQuestion),
],
debug=True
)
