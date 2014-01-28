#!/usr/bin/env python

from google.appengine.ext import ndb;
from google.appengine.ext import db;

class User(ndb.Model):
	user=ndb.UserProperty()
	uname=ndb.StringProperty()
	pwd=ndb.StringProperty()

class Question(ndb.Model):
	#the actual question in string
	question=ndb.StringProperty()
	#discrimination
	a=ndb.FloatProperty()
	#difficulty
	b=ndb.FloatProperty()
	#guessing
	c=ndb.FloatProperty()
	#posted by
	poster=ndb.UserProperty()
	#time
	time=ndb.DateTimeProperty(auto_now=True)

class Answer(ndb.Model):
	#reference
	question=ndb.KeyProperty(Question)
	#the actual answer in string
	answer=ndb.StringProperty()
	#correct or not
	correct=ndb.BooleanProperty()

class AnsweredQuestion(ndb.Model):
	#flag: true=Ability Evaluation answer, false=Parameter estimation Answer
	evaluation=ndb.BooleanProperty();
	#the user who answered
	user=ndb.UserProperty()
	question=ndb.KeyProperty(Question)
	#the answer the user gave
	answer=ndb.KeyProperty(Answer)
	#the time at which this was given
	time=ndb.DateTimeProperty(auto_now=True)

class Test(ndb.Model):
	user=ndb.KeyProperty(User)
	start=ndb.DateTimeProperty()
	durationLeftInSeconds=ndb.IntegerProperty()

class TestSheet(ndb.Model):
	test=ndb.KeyProperty(Test)
	question=ndb.KeyProperty(Question)
	answer=ndb.KeyProperty(Answer)
	
class EstimationCredentials(ndb.Model):
	user=ndb.UserProperty()
	estimatedTheta=ndb.FloatProperty()
	
class globalInstances(ndb.Model):
	examinee=ndb.UserProperty()
	TotalQuestions=ndb.StringProperty()
	#this question number will contain the id of the question to give so it is quite similar to number 
	questionNumberToGive=ndb.StringProperty()
	questionTimerEnd=ndb.StringProperty()
	theta=ndb.FloatProperty()

class Setting(ndb.Model):
	prop=ndb.StringProperty()
	val=ndb.StringProperty()
