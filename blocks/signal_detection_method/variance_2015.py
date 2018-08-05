import sys
import numpy
import math
from collections import OrderedDict

from math import ceil, floor

from gnuradio import gr

"""

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

var_avg = 0.0
last_n_samples = []

class Variance2015(gr.sync_block):
    def __init__(self,
        num_bins,
        center_frequency,
        signal_frequency,
        signal_bandwidth,
        signal_pulse_duration,
        **extra_args):

        gr.sync_block.__init__(self,
            name=self.__class__.__name__,
            in_sig=[(numpy.float32, num_bins)],
            out_sig=[(numpy.float32, 1)])

        self.num_bins = num_bins
        self.center_frequency = center_frequency
        self.signal_frequency = signal_frequency
        self.signal_bandwidth = signal_bandwidth
        self.signal_pulse_duration = signal_pulse_duration


    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        center = self.num_bins / 2
        offset = (self.signal_frequency - self.center_frequency) * 1.0 / sample_rate
        bandwidth = self.signal_bandwidth * 1.0 / sample_rate
        self.signal_min_bin = int(center + floor(offset - bandwidth / 2))
        self.signal_max_bin = int(center + ceil(offset + bandwidth / 2))



    def work(self, input_items, output_items):
        global var_avg
        global last_n_samples

        num_windows = self.sample_rate #sample_rate = sampling_rate / num bins
        noise_arr = numpy.array([])

        a, b, c, d = 0, self.signal_min_bin, self.signal_max_bin, self.num_bins

        noise_arr = numpy.array(input_items[0][0,b:c])

        noise_mean = numpy.mean(noise_arr)
        noise_norm = numpy.asarray(noise_arr) - noise_mean
        noise_var = numpy.var(noise_norm)

        last_n_samples.append(noise_var)
        if len(last_n_samples) >= num_windows:
            for i in range(int(math.ceil(self.sample_rate * self.signal_pulse_duration))):
                numpy.delete(last_n_samples, numpy.argmax(last_n_samples))
            var_avg = numpy.mean(last_n_samples)
            last_n_samples = []

        if var_avg == 0:
            output_items[0][0] = 0
        else:
            output_items[0][0] = noise_var

        return 1
