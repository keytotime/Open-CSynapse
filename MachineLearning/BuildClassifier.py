# Sam Callister April 18, 2016
# Builder method to return classifiers
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import SGDClassifier, PassiveAggressiveClassifier
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.linear_model import Perceptron
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
	else:
		raise ValueError('Classifer'  + name + ' is not supported')