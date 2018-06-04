from gnuradio import gr
from gnuradio import blocks
from gnuradio import analog
from gnuradio import fft

from frequencydetect import FrequencyDetect

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

RDFRadioProcessing_output_types = copy(FrequencyDetect_output_types)
RDFRadioProcessing_output_types['direction'] = gr.sizeof_int

RDFRadioProcessing_output_slots = (
    lambda keys: {k:keys.index(k) for k in keys})(
    RDFRadioProcessing_output_types)

class RDFRadioProcessing(gr.hier_block2)

    def __init__(self, detect_config, input_sample_rate):
        """
        :param detect_config:
            The parameters to configure the signal detection block.
        :param input_sample_rate:
            The sample rate, in Hz
        """
        gr.hier_block2.__init__(self, 'RDFRadioProcessing',
            gr.io_signature2(2, 2, gr.sizeof_gr_complex, gr.sizeof_complex),
            gr.io_signaturev(
                len(DetectCollar_outputs),
                len(DetectCollar_outputs),
                [size for size in RDFRadioProcessing_output_types.values()])

        ##################################################
        # Variables
        ##################################################
        self.input_sample_rate = input_sample_rate
        self.num_fft_bins = config['fft bins']
        self.pulse_freq_offset = config['pulse frequency offset']
        self.pulse_bandwidth = config['pulse bandwidth']
        self.output_sample_rate = self.input_sample_rate / self.num_fft_bins
        
        ##################################################
        # Blocks
        ##################################################
        self.gr_vectorize = blocks.stream_to_vector(
            gr.sizeof_gr_complex, self.num_fft_bins)

        self.gr_fft = fft.fft_vcc(
            self.num_fft_bins,
            forward=True,
            window=window.blackman_harris(self.num_fft_bins))

        self.gr_mag_squared = blocks.complex_to_mag_squared(self.num_fft_bins)
        self.frequency_detect = FrequencyDetect(
            resolution=self.input_sample_rate * 1.0 / self.num_fft_bins
            num_bins=self.num_fft_bins,
            center_frequency = 0,
            desired_frequency=self.pulse_freq_offset,
            desired_bandwidth=self.pulse_bandwidth)

        self.gr_direction_decimate = blocks.keep_one_in_n(
            gr.sizeof_gr_complex,
            self.num_fft_bins)

        ##################################################
        # Connections
        ##################################################
        self.connect(
            (self, 0)
            self.gr_vectorize,
            self.gr_fft,
            self.gr_mag_squared,
            self.detect_frequency)

        for k in FrequencyDetect_outputs.keys():
            self.connect(
                (self.frequency_detect, FrequencyDetect_output_slots[k]),
                (self, DetectCollar_output_slots[k]))

        self.connect(
            (self, 1),
            self.gr_direction_decimate,
            (self, DetectCollar_output_slots['direction'])
