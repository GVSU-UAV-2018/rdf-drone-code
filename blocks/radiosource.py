from fractions import Fraction

from gnuradio import gr
from gnuradio import blocks
from gnuradio import filter as gr_filter
import osmosdr

"""
Wrapper for osmosdr block.
Performs resampling (with anti-image/antialias filtering) to provide a sample rate
independent of the sample rates supported by the receiver.
"""

class RadioSource(gr.hier_block2):

    def __init__(self, preferred_sample_rate, frequency_offset, signal_frequency=None, gains=None):

        gr.hier_block2.__init__(self, "Radio Source",
            gr.io_signature(0, 0, gr.sizeof_gr_complex),
            gr.io_signature(1, 1, gr.sizeof_gr_complex))

        ##################################################
        # Blocks
        ##################################################
        self.source = osmosdr.source('sensitivity')
        self.frequency_offset = frequency_offset

        self.set_frequency(signal_frequency)
        self.set_gains(gains)

        self._set_closest_possible_sample_rate(preferred_sample_rate)
        self._set_closest_possible_prefilter(preferred_sample_rate)
        resample_ratio = self._calc_resample_ratio(preferred_sample_rate)
        self.resample = gr_filter.rational_resampler_ccc(
            interpolation=resample_ratio.numerator,
            decimation=resample_ratio.denominator)

        print('Selected output sample rate', self.sample_rate())


        ##################################################
        # Connections
        ##################################################
        self.connect(self.source, self.resample, self)


    def sample_rate(self):
        return (
            int(self.source.get_sample_rate())
            * int(self.resample.resampler.interpolation())
            / int(self.resample.resampler.decimation()))

    def get_center_frequency(self):
        return self.source.get_center_freq()

    def get_signal_frequency(self):
        return self.get_center_frequency() + self.frequency_offset

    def set_signal_frequency(self, signal_frequency):
        if signal_frequency is None:
            return
        self.source.set_center_freq(signal_frequency - self.frequency_offset)

    def get_gain_names(self):
        return self.source.get_gain_names()

    def get_gains(self):
        return [self.source.get_gain(n) for n in self.get_gain_names()]

    def set_gains(self, gains):
        if gains is None:
            return
        gain_stage_names = self.source.get_gain_names()
        actual_gains = [
            self.source.set_gain(g, n) for g, n in zip(gains, gain_stage_names)]
        if actual_gains == gains:
            print 'Set all gains'
        else:
            print 'Failed to set all gains'
        print('Gain stages', gain_stage_names)
        print('Attempted  ', gains)
        print('Actual     ', actual_gains)


    def _set_closest_possible_sample_rate(self, preferred_sample_rate):
        try:
            best_available_sample_rate = min(
                filter(
                    lambda r: r >= preferred_sample_rate,
                    self.source.get_sample_rates().values()))
            self.source.set_sample_rate(best_available_sample_rate)
        except ValueError:
            print 'Could not set internal sample rate'
        print(
            'Available sample rates: ',
            self.source.get_sample_rates().values())
        print('Selected input sample rate', self.source.get_sample_rate())

    def _set_closest_possible_prefilter(self, preferred_sample_rate):
        try:
            best_available_prefilter = min(
                filter(
                    lambda r: r >= preferred_sample_rate,
                    self.source.get_bandwidth_range().values()))
            self.source.set_bandwidth(best_available_prefilter)
        except ValueError:
            print 'Could not set prefilter'
        print(
            'Available prefilters: ',
            self.source.get_bandwidth_range().values())
        print('Selected prefilter', self.source.get_bandwidth())

    def _calc_resample_ratio(self, preferred_sample_rate):
        result = Fraction(
            int(preferred_sample_rate),
            int(self.source.get_sample_rate()))
        print('Interpolation', result.numerator)
        print('Decimation', result.denominator)
        return result
