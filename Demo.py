from MachineLearning.ParseImage import getPixels
from sklearn.decomposition import PCA
from MachineLearning.BuildClassifier import getDiscreetClassifier
from MachineLearning.ClassifyData import predict
from MachineLearning.Constants import Constants

def makeInts(line):
	info = line.split(',')
	return (info[0],[int(x) for x in info[1:]])

def classifyForDemo(trainFile, newImageFile):
	imagePixels = getPixels(newImageFile,(Constants.DEMO_SIZE,Constants.DEMO_SIZE))
	# get data out of file
	data = [makeInts(line) for line in trainFile.read().split('\n')]
	pixels = []
	labels = []
	for x in data:
		labels.append(x[0])
		pixels.append(x[1])

	# make big list of photos putting the last one on the end
	pixels.append(imagePixels)

	components = len(pixels)
	if(components > 200):
		components = 200

	pca = PCA(n_components=components,copy=False)

	transformed = pca.fit_transform(pixels)

	alg = getDiscreetClassifier('passiveAggressive')
	alg.fit(transformed[:-1], labels)
	return predict(alg, transformed[-1])[0][0]
