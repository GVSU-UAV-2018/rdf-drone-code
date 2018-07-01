import sys
import numpy
import math

from math import ceil, floor

from gnuradio import gr

class SNRExtract(gr.sync_block):
    def __init__(self,
        sample_snr):

        gr.sync_block.__init__(self,
            name="SNRExtract",
            in_sig=[(numpy.float32)],
            out_sig=None)

        self.sample_snr = sample_snr
        self.snr_samples = []

    def work(self, input_items, output_items):
        self.snr_samples.append(input_items[0])
        return 1
