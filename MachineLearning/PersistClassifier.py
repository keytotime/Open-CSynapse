import pickle
from sklearn.externals import joblib

# Saves classifier into pickle object. Idea for saving classifiers
# taken from http://scikit-learn.org/stable/modules/model_persistence.html

# params clf -> Classifier
# returns string representing object 

def saveClassifierAsString(clf):
	return pickle.dumps(clf)

# Loads classifier from string
def loadClassifierFromString(s):
	return pickle.loads(s)
