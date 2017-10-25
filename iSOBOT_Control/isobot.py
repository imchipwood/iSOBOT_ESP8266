import requests
import ping
import socket
import time
import re

# Code pulled from
# http://web.cecs.pdx.edu/~mperkows/CLASS_479/Projects-2012/Mathias_Sunardi-iSobot_controller_report.pdf


class iSobotException(Exception):
	pass


class iSobot(object):
	def __init__(self, url="http://192.168.4.1", channel=0, debug=False):
		print("{} - channel {}".format(url, channel))
		self._url = None
		self.url = url
		assert channel in [0, 1]
		self.channel = channel
		self.debug = debug

	@staticmethod
	def _ping(url):
		try:
			print("{} - Checking connection ".format(url))
			ping.do_one(url, timeout=5, psize=1)
		except socket.error as e:
			print("{} - ERROR Can't connect".format(url))
			raise e

	@property
	def url(self):
		return self._url

	@url.setter
	def url(self, url):
		self._ping(url)
		self._url = url

	"""
	 # Construct command string
	 # Returns integer. To use: convert returned value using hex() then process as array of characters excluding '0x'
	 # How to construct isobot command string:
	 ## command = [channel (1 bit)]:[type (2 bits)]:[checksum (3 bits)]:[commandbyte1 (8 bits)]:[commandbyte2 (8 bits)]:[params (8 bits)]
	 ## channel: 0 -> Mode A, 1 -> Mode B
	 ## type: 00 -> Type 0, 01 -> Type 1
	 ## checksum: How to calculate:
	 ### 1. add the header bits (channel, type, and checksum). For this, just give checksum 0x00 in the calculation.
	 ### After the calculation, this value will be updated.
	 ### 2. Do sum (logical OR) on the sum bits, 3 bits at a time. (see below: implemented as 3-bits right-shift)
	 ### 3. Return the last three bits of this value as the checksum.
	 ### 4. Add the checksum to the header bits (just do normal +)
	 ## commandbyte1: see isobot.py for the command bytes
	 ## commandbyte2: see isobot.py for the command bytes. Not used in command Type 1
	 ## params: ALWAYS 0x03 (don't know what it is for)
	 # Example:
	 ## For Mode A (channel bit: 0), Type 1 (type bits: 01), checksum (bits: 000):
	 ### header_bits = channel:type:checksum
	 ### = 0:01:000
	 ### Notice this is a 6-bits string. You must look at it as a byte.
	 ### header_bits (as byte, in hex) = 00001000 = 0x08
	 ## For Mode B (channel bit: 1), Type 1 (type bits: 01), checksum (bits: 000):
	 ### header_bits = 1:01:000
	 ### header_bits (as byte, in hex) = 00101000 = 0x28
	 ## Walk forward byte: CMD_FWRD = 0xb7 = 10110111 (see  isobot.py)
	 ## Params: 0x03 = 00000011
	 ## command string in Mode A, Type 1 (checksum not calculated yet): [header_bits]:[walkforwardbyte]:[params] = [00101000]:[10110111]:[00000011]
	 ## Caculate checksum:
	 ### sum = 0x28 + 0xb7 + 0x03
	 ### = 226 = 0xe2 = 11100010
	 ### take and sum 3 bits at a time (i.e. scan 3 bits at a time from right to left)
	 ### 010 + 100 + 011 (padded with zero) = (1)001
	 ### The total is actually 9 (0x09) but we only use the last three bits. So checksum = 0x01
	 ## Add the checksum to the header bits:
	 ### 0x28 + 0x01 = 0x29 = 00101001
	 ## The command string becomes: [00101000]:[10110111]:[00000011] = 0x29b703
	"""

	def calcChecksum(self, header, byte0, byte1, byte2):
		s = header + byte0 + byte1 + byte2
		s = (s & 7) + ((s >> 3) & 7) + ((s >> 6) & 7)
		return s & 7

	def makeCmd(self, cmdType=1, cmd1=0, cmd2=0):
		if cmdType not in [0, 1]:
			raise iSobotException("{} - Channel or command type invalid. Valid channels/types are '0' and '1'".format(self.url))

		# param is constant @ 0x03
		param = 0x03

		# Calculate checksum
		header = (self.channel << 5) + (cmdType << 3)
		checksum = self.calcChecksum(header, cmd1, cmd2, param)
		headersum = header + checksum

		if cmdType == 0:
			# two cmds
			return hex((headersum << 24) + (cmd1 << 16) + (cmd2 << 8) + param)
		else:
			# one command
			return hex((headersum << 16) + (cmd1 << 8) + param)

	def sendCmd(self, cmd):
		try:
			url = "{}/cmd:{}".format(self._url, cmd)
			r = requests.post(url, data={'cmd': cmd}, timeout=5)
			if r.status_code == 200:
				if self.debug:
					print("{} - HTTP Post success!".format(self.url))
			else:
				print("{} - HTTP Post failed. Status, reason: {}, {}".format(self.url, r.status_code, r.reason))
		except requests.exceptions.ConnectionError as e:
			print("{} - HTTP post failed: {}".format(self.url, e))
		except Exception as e:
			raise e

	# Repeat sending command
	# Default # of tries: 300. Some actions (e.g. Walk) require the command to be sent for a period of time.
	# e.g. sending the Walk FWRD command once, the robot will accept the command but not move forward
	def repeatCmd(self, cmd, rep=300):
		for i in range(rep):
			self.sendCmd(cmd)
			time.sleep(0.1)

	def formatType1Cmd(self, cmd):
		"""Format the hex string"""
		# Remove leading 0x in hex string
		cmd = re.sub(r'0x', '', cmd)

		# The string must be 6 digits long
		cmd = cmd.zfill(6)
		
		# Needs carriage return
		cmd += '\r'

		if self.debug:
			print("{} - Command string: {}".format(self.url, cmd))
		return cmd

	def isobotDoType1(self, action, repeat=3):
		# Shorthand function for lazy people
		try:
			cmd = self.formatType1Cmd(self.makeCmd(1, action))
			self.repeatCmd(cmd, repeat)
		except Exception as e:
			print("{} - FAILED: action {}, repeat {}".format(self.url, action, repeat))
			raise e

		return True


if __name__ == "__main__":

	bot = iSobot()
	commands = [
		(bot.CMD_CHEER1, 1),
		('sleep 8', 0),
		(0x00, 2),
		(bot.CMD_FWRD, 10),
		(bot.CMD_GORILLA, 1),
		# (bot.CMD_MOONWALK),
		# (bot.CMD_42B),
		# (bot.CMD_1P),
		# (bot.CMD_3BEEPS),
		# (bot.CMD_2G),
		# (0x00),
		# (bot.CMD_21K),
		# (bot.CMD_22K),
	]
	try:
		for cmd, repeat in commands:
			if isinstance(cmd, str):
				sleepLength = int(cmd.split(' ')[-1])
				print('sleeping {}'.format(sleepLength))
				time.sleep(sleepLength)
			else:
				print("{},{:02x}".format(ch, cmd))
				bot.isobotDoType1(cmd, repeat=repeat)
				time.sleep(1)
			# time.sleep(8)

	except KeyboardInterrupt:
		print("keyboard interrupt, stopping")
		pass
	except Exception as e:
		raise e
