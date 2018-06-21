from fractions import gcd

from gnuradio import gr
from gnuradio import blocks
from gnuradio import filter as gr_filter
import osmosdr

"""
Wrapper for osmosdr block.
"""

class RadioSource(gr.hier_block2):

    def __init__(self, preferred_sample_rate, gains, frequency_offset, signal_frequency, direction=-1):
        
        gr.hier_block2.__init__(self, "Radio Source",
            gr.io_signature(0, 0, gr.sizeof_gr_complex),
            gr.io_signature2(2, 2, gr.sizeof_gr_complex, gr.sizeof_int))
        
        ##################################################
        # Blocks
        ##################################################
        self.source = osmosdr.source('sensitivity')
        self.direction = blocks.vector_source_i([direction], repeat=True)
        
        self.source.set_center_freq(signal_frequency - frequency_offset)
        
        gain_stage_names = self.source.get_gain_names()
        actual_gains = [
            self.source.set_gain(g, n) for g, n in zip(gains, gain_stage_names)]
        if actual_gains == gains:
            print 'Gains match'
        else:
            print 'Failed to set all gains'
        print('Gain stages', gain_stage_names)
        print('Attempted  ', gains)
        print('Actual     ', actual_gains)
        
        best_available_sample_rate = min(
            filter(
                lambda r: r >= preferred_sample_rate,
                self.source.get_sample_rates().values()))
        self.source.set_sample_rate(best_available_sample_rate)
        print('Selected input sample rate', self.source.get_sample_rate())
        try:
            best_available_prefilter = min(
                filter(
                    lambda r: r >= preferred_sample_rate,
                    self.source.get_bandwidth_range().values()))
            self.source.set_bandwidth(best_available_prefilter)
        except ValueError:
            print 'Could not set prefilter'
            print('Available prefilters: ', self.source.get_bandwidth_range().values())
        print('Selected prefilter', self.source.get_bandwidth())
        
        common_rate = gcd(self.source.get_sample_rate(), preferred_sample_rate)
        interpolation = int(preferred_sample_rate / common_rate)
        decimation = int(self.source.get_sample_rate() / common_rate)
        print('Common rate', common_rate)
        print('Interpolation', interpolation)
        print('Decimation', decimation)
        self.resample = gr_filter.rational_resampler_ccc(
            interpolation=interpolation,
            decimation=decimation)
        
        self._sample_rate = preferred_sample_rate
        print('Selected output sample rate', self.sample_rate())

        ##################################################
        # Connections
        ##################################################
        self.connect(self.source, self.resample, (self, 0))
        self.connect(self.direction, (self, 1))
    
    def sample_rate(self):
        return self._sample_rate

    def get_center_frequency(self):
        return self.source.get_center_freq()
