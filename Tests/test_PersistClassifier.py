import sys
sys.path.insert(0, '../')

import MachineLearning
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
		saveAble = svmC.fit(self.data.data, self.data.target)
		meanScoreTimeTaken = CV.doShuffleCrossValidation(svmC, self.data.data, self.data.target)
		print('old: ' + str(meanScoreTimeTaken))
		s = saveClassifierAsString(saveAble)
		print('saved')
		clf = loadClassifierFromString(s)
		print clf.score(self.data.data,self.data.target)
