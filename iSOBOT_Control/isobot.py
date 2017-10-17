import requests
import time
import re

# Code pulled from
# http://web.cecs.pdx.edu/~mperkows/CLASS_479/Projects-2012/Mathias_Sunardi-iSobot_controller_report.pdf


class iSobotException(Exception):
	pass


class iSobot(object):
	serialPort = 0
	# iSobot Command byte list
	# Source: http://minkbot.blogspot.com/2009/08/isobot-infrared-remote-protocol-hack.html
	# Standard commands
	CMD_RC = 0x07
	CMD_PM = 0x08
	CMD_SA = 0x09
	CMD_VC = 0x0a
	CMD_1P = 0x13  # left punch
	CMD_2P = 0x14  # right punch
	CMD_3P = 0x15  # left side whack (arm outwards)
	CMD_4P = 0x16  # right side whack
	CMD_11P = 0x17  # left + right punch
	CMD_12P = 0x18  # right + left punch
	CMD_13P = 0x19  # left up-down chop
	CMD_14P = 0x1a  # right up-down chop
	CMD_21P = 0x1b  # both up-down chop
	CMD_22P = 0x1c  # both down-up chop
	CMD_23P = 0x1d  # right + left punch, both up-down chop, both whack
	CMD_24P = 0x1e  # look left, up-down chop
	CMD_31P = 0x1f  # look right, up-down chop
	CMD_32P = 0x20  # "c'mon, snap out of it" slap
	CMD_34P = 0x21  # both whack
	CMD_1K = 0x22  # left wide kick
	CMD_2K = 0x23  # right wide kick
	CMD_3K = 0x24  # left kick
	CMD_4K = 0x25  # right kick
	CMD_11K = 0x26  # left side kick
	CMD_12K = 0x27  # right side kick
	CMD_13K = 0x28  # left back kick
	CMD_14K = 0x29  # right back kick
	CMD_31K = 0x2a  # right high side kick
	CMD_42K = 0x2b  # right soccer/low kick
	CMD_21K = 0x2c  # left + right high side kick
	CMD_22K = 0x2d  # right + left soccer/low kick
	CMD_23K = 0x2e  # combo kick low-left, high-side-right, left
	CMD_24K = 0x2f  # another left kick
	CMD_31K = 0x30  # right high kick
	CMD_34K = 0x31  # split
	CMD_1G = 0x32  # Block! "whoa buddy"
	CMD_2G = 0x33  # right arm block
	CMD_3G = 0x34  #
	CMD_4G = 0x35  # both arms block
	CMD_11G = 0x36  # dodge right (move left)
	CMD_12G = 0x37  # dodge left (move right)
	CMD_13G = 0x38  # headbutt
	CMD_14G = 0x39  # right arm to face
	CMD_21G = 0x3a  # taunt1
	CMD_22G = 0x3b  # hit & down
	CMD_23G = 0x3c  # dodge right, left, block left, head, fall down
	CMD_A = 0x3d
	CMD_B = 0x3e
	CMD_1A = 0x3f  # "Roger!" raise right arm
	CMD_2A = 0x40  # weird gesture
	CMD_2A = 0x41  # "All your base are belong to isobot"
	CMD_3A = 0x42  # "absolutely not!" flaps both arms
	CMD_4A = 0x43  # bow/crouch? and get back up
	CMD_11A = 0x44  # "Good morning!" raise both arms, stand on left foot
	CMD_12A = 0x45  # "Greetings I come in peace" wave right arm
	CMD_13A = 0x46  # "Y'all come back now, you hear!"
	CMD_14A = 0x47  # "Wassap!?" opens both arms sideways over and down
	CMD_21A = 0x48  # "Greetings human" raise left arm and bow
	CMD_22A = 0x49  # "It's an honor to meet you!" bow and shake right hand
	CMD_23A = 0x4a  # "Bye bye"
	CMD_31A = 0x4b  # "Bon voyage!"
	CMD_32A = 0x4c  # *clap* *clap* "Thanks! I'll be here all week" raise right arm
	CMD_33A = 0x4d  # "T-t-that's all robots!" raise left arm, stand on left foot
	CMD_41A = 0x4e  # "Domo arigato from isobot-o"
	CMD_42A = 0x4f
	CMD_43A = 0x50
	CMD_111A = 0x51
	CMD_222A = 0x52
	CMD_333A = 0x53
	CMD_11B = 0x54  # Walk forward + "Give me a bear hug"
	CMD_12B = 0x55
	CMD_13B = 0x56
	CMD_14B = 0x57
	CMD_31B = 0x58
	CMD_22B = 0x59
	CMD_23B = 0x5a
	CMD_24B = 0x5b
	CMD_31B = 0x5c
	CMD_32B = 0x5d  # "woe is me ... what to do ... what to do" bow, shakes head
	CMD_33B = 0x5e  # "No no .... not again. ... No no"
	CMD_234B = 0x5f  # "Oh, I can't believe I did that"
	CMD_41B = 0x60  # "I throw myself into a mercy" (?)
	CMD_42B = 0x61  # "Oh, like a dagger through my heart"
	CMD_43B = 0x62  # Same as 44B but no voice
	CMD_44B = 0x63  # "Ouch, that hurts!"
	CMD_112A = 0x65  # points left "wahoo"
	CMD_113A = 0x66  # pose northwest "hoo-ah!"
	CMD_114A = 0x67  # points left "kapwingg"
	CMD_124A = 0x6b  # "iz nice. you like?"
	CMD_131A = 0x6c  # both arm wave left right left
	CMD_132A = 0x6d  # drunk
	CMD_113B = 0x6e  # "no please make it stop." "please i can't take it anymore" "no no" lying down and get up
	CMD_114B = 0x6f  # "yippe yippe" 3 times, goal post arms
	CMD_121B = 0x70  # "ho ho ho ... <something-something> isobot"
	CMD_122B = 0x71  # "yeehaaw" both arm wave left right
	CMD_123B = 0x72
	CMD_124B = 0x73  # stand on one foot, goal post arms, "wow that's amazing"
	CMD_131B = 0x74  # bow, arms over head and down
	CMD_132B = 0x75
	CMD_133B = 0x76
	CMD_134B = 0x77
	CMD_141A = 0x78
	CMD_143A = 0x79  # sit cross legged
	CMD_144A = 0x7b  # ... owl?
	CMD_211B = 0x7c
	CMD_212B = 0x7d  # "Ahh, let me get comfortable. I'm too sexy for my servos" lie down, flips over, gets up
	CMD_213B = 0x7e
	CMD_221B = 0x80  # balancing act + bleeps (+)
	CMD_222B = 0x81  # looks like a push up
	CMD_223B = 0x82
	CMD_224B = 0x83  # "You can count on me"
	CMD_232B = 0x85
	CMD_233B = 0x86
	CMD_241B = 0x88  # headstand
	CMD_242B = 0x89
	CMD_A = 0x8a  # flip forward back forward about 3 times
	CMD_B = 0x8b
	CMD_AB = 0x8c
	CMD_AAA = 0x8d
	CMD_BBB = 0x8e
	CMD_BAB = 0x8f  # "BANZAI" 3 times
	CMD_ABB = 0x95  # chicken
	CMD_BBA = 0x97  # dancing (+)
	CMD_ABA = 0x98  # giant robot motion
	CMD_ABAB = 0x99
	CMD_AAAA = 0x9a
	CMD_FWRD = 0xb7
	CMD_BWRD = 0xb8
	CMD_FWLT = 0xb9
	CMD_FWRT = 0xba
	CMD_LEFT = 0xbb
	CMD_RGHT = 0xbc
	CMD_BKLT = 0xbd
	CMD_BKRT = 0xbe
	CMD_411A = 0xc7
	CMD_412A = 0xc8
	CMD_413A = 0xc9
	CMD_444B = 0xca
	CMD_444A = 0xcb  # nothing
	CMD_LVSoff = 0xd3
	CMD_HP = 0xd5
	CMD_NOIMP = 0xd6
	CMD_END = 0xd7
	MSG_NOIMP = 0x848080
	MSG_NOIMP = 0x848080
	MSG_RUP = 0x878280
	MSG_RDW = 0x808280
	MSG_RRT = 0x8480f0
	MSG_RLT = 0x848080
	MSG_LUP = 0x84f080
	MSG_LDW = 0x841080
	MSG_LRT = 0xec8080
	MSG_LLT = 0x0c8080

	# Bonus Commands
	CMD_TURNON = 0x01
	CMD_ACTIVATED = 0x02
	CMD_READY = 0x03
	CMD_RC_CONFIRM = 0x04
	CMD_RC_PROMPT = 0x05
	CMD_MODE_PROMPT = 0x06
	CMD_IDLE_PROMPT = 0x0B  # = 0x0C,= 0x0D,= 0x0E all the same
	CMD_HUMMING_PROMPT = 0x0F
	CMD_COUGH_PROMPT = 0x10
	CMD_TIRED_PROMPT = 0x11
	CMD_SLEEP_PROMPT = 0x12
	CMD_FART = 0x40  # 2A
	CMD_SHOOT_RIGHT = 0x64
	CMD_SHOOT_RIGHT2 = 0x68
	CMD_SHOOT2 = 0x69
	CMD_BEEP = 0x6a
	CMD_BANZAI = 0x7F  # "TAKARA TOMY"
	CMD_CHEER1 = 0x90
	CMD_CHEER2 = 0x91
	CMD_DOG = 0x92
	CMD_CAR = 0x93
	CMD_EAGLE = 0x94
	CMD_ROOSTER = 0x95
	CMD_GORILLA = 0x96
	CMD_LOOKOUT = 0xA1
	CMD_STORY1 = 0xA2  # knight and princess
	CMD_STORY2 = 0xA3  # ready to start day
	CMD_GREET1 = 0xA4  # good morning
	CMD_GREET2 = 0xA5  # do somthing fun
	CMD_POOP = 0xA6  # poops his pants
	CMD_GOOUT = 0xA7  # ready to go out dancing
	CMD_HIBUDDY = 0xA8  # .. bring a round of drinks
	CMD_INTRODUCTION = 0xA9
	CMD_ATYOURSERVICE = 0xAA
	CMD_SMELLS = 0xAB
	CMD_THATWASCLOSE = 0xAC
	CMD_WANNAPICEOFME = 0xAD
	CMD_RUNFORYOURLIFE = 0xAE
	CMD_TONEWTODIE = 0xAF
	# 0xB0 - nothing?
	CMD_SWANLAKE = 0xB1
	CMD_DISCO = 0xB2
	CMD_MOONWALK = 0xB3
	CMD_REPEAT_PROMPT = 0xB4
	CMD_REPEAT_PROMPT2 = 0xB5
	CMD_REPEAT_PROMPT3 = 0xB6
	# 0xB7-= 0xC4 single steps in different directions
	CMD_HEADSMASH = 0xC5
	CMD_HEADHIT = 0xC6
	# 0xCC-= 0xD2 - unknown (use param?)
	# after exercising one of these I am getting only beeps instead of voice/sounds
	# (looks like a tool to synchronize sound with moves)
	CMD_HIBEEP = 0xD3
	# = 0xD4 - unknown (use param?)
	CMD_BEND_BACK = 0xD8  # same untill = 0xDB
	CMD_SQUAT = 0xDB  # also = 0xDC # doesn't work (both)
	CMD_BEND_FORWARD = 0xDD
	CMD_HEAD_LEFT_60 = 0xDE
	CMD_HEAD_LEFT_45 = 0xDF
	CMD_HEAD_LEFT_30 = 0xE0
	CMD_HEAD_RIGHT_30 = 0xE1
	CMD_HEAD_RIGHT_45 = 0xE2
	CMD_HEAD_RIGHT_60 = 0xE3
	# seems identical to A & B getups
	CMD_GETUP_BELLY = 0xE4
	CMD_GETUP_BACK = 0xE5
	# E6 unknown
	CMD_HEAD_SCAN_AND_BEND = 0xE7
	CMD_ARM_TEST = 0xE8
	CMD_FALL_AND_LEG_TEST = 0xE9
	CMD_THANKYOUSIR = 0xEA
	CMD_ILOVEYOU_SHORT = 0xEB
	CMD_3BEEPS = 0xEC
	CMD_FALL_DEAD = 0xED
	CMD_3BEEPS_AND_SLIDE = 0xEE
	# EF-FF unknown

	def __init__(self, url="http://192.168.4.1"):
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

	def makeCmd(self, ch=0, cmdType=1, cmd1=0, cmd2=0):
		if ch not in [0, 1] or cmdType not in [0, 1]:
			raise iSobotException("Channel or command type invalid. Valid channels/types are '0' and '1'")

		# param is constant @ 0x03
		param = 0x03

		# Calculate checksum
		header = (ch << 5) + (cmdType << 3)
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
				print("HTTP Post success!")
			else:
				print("HTTP Post failed. Status, reason: {}, {}".format(r.status_code, r.reason))
		except requests.exceptions.ConnectionError as e:
			print("HTTP post failed: {}".format(e))
		except Exception as e:
			raise e

	# Repeat sending command
	# Default # of tries: 300. Some actions (e.g. Walk) require the command to be sent for a period of time.
	# e.g. sending the Walk FWRD command once, the robot will accept the command but not move forward
	def repeatCmd(self, cmd, rep=300):
		for i in range(rep):
			# print("Tx {}".format(i))
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
		
		print("Command string: {}".format(cmd))
		return cmd

	def isobotDoType1(self, action, channel=0, repeat=3):
		# Shorthand function for lazy people
		try:
			cmd = self.formatType1Cmd(self.makeCmd(channel, 1, action))
			self.repeatCmd(cmd, repeat)
		except Exception as e:
			print("FAILED: action {}, channel {}, repeat {}".format(action, channel, repeat))
			raise e

		return True


if __name__ == "__main__":

	bot = iSobot()
	commands = [
		# (0, bot.CMD_CHEER1),
		# (0, bot.CMD_GORILLA),
		# (0, bot.CMD_MOONWALK),
		# (0, bot.CMD_42B),
		# (0, bot.CMD_1P),
		# (0, bot.CMD_3BEEPS),
		# (0, bot.CMD_2G),
		(0, bot.CMD_FWRD),
		# (0, 0x00),
		# (0, bot.CMD_21K),
		# (0, bot.CMD_22K),
		# (1, 0x00),
	]
	try:
		for ch, cmd in commands:
			print("{},{:02x}".format(ch, cmd))
			bot.isobotDoType1(cmd, ch, repeat=10)
			time.sleep(8)

	except KeyboardInterrupt:
		print("keyboard interrupt, stopping")
		pass
	except Exception as e:
		raise e
