import sys
sys.path.insert(0, '../')
from MachineLearning import TrainClassifier
from MachineLearning.Clean import cleanData
from MachineLearning.BuildClassifier import getDiscreetClassifier
from MachineLearning.ClassifyData import predict
import MachineLearning.CrossValidate as CV
from sklearn.datasets import load_iris
import unittest

class IrisDataTestCase(unittest.TestCase):
	def setUp(self):
		self.data = load_iris()

class TestPredict(IrisDataTestCase):
	def runTest(self):
		svm = 'svm'
		svmC = getDiscreetClassifier(svm)
		meanScore = CV.doShuffleCrossValidation(svmC, self.data.data, self.data.target).meanScore
		trained = TrainClassifier.trainWithLabels(getDiscreetClassifier(svm),self.data.data, self.data.target)
		predictions = predict(trained, self.data.data)
		# Ensure the score after from predicting is close to the cross validation score
		correct = 0
		for x in range(len(predictions)):
			if(predictions[x][0] == self.data.target[x]):
				correct += 1
		newScore = float(correct) / len(self.data.target)
		result = abs(meanScore - newScore)
		self.assertTrue(result < .05)