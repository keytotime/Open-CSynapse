# Sam Callister April 23, 2016
# Used to Ensure GetData Points works correctly

# Add parent directory to python path to enable the running of single 
# Tests for this directory
import sys
sys.path.insert(0, '../')

import MachineLearning
from MachineLearning.GetDataPoints import getDataPoints
from MachineLearning.Clean import cleanData
from MachineLearning.BuildClassifier import getDiscreetClassifier
import MachineLearning.CrossValidate as CV
import unittest
import os
import json


class LoadFileTestCase(unittest.TestCase):
	def setUp(self):
		locationOfFile = os.path.dirname(__file__)
		if(locationOfFile != ''):
			locationOfFile += '/'
		locationOfFile +='irisData.txt'
		self.filename = locationOfFile


class DataPointsTest(LoadFileTestCase):
	def runTest(self):
		data = cleanData(self.filename)
		result = getDataPoints(data.data, data.target,2)
		self.assertTrue(len(result) > 0)
		jsonResult = json.dumps(result)
		reloaded = json.loads(jsonResult)
		self.assertTrue(len(reloaded) > 0)

if __name__ == '__main__':
    unittest.main()