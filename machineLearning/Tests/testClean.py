# Sam Callister April 18, 2016
# Used to Ensure Clean is working and it can feed data into a classifier

# Needed to be able to import modules from the parent directory
import sys
sys.path.insert(0,'..')

from Clean import cleanData
from BuildClassifier import getDiscreetClassifier
import CrossValidate as CV

import unittest


class LoadFileTestCase(unittest.TestCase):
	def setUp(self):
		self.filename = 'irisData.txt'

class CleanTest(LoadFileTestCase):
	def runTest(self):
		data = cleanData(self.filename)
		knearest = getDiscreetClassifier('knearest')
		result = CV.doShuffleCrossValidation(knearest, data.data, data.target)
		print('knearest result: ' + str(result))


if __name__ == '__main__':
    unittest.main()