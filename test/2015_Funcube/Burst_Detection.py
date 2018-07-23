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
var_avg = 0.0
var_avg_temp = 0.0
prev_time = 0.0
collar_offset = 3000
sample_freq_decim = 16000.0
collar_bandwidth = 1000.0
max_bin = int(((collar_offset+collar_bandwidth/2)/sample_freq_decim) * 512)
min_bin = int(((collar_offset-collar_bandwidth/2)/sample_freq_decim) * 512)
v_avg = numpy.array([0.0,0.0])
detection = numpy.array([0.0,0.0])
prv_scanning = 0
num_detections = 0.0

class Burst_Detection(gr.sync_block):
    """
    docstring for block Burst_Detection
    """
    def __init__(self, SNR):
        gr.sync_block.__init__(self,
            name="Burst_Detection",
            in_sig=[(numpy.float32,512)],
            out_sig=None)
	self.SNR = SNR
	self.scanning = 0

    def update_SNR(self,SNR):
	self.SNR = SNR

    def update_scanning(self,scanning,bearing):
	self.scanning = scanning
	self.bearing = bearing

    def get_detection(self):
	global detection
	return detection

    def work(self, input_items, output_items):
        global var_avg
	global min_bin
	global max_bin
	global average_mag
	global i
	global var_avg_temp
	in0 = input_items[0]
	global v_avg
	global detection
	global prv_scanning
	global num_detections
	
	noise_mean = numpy.mean(in0[0][min_bin:max_bin])
	noise_norm = numpy.asarray(in0[0][min_bin:max_bin]) - noise_mean
	noise_var = numpy.var(noise_norm)
	
	if(i<31):
		var_avg_temp = var_avg_temp + noise_var
		i = i + 1	
	else:
		var_avg = var_avg_temp / 31
		var_avg_temp = 0.0
		i = 0

	if(noise_var > self.SNR*var_avg):
		#if there is a change in state of scanning, and it was not scanning prior
		if((self.scanning != prv_scanning) and (prv_scanning == 0)):
			v_avg = numpy.array([0.0,0.0])
			num_detections = 0.0
			prv_scanning = self.scanning
		elif((self.scanning != prv_scanning) and (prv_scanning == 1)):
			v_avg = v_avg / num_detections
			detection_mag = numpy.linalg.norm(v_avg)
			detection_ang = numpy.arctan2(v_avg[1],v_avg[0]) 
			if (detection_ang < 0):
	    			detection_ang += 2 * math.pi
			detection_ang = math.degrees(detection_ang)
			detection = numpy.array([detection_mag, detection_ang])
			prv_scanning = self.scanning
		else:
			prv_scanning = self.scanning	
		if(self.scanning == 1):
			v_avg = v_avg + numpy.array([numpy.max(noise_norm)*math.cos(self.bearing),numpy.max(noise_norm)*math.sin(self.bearing)])
			num_detections += 1.0

	return len(input_items[0])
