# Returns data with predicted labels
def predict(clf, data):
	predictions = clf.predict(data)
	return zip(predictions, data)