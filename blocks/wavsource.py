from gnuradio import gr
from gnuradio import blocks
from gnuradio import analog

"""
Implements playback of a recorded sample.

    ,------------------------------------------------------.
    |  ,----------.   ,------------------.   ,----------.  |
    |  | wav file |-->| float-to-complex |-->| throttle |--|--> radio signal
    |  `----------'   `------------------'   `----------'  |
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
            gr.io_signature(1, 1, gr.sizeof_gr_complex))

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

        ##################################################
        # Connections
        ##################################################
        if throttle:
            self.connect(self.gr_float_to_complex, self.gr_throttle, self)
        else:
            self.connect(self.gr_float_to_complex, self)

        self.connect((self.gr_wav_source, 0), (self.gr_float_to_complex, 0))
        self.connect((self.gr_wav_source, 1), (self.gr_float_to_complex, 1))


    def play(self, filename):
        self.lock()

        self.disconnect(self.gr_wav_source)

        self.gr_wav_source = blocks.wavfile_source(
            self.playback_folder+'/'+filename)
        
        self.gr_throttle.set_sample_rate(self.sample_rate())

        self.connect((self.gr_wav_source, 0), (self.gr_float_to_complex, 0))
        self.connect((self.gr_wav_source, 1), (self.gr_float_to_complex, 1))
        
        self.unlock()
    
    def sample_rate(self):
        return self.gr_wav_source.sample_rate()

    def finished(self):
        return self.gr_wav_source.finished()
