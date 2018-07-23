#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2015 <+YOU OR YOUR COMPANY+>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import scipy
import numpy
import math
from scipy import fftpack
from scipy import stats
from scipy import signal
from gnuradio import gr

i = 0
num_windows = 183 #31

var_avg = 0.0
var_avg_temp = 0.0
prev_time = 0.0

class collar_detect(gr.sync_block):
    """
    docstring for block collar_detect
    """
    def __init__(self, sample_rate, fft_size, collar_offset, bandwidth, SNR):
        gr.sync_block.__init__(self,
            name="collar_detect",
            in_sig=[(numpy.float32,fft_size)],
            out_sig=None)
        
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.collar_offset = collar_offset
        self.bandwidth = bandwidth
        self.SNR = SNR

        resolution = self.sample_rate / self.fft_size
        center = self.fft_size / 2
        offset = self.collar_offset * 1.0 / resolution
        bandwidth = self.bandwidth * 1.0 / resolution
        #self.min_bin = int(center + math.floor(offset - bandwidth / 2))
        #self.max_bin = int(center + math.ceil(offset + bandwidth / 2))
        self.min_bin = int(((self.collar_offset-self.bandwidth/2.0)/self.sample_rate) * self.fft_size) #I'm not sure about this
        self.max_bin = int(((self.collar_offset+self.bandwidth/2.0)/self.sample_rate) * self.fft_size) #I'm not sure about this
        print "Min bin: " + str(self.min_bin)
        print "Max bin: " + str(self.max_bin)

    def work(self, input_items, output_items):
        global var_avg
	global min_bin
	global max_bin
	global average_mag
	global i
	global var_avg_temp
	in0 = input_items[0]
	
	noise_mean = numpy.mean(in0[0][self.min_bin:self.max_bin])
	noise_norm = numpy.asarray(in0[0][self.min_bin:self.max_bin]) - noise_mean
	noise_var = numpy.var(noise_norm)
	
	if(i<num_windows):
		var_avg_temp = var_avg_temp + noise_var
		i = i + 1	
	else:
		var_avg = var_avg_temp / num_windows
		var_avg_temp = 0.0
		i = 0
	
	if(noise_var > self.SNR*var_avg):
	#	print numpy.max(noise_norm)
                print noise_var / var_avg
	        with open("data.txt", "a") as myfile:
                    myfile.write(str(noise_var / var_avg) + "\n")
	return len(input_items[0])

