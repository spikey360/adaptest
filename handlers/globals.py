# a simple global file which can be used if/when required by importing :) 
# all the previous variables in this file has been deprecated!
from math import fabs

correctAnswer=1.0
incorrectAnswer=0.0
passAnswer=0.0

tougherQuestion=1000
easierQuestion=2000
maxInfoQuestion=3000

#first function in this accursed file :D
def identicalTo(numberA,numberB,marginOfError=0.01):
	if math.fabs(numberA-numberB) <= marginOfError:
		return True
	return False



