# Sam Callister April 18, 2016
# Used to get accuracy scores for the given algorithm

from sklearn import cross_validation

# Does crossvalidation by randomling choosing samples from the data to hold out
def doShuffleCrossValidation(classifier, data, labels, testSize = 0.1, epochs = 100):
	cxShuffle = cross_validation.ShuffleSplit(len(data),n_iter=epochs,test_size=testSize)
	return getMeanScore(classifier, data, labels, cxShuffle)

def doFoldCrossValidation(classifier, data, labels, numFolds = 10, shuffleFirst=True):
	cxFold = cross_validation.KFold(len(data), n_folds=numFolds, shuffle=shuffleFirst)
	return getMeanScore(classifier, data, labels, cxFold)

# Gets the mean score of cross validation with the provided classifier and type of
# crossvalidation
# Params: classifier - classifier used to predict labels
# typeCv - type of crossvalidation to perform on data
def getMeanScore(classifier, data, labels, typeCv):
	scores = cross_validation.cross_val_score(classifier, data, labels, cv=typeCv)
	return scores.mean()

