# Sam Callister April 18, 2016
# Builder method to return classifiers
import sys
sys.path.insert(0, '../')

from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import SGDClassifier, PassiveAggressiveClassifier, Perceptron, LinearRegression,\
Ridge, Lasso, ElasticNet, Lars, OrthogonalMatchingPursuit, BayesianRidge, LogisticRegression
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier


# Returns the classfier corresponding to name
# Params: name - name of classifier to return
# numberOfLabels - number of unique labels in data
# Return: classifier or exception
def getDiscreetClassifier(name, params={}):
	if(name == 'svm'):
		return SVC(**params)
	elif(name == 'knearest'):
		return KNeighborsClassifier(**params)
	elif(name == 'guassNB'):
		return GaussianNB()
	elif(name == 'sgd'):
		return SGDClassifier(**params)
	elif(name == 'adaBoost'):
		return AdaBoostClassifier(**params)
	elif(name == 'randomForest'):
		return RandomForestClassifier(**params)
	elif(name == 'perceptron'):
		return Perceptron(**params)
	elif(name == 'nearestCentroid'):
		return NearestCentroid(**params)
	elif(name == 'passiveAggressive'):
		return PassiveAggressiveClassifier(**params)
	elif(name == 'decisionTree'):
		return DecisionTreeClassifier(**params)
	elif(name == 'leastSquares'):
		return LinearRegression()
	elif(name == 'ridge'):
		return Ridge()
	elif(name == 'lasso'):
		return Lasso()
	elif(name == 'elasticNet'):
		return ElasticNet()
	elif(name == 'lars'):
		return Lars()
	elif(name == 'orthogonalMatchingPursuit'):
		return OrthogonalMatchingPursuit()
	elif(name == 'bayesianRidge'):
		return BayesianRidge()
	elif(name == 'logisticRegression'):
		return LogisticRegression()
	else:
		raise ValueError('Classifer'  + name + ' is not supported')