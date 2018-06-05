from gnuradio import gr
from gnuradio import blocks
from gnuradio import analog

"""
Implements a simulated ideal signal to test the frequency detection.

    ,---------------------------------------.
    |  ,------------------.   ,----------.  |
    |  | signal generator |-->| throttle |--|--> radio signal
    |  `------------------'   `----------'  |
    |                 ,-------.   ,------.  |
    |                 | index |-->| copy |--|--> index
    |                 `-------'   `------'  |
    `---------------------------------------'
    The |copy| block in this flowgraph is there to work around a GNU radio bug.
    Blocks connected to the output of a hierarchical block do not disconnect correctly.

"""

class ToneSource(gr.hier_block2):

    def __init__(self, radio_config, frequency, throttle=True):
        """
        :param radio_config:
            The parameters to configure the radio, such as sample rate.
            Because we're creating a simulated signal, only the sample rate
            is used.
        :param frequency:
            The frequency to generate.
        """
        gr.hier_block2.__init__(self, "ToneSource",
            gr.io_signature(0, 0, gr.sizeof_gr_complex),
            gr.io_signature2(2, 2, gr.sizeof_gr_complex, gr.sizeof_int))

        ##################################################
        # Variables
        ##################################################
        self.sample_rate = radio_config['sample rate']
        self.frequency = frequency

        ##################################################
        # Blocks
        ##################################################
        self.gr_signal_source = analog.sig_source_c(self.sample_rate, analog.GR_COS_WAVE, self.frequency, 1.0)
        self.gr_throttle = blocks.throttle(gr.sizeof_gr_complex, self.sample_rate)
        self.gr_copy = blocks.copy(gr.sizeof_float)

        self.gr_constant = blocks.null_source(gr.sizeof_int)

        ##################################################
        # Connections
        ##################################################
        if throttle:
            self.connect(self.gr_signal_source, self.gr_throttle, (self, 0))
        else:
            self.connect(self.gr_signal_source, (self, 0))

        self.connect(self.gr_copy, (self, 1))
        self.connect(self.gr_constant, self.gr_copy)


    def play(self, index):
        self.lock()

        self.disconnect(self.gr_constant)

        self.index = index
        self.gr_constant = blocks.vector_source_i([index], repeat=True)

        self.connect(self.gr_constant, self.gr_copy)
        
        self.unlock()
