import sys

from spectrum_average import SpectrumAverage
from variance import Variance
from variance_2015 import Variance2015

available_detection_methods = {
    SpectrumAverage.__name__: SpectrumAverage,
    Variance.__name__: Variance,
	Variance2015.__name__: Variance2015}

def select_detection_method(name):
    if name not in available_detection_methods:
        print('Unrecognized detection method: {}'.format(name))
        print_detection_methods()
        sys.exit(-1)
    else:
        return available_detection_methods[name]

def print_detection_methods():
    print('Available detection methods:')
    for k in available_detection_methods.keys():
        print('\t{0}'.format(k))
