# Sam Callister April 23, 2016
# Used to Ensure GetData Points works correctly

import MachineLearning
from MachineLearning.GetDataPoints import get2DPoints
from MachineLearning.Clean import cleanData
from MachineLearning.BuildClassifier import getDiscreetClassifier
import MachineLearning.CrossValidate as CV
import unittest
import os

class LoadFileTestCase(unittest.TestCase):
	def setUp(self):
		locationOfFile = os.path.dirname(__file__) + '/irisData.txt'
		self.filename = locationOfFile


class DataPointsTest(LoadFileTestCase):
	def runTest(self):
		data = cleanData(self.filename)
		result = get2DPoints(data.data, data.target)
		self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main()