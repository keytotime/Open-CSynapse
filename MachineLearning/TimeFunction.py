# Sam Callister April 18, 2016
# Used to time the given function

from collections import namedtuple

from time import clock
# Takes a function which must come with all necessary arguments such that 
# it can be called f(). Times the function and returns the time taken to call
# the function.
def timeFunction(f):
	initial = clock()
	returnValue = f()
	final = clock()
	timeTaken = final - initial
	# Tuple mapping for returning function result and timetaken
	TimedResult = namedtuple('TimedResult','result,timeTaken')
	return TimedResult(returnValue, timeTaken)