# Sam Callister April 18, 2016
# Used to Ensure Clean is working and it can feed data into a classifier

# Add parent directory to python path to enable the running of single 
# Tests for this directory
import sys
sys.path.insert(0,'..')
import os
import MachineLearning
from MachineLearning.Clean import cleanData
from MachineLearning.BuildClassifier import getDiscreetClassifier
import MachineLearning.CrossValidate as CV
import unittest


class LoadFileTestCase(unittest.TestCase):
	def setUp(self):
		locationOfFile = os.path.dirname(__file__)
		if(locationOfFile != ''):
			locationOfFile += '/'
		locationOfFile +='irisData.txt'
		self.filename = locationOfFile


class CleanTest(LoadFileTestCase):
	def runTest(self):
		data = cleanData(self.filename)
		knearest = getDiscreetClassifier('knearest')
		resultTime = CV.doShuffleCrossValidation(knearest, data.data, data.target)
		print('knearest result: ' + str(resultTime.meanScore) + ' Time taken: ' + str(resultTime.timeTaken))
		self.assertTrue(resultTime.timeTaken > 0)

if __name__ == '__main__':
    unittest.main()