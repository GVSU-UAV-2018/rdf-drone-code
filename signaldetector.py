import time
from gnuradio import gr
from gnuradio import blocks
from gnuradio import filter as gr_filter

import programsetup
import filterdesign
from blocks.radiosource import RadioSource
from blocks.signal_detection_method import *
from blocks.asyncsink import AsyncSink

class SignalDetector(gr.top_block):
    def __init__(self, config):
        gr.top_block.__init__(self, self.__class__.__name__)

        self._start_time = -1
        self._end_time = 0
        self._running = False

        self.source = RadioSource(
            preferred_sample_rate=config.sample_rate,
            frequency_offset=config.frequency_offset)

        n, d = filterdesign.bandpass(
            order=4,
            low=config.frequency_offset - config.signal_bandwidth * 0.5,
            high=config.frequency_offset + config.signal_bandwidth * 0.5,
            sample_rate=config.sample_rate)
        self.filter = gr_filter.iir_filter_ccc(n, d, oldstyle=False)

        self.vectorize = blocks.stream_to_vector(
            gr.sizeof_gr_complex,
            config.fft_resolution)

        self.processing = select_detection_method(config.detection_method)(
            num_bins=config.fft_resolution,
            center_frequency=0,
            signal_frequency=config.frequency_offset,
            signal_bandwidth=config.signal_bandwidth,
            threshold=config.snr_threshold,
            decay_time=config.decay_time,
            decay_strength=config.decay_strength)

        self.extract = AsyncSink()

        self.connect(
            self.source,
            self.filter,
            self.vectorize,
            self.processing,
            self.extract)

        self.processing.set_sample_rate(
            config.sample_rate / config.fft_resolution)


    def get_signal_frequency(self):
        return self.source.get_signal_frequency()

    def set_signal_frequency(self, signal_frequency):
        print('Setting signal frequency to {0}'.format(signal_frequency))
        self.source.set_signal_frequency(signal_frequency)

    def get_gain_names(self):
        return self.source.get_gain_names()

    def get_gains(self):
        return self.source.get_gains()

    def set_gains(self, gains):
        print('Setting gains to {0}'.format(gains))
        self.source.set_gains(gains)

    def set_gain(self, stage, gain):
        if type(stage) == int:
            stage = self.get_gain_names()[stage]
        print('Setting gain {0} to {1}'.format(stage, gain))
        self.source.set_gain(gain, stage)


    def start_scan(self, seconds):
        print('Starting scan...')
        self._start_time = time.time()
        gr.top_block.start(self)
        self._running = True
        self._end_time = self._start_time + seconds

    def stop_if_finished(self):
        if self.running() and time.time() >= self._end_time:
            print('Scan finished.')
            gr.top_block.stop(self)
            gr.top_block.wait(self)
            self._running = False

    def running(self):
        return self._running

    def percent_finished(self):
        if not self.running():
            return 0
        result = int((time.time() - self._start_time)
            * 100.0 / (self._end_time - self._start_time))
        if result < 0:
            return 0
        elif result > 99:
            return 99
        else:
            return result

    def time_remaining(self):
        if not self.running():
            return 0
        return self._end_time - time.time()


    def pop_samples(self):
        return self.extract.pop_all_samples()
