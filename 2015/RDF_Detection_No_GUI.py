#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Rdf Detection No Gui
# Generated: Mon Oct 26 23:51:08 2015
##################################################

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import fft
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from optparse import OptionParser
from radiosource import RadioSource
from collar_detect import collar_detect
import sys
import time
import time
import math

fft_size = 512
samp_rate = 93750
collar_freq = 151823000
freq_offset = 3000
bandwidth = 1000
gains = [8, 8, 15] #[1, 1, 15] #LNA: 1, MIXER: 1, IF: 20 as per prev group
SNR = 5.0

class RDF_Detection_No_GUI(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Rdf Detection No Gui")

        ##################################################
        # Variables
        ##################################################
        global fft_size
        global samp_rate
        global collar_freq
        global freq_offset
        global bandwidth	
        global gains
        global SNR
        self.fft_size = fft_size
        self.samp_rate = samp_rate
        self.collar_freq = collar_freq 
        self.freq_offset = freq_offset
        self.bandwidth = bandwidth
        self.gains = gains
        self.SNR = SNR

        ##################################################
        # Blocks
        ##################################################
        self.source = RadioSource(
            preferred_sample_rate=self.samp_rate,
            gains=self.gains,
            frequency_offset=self.freq_offset,
            signal_frequency=self.collar_freq)
        #self.fcdproplus_fcdproplus_0 = fcdproplus.fcdproplus("",1)
        #self.fcdproplus_fcdproplus_0.set_lna(1)
        #self.fcdproplus_fcdproplus_0.set_mixer_gain(1)
        #self.fcdproplus_fcdproplus_0.set_if_gain(gain) #20
        #self.fcdproplus_fcdproplus_0.set_freq_corr(0)
        #self.fcdproplus_fcdproplus_0.set_freq(collar_freq - 3000)
        
        self.fft_vxx_0 = fft.fft_vfc(self.fft_size, True, (window.rectangular(self.fft_size)), 1)
        self.collar_detect_Burst_Detection_0 = collar_detect(self.samp_rate, self.fft_size, 
            self.freq_offset, self.bandwidth, self.SNR)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_float*1, self.fft_size)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(self.fft_size)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(self.fft_size)
        self.band_pass_filter_0 = filter.fir_filter_ccf(1, firdes.band_pass( #1 instead of 12 to keep 93750 rate
            100, self.samp_rate, self.freq_offset - (self.bandwidth / 2),
            self.freq_offset + (self.bandwidth / 2), 600, firdes.WIN_RECTANGULAR, 6.76))

        ##################################################
        # Connections
        ##################################################
        self.connect((self.source, 0), (self.band_pass_filter_0, 0))
        self.connect((self.band_pass_filter_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.fft_vxx_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.collar_detect_Burst_Detection_0, 0))

    '''def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.band_pass_filter_0.set_taps(firdes.band_pass(100, self.samp_rate, 2.5e3, 3.5e3, 600, firdes.WIN_RECTANGULAR, 6.76))

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.fcdproplus_fcdproplus_0.set_if_gain(self.gain)

    def get_collar_freq(self):
        return self.collar_freq

    def set_collar_freq(self, freq):
        global collar_freq
        collar_freq = freq
        self.fcdproplus_fcdproplus_0.set_freq(collar_freq - 3000)

    def get_SNR(self):
        return self.SNR

    def set_SNR(self, snr):
	global SNR
        SNR = snr
	print SNR
	
    def update_vars(self, rcvd_msg):
	global bearing_deg
	global collar_freq
	collar_freq = rcvd_msg.data[0]
	self.collar_detect_Burst_Detection_0.update_SNR(rcvd_msg.data[2])
	self.collar_detect_Burst_Detection_0.update_scanning(rcvd_msg.scanning,bearing)
	self.fcdproplus_fcdproplus_0.set_freq(collar_freq - 3000)
	self.fcdproplus_fcdproplus_0.set_if_gain(rcvd_msg.data[1])'''

sigproc = RDF_Detection_No_GUI()

while True:
    sigproc.start()
    time.sleep(5)
    sigproc.stop()
    sigproc.wait()
