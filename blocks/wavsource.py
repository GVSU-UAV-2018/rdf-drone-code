from gnuradio import gr
from gnuradio import blocks
from gnuradio import analog

"""
Implements playback of a series of recorded samples.
Each sample is contained in a file named with the index of the sample.
This index is output with each point in the sample.

    ,------------------------------------------------------.
    |  ,----------.   ,------------------.   ,----------.  |
    |  | wav file |-->| float-to-complex |-->| throttle |--|--> radio signal
    |  `----------'   `------------------'   `----------'  |
    |                               ,-------------------.  |
    |                               | index of wav file |--|--> index
    |                               `-------------------'  |
    `------------------------------------------------------'
"""

class WavSource(gr.hier_block2):

    def __init__(self, playback_folder, throttle=True):
        """
        :param radio_config:
            The parameters to configure the radio (or in this case, file),
            such as sample rate.
            Unrecognized parameters are ignored.
        :param playback_folder:
            The name of the folder containing the samples to play.
            Each sample should be a file 'N.wav', where N is an integer number > 0.
        """
        gr.hier_block2.__init__(self, "Wav Source",
            gr.io_signature(0, 0, gr.sizeof_gr_complex),
            gr.io_signature2(2, 2, gr.sizeof_gr_complex, gr.sizeof_int))

        ##################################################
        # Variables
        ##################################################
        self.playback_folder = playback_folder

        ##################################################
        # Blocks
        ##################################################
        self.gr_float_to_complex = blocks.float_to_complex()
        self.gr_throttle = blocks.throttle(gr.sizeof_gr_complex, 1)

        self.gr_wav_source = blocks.null_source(gr.sizeof_float)
        self.gr_constant = blocks.vector_source_i([-1], repeat=True)

        ##################################################
        # Connections
        ##################################################
        if throttle:
            self.connect(self.gr_float_to_complex, self.gr_throttle, (self, 0))
        else:
            self.connect(self.gr_float_to_complex, (self, 0))

        self.connect(self.gr_constant, (self, 1))

        self.connect((self.gr_wav_source, 0), (self.gr_float_to_complex, 0))
        self.connect((self.gr_wav_source, 1), (self.gr_float_to_complex, 1))


    def play(self, index):
        self.lock()

        self.disconnect(self.gr_wav_source)

        self.index = index
        self.gr_wav_source = blocks.wavfile_source(
            self.playback_folder+'/'+str(index)+'.wav')
        self.gr_constant.set_data([index])
        
        self.gr_throttle.set_sample_rate(self.sample_rate())

        self.connect((self.gr_wav_source, 0), (self.gr_float_to_complex, 0))
        self.connect((self.gr_wav_source, 1), (self.gr_float_to_complex, 1))
        
        self.unlock()
    
    def sample_rate(self):
        return self.gr_wav_source.sample_rate()

    def finished(self):
        return self.gr_wav_source.finished()
