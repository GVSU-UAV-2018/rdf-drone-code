from collections import OrderedDict

import numpy
from gnuradio import gr
from gnuradio import blocks
from gnuradio import analog
from gnuradio import fft
from gnuradio.fft import window

from frequencydetect import FrequencyDetect
from frequencydetect import FrequencyDetect_output_types
from frequencydetect import FrequencyDetect_output_python_types
from frequencydetect import FrequencyDetect_output_slots

"""
Calculates power spectral density (PSD) of a signal.

                   ,--------------------------------------.
                   |   ,-----------.   ,-----.   ,-----.  |
    radio signal --|-->| vectorize |-->| FFT |-->| **2 |--|--> PSD vector
                   |   `-----------'   `-----'   `-----'  |
                   `--------------------------------------'
"""

class PowerSpectralDensity(gr.hier_block2):

    def __init__(self,
        num_fft_bins):

        gr.hier_block2.__init__(self, self.__class__.__name__,
            gr.io_signature(1, 1, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex * num_fft_bins))

        ##################################################
        # Variables
        ##################################################
        self.num_fft_bins = num_fft_bins
        
        ##################################################
        # Blocks
        ##################################################
        self.gr_vectorize = blocks.stream_to_vector(
            gr.sizeof_gr_complex, self.num_fft_bins)

        self.gr_fft = fft.fft_vcc(
            self.num_fft_bins,
            forward=True,
            window=window.blackman_harris(self.num_fft_bins),
            shift=True)

        self.gr_mag_squared = blocks.complex_to_mag_squared(self.num_fft_bins)

        ##################################################
        # Connections
        ##################################################
        self.connect(
            self,
            self.gr_vectorize,
            self.gr_fft,
            self.gr_mag_squared,
            self)
    
    def set_sample_rate(self, rate):
        self.input_sample_rate = rate
    
    def output_sample_rate(self):
        return self.input_sample_rate / self.num_fft_bins
