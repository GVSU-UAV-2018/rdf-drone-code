import sys
import numpy
import math
from collections import OrderedDict

from math import ceil, floor

from gnuradio import gr

from movingaverage import MovingAverageEstimator

"""
A Gnu Radio block that detects the presence of a specified
signal frequency given a power spectrum.

The detection method used here is similar to that used by the 2015 project group.
We compare the frequency-domain variance right now to an estimate of what that
variance would be if we only had noise. If the variance right now reaches a given
threshold, then we assume we have a real signal and output the peak intensity
of that signal. Otherwise we output 0.

The one major difference from the 2015 project group's algorithm is that we use
an exponential moving average for the variance estimate. The 2015 algorithm
used a simple average, resetting it every few samples.

Configuration:
    * resolution is the FFT resolution, in Hz
    * num_bins is the number of FFT bins (bandwidth is resolution * n_bins)
    * center_frequency is the center frequency of the power spectrum, in Hz
    * desired_frequency is the frequency of the signal to detect, in Hz
    * desired_bandwidth is the width of the signal detection band, in Hz
    * decay_time is the time between transmitter pulses
    * detection_threshold is the difference between 

Inputs:
    * a power spectrum having the specified resolution, center frequency,
      and number of bins

Outputs:
    * an estimated signal strength

                              .       :     :                      estimated
                              .       :     :                   ,- signal power
                              .       :  A  :                  /   density
                              .       :`/`\`:``````````````````
~~~^~^~~^~^~^^~~~^~^~^~^^^~~^~.^~^~~~~:'   ':~~~~^~^~^^^^~~^~
                              .
'------------------.-----------------''--.--''-------.------'
                   |          .          |           |
                ignored       .    signal band    ignored
                              |
                            center
                          frequency



Variance of the input signal right now


        ,            ,            ,
        |            |            |            . . .
    ,~,~'`~.~",  ,.~.'~~~.        |   ,~~.
~^~'    :      ~'         `~~~`~~~'~~'    `~~~~
        :
        |
  signal pulse


Delayed moving average


           ,.           ,._          ,
           | `~.._      |  `.        |`~...    . . .
     ,,~~'''      '''~~~'    '~..    |     `~..
~`~''                            ````
"""


class Variance(gr.sync_block):
    def __init__(self,
        num_bins,
        center_frequency,
        signal_frequency,
        signal_bandwidth,
        threshold,
        decay_time,
        decay_strength,
        **extra_args):

        gr.sync_block.__init__(self,
            name=self.__class__.__name__,
            in_sig=[(numpy.float32, num_bins)],
            out_sig=[(numpy.float32, 1)])

        self.num_bins = num_bins
        self.center_frequency = center_frequency
        self.signal_frequency = signal_frequency
        self.signal_bandwidth = signal_bandwidth
        self.threshold = threshold
        self.decay_time = decay_time
        self.decay_strength = decay_strength


    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        bin_width = self.sample_rate
        center = self.num_bins / 2
        offset = (self.signal_frequency - self.center_frequency) * 1.0 / bin_width
        bandwidth = self.signal_bandwidth * 1.0 / bin_width
        self.signal_min_bin = int(center + floor(offset - bandwidth / 2))
        self.signal_max_bin = int(center + ceil(offset + bandwidth / 2))

        decay_n_samples = self.decay_time * self.sample_rate
        decay_constant = self.decay_strength**(-1.0/decay_n_samples)
        self.expected_variance = MovingAverageEstimator(
            rate=decay_constant, warmup=decay_n_samples)



    def work(self, input_items, output_items):

        signal_arr = numpy.array([])
        noise_arr = numpy.array([])

        a, b, c, d = 0, self.signal_min_bin, self.signal_max_bin, self.num_bins

        signal_arr = numpy.array(input_items[0][0,b:c])

        signal_variance = numpy.var(signal_arr)

        if (self.expected_variance.remaining_warmup == 0
        and signal_variance > self.threshold**2 * self.expected_variance.estimate):
            output_items[0][0] = numpy.sqrt(signal_variance - self.expected_variance.estimate)
        else:
            output_items[0][0] = 0

        self.expected_variance.update(signal_variance)

        return 1
