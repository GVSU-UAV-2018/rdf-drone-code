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
from gnuradio import gr
from gnuradio import blocks

from pymavlink import mavutil

import programsetup
from blocks.radiosource import RadioSource
from blocks.psd import PowerSpectralDensity
from blocks.signal_detection_method import *
from blocks.snrextract import SNRExtract

connection_string = "/dev/ttyACM0"
baud_rate = 57600
src_id = 1
comp_id = 177

current_VHF_FREQ = 150.801
current_VHF_SNR = 0.0

#These need to be configurable
snr_wait_time = 5

gr_sigprocessing = None
os.chdir('/home/pi/rdf-drone-code')

config = programsetup.get_radio_cmdline_config()
print(config)

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
            signal_frequency=(int)(current_VHF_FREQ * 1000000),
            signal_bandwidth=config.signal_bandwidth,
            threshold=config.snr_threshold,
            decay_time=config.detection_interval)

        self.extract = SNRExtract(sample_snr = 0)

        self.connect(self.source, self.psd, self.processing, self.extract)

        self.psd.set_sample_rate(config.sample_rate)
        self.processing.set_sample_rate(self.psd.output_sample_rate)

def send_hb_pi():
    alive_file = open('/tmp/gvsu-rdf-alive', 'w+')
    alive_file.write("1")
    alive_file.close()

def run_scan():
    global current_VHF_SNR
    global gr_sigprocessing
    global snr_wait_time
    global snr_threshold

    scan_completed = False

    print "RDF scanning..."
    sys.stdout.flush()

    while not scan_completed: #blocking is okay... cancel scan handled by MP
        watchdog.keep_alive(snr_wait_time + 5)
        try:
            gr_sigprocessing.start() #start gnu radio processing
            time.sleep(int(snr_wait_time / 2))
            send_hb_pi()
            time.sleep(int(snr_wait_time / 2))
            gr_sigprocessing.stop() #stop gnu radio processing
            gr_sigprocessing.wait() #keep alive

            current_VHF_SNR = numpy.max(gr_sigprocessing.extract.snr_samples)
        except:
            print("Error: ", sys.exc_info()[0])
            scan_completed = False
            continue

        gr_sigprocessing.extract.snr_samples = []
        print "RDF scan complete. VHF_SNR: " + str(current_VHF_SNR)
        print "Sending VHF_SNR..."
        sys.stdout.flush()        

        mavlink_con.mav.param_set_send(0, 0, "VHF_SNR", current_VHF_SNR, 9)
        print "VHF_SNR sent"
        sys.stdout.flush()
        scan_completed = True

def set_vhf_freq(msg):
    global current_VHF_FREQ
    global gr_sigprocessing

    print "Setting VHF_FREQ..."
    sys.stdout.flush()
    current_VHF_FREQ = msg.param_value
    gr_sigprocessing = None
    gr_sigprocessing = SigProcessing()
    print "VHF_FREQ: " + str(current_VHF_FREQ)
    sys.stdout.flush()

def send_hb(msg):
    print "Sending HEARTBEAT..."
    sys.stdout.flush()
    mavlink_con.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER, 
        mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, mavutil.mavlink.MAV_STATE_ACTIVE)
    print "HEARTBEAT sent"
    sys.stdout.flush()




print "Setting up MavLink com on " + connection_string
print "Setting Pi System ID: " + str(src_id)
print "Setting Pi Comp ID: " + str(comp_id)
sys.stdout.flush()
mavlink_con = mavutil.mavlink_connection(connection_string, 
    baud=baud_rate, source_system=src_id, source_component=comp_id)
print "Connection ok"
print "Waiting for drone HEARTBEAT..."
sys.stdout.flush()
watchdog.keep_alive(5)
mavlink_con.wait_heartbeat()
print "Received drone HEARTBEAT"
print "Sending initial HEARTBEAT..." 
sys.stdout.flush()
mavlink_con.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER, 
    mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, mavutil.mavlink.MAV_STATE_BOOT)
print "HEARTBEAT sent" 
sys.stdout.flush()

snr_wait_time = config.time
gr_sigprocessing = SigProcessing()
messages = ['COMMAND_LONG', 'HEARTBEAT', 'PARAM_SET']

while True:
    print "Listenting for MavLink message..."
    sys.stdout.flush()

    watchdog.keep_alive(5)
    msg = mavlink_con.recv_match(type=messages, blocking=False)

    if msg is not None:
        msg_type = msg.get_type()
        print "Received " + str(msg_type) + " message"
        sys.stdout.flush()
        
        if msg_type == 'COMMAND_LONG':
            if msg.command == mavutil.mavlink.MAV_CMD_USER_1:
                run_scan(msg)
        elif msg_type == 'PARAM_SET':
            if msg.param_id == 'VHF_FREQ':
                set_vhf_freq(msg)
        elif msg_type == 'HEARTBEAT':
            send_hb(msg)

    send_hb_pi()
