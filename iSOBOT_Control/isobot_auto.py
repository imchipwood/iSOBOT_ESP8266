import time
import csv

from isobot import iSobot
from isobot_commands import commands


class iSobotAuto(iSobot):
	def __init__(self, url="http://192.168.4.1", channel=0, commandPath=None, debug=False):
		super(iSobotAuto, self).__init__(url, channel, debug)
		self.commandPath = commandPath
		self.commands = self.parseCommandFile()

	def parseCommandFile(self):
		fieldnames = ['Command', 'Duration']
		commands = []
		with open(self.commandPath, 'r') as inf:
			reader = csv.DictReader(inf, fieldnames=fieldnames)
			# skip the header
			reader.next()
			# read each row into the list of commands
			for row in reader:
				commands.append(row)
		return commands

	def start(self):
		for command in self.commands:
			action = commands[command['Command']]
			duration = int(command['Duration'])
			if action == 'sleep':
				time.sleep(duration)
			else:
				self.isobotDoType1(action=action, repeat=duration)


if __name__ == "__main__":
	isobot = iSobotAuto(
		commandPath="commands_A.txt"
	)
	isobot.start()
