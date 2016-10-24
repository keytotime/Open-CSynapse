from PIL import Image
from sklearn.decomposition import PCA
from Constants import Constants
# Returns list of resized black and white pixels comprising the image
# @params filename:name of file
# size:(xSize,ySize) to resize the image to
def getPixels(filename, size):
	image = Image.open(filename).resize(size).convert('L')
	data = image.getdata()
	return list(data)

def stringifyNums(nums):
	return [str(x) for x in nums]

def vectorizeImages(labeledFiles):
	allFiles = []
	labels = []
	for key, value in labeledFiles.iteritems():
		allFiles.extend(value)
		labels.append((key,len(value)))

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
