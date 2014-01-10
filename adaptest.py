#!/usr/bin/env python

import webapp2
import handlers.homehandler
import handlers.performancehandler
import handlers.answerquestion
import handlers.addquestion
import handlers.performestimation

######################
HomeHandler=handlers.homehandler.HomeHandler
PerformanceHandler=handlers.performancehandler.PerformanceHandler
AnswerQuestion=handlers.answerquestion.AnswerQuestion
AddQuestion=handlers.addquestion.AddQuestion
PerformEstimation=handlers.performestimation.PerformEstimation
######################

app=webapp2.WSGIApplication(
[('/',HomeHandler),
('/estim/admin/add',AddQuestion),
(r'/estim/admin/perform/(\S+)',PerformEstimation),
('/estim/admin/performance',PerformanceHandler),
(r'/estim/answer/(\S+)',AnswerQuestion),
],
debug=True
)
