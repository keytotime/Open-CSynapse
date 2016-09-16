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
def getDiscreetClassifier(name):
	if(name == 'svm'):
		return SVC()
	elif(name == 'knearest'):
		return KNeighborsClassifier()
	elif(name == 'guassNB'):
		return GaussianNB()
	elif(name == 'sgd'):
		return SGDClassifier()
	elif(name == 'adaBoost'):
		return AdaBoostClassifier(n_estimators=100)
	elif(name == 'randomForest'):
		return AdaBoostClassifier(n_estimators=20)
	elif(name == 'perceptron'):
		return Perceptron(n_iter=50)
	elif(name == 'nearestCentroid'):
		return NearestCentroid()
	elif(name == 'passiveAggressive'):
		return PassiveAggressiveClassifier()
	elif(name == 'decisionTree'):
		return DecisionTreeClassifier()
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