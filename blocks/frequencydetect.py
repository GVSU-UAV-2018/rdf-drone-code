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
    * estimated signal power density (mean power/bin)
    * estimated noise power density (mean power/bin)
    * standard deviation of the power in the noise bins
    * a measure of confidence that there is a significant signal

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

FrequencyDetect_output_types = OrderedDict()
FrequencyDetect_output_types['snr'] = gr.sizeof_float
FrequencyDetect_output_types['signal estimate'] = gr.sizeof_float
FrequencyDetect_output_types['noise estimate'] = gr.sizeof_float
FrequencyDetect_output_types['noise std'] = gr.sizeof_float
FrequencyDetect_output_types['confidence'] = gr.sizeof_float

FrequencyDetect_output_python_types = OrderedDict()
FrequencyDetect_output_python_types['snr'] = numpy.float32
FrequencyDetect_output_python_types['signal estimate'] = numpy.float32
FrequencyDetect_output_python_types['noise estimate'] = numpy.float32
FrequencyDetect_output_python_types['noise std'] = numpy.float32
FrequencyDetect_output_python_types['confidence'] = numpy.float32


FrequencyDetect_output_slots = (
    lambda keys: OrderedDict([(k, keys.index(k)) for k in keys]))(
    FrequencyDetect_output_types.keys())

class FrequencyDetect(gr.sync_block):
    def __init__(self,
        num_bins,
        center_frequency,
        signal_frequency,
        signal_bandwidth):

        gr.sync_block.__init__(self,
            name="FrequencyDetect",
            in_sig=[(numpy.float32, num_bins)],
            out_sig=[T for T in FrequencyDetect_output_python_types.values()])

        self.num_bins = num_bins
        self.center_frequency = center_frequency
        self.signal_frequency = signal_frequency
        self.signal_bandwidth = signal_bandwidth



    def set_resolution(self, resolution):
        self.resolution = resolution
        center = self.num_bins / 2
        offset = (self.signal_frequency - self.center_frequency) * 1.0 / resolution
        bandwidth = self.signal_bandwidth * 1.0 / resolution
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
        noise_std = numpy.std(noise_arr)
    
        snr = signal_estimate / noise_estimate
        confidence = signal_estimate / noise_std # NOT CORRECT!

        if snr > 10:
            print snr

        output_slots = FrequencyDetect_output_slots
        output_items[output_slots['snr']][0] = snr
        output_items[output_slots['signal estimate']][0] = signal_estimate
        output_items[output_slots['noise estimate']][0] = noise_estimate
        output_items[output_slots['noise std']][0] = noise_std
        output_items[output_slots['confidence']][0] = confidence

        return 1
