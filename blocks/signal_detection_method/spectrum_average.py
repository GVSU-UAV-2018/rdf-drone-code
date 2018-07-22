import sys
import numpy
import math
from collections import OrderedDict

from math import ceil, floor

from gnuradio import gr

"""
A Gnu Radio block that detects the presence of a specified
signal frequency given a power spectrum.

Configuration:
    * resolution is the width of each bin in the power spectrum, in Hz
    * num_bins is the number of bins in the power spectrum
    * center_frequency is the center frequency of the power spectrum, in Hz
    * desired_frequency is the frequency of the signal to detect, in Hz
    * desired_bandwidth is the width of the signal detection band, in Hz

Inputs:
    * a power spectrum having the specified resolution, center frequency,
      and number of bins

Outputs:
    * an estimated SNR

SNR is calculated as the mean power of the signal band
divided by the mean power of everything else.

                              .       :     :                      estimated
                              .       :     :                   ,- signal power
                              .       :  A  :                  /   density
                              .       :`/`\`:``````````````````
~~~^~^~~^~^~^^~~~^~^~^~^^^~~^~.^~^~~~~:'   ':~~~~^~^~^^^^~~^~``\   estimated
                              .                                 '- noise power
'------------------.-----------------''--.--''-------.------'      density
                   |          .          |           |
              noise band      .    signal band   noise band
                              |
                            center
                          frequency
"""


class SpectrumAverage(gr.sync_block):
    def __init__(self,
        num_bins,
        center_frequency,
        signal_frequency,
        signal_bandwidth,
        **extra_args):

        gr.sync_block.__init__(self,
            name=self.__class__.__name__,
            in_sig=[(numpy.float32, num_bins)],
            out_sig=[(numpy.float32, 1)])

        self.num_bins = num_bins
        self.center_frequency = center_frequency
        self.signal_frequency = signal_frequency
        self.signal_bandwidth = signal_bandwidth



    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        center = self.num_bins / 2
        offset = (self.signal_frequency - self.center_frequency) * 1.0 / sample_rate
        bandwidth = self.signal_bandwidth * 1.0 / sample_rate
        self.signal_min_bin = int(center + floor(offset - bandwidth / 2))
        self.signal_max_bin = int(center + ceil(offset + bandwidth / 2))



    def work(self, input_items, output_items):

        signal_arr = numpy.array([])
        noise_arr = numpy.array([])

        a, b, c, d = 0, self.signal_min_bin, self.signal_max_bin, self.num_bins

        signal_arr = numpy.array(input_items[0][0,b:c])
        noise_arr = numpy.concatenate((
            numpy.array(input_items[0][0,a:b]),
            numpy.array(input_items[0][0,c:d])))

        noise_estimate = numpy.mean(noise_arr)
        signal_estimate = numpy.mean(signal_arr)
    
        snr = signal_estimate / noise_estimate #SNR = Psig / Pnoise

        output_items[0][0] = snr

        return 1
