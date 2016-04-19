# Sam Callister April 18, 2016
# Used to Ensure BuildClassifier and CrossValidate are working

from sklearn.datasets import load_iris
from BuildClassifier import getDiscreetClassifier
import CrossValidate as CV

import unittest


class IrisDataTestCase(unittest.TestCase):
	def setUp(self):
		self.data = load_iris()

class SvmTest(IrisDataTestCase):
	def runTest(self):
		svm = 'svm'
		svmC = getDiscreetClassifier(svm)
		result = CV.doShuffleCrossValidation(svmC, self.data.data, self.data.target)
		print('Svm result: ' + str(result))

class KNearestTest(IrisDataTestCase):
	def runTest(self):
		knearest = 'knearest'
		kC = getDiscreetClassifier(knearest)
		result = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
		print('knearest result: ' + str(result))

class BogusClassifierTest(IrisDataTestCase):
	def runTest(self):
		with self.assertRaises(ValueError):
			getDiscreetClassifier('blksci')

if __name__ == '__main__':
    unittest.main()