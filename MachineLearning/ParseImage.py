from PIL import Image

# Returns list of black and white pixels comprising the image
def getPixelsFromFile(filename):
	image = Image.open(filename).convert('L')
	return list(image.getdata())

def getPixelsFrom(array):
	image = Image.fromstring(array).convert('L')
	return list(image.getdata())