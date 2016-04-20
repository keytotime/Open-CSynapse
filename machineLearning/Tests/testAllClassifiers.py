# Sam Callister April 18, 2016
# Used to Ensure BuildClassifier and CrossValidate are working

# Needed to be able to import modules from the parent directory
import sys
sys.path.insert(0,'..')

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

class GuassianTest(IrisDataTestCase):
	def runTest(self):
		gauss = 'guassNB'
		kC = getDiscreetClassifier(gauss)
		result = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
		print('Guassian Naive Bayes result: ' + str(result))

class SGDTest(IrisDataTestCase):
	def runTest(self):
		sgd = 'sgd'
		kC = getDiscreetClassifier(sgd)
		result = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
		print('SGD result: ' + str(result))

class AdaBoostTest(IrisDataTestCase):
	def runTest(self):
		adabost = 'adaBoost'
		kC = getDiscreetClassifier(adabost)
		result = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
		print('adabost result: ' + str(result))

# class NeuralNetTest(IrisDataTestCase):
# 	def runTest(self):
# 		net = 'neuralNet'
# 		kC = getDiscreetClassifier(net)
# 		result = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
# 		print('neural net result: ' + str(result))


class BogusClassifierTest(IrisDataTestCase):
	def runTest(self):
		with self.assertRaises(ValueError):
			getDiscreetClassifier('blksci')

if __name__ == '__main__':
    unittest.main()