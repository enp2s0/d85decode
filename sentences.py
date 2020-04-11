import struct

class DroneSentenceProcessor:
	last_packet_id = -1
	sentence_len = -1
	latitude = -1
	longitude = -1
	altitude = -1
	distance = -1
	fence_alt = -1
	fence_radius = -1
	flight_mode = -1
	voltage = -1
	gps_fix_count = -1
	status1 = -1
	control_signal = -1

	alt_flight_mode = ""

	camera_status = ""

	has_data = False

	def __init__(self):
		pass

	def feed(self, sentence):
		# Decode basic data common to all sentences.
		msg_len = int(sentence[4])
		self.last_packet_id = int(sentence[7])
		msg_type = int(sentence[13])

		if msg_len == 0:
			# This should never happen, but if it does, catch it before trying to decode it.
			print("Error: empty sentence received.")
		elif msg_type == 0:

			pass
		elif msg_type == 1:
			print(f"{self.last_packet_id:3} | " + self.decodeStatusSentence(sentence))
		elif msg_type == 2 or msg_type == 3:
			print(f"{self.last_packet_id:3} | " + "Unsupported: SetParam")
		elif msg_type == 4:
			if self.alt_flight_mode == "":
				self.alt_flight_mode = "following"
				print(f"{self.last_packet_id} | Follow mode activated.")
		elif msg_type == 5:
			if self.alt_flight_mode == "following":
				self.alt_flight_mode = ""
				print(f"{self.last_packet_id} | Follow mode deactivated.")
		elif msg_type == 6:
			if self.alt_flight_mode == "":
				self.alt_flight_mode = "orbiting"
				print(f"{self.last_packet_id} | Orbit mode activated.")
		elif msg_type == 7:
			if self.alt_flight_mode == "orbiting":
				self.alt_flight_mode = ""
				print(f"{self.last_packet_id} | Orbit mode deactivated.")
		elif msg_type == 8:
			if self.alt_flight_mode == "":
				self.alt_flight_mode = "guided"
				print(f"{self.last_packet_id} | Guided flight mode activated.")
		elif msg_type == 9:
			if self.alt_flight_mode == "guided":
				self.alt_flight_mode = ""
				print(f"{self.last_packet_id} | Guided flight mode deactivated.")
		elif msg_type == 16:
			print(f"{self.last_packet_id:3} | " + "Unsupported: Alt GuidedMode")
		elif msg_type == 22:
			if self.alt_flight_mode == "":
				self.alt_flight_mode = "rtl"
				print(f"{self.last_packet_id} | Return-to-home activated.")
		elif msg_type == 23:
			if self.alt_flight_mode == "rtl":
				self.alt_flight_mode = ""
				print(f"{self.last_packet_id} | Return-to-home deactivated.")
		elif msg_type == 24 or msg_type == 25:
			print(f"{self.last_packet_id:3} | " + "Unsupported: Camera/Video")
		elif msg_type == 26: # wifi switch
			print(f"{self.last_packet_id:3} | " + "Unsupported: WiFi Switch")
		elif msg_type == 69 or msg_type == 78:
			# See PROTOCOL.md for why these exist and why they are abnormally large.
			print(f"{self.last_packet_id:3} | " + self.decodeCameraSentence(sentence))
		else:
			# Print some basic information if we get an unsupported sentence.
			print(f"{self.last_packet_id:3} | Unknown sentence: type: {msg_type:2x}, len: {msg_len:4}")

	def decodeStatusSentence(self, sentence):
		# I got these byte locations through trial-and-error and reverse
		# engineering the Potensic-M2 Android application.
		self.sentence_len = int(sentence[14])
		self.latitude = struct.unpack('i', sentence[16:20])[0] / 10000000
		self.longitude = struct.unpack('i', sentence[20:24])[0] / 10000000
		self.altitude = struct.unpack('h', sentence[24:26])[0]
		self.distance = struct.unpack('h', sentence[26:28])[0]
		self.fence_alt = struct.unpack('h', sentence[28:30])[0]
		self.fence_distance = struct.unpack('h', sentence[30:32])[0]
		self.fence_radius = int(sentence[32])
		self.flight_mode = int(sentence[33])
		self.voltage = int(sentence[34]) / 10
		self.gps_fix_count = int(sentence[35])
		self.status1 = int(sentence[36])
		self.control_signal = int(sentence[37])
		self.has_data = True
		return f"lat: {self.latitude:3.7f}, lon: {self.longitude:3.7f}, alt: {self.altitude:3}m, dist: {self.distance:4}m, fm: {self.flight_mode_str():17}, bat: {self.voltage}V, fix: {self.gps_fix_count:2}"

	def decodeCameraSentence(self, sentence):
		# Decode the sentence. These sentences are pretty simple, with just a
		# string field describing the operation.
		self.camera_status = str(sentence [12:].decode("utf-8"))
		self.has_data = True

		# TODO: handle any error codes that we might receive.
		# I haven't seen any errors during my flights, but it *could*
		# happen and would result in a "Camera status unknown" error here.
		#
		# TODO: properly handle video start vs. video end. This difficult
		# because we appear to get the same message for start and end events,
		# and I would really like to avoid local state in this program (it
		# could cause desyncs if we lose packets, which is very possible when
		# using UDP over a wireless link to a drone).
		if self.camera_status == "": # This should never happen.
			return "No data available!"
		elif self.camera_status == "SNAP_OK": # Received when the drone successfully takes a picture.
			return "Picture OK."
		elif self.camera_status == "REC_OK": # Received when the drone starts or ends a video.
			return "Record OK."
		else:
			return "Camera status unknown!"

	def flight_mode_str(self):
		# Convert the flight_mode variable to a descriptive string.
		if self.flight_mode == 0:
			return "         grounded"
		if self.flight_mode == 1:
			return "    manual flight"
		if self.flight_mode == 2:
			return "gps-assist flight"
		if self.flight_mode == 3:
			return "   return-to-home"
		if self.flight_mode == 5:
			return "         orbiting"
		return f"unknown: {self.flight_mode}"
