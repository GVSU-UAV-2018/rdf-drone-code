import sys
import numpy
import math
from collections import OrderedDict

from math import ceil, floor

from gnuradio import gr

"""
TODO: what is this?
"""

class VarianceTimeBased(gr.sync_block):
    def __init__(self,
        num_bins,
        threshold,
        **extra_args):

        gr.sync_block.__init__(self,
            name=self.__class__.__name__,
            in_sig=[(numpy.float32, num_bins)],
            out_sig=[(numpy.float32, 1)])

        self.num_bins = num_bins
        self.threshold = threshold


    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate


    def work(self, input_items, output_items):
        if self.last_n_samples is None:
            self.last_n_samples = []
        num_windows = (int)(self.sample_rate / self.num_bins) 

        noise_arr = numpy.array(input_items[0][0,0:self.num_bins])
        noise_var = numpy.var(noise_arr)
        
        self.last_n_samples.append(noise_var)
        if len(self.last_n_samples) >= num_windows:
            self.baseline = numpy.mean(self.last_n_samples)

        if self.baseline is None or noise_var < self.baseline * self.threshold:
            output_items[0][0] = 0
        else:
            output_items[0][0] = noise_var - self.baseline

        return 1
