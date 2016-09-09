# Sam Callister April 18, 2016
# Used to Ensure BuildClassifier and CrossValidate are working

# Needed to be able to import modules from the parent directory
import sys
sys.path.insert(0, '../')
import MachineLearning
from MachineLearning.Clean import cleanData
from MachineLearning.BuildClassifier import getDiscreetClassifier
import MachineLearning.CrossValidate as CV
import unittest
from sklearn.datasets import load_iris

class IrisDataTestCase(unittest.TestCase):
	def setUp(self):
		self.data = load_iris()

class SvmTest(IrisDataTestCase):
	def runTest(self):
		svm = 'svm'
		svmC = getDiscreetClassifier(svm)
		meanScoreTimeTaken = CV.doShuffleCrossValidation(svmC, self.data.data, self.data.target)
		print('Svm result: ' + str(meanScoreTimeTaken.meanScore) + ' Time taken:' + str(meanScoreTimeTaken.timeTaken) + ' seconds')

class KNearestTest(IrisDataTestCase):
	def runTest(self):
		knearest = 'knearest'
		kC = getDiscreetClassifier(knearest)
		meanScoreTimeTaken = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
		print('knearest result: ' + str(meanScoreTimeTaken.meanScore) + ' Time taken:' + str(meanScoreTimeTaken.timeTaken) + ' seconds')

class GuassianTest(IrisDataTestCase):
	def runTest(self):
		gauss = 'guassNB'
		kC = getDiscreetClassifier(gauss)
		meanScoreTimeTaken = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
		print('Guassian Naive Bayes result: ' + str(meanScoreTimeTaken.meanScore) + ' Time taken:' + str(meanScoreTimeTaken.timeTaken) + ' seconds')

class SGDTest(IrisDataTestCase):
	def runTest(self):
		sgd = 'sgd'
		kC = getDiscreetClassifier(sgd)
		meanScoreTimeTaken = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
		print('SGD result: ' + str(meanScoreTimeTaken.meanScore) + ' Time taken:' + str(meanScoreTimeTaken.timeTaken) + ' seconds')

class AdaBoostTest(IrisDataTestCase):
	def runTest(self):
		adabost = 'adaBoost'
		kC = getDiscreetClassifier(adabost)
		meanScoreTimeTaken = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
		print('adabost result: ' + str(meanScoreTimeTaken.meanScore) + ' Time taken:' + str(meanScoreTimeTaken.timeTaken) + ' seconds')

class RandomForestTest(IrisDataTestCase):
	def runTest(self):
		rForest = 'randomForest'
		kC = getDiscreetClassifier(rForest)
		meanScoreTimeTaken = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
		print('Random Forest result: ' + str(meanScoreTimeTaken.meanScore) + ' Time taken:' + str(meanScoreTimeTaken.timeTaken) + ' seconds')

class PerceptronTest(IrisDataTestCase):
	def runTest(self):
		preceptron = 'perceptron'
		kC = getDiscreetClassifier(preceptron)
		meanScoreTimeTaken = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
		print('Perceptron result: ' + str(meanScoreTimeTaken.meanScore) + ' Time taken:' + str(meanScoreTimeTaken.timeTaken) + ' seconds')

class NearestCentroidTest(IrisDataTestCase):
	def runTest(self):
		nCentroid = 'nearestCentroid'
		kC = getDiscreetClassifier(nCentroid)
		meanScoreTimeTaken = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
		print('Nearest Centroid result: ' + str(meanScoreTimeTaken.meanScore) + ' Time taken:' + str(meanScoreTimeTaken.timeTaken) + ' seconds')

class PassiveAggressiveTest(IrisDataTestCase):
	def runTest(self):
		pa = 'passiveAggressive'
		kC = getDiscreetClassifier(pa)
		meanScoreTimeTaken = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
		print('Passive Aggressive result: ' + str(meanScoreTimeTaken.meanScore) + ' Time taken:' + str(meanScoreTimeTaken.timeTaken) + ' seconds')

class decisionTreeTest(IrisDataTestCase):
	def runTest(self):
		dt = 'decisionTree'
		kC = getDiscreetClassifier(dt)
		meanScoreTimeTaken = CV.doShuffleCrossValidation(kC, self.data.data, self.data.target)
		print('Decision Tree result: ' + str(meanScoreTimeTaken.meanScore) + ' Time taken:' + str(meanScoreTimeTaken.timeTaken) + ' seconds')

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