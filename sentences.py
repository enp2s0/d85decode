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

	camera_status = ""

	has_data = False

	def __init__(self):
		pass

	def feed(self, sentence):
		# Decode basic data common to all sentences.
		msg_len = int(sentence[4])
		self.last_packet_id = int(sentence[7])
		msg_type = int(sentence[14])

		if msg_len == 0: # This should never happen, but if it does, catch it before trying to decode it.
			print("Error: empty sentence received.")
		elif msg_type == 0x1A: # Drone Status Sentence, sent periodically (seems to be about 2/sec)
			self.decodeStatusSentence(sentence)
		elif msg_type == 0x41: # Camera Status Sentence, sent when a picture is taken
			self.decodeCameraSentence(sentence)
		elif msg_type == 0x43: # Video Status Sentence, sent when a video is started or ended.
			self.decodeCameraSentence(sentence)
		elif msg_type == 0x05: # Mode Update Sentence, sometimes sent when the flight mode is changed.
			self.decodeModeUpdateSentence(sentence)
		else: # Print some basic information if we get an unsupported sentence.
			print(f"{msg_id:3} | Unknown sentence:  type: {msg_type:2x}, len: {msg_len:4}")

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
			print("No data available!")
		elif self.camera_status == "SNAP_OK": # Received when the drone successfully takes a picture.
			print(f"{self.last_packet_id:3} | Picture OK.")
		elif self.camera_status == "REC_OK": # Received when the drone starts or ends a video.
			print(f"{self.last_packet_id:3} | Record OK.")
		else:
			print("Camera status unknown!")

	def decodeModeUpdateSentence(self, sentence):
		# I have yet to find anything useful in this sentence. It seems to be sent
		# whenever you enable certian flight modes, but it doesn't seem to be
		# useful in any way.
		#
		# Interestingly, these messages always come in groups of 3.
		pass

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

	def print_pretty(self):
		# Print one line of status information.
		if self.has_data:
			print(f"lat: {self.latitude:3.7f}, lon: {self.longitude:3.7f}, alt: {self.altitude:3}m, dist: {self.distance:4}m, fm: {self.flight_mode_str():17}, bat: {self.voltage}V, fix: {self.gps_fix_count:2}")
		else:
			print("No data available!")
