import sys
import numpy
import math

from math import ceil, floor

from gnuradio import gr

FrequencyDetect_outputs = ordereddict{
    'snr': gr.sizeof_float,
    'signal mean', gr.sizeof_float,
    'noise mean', gr.sizeof_float,
    'noise std', gr.sizeof_float,
    'confidence', gr.sizeof_float
}

class FrequencyDetect(gr.sync_block):
    """
    docstring for block Pulse_Detect
    """
    def __init__(self,
        input_sample_rate,
        num_fft_bins,
        center_frequency,
        desired_frequency,
        desired_bandwidth):
        gr.sync_block.__init__(self,
            name="Pulse_Detect",
            in_sig=[(numpy.float32, fft_bins)],
            out_sig=[size for (i, size) in FrequencyDetect])

        self.signal_output = None

        # These calculations assume complex sampling,
        # so our sampled band goes from -sample_rate to +sample_rate
        # instead of from 0 to +sample_rate.
        fft_resolution = sample_rate / fft_bins
        fft_dc_bin = fft_bins / 2
        pulse_offset_bins = pulse_freq_offset * 1.0 / fft_resolution
        pulse_bw_bins = pulse_bandwidth * 1.0 / fft_resolution
        self.pulse_min_bin = fft_dc_bin + floor(pulse_offset_bins - pulse_bw_bins / 2)
        self.pulse_max_bin = fft_dc_bin + ceil(pulse_offset_bins + pulse_bw_bins / 2)

    def work(self, input_items, output_items):
        
        signal_arr = input_items[0][self.pulse_min_bin:self.pulse_max_bin]
        noise_arr = numpy.concatenate((
            input_items[0][0:self.pulse_min_bin],
            input_items[0][self.pulse_max_bin:fft_bins]))

        noise_estimate = numpy.mean(noise_arr)
        signal_estimate = numpy.mean(signal_arr)
        noise_std = numpy.std(noise_arr)
        
        snr = signal_mean / noise_mean
        signal_confidence = snr / noise_std

        output_items[0][0] = snr
        output_items[1][0] = signal_estimate
        output_items[2][0] = noise_estimate
        output_items[3][0] = noise_std
        output_items[4][0] = signal_confidence

        return len(input_items[0])
