#/usr/bin/env python3

import binascii
import sys
import struct
import socket
import argparse
import time

# All of the sentence-specific decoding stuff.
import sentences

# Set up command-line arguments.
parser = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter,
	description = "Decode and display data from a Potensic d85 drone.")
parser.add_argument("--ip", help = "IPv4 address to listen on", default = "0.0.0.0", type = str)
parser.add_argument("--drone", help = "IPv4 address of the drone", default = "192.168.99.1", type = str)
parser.add_argument("--port", help = "port to listen on", default = 8001, type = int)
parser.add_argument("--recvbuf", help = "size of UDP receive buffer", default = 4096, type = int)
parser.add_argument("--refresh", help = "data refresh rate (milliseconds)", default = 10, type = int)
args = parser.parse_args()

# Connect to the network.
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(0)
sock.bind((args.ip, args.port))

SSP = sentences.DroneStatusSentenceProcessor()
CSP = sentences.CameraStatusSentenceProcessor()

print("Ready, waiting for data...")

# Main loop. Reads sentences and decodes them.
while True:
	try:
		sentence, drone_addr = sock.recvfrom(args.recvbuf)

		# Only listen to packets sent by the drone.
		if drone_addr[0] == args.drone:
			# Decode basic data common to all sentences.
			msg_len = int(sentence[4])
			msg_type = int(sentence[8])

			if msg_len == 0: # This should never happen, but if it does, catch it before trying to decode it.
				print("Error: empty sentence received.")
			elif msg_type == 0xD0: # Drone Status Sentence, sent periodically (seems to be about 2/sec)
				SSP.feed(sentence = sentence)
			elif msg_type == 0x11: # Camera Status Sentence, sent when a picture is taken
				CSP.feed(is_video = False, sentence = sentence)
			elif msg_type == 0x12: # Video Status Sentence, sent when a video is started or ended.
				CSP.feed(is_video = True, sentence = sentence)
			else: # Print some basic information if we get an unsupported sentence.
				print(f"Unknown sentence received: id {msg_type}, len {msg_len}.")

	# If there is no data available...
	except BlockingIOError:
		time.sleep(args.refresh / 1000.0)

	if SSP.has_new_data():
		SSP.print_pretty()
		SSP.clear()
	if CSP.has_new_data():
		CSP.print_pretty()
		CSP.clear()
