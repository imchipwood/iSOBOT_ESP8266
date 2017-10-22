import time
import csv

from isobot import iSobot


class iSobotAuto(iSobot):
	def __init__(self, url="http://192.168.4.1", channel=0, commandPath=None, debug=False):
		super(iSobotAuto, self).__init__(url, channel, debug)
		self.commandPath = commandPath
		self.commands = {}

	def parseCommandFile(self):
		fieldnames = ['Command', 'Duration']
		with open(self.commandPath, 'r') as inf:
			# list of dicts
			self.commands = csv.DictReader(inf, fieldnames=fieldnames)

	def start(self):
		for command in self.commands:
			action = command['Command']
			duration = int(command['Duration'])
			if action == 'sleep':
				time.sleep(duration)
			else:
				self.isobotDoType1(action=action, repeat=duration)
