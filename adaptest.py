#!/usr/bin/env python

import webapp2
import handlers.homehandler
import handlers.performancehandler
import handlers.answerquestion
import handlers.addquestion
import handlers.performestimation
import handlers.addestimationcredential
import handlers.computation
import handlers.testmodule

######################
HomeHandler=handlers.homehandler.HomeHandler
PerformanceHandler=handlers.performancehandler.PerformanceHandler
AnswerQuestion=handlers.answerquestion.AnswerQuestion
AddQuestion=handlers.addquestion.AddQuestion
PerformEstimation=handlers.performestimation.PerformEstimation
CredentialHandler=handlers.addestimationcredential.CredentialHandler
ModifyCredentialHandler=handlers.addestimationcredential.ModifyCredentialHandler
GetKhiHandler=handlers.computation.GetKhi
TestModule=handlers.testmodule.TestModule
######################

app=webapp2.WSGIApplication(
[('/',HomeHandler),
('/estim/admin/add',AddQuestion),
(r'/estim/admin/perform/(\S+)',PerformEstimation),
('/estim/admin/performance',PerformanceHandler),
('/estim/admin/credentials',CredentialHandler),
(r'/estim/admin/credentials/(\S+)',ModifyCredentialHandler),
(r'/estim/admin/computation/getkhi/(\S+)',GetKhiHandler),
(r'/estim/answer/(\S+)',AnswerQuestion),
('/test',TestModule),
],
debug=True
)
