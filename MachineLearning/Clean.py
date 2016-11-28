# Sam Callister April 18, 2016
# Used to Prepare data for ML algorithms
from collections import namedtuple, defaultdict
import csv
# returns (data, labels)
def cleanData(fileName):
	# list of labels
	target = list()
	# list of data
	data = list()

	possibleHeader = ''
	# Read data in from file
	with open(fileName, 'r') as f:
		possibleHeader = f.readline()
		hasHeader = csv.Sniffer().has_header(possibleHeader)
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
	DataLabels = namedtuple('DataLabels','headers,data,target')
	# Return the training/test data
	return DataLabels(possibleHeader,data, target)

def cleanUntagged(filename):
	#list of data
	data = []
	possibleHeader = ''
	# Read data in from file
	with open(filename, 'r') as f:
		possibleHeader = f.readline()
		hasHeader = csv.Sniffer().has_header(possibleHeader)
		if(not hasHeader):
			f.seek(0)
		reader = csv.reader(f, skipinitialspace=True)
		for line in reader:
			# Cast every value to a float
			casted = [float(value) for value in line]
			# Add bias feature to the data
			casted.append(1)
			data.append(casted)

	# Tuple mapping for returning data and labels
	DataLabels = namedtuple('DataLabels','headers,data')
	return DataLabels(possibleHeader, data)


def regressionData(filename):
	#list of data
	data = []
	headers = ''
	# Read data in from file
	with open(filename, 'r') as f:
		headers = f.readline()
		hasHeader = csv.Sniffer().has_header(headers)
		if(not hasHeader):
			raise ValueError('No Headers in File')

		headers = [x.rstrip() for x in headers.split(',')]
		firstLine = [x.rstrip() for x in f.readline().split(',')]
		nonFloatIndexes = set()
		removeTheseHeaders = set()
		for index, x in enumerate(firstLine):
			try:
				float(x)
			except Exception:
				nonFloatIndexes.add(index)
				removeTheseHeaders.add(headers[index])

		headers = [x for x in headers if(x not in removeTheseHeaders)]
		reader = csv.reader(f, skipinitialspace=True)
		# skip first row of headers
		reader.next()
		for line in reader:
			casted = [float(value[1]) for value in enumerate(line) if(value[0] not in nonFloatIndexes)]
			data.append(casted)

	# Tuple mapping for returning data and labels
	DataLabels = namedtuple('DataLabels','headers,data')
	return DataLabels(headers, data)

def getHeaders(filename):
	# Read data in from file
	with open(filename, 'r') as f:
		possibleHeader = f.readline()
		hasHeader = csv.Sniffer().has_header(possibleHeader)
		if(hasHeader):
			return possibleHeader
		else:
			return ''

# Returns [{header:headerName,values:[1,2,4]}...]
def getHeaderPoints(filename):
	with open(filename, 'r') as f:
		labels = []
		reader = csv.reader(f, skipinitialspace=True)
		headers = reader.next()[1:]
		values = defaultdict(list)
		for line in reader:
			labels.append(line[0])
			for index,x in enumerate(line[1:]):
				values[index].append(float(x))
		final = []
		for index, x in enumerate(headers):
			toAdd = {}
			toAdd['header'] = x
			toAdd['values'] = values[index]
			final.append(toAdd)

		return {'labels':labels,'headerPoints':final}
