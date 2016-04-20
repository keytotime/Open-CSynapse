# Sam Callister April 18, 2016
# Builder method to return classifiers
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import AdaBoostClassifier

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
	else:
		raise ValueError('Classifer'  + name + ' is not supported')