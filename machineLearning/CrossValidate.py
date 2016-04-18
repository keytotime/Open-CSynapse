# Sam Callister April 18, 2016
# Class which splits up data to do cross valiation

import random as random
from collections import namedtuple

# Divides the data into a train set and test set
# Params: labeledData - List of all the data, label and data are contained
# in the same element.
# fold - Fold of cross validation. e.g. 10 fold = 10% of data held out
# Returns: ()
def setupCrossValidation(labeledData, fold):
	# Number of elements for the test set
	sizeTestSet = max(int(len(labeledData) / fold), 1)
	# Shuffle the data
	random.shuffle(labeledData)
	# Take the first sizeTestSet elmements for the test set
	test = labeledData[:sizeTestSet]
	# The rest of the data is the training set
	train = labeledData[sizeTestSet:]
	# Tuple mapping for returning train and test data
	TrainTest = namedtuple('TrainTest','trainData,testData')
	# Return the training/test data
	return TrainTest(train, test)