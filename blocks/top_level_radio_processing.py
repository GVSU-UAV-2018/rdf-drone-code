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
Implements most of the processing of the radio signal.
Given an input signal, outputs parameters indicating the relative strength
of the received signal. 

                   ,-----------------------------------.
                   |   ,-----------.   ,-----.         |
    radio signal --|-->| vectorize |-->| FFT |-.       |
                   |   `-----------'   `-----' |       |
                   | ,-------------------------'       |
                   | |  ,-----------.   ,-----------.  | ,-> signal strength
                   | |  | magnitude |   | frequency |--|-'
                   | '->|  squared  |-->|  detect   |--|--> -. statistics about
                   |    `-----------'   |           |--|--> -'  received signal
                   |                    `-----------'  |
                   |            ,----------.           |
       direction --|----------->| decimate |-----------|--> direction
                   |            `----------'           |
                   `-----------------------------------'
"""

RDFRadioProcessing_output_types = FrequencyDetect_output_types.copy()
RDFRadioProcessing_output_types['direction'] = gr.sizeof_int

RDFRadioProcessing_output_python_types = FrequencyDetect_output_python_types.copy()
RDFRadioProcessing_output_python_types['direction'] = numpy.int32

RDFRadioProcessing_output_slots = (
    lambda keys: OrderedDict([(k, keys.index(k)) for k in keys]))(
    RDFRadioProcessing_output_types.keys())

class RDFRadioProcessing(gr.hier_block2):

    def __init__(self, detection_config, input_sample_rate):
        """
        :param detect_config:
            The parameters to configure the signal detection block.
        :param input_sample_rate:
            The sample rate, in Hz
        """
        gr.hier_block2.__init__(self, 'RDFRadioProcessing',
            gr.io_signature2(2, 2, gr.sizeof_gr_complex, gr.sizeof_int),
            gr.io_signaturev(
                len(RDFRadioProcessing_output_types),
                len(RDFRadioProcessing_output_types),
                [size for size in RDFRadioProcessing_output_types.values()]))

        ##################################################
        # Variables
        ##################################################
        self.input_sample_rate = input_sample_rate
        self.num_fft_bins = detection_config['fft bins']
        self.pulse_freq_offset = detection_config['pulse frequency offset']
        self.pulse_bandwidth = detection_config['pulse bandwidth']
        self.output_sample_rate = self.input_sample_rate / self.num_fft_bins
        
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
        self.frequency_detect = FrequencyDetect(
            resolution=self.input_sample_rate * 1.0 / self.num_fft_bins,
            num_bins=self.num_fft_bins,
            center_frequency = 0,
            desired_frequency=self.pulse_freq_offset,
            desired_bandwidth=self.pulse_bandwidth)

        self.gr_direction_decimate = blocks.keep_one_in_n(
            gr.sizeof_int,
            self.num_fft_bins)

        ##################################################
        # Connections
        ##################################################
        self.connect(
            (self, 0),
            self.gr_vectorize,
            self.gr_fft,
            self.gr_mag_squared,
            self.frequency_detect)

        for k in FrequencyDetect_output_slots.keys():
            self.connect(
                (self.frequency_detect, FrequencyDetect_output_slots[k]),
                (self, FrequencyDetect_output_slots[k]))

        self.connect(
            (self, 1),
            self.gr_direction_decimate,
            (self, RDFRadioProcessing_output_slots['direction']))
