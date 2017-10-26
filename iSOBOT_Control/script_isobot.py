__author__ = "chawood@pdx.edu"
import argparse
import os
import json
from multiprocessing import Process
from isobot_auto import iSobotAuto


def parseArgs():
	"""Parse input arguments"""
	parser = argparse.ArgumentParser()
	parser.add_argument('cfgfiles', type=str, help="Comma-separated list of config file paths. Maximum of 2 files")
	parser.add_argument('-debug', '-d', action="store_true", help="Enable debug messages")
	return parser.parse_args()


def checkPaths(paths):
	"""Check config paths exist, attempt to recover if not"""
	newPaths = []
	for configPath in paths:
		if not os.path.exists(configPath):
			print("{} doesn't exist, trying cwd".format(configPath))
			tmpConfigPath = os.path.join(os.getcwd(), configPath)
			if os.path.exists(tmpConfigPath):
				newPaths.append(configPath)
			else:
				raise OSError("Config file could not be found")
		else:
			newPaths.append(configPath)
	return newPaths


def parseConfigs(configPaths, debug):
	"""Parse JSON configuration files"""
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


def main(configPaths=None, dbg=None):
	global debug
	# get input args
	if not configPaths:
		parsedArgs = parseArgs()
		configPaths = parsedArgs.cfgfiles.split(',')
		dbg = parsedArgs.debug
	debug = dbg

	# Check paths exist
	configPaths = checkPaths(configPaths)

	# Create iSobot objects
	iSobots = parseConfigs(configPaths, debug)

	# launch the iSobot threads
	threads = []
	for iSobot in iSobots:
		thread = Process(target=iSobot.start)
		print("Starting control thread for iSobot @ {}".format(iSobot.url))
		thread.start()
		threads.append(thread)

	# wait for all threads to complete, allow keyboard interrupt to kill
	try:
		for thread in threads:
			thread.join()
	except KeyboardInterrupt:
		pass
	except Exception as e:
		print(e)
	finally:
		# Force all threads to stop
		for thread in threads:
			thread.terminate()

	print("\nAll processes completed.\n")


if __name__ == "__main__":
	main()
