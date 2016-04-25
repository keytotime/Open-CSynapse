# Sam Callister April 23, 2016
# Returns 2 diemensional representation of data

from sklearn.decomposition import PCA

def get2DPoints(data, labels):
	# Check dimensionality
	if(len(data[0]) < 3):
		# Return points and labels in a dictionary
		return packPoints(data, labels)
	else:
		# Do PCA to get 2 diemensional data
		pca = PCA(n_components=2, copy=False)
		# Map the data
		transformedData = pca.fit_transform(data)
		return packPoints(transformedData, labels)
# Puts the points into a dictionary of form label:pointList
def packPoints(data, labels):
	points = {}
	# Iterate over points adding them to dictionary
	for i in range(len(data)):
		# Convert np array to list so it can be serialized
		cPoint = data[i].tolist()
		cLabel = labels[i]
		if(cLabel in points.keys()):
			points[cLabel].append(cPoint)
		else:
			newLabelList = list()
			newLabelList.append(cPoint)
			points[cLabel] = newLabelList

	return points