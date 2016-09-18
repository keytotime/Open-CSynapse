# Sam Callister April 18, 2016
# Used to Prepare data for ML algorithms
from collections import namedtuple

# returns (data, labels)
def cleanData(fileName):
	# list of labels
	target = list()
	# list of data
	data = list()
	# Read data in from file
	with open(fileName, 'r') as f:
		for line in f:
			stripped = line.rstrip('\n').rstrip()
			splitData = stripped.split(',')
			# Label is in first spot
			target.append(splitData[0])
			dataPoint = splitData[1:]
			# Cast every value to a float
			casted = [float(value) for value in dataPoint]
			# Add bias feature to the data
			casted.append(1)
			data.append(casted)

	# Tuple mapping for returning data and labels
	DataLabels = namedtuple('DataLabels','data,target')
	# Return the training/test data
	return DataLabels(data, target)

def cleanUntagged(filename):
	#list of data
	data = []

	# Read data in from file
	with open(filename, 'r') as f:
		for line in f:
			stripped = line.rstrip('\n').rstrip()
			splitData = stripped.split(',')
			# Label is in first spot
			
			# Cast every value to a float
			casted = [float(value) for value in splitData]
			# Add bias feature to the data
			casted.append(1)
			data.append(casted)

	return data