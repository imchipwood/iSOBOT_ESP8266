__author__ = "chawood@pdx.edu"
import time
import csv

from isobot import iSobot, commands

ACTION_KEY = 'Command'
DURATION_KEY = 'Duration'
COMMAND_SLEEP = 'sleep'


class iSobotAuto(iSobot):
	"""Automate multiple iSOBOT motions read from a config file"""
	def __init__(self, url="http://192.168.4.1", channel=0, commandPath=None, debug=False):
		super(iSobotAuto, self).__init__(url, channel, debug)
		self.commandPath = commandPath
		self.commands = self.parseCommandFile()

	def parseCommandFile(self):
		"""Parse a command file to extract actions & their durations

		@return: list of dicts
		"""
		fieldnames = [ACTION_KEY, DURATION_KEY]
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
		"""Execute actions parsed from commands file

		@return: Nones
		"""
		for i, command in enumerate(self.commands):
			rawcmd = command[ACTION_KEY]
			if '#' in rawcmd:
				continue
			# convert string command to hex #
			action = commands[rawcmd]
			# convert string duration to float
			duration = float(command[DURATION_KEY])

			print("{} - Executing command {} - {}, {}".format(self.url, i, action, duration))

			if action == COMMAND_SLEEP:
				time.sleep(duration)
			else:
				self.isobotDoType1(action=action, repeat=int(duration))


if __name__ == "__main__":
	isobot = iSobotAuto(
		commandPath="commands_A.txt"
	)
	isobot.start()
