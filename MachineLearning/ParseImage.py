from PIL import Image
from sklearn.decomposition import PCA
from Constants import Constants
from collections import namedtuple
# Returns list of resized black and white pixels comprising the image
# @params filename:name of file
# size:(xSize,ySize) to resize the image to
def getPixels(filename, size):
	image = Image.open(filename).resize(size).convert('L')
	data = image.getdata()
	return list(data)

def stringifyNums(nums):
	return [str(x) for x in nums]

def demoAddLabels(label, pixels):
	result = [label]
	result.extend(stringifyNums(pixels))
	return result

def vectorizeToAdd(allFiles,label):
	size = (Constants.DEMO_SIZE,Constants.DEMO_SIZE)
	# Get pixel data according to minimum size
	pixelData = [getPixels(x, size) for x in allFiles]

	# Add labels back in
	labeledData = [demoAddLabels(label,x) for x in pixelData]
	

	# Compose string to save data in
	data = [','.join(x) for x in labeledData]
	return '\n'.join(data)

def vectorizeForDemo(allFiles, labels):
	size = (Constants.DEMO_SIZE,Constants.DEMO_SIZE)
	# Get pixel data according to minimum size
	pixelData = [getPixels(x, size) for x in allFiles]

	# Add labels back
	labeledData = []
	pos = 0
	for x in labels:
		for i in range(x[1]):
			newList = list(pixelData[i + pos])
			newList.insert(0,x[0])
			labeledData.append(newList)
		pos += x[1]

	# Compose string to save data in
	data = [','.join(stringifyNums(x)) for x in labeledData]
	return '\n'.join(data)

def vectorizeImages(labeledFiles, demo=False):
	allFiles = []
	labels = []
	for key, value in labeledFiles.iteritems():
		allFiles.extend(value)
		labels.append((key,len(value)))

	if(demo):
		return vectorizeForDemo(allFiles, labels)
	else:
		# Find min X and Y sizes
		minX, minY = (float('inf'), float('inf'))
		for x in allFiles:
			x, y = Image.open(x).size
			minX = min(minX, x)
			minY = min(minY, y)
		size = (minX, minY)

		# Get pixel data according to minimum size
		pixelData = [getPixels(x, size) for x in allFiles]
		# Set number of components
		components = Constants.PCA_COMPONENTS
		if(len(pixelData[0]) < Constants.PCA_COMPONENTS):
			components = len(pixelData[0])
		# Init PCA algo
		pca = PCA(n_components=components,copy=False)
		# Perform PCA and return the results
		transformed = pca.fit_transform(pixelData)
		# Add labels back
		labeledData = []
		pos = 0
		for x in labels:
			for i in range(x[1]):
				newList = list(transformed[i + pos])
				newList.insert(0,x[0])
				labeledData.append(newList)
			pos += x[1]

		# Compose string to save data in
		data = [','.join(stringifyNums(x)) for x in labeledData]
		return '\n'.join(data)

def vectorizeForClassify(labeledFiles, unlabeledList, trainingPath=None, classifyingPath=None):
	allFiles = []
	labels = []
	for key, value in labeledFiles.iteritems():
		allFiles.extend(value)
		labels.append((key,len(value)))

	for name, path in unlabeledList:
		allFiles.append(path)

	# Find min X and Y sizes
	minX, minY = (float('inf'), float('inf'))
	for x in allFiles:
		x, y = Image.open(x).size
		minX = min(minX, x)
		minY = min(minY, y)
	size = (minX, minY)
	# Get pixel data according to minimum size
	pixelData = [getPixels(x, size) for x in allFiles]
	# Set number of components
	components = Constants.PCA_COMPONENTS
	if(len(pixelData[0]) < Constants.PCA_COMPONENTS):
		components = len(pixelData[0])
	# Init PCA algo
	pca = PCA(n_components=components,copy=False)
	# Perform PCA and return the results
	transformed = pca.fit_transform(pixelData)
	# Make list of training data and labels
	labelsForTraining = []
	trainingData = []
	pos = 0
	for x in labels:
		for i in range(x[1]):
			newList = list(transformed[i + pos])
			trainingData.append(newList)
			labelsForTraining.append(x[0])
		pos += x[1]

	# seperate into training data and data to be classified
	toClassify = transformed[pos:]
	toClassifyData = []
	toClassifyLabels = []
	for index, val in enumerate(unlabeledList):
		filename = val[0]
		toClassifyData.append(toClassify[index])
		toClassifyLabels.append(filename)
	# if filename is given, write training data and data to classify into files
	if(trainingPath!= None and classifyingPath != None):
		with open(trainingPath, 'w') as f:
			toWrite = []
			for i, x in enumerate(labelsForTraining):
				newList = []
				newList.append(x)
				for c in trainingData[i]:
					newList.append(str(c))
				toWrite.append(newList)

			lines = [','.join(x) for x in toWrite]
			final = '\n'.join(lines)
			f.write(final)
		with open(classifyingPath, 'w') as f:
			toWrite = []
			for x in toClassifyData:
				newList = []
				for c in x:
					newList.append(str(c))
				toWrite.append(newList)

			lines = [','.join(x) for x in toWrite]
			final = '\n'.join(lines)
			f.write(final)

		return toClassifyLabels
	else:
		ClassifyLabel = namedtuple('ClassifyLabel','data,names')
		DataLabels = namedtuple('DataLabels','data,target')
		return (DataLabels(trainingData,labelsForTraining), ClassifyLabel(toClassifyData, toClassifyLabels))
