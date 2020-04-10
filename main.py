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
parser.add_argument("--all", help = "show all sentences that are received instead of just the meaningful ones", action = "store_true")
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
			msg_id = int(sentence[7])
			msg_type = int(sentence[14])

			if msg_len == 0: # This should never happen, but if it does, catch it before trying to decode it.
				print("Error: empty sentence received.")
			elif msg_type == 0x1A: # Drone Status Sentence, sent periodically (seems to be about 2/sec)
				SSP.feed(sentence = sentence)
				SSP.print_pretty()
				SSP.clear()
			elif msg_type == 0x41: # Camera Status Sentence, sent when a picture is taken
				CSP.feed(is_video = False, sentence = sentence)
				CSP.print_pretty()
				CSP.clear()
			elif msg_type == 0x43: # Video Status Sentence, sent when a video is started or ended.
				CSP.feed(is_video = True, sentence = sentence)
				CSP.print_pretty()
				CSP.clear()
			elif msg_type == 0x05: # Mode Update Sentence, sometimes sent when the flight mode is changed.
				# These sentences appear to be meaningless. Only show them if --all is specified.
				if args.all:
					print(f"{msg_id:3} | Mode Update Sentence")
			else: # Print some basic information if we get an unsupported sentence.
				print(f"{msg_id:3} | Unknown sentence:  type: {msg_type:2x}, len: {msg_len:4}")

	# If there is no data available...
	except BlockingIOError:
		# Sleep to lower CPU load. Without sleep(), the program ties up an entire
		# core throwing BlockingIOError as fast as it can, over and over again.
		# args.refresh is in milliseconds, sleep() takes seconds.
		time.sleep(args.refresh / 1000.0)
