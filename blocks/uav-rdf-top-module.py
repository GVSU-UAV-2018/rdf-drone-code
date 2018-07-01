'''
' RDF UAV
' Provides a MavLink interface to Mission Planner
' via the flight controller on the 3DR Solo. Runs
' GNU radio scripts as necessary.
'
' GVSU UAV Team 2018
'''
import time
import sys
from pymavlink import mavutil

from snrextract import SNRExtract

connection_string = "COM5"
baud_rate = 57600
src_id = 1
comp_id = 177

current_VHF_FREQ = 0.0
current_VHF_SNR = 12.322


def run_scan(msg):
	global current_VHF_SNR
	scan_completed = False
	
	print "RDF scanning..."
	sys.stdout.flush()
	#run top_block 
	
	while not scan_completed: #blocking is okay... cancel scan handled by MP
		#Check for SNR value. Simulate for now
		snr_good = 0.0
		snr_good_count = 0
		time.sleep(5) #make this configurable
		
		for x in SNRExtract.snr_samples:
			if x > 5: #make this configurable too
				snr_good += x
				snr_good_count += 1
		if snr_good_count > 0:
			current_VHF_SNR = snr_good / snr_good_count
		else:
			current_VHF_SNR = sum(SNRExtract.snr_samples) / len(SNRExtract.snr_samples)
	
		print "RDF scan complete. VHF_SNR: " + str(current_VHF_SNR)
		print "Sending VHF_SNR..."
		sys.stdout.flush()		
	
		mavlink_con.mav.param_set_send(0, 0, "VHF_SNR", current_VHF_SNR, 9)
		print "VHF_SNR sent"
		sys.stdout.flush()
		scan_completed = True
	
def set_vhf_freq(msg):
	global current_VHF_FREQ
	
	print "Setting VHF_FREQ..."
	sys.stdout.flush()
	current_VHF_FREQ = msg.param_value
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
mavlink_con.wait_heartbeat()
print "Received drone HEARTBEAT"
print "Sending initial HEARTBEAT..." 
sys.stdout.flush()
mavlink_con.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER, 
	mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, mavutil.mavlink.MAV_STATE_BOOT)
print "HEARTBEAT sent" 
sys.stdout.flush()

while True:
	print "Listenting for MavLink message..."
	sys.stdout.flush()
	
	#block while waiting for message to be sent. Blocking ok in this context
	msg = mavlink_con.recv_match(blocking=True)
	
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