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
	evaluation=ndb.BooleanProperty()
	#the user who answered
	user=ndb.UserProperty()
	question=ndb.KeyProperty(Question)
	#the answer the user gave
	answer=ndb.KeyProperty(Answer)
	#the time at which this was given
	time=ndb.DateTimeProperty(auto_now=True)

class EstimationCredentials(ndb.Model):
	user=ndb.UserProperty()
	estimatedTheta=ndb.FloatProperty()
	
class globalInstances(ndb.Model):
	examinee=ndb.UserProperty()
	#the present assessment of the ability of the candidate
	theta=ndb.FloatProperty()
	#first question wrong/right after all correct/incorrect; False=Not reached yet
	inflexion_1=ndb.BooleanProperty()
	#first question right/wrong after activating inflexion_1
	inflexion_2=ndb.BooleanProperty()
	isTestFinished=ndb.BooleanProperty()
	start=ndb.DateTimeProperty(auto_now_add=True)
	durationInSeconds=ndb.IntegerProperty()
	
class Setting(ndb.Model):
	prop=ndb.StringProperty()
	val=ndb.StringProperty()

