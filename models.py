#!/usr/bin/env python

from google.appengine.ext import ndb;

class Question(ndb.Model):
	#the actual question in string
	question=ndb.StringProperty()
	#difficulty
	a=ndb.FloatProperty()
	#discrimination
	b=ndb.FloatProperty()
	#guessing
	c=ndb.FloatProperty()
	#posted by
	poster=ndb.KeyProperty(User)
	#time
	time=ndb.DateTimeProperty(auto_now=True)

class Answer(ndb.Model):
	#reference
	question=ndb.KeyProperty(Question)
	#the actual answer in string
	answer=ndb.StringProperty()
	#correct or not
	correct=ndb.BooleanProperty()

class User(ndb.Model):
	user=ndb.UserProperty()
	uname=ndb.StringProperty()
	pwd=ndb.StringProperty()

class Test(ndb.Model):
	user=ndb.KeyProperty(User)
	start=ndb.DateTimeProperty()
	durationLeftInSeconds=ndb.IntegerProperty()

class TestSheet(ndb.Model):
	test=ndb.KeyProperty(Test)
	question=ndb.KeyProperty(Question)
	answer=ndb.KeyProperty(Answer)
	
class Credentials(ndb.Model):
	user=ndb.KeyProperty(User)
	estimatedTheta=ndb.FloatProperty()
