import sys
sys.path.insert(0, '../')

from MachineLearning import TrainClassifier
from MachineLearning.Clean import cleanData
from MachineLearning.BuildClassifier import getDiscreetClassifier
import MachineLearning.CrossValidate as CV
import unittest
from sklearn.datasets import load_iris
from MachineLearning.PersistClassifier import saveClassifierAsString, loadClassifierFromString

class IrisDataTestCase(unittest.TestCase):
	def setUp(self):
		self.data = load_iris()

class SaveAndLoadTest(IrisDataTestCase):
	def runTest(self):
		svm = 'svm'
		svmC = getDiscreetClassifier(svm)
		saveAble = TrainClassifier.trainWithLabels(svmC,self.data.data, self.data.target)
		meanScore = CV.doShuffleCrossValidation(svmC, self.data.data, self.data.target).meanScore
		s = saveClassifierAsString(saveAble)
		clf = loadClassifierFromString(s)
		newScore = clf.score(self.data.data,self.data.target)
		result = abs(meanScore - newScore)
		# Ensure the score after reloading the classifier is close to the cross validation score
		self.assertTrue(result < .05)
