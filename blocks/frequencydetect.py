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

                              .      :       :                     estimated
                              .      :       :                  ,- signal power
                              .      :   A   :                 /   density
                              .      :``/`\``:`````````````````
~~~^~^~~^~^~^^~~~^~^~^~^^^~~^~.^~^~~~:~'   '~:~~~^~^~^^^^~~^~``\   estimated
                              .                                 '- noise power
'------------------.----------------''---.---''------.------'      density
                   |          .          |           |
              noise band      .    signal band   noise band
                              |
                            center
                          frequency
"""

FrequencyDetect_output_types = OrderedDict{
    'snr': gr.sizeof_float,
    'signal estimate', gr.sizeof_float,
    'noise estimate', gr.sizeof_float,
    'noise std', gr.sizeof_float,
    'confidence', gr.sizeof_float
}

FrequencyDetect_output_slots = (
    lambda keys: {k:keys.index(k) for k in keys})(
    FrequencyDetect_output_types)

class FrequencyDetect(gr.sync_block):
    def __init__(self,
        resolution,
        num_bins,
        center_frequency,
        desired_frequency,
        desired_bandwidth):

        gr.sync_block.__init__(self,
            name="FrequencyDetect",
            in_sig=[(numpy.float32, num_bins)],
            out_sig=[size for size in FrequencyDetect_output_types.values()])

        center_bin = num_bins / 2
        offset = (desired_frequency - center_frequency) * 1.0 / resolution
        bandwidth = desired_bandwidth * 1.0 / resolution
        self.pulse_min_bin = center_bin + floor(offset - bandwidth / 2)
        self.pulse_max_bin = center_bin + ceil(offset + bandwidth / 2)

    def work(self, input_items, output_items):
        signal_arr = input_items[0][self.pulse_min_bin:self.pulse_max_bin]
        noise_arr = numpy.concatenate((
            input_items[0][0:self.pulse_min_bin],
            input_items[0][self.pulse_max_bin:num_bins]))

        noise_estimate = numpy.mean(noise_arr)
        signal_estimate = numpy.mean(signal_arr)
        noise_std = numpy.std(noise_arr)
        
        snr = signal_estimate / noise_estimate
        confidence = snr / noise_std

        output_slots = FrequencyDetect_output_slots
        output_items[output_slots['snr']][0] = snr
        output_items[output_slots['signal estimate']][0] = signal_estimate
        output_items[output_slots['noise estimate']][0] = noise_estimate
        output_items[output_slots['noise std']][0] = noise_std
        output_items[output_slots['confidence']][0] = confidence

        return len(input_items[0])
