import sys

from spectrum_average import SpectrumAverage
from variance import Variance

available_detection_methods = {
    SpectrumAverage.__name__: SpectrumAverage,
    Variance.__name__: Variance}

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
