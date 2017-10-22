import argparse
import os
import json
import threading
from isobot_auto import iSobotAuto

global debug


def dprint(message):
	global debug
	if debug:
		print(message)


def parseArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument('cfgfiles', type=str, help="Comma-separated list of config file paths. Maximum of 2 files")
	parser.add_argument('-debug', '-d', type=bool, default=False, help="Enable debug messages")
	return parser.parse_args()


def checkPaths(paths):
	# check paths exist
	newPaths = []
	for configPath in paths:
		if not os.path.exists(configPath):
			dprint("{} doesn't exist, trying cwd".format(configPath))
			tmpConfigPath = os.path.join(os.getcwd(), configPath)
			if os.path.exists(tmpConfigPath):
				newPaths.append(configPath)
			else:
				raise OSError("Config file could not be found")
		else:
			newPaths.append(configPath)
	return newPaths


def parseConfigs(configPaths):
	global debug
	iSobots = []
	for configPath in configPaths:
		with open(configPath, 'r') as inf:
			config = json.load(inf)
			iSobots.append(
				iSobotAuto(
					url=config['url'],
					channel=config['channel'],
					commandPath=config['commandPath'],
					debug=debug
				)
			)
	return iSobots


def main():
	global debug
	# get input args
	parsedArgs = parseArgs()
	configPaths = parsedArgs.cfgfiles.split(',')
	debug = parsedArgs.debug

	# Check paths exist
	configPaths = checkPaths(configPaths)

	# Create iSobot objects
	iSobots = parseConfigs(configPaths)

	# launch the iSobot threads
	for iSobot in iSobots:
		thread = threading.Thread(target=iSobot.start)
		print("Starting control thread for iSobot @ {}".format(iSobot.url))
		thread.start()
		thread.join()

	print("All threads complete")


if __name__ == "__main__":
	main()
