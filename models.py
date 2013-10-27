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
