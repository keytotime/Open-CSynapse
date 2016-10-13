from scipy.stats import pearsonr
from collections import namedtuple

result = namedtuple('result', 'r p')

def reg(x, y):
	strength, probability = pearsonr(x, y)
	return result(r=strength,p=probability)