from collections import ordereddict

from gnuradio import gr
from gnuradio import blocks
from gnuradio import analog
from gnuradio import fft

from detectfrequency import DetectFrequency

"""
Implements the collar detection algorithm.
Given an input signal, outputs parameters indicating the relative strength
of the 

                   ,-----------------------------------.
                   |   ,-----------.   ,-----.         |
    radio signal --|-->| vectorize |-->| FFT |-.       |
                   |   `-----------'   `-----' |       |
                   | ,-------------------------'       |
                   | |  ,-----------.   ,-----------.  | ,-> signal strength
                   | |  | magnitude |   |  detect   |--|-'
                   | '->|  squared  |-->| frequency |--|--> -. statistics about
                   |    `-----------'   |           |--|--> -'  received signal
                   |                    `-----------'  |
                   |            ,----------.           |
       direction --|----------->| decimate |-----------|--> direction
                   |            `----------'           |
                   `-----------------------------------'
"""

DetectCollar_outputs = ordereddict{
    'snr': (0, gr.sizeof_float),
    'signal mean', (1, gr.sizeof_float),
    'noise mean', (2, gr.sizeof_float),
    'noise std', (3, gr.sizeof_float),
    'confidence', (4, gr.sizeof_float),
    'direction', (5, gr.sizeof_float)
}

class DetectCollar(gr.hier_block2)

    def __init__(self, detect_config, input_sample_rate):
        """
        :param detect_config:
            The parameters to configure the signal detection block.
        """
        gr.hier_block2.__init__(self, 'DetectCollar',
            gr.io_signature2(2, 2, gr.sizeof_gr_complex, gr.sizeof_complex),
            gr.io_signaturev(
                len(DetectCollar_outputs),
                len(DetectCollar_outputs),
                [size for k,(index,size) in DetectCollar_outputs])

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
        self.detect_frequency = DetectFrequency(
            input_sample_rate = self.input_sample_rate
            num_fft_bins=self.num_fft_bins,
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
        for i in range(5):
            self.connect((self.detect_frequency, i), (self, i))
        self.connect(
            (self, 1),
            self.gr_direction_decimate,
            (self, DetectCollar_outputs['direction'])