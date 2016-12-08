# Sam Callister April 18, 2016
# Used to get accuracy scores for the given algorithm

from sklearn import cross_validation
from TimeFunction import timeFunction
from collections import namedtuple

# Does crossvalidation by randomling choosing samples from the data to hold out
def doShuffleCrossValidation(classifier, data, target, testSize = 0.1, epochs = 100):
	# try cross validation 200 times before failing
	numTries = 200
	for x in range(numTries):
		try:
			cxShuffle = cross_validation.ShuffleSplit(len(data),n_iter=epochs,test_size=testSize)
			return getMeanScore(classifier, data, target, cxShuffle)
		except ValueError:
			pass
	raise ValueError('Cross validation failed, need more than one type of label')

def doFoldCrossValidation(classifier, data, target, numFolds = 10, shuffleFirst=True):
	cxFold = cross_validation.KFold(len(data), n_folds=numFolds, shuffle=shuffleFirst)
	return getMeanScore(classifier, data, target, cxFold)


# Gets the mean score of cross validation with the provided classifier and type of
# crossvalidation
# Params: classifier - classifier used to predict labels
# typeCv - type of crossvalidation to perform on data
# Returns named tuple (meanScore, timeTaken)
def getMeanScore(classifier, data, target, typeCv):
	scoresTime = timeFunction(lambda: cross_validation.cross_val_score(classifier, data, target, cv=typeCv))
	# Named tuple for (meanScore, time)
	MeanTime = namedtuple('MeanTime','meanScore,timeTaken')
	return MeanTime(scoresTime.result.mean(), scoresTime.timeTaken)
	

