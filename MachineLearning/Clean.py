# Sam Callister April 18, 2016
# Used to Prepare data for ML algorithms
from collections import namedtuple
import csv

# returns (data, labels)
def cleanData(fileName):
	# list of labels
	target = list()
	# list of data
	data = list()
	# Read data in from file
	with open(fileName, 'r') as f:
		possibleHeader = f.readline()
		hasHeader = csv.Sniffer().has_header(f.readline())
		if(not hasHeader):
			f.seek(0)
		reader = csv.reader(f, skipinitialspace=True)
		for line in reader:
			# Label is in first spot
			target.append(line[0])
			dataPoint = line[1:]
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
		possibleHeader = f.readline()
		hasHeader = csv.Sniffer().has_header(f.readline())
		if(not hasHeader):
			f.seek(0)
		reader = csv.reader(f, skipinitialspace=True)
		for line in reader:
			# Cast every value to a float
			casted = [float(value) for value in line]
			# Add bias feature to the data
			casted.append(1)
			data.append(casted)

	return data