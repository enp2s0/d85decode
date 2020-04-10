#/usr/bin/env python3

import binascii
import sys
import struct
import socket
import argparse

# All of the sentence-specific decoding stuff.
import sentences

# Set up command-line arguments.
parser = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter,
	description = "Decode and display data from a Potensic d85 drone.")
parser.add_argument("--ip", help = "IPv4 address to listen on", default = "0.0.0.0", type = str)
parser.add_argument("--port", help = "port to listen on", default = 8001, type = int)
parser.add_argument("--recvbuf", help = "size of UDP receive buffer", default = 4096, type = int)
args = parser.parse_args()

# Connect to the network.
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((args.ip, args.port))

print("Ready, waiting for data...")

# Main loop. Reads sentences and decodes them.
while True:
	sentence = sock.recv(args.recvbuf)

	# Decode basic data common to all sentences.
	msg_len = int(sentence[4])
	msg_type = int(sentence[8])

	if msg_len == 0: # This should never happen, but if it does, catch it before trying to decode it.
		print("Error: empty sentence received.")
	elif msg_type == 0xD0: # Drone Status Sentence, sent periodically (seems to be about 2/sec)
		processor = sentences.DroneStatusSentenceProcessor(sentence = sentence)
		processor.print_pretty()
	elif msg_type == 0x11: # Camera Status Sentence, sent when a picture is taken
		processor = sentences.CameraStatusSentenceProcessor(is_video = False, sentence = sentence)
		processor.print_pretty()
	elif msg_type == 0x12: # Video Status Sentence, sent when a video is started or ended.
		processor = sentences.CameraStatusSentenceProcessor(is_video = True, sentence = sentence)
		processor.print_pretty()
	else: # Print some basic information if we get an unsupported sentence.
		print(f"Unknown sentence received: id {msg_type}, len {msg_len}.")
