# Sam Callister April 18, 2016
# Builder method to return classifiers
from sklearn import svm, neighbors

# Returns the classfier corresponding to name
# Params: name - name of classifier to return
# numberOfLabels - number of unique labels in data
# Return: classifier or exception
def getDiscreetClassifier(name):
	if(name == 'svm'):
		return svm.SVC()
	elif(name == 'knearest'):
		return neighbors.KNeighborsClassifier()
	else:
		raise ValueError('Classifer'  + name + ' is not supported')