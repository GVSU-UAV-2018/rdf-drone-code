''' RDF UAV
' Provides a MavLink interface to Mission Planner
' via the flight controller on the 3DR Solo. Runs
' GNU radio scripts as necessary.
'
' GVSU UAV Team 2018
'''

import watchdog
watchdog.keep_alive(5)

import os
import time
import sys
import math
import numpy
from argparse import ArgumentParser
from gnuradio import gr
from gnuradio import blocks

from pymavlink import mavutil

import programsetup
from blocks.radiosource import RadioSource
from blocks.psd import PowerSpectralDensity
from blocks.signal_detection_method import *
from blocks.snrextract import SNRExtract

#TODO: use configuration file for all of these parameters

connection_string = "/dev/serial0"
baud_rate = 57600
src_id = 1
comp_id = 177

current_VHF_FREQ = 151.823
current_VHF_SNR = 0.0

snr_wait_time = 5

gr_sigprocessing = None

argp = ArgumentParser()
config_defaults = programsetup.get_file_config()
programsetup.add_config_section_acquisition(argp, config_defaults['acquisition'])
programsetup.add_config_section_system(argp, config_defaults['system'])
programsetup.add_config_section_signal_detection(argp, config_defaults['signal detection'])
config = argp.parse_args()
print('Configuration:')
print(config)

snr_wait_time = config.time
messages = ['COMMAND_LONG', 'HEARTBEAT', 'PARAM_SET']


class SigProcessing(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)

        self.source = RadioSource(
            preferred_sample_rate=config.sample_rate,
            gains=config.gains,
            frequency_offset=config.frequency_offset,
            signal_frequency=(int)(current_VHF_FREQ * 1000000))

        self.psd = PowerSpectralDensity(
            num_fft_bins=config.fft_resolution)

        self.processing = select_detection_method(config.detection_method)(
            num_bins=config.fft_resolution,
            center_frequency=(int)(current_VHF_FREQ * 1000000),
            signal_frequency=(int)(current_VHF_FREQ * 1000000)+config.frequency_offset,
            signal_bandwidth=config.signal_bandwidth,
            threshold=config.snr_threshold,
            decay_time=config.detection_interval)

        self.extract = SNRExtract(sample_snr = 0)

        self.connect(self.source, self.psd, self.processing, self.extract)

        self.psd.set_sample_rate(config.sample_rate)
        self.processing.set_sample_rate(self.psd.output_sample_rate())

def run_scan(msg):
    global current_VHF_SNR
    global gr_sigprocessing
    global snr_wait_time
    global snr_threshold

    scan_completed = False

    print "RDF scanning..."

    # TODO: This loop blocks and runs once. Make it cancelable/non-blocking and an actual loop
    while not scan_completed: #blocking is okay... cancel scan handled by MP
        watchdog.keep_alive(snr_wait_time + 5)
        gr_sigprocessing.start() #start gnu radio processing
        time.sleep(snr_wait_time)
        gr_sigprocessing.stop() #stop gnu radio processing
        gr_sigprocessing.wait() #keep alive

        current_VHF_SNR = max(gr_sigprocessing.extract.snr_samples)

        gr_sigprocessing.extract.snr_samples = []
        print "RDF scan complete. VHF_SNR: " + str(current_VHF_SNR)
        print "Sending VHF_SNR..."

        mavlink_con.mav.param_set_send(0, 0, "VHF_SNR", current_VHF_SNR, 9)
        print "VHF_SNR sent"
        scan_completed = True

def set_vhf_freq(msg):
    global current_VHF_FREQ
    global gr_sigprocessing

    print "Setting VHF_FREQ..."
    current_VHF_FREQ = msg.param_value
    gr_sigprocessing = None
    gr_sigprocessing = SigProcessing()
    print "VHF_FREQ: " + str(current_VHF_FREQ)

def send_hb(msg):
    mavlink_con.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER, 
        mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, mavutil.mavlink.MAV_STATE_ACTIVE)

print "Setting up MavLink com on " + connection_string
print "Setting Pi System ID: " + str(src_id)
print "Setting Pi Comp ID: " + str(comp_id)
mavlink_con = mavutil.mavlink_connection(connection_string, 
    baud=baud_rate, source_system=src_id, source_component=comp_id)
print "Connection ok"

print "Waiting for drone HEARTBEAT..."
watchdog.keep_alive(5)
mavlink_con.wait_heartbeat()
print "Received drone HEARTBEAT"

print "Sending initial HEARTBEAT..."
mavlink_con.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
    mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, mavutil.mavlink.MAV_STATE_BOOT)
print "HEARTBEAT sent"

gr_sigprocessing = SigProcessing()

while True:

    watchdog.keep_alive(5)
    msg = mavlink_con.recv_match(type=messages, blocking=False)

    if msg is not None:
        msg_type = msg.get_type()
        if msg_type != 'HEARTBEAT':
            print "Received " + str(msg_type) + " message"

        if msg_type == 'COMMAND_LONG':
            if msg.command == mavutil.mavlink.MAV_CMD_USER_1:
                run_scan(msg)
        elif msg_type == 'PARAM_SET':
            if msg.param_id == 'VHF_FREQ':
                set_vhf_freq(msg)
        elif msg_type == 'HEARTBEAT':
            send_hb(msg)
