#!/usr/bin/env python

import webapp2
import jinja2
import os
import random
import cgi
import logging
import time

#at this point idk which i need 
from models.objects import Question
from models.objects import Answer
from models.objects import AnsweredQuestion
from models.objects import EstimationCredentials
from models.objects import globalInstances

from models.dbhelper import fetchGlobal
from models.dbhelper import update_or_Insert

from datetime import datetime
from google.appengine.api import users
from google.appengine.ext import db

jinjaEnv=jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname("views/")))

QUESTION_PAGE_HTML = """\
<html>
	<head>
		<title>Question Number - %s</title>
		<script>
		function clickOn30Sec()
		{
			//end epoch
			var endEpoch=%s;
			//current epoch
			
			// get tag element
			var countdown = document.getElementById('txt');
			// update the tag with id "txt" every 1 second
			setInterval(function() 
				{
				var currentEpoch=parseInt((new Date).getTime()/1000);
				var secondsLeft=endEpoch-currentEpoch;
				if(secondsLeft>=0)
					countdown.innerHTML = "Time Left : "+secondsLeft+"s";
				else
					document.getElementById('submitBtn').click();
				},1000);
		}
		</script>
	</head>
	<body onload="clickOn30Sec()">
		<form id="myForm" action="/test" method="post">
			<div>
				<h1> %s </h1>
				<input type="radio" name="option" value="1">%s<br>
				<input type="radio" name="option" value="2">%s<br>
				<input type="radio" name="option" value="3">%s<br>
				<input type="radio" name="option" value="4">%s<br>
				<input type="hidden" name="answer" value="%s"/>
			</div> 
			<br><br>
			<div id="txt"></div>
			<div>
				<input id="submitBtn" type="submit" value="Submit">
			</div>    
		</form>
	</body>
</html>
"""

class TestModule(webapp2.RequestHandler):
	def post(self):
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		
		currUser=fetchGlobal(user)
		questionNumberToGive=int(currUser.questionNumberToGive)
		TotalQuestions=int(currUser.TotalQuestions)
		TotalQuestions=TotalQuestions-1
		if self.request.get('option',"") is not "":
			if self.request.get('option') == self.request.get('answer'):
				questionNumberToGive=questionNumberToGive+5
			elif self.request.get('option') != self.request.get('answer'):
				questionNumberToGive=questionNumberToGive+1
		else:
			questionNumberToGive=questionNumberToGive+2
		
		questionTimerEnd=round(time.time()+30.5)
		update_or_Insert(user, str(TotalQuestions), str(questionNumberToGive), str(questionTimerEnd))
		time.sleep( 2 )
		self.redirect("/test")
	
	def get(self):
		user=users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		
		currUser=fetchGlobal(user)
		questionNumberToGive=int(currUser.questionNumberToGive)
		TotalQuestions=int(currUser.TotalQuestions)
		questionTimerEnd=currUser.questionTimerEnd
		if TotalQuestions>0:
			f = open('db.txt')
			lines = f.readlines()
			f.close()
			questionNumber=10-TotalQuestions
			question= lines[questionNumberToGive]
			vals=question.split(",")
			qNo=str(questionNumber+1)
			CorrectOption=str(int(float(vals[5])))
			self.response.write(QUESTION_PAGE_HTML % (qNo,questionTimerEnd,vals[0],vals[1],vals[2],vals[3],vals[4],CorrectOption))
		else:
			self.response.write("You Have finished giving the test, kindly press Take Test Button to redo the test!!!")
