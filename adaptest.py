#!/usr/bin/env python

import webapp2
import handlers.homehandler
import handlers.performancehandler
import handlers.answerquestion
import handlers.addquestion
import handlers.performestimation
import handlers.addestimationcredential
import handlers.computation
import handlers.parametercalculator
import handlers.testmodule
import handlers.addquestion2
import test.unittestinghandler

######################
HomeHandler=handlers.homehandler.HomeHandler
PerformanceHandler=handlers.performancehandler.PerformanceHandler
AnswerQuestion=handlers.answerquestion.AnswerQuestion
AddQuestion=handlers.addquestion.AddQuestion
PerformEstimation=handlers.performestimation.PerformEstimation
CredentialHandler=handlers.addestimationcredential.CredentialHandler
ModifyCredentialHandler=handlers.addestimationcredential.ModifyCredentialHandler
GetKhiHandler=handlers.computation.GetKhi
ParameterCalculatorHandler=handlers.parametercalculator.ParameterCalculatorHandler
ParameterCalculatorWorker=handlers.parametercalculator.ParameterCalculatorWorker
TestModule=handlers.testmodule.TestModule
UnitTestingHandler=test.unittestinghandler.UnitTestingHandler
MultiDummyQuestionInserver=handlers.addquestion2.AddQuestion2
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
('/estim/admin/calculateparams',ParameterCalculatorHandler),
('/estim/admin/tasks/calculateparams',ParameterCalculatorWorker),
('/test',TestModule),
('/unittest',UnitTestingHandler),
('/mInsert',MultiDummyQuestionInserver),
],
debug=True
)
