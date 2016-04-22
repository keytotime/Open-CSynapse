# Sam Callister April 18, 2016
# Used to Ensure Clean is working and it can feed data into a classifier

# Needed to be able to import modules from the parent directory
import os


import MachineLearning
from MachineLearning.Clean import cleanData
from MachineLearning.BuildClassifier import getDiscreetClassifier
import MachineLearning.CrossValidate as CV
import unittest


class LoadFileTestCase(unittest.TestCase):
	def setUp(self):
		locationOfFile = os.path.dirname(__file__) + '/irisData.txt'
		self.filename = locationOfFile


class CleanTest(LoadFileTestCase):
	def runTest(self):
		data = cleanData(self.filename)
		knearest = getDiscreetClassifier('knearest')
		result = CV.doShuffleCrossValidation(knearest, data.data, data.target)
		print('knearest result: ' + str(result))


if __name__ == '__main__':
    unittest.main()