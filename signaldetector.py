

from gnuradio import gr
from gnuradio import blocks

import programsetup
from blocks.radiosource import RadioSource
from blocks.psd import PowerSpectralDensity
from blocks.signal_detection_method import *
from blocks.asyncsink import AsyncSink

class SignalDetector(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, config)

        self._start_time = -1
        self._end_time = 0
        self._running = False

        self.source = RadioSource(
            preferred_sample_rate=config.sample_rate,
            frequency_offset=config.frequency_offset)

        self.psd = PowerSpectralDensity(
            num_fft_bins=config.fft_resolution)

        self.processing = select_detection_method(config.detection_method)(
            num_bins=config.fft_resolution,
            center_frequency=0,
            signal_frequency=config.frequency_offset,
            signal_bandwidth=config.signal_bandwidth,
            threshold=config.snr_threshold,
            decay_time=config.detection_interval)

        self.extract = AsyncSink(sample_snr = 0)

        self.connect(self.source, self.psd, self.processing, self.extract)

        self.psd.set_sample_rate(config.sample_rate)
        self.processing.set_sample_rate(self.psd.output_sample_rate())


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
        print('Setting gain {0} to {1}'.format(stage, gains))
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
        return int((time.time() - self._start_time)
            * 1.0 / (self._end_time - self._start_time))

    def time_remaining(self)
        if not self.running():
            return 0
        return self._end_time - time.time()


    def pop_samples(self):
        return self.extract.pop_all()
