#! /usr/bin/env python3

"""
Utility to add/update/download the private resources that are not LFS tracked
"""

import os, sys, subprocess, traceback 
import logging, argparse, json

PRIVATE_RESOURCES_PATH = "https://artifactory.galois.com/artifactory/besspin_generic-nix/lfs-private-resources"
TEST_FILE = "test.json"
TRACKING_DATA = "private-tracker.json"

def error(msg):
    logging.error(msg)
    exit(1)

def shellCommand (argsList, errorMessage, check=True, **kwargs):
    logging.debug (f"shellCommand: <{' '.join(argsList)}>.")
    try:
        subprocess.run(argsList, check=check, **kwargs)
    except:
        traceback.print_exc()
        error(errorMessage)

def transfer (direction, localPath, remotePath):
    if (direction=="upload"):
        flag = "-T"
        preposition = "to"
    elif (direction=="download"):
        flag = "-o"
        preposition = "from"
    else:
        error("<transfer> has to be called with either <upload> or <download>.")

    shellCommand (  [   
                    "curl", "-H", f"X-JFrog-Art-Api:{os.environ['API_KEY']}",
                    flag, localPath, 
                    os.path.join(PRIVATE_RESOURCES_PATH,remotePath)
                ],
                f"Failed to {direction} <{localPath}> {preposition} <{remotePath}>!"
            )

class ApiKey:
    def __init__(self):
        self.goodApiKey = False
        self.testFilePath = os.path.join("/tmp",TEST_FILE)
        
    def verify(self):
        if (self.goodApiKey):
            return
        if ("API_KEY" not in os.environ):
            error(f"<API_KEY> is unset!")
        if (os.path.isfile(self.testFilePath)):
            os.remove(self.testFilePath)
        # Artifactory returns a json with bad status for bad API keys, so let's fetch the test file
        transfer("download",self.testFilePath,TEST_FILE)
        with open(self.testFilePath,"r") as f:
            testDict = json.load(f)
        if (("text" in testDict) and (testDict["text"] == "OK!")):
            self.goodApikey = True
        else:
            logging.debug(f"Curl output: {testDict}")
            error(f"Invalid <{TEST_FILE}>. Please verify your <API_KEY>.")

class TrackData:
    def __init__(self, repoDir):
        self.jsonPath = os.path.join(repoDir,TRACKING_DATA)
        self.loadJson()

    def loadJson(self):
        try:
            with open(self.jsonPath,"r") as fJson:
                self._data = json.load(fJson)
        except:
            traceback.print_exc()
            error(f"Failed to load the tracking data from {self.jsonPath}")

    def writeJson(self):
        try:
            with open(self.jsonPath,"w") as fJson:
                json.dump(self._data, fJson)
        except:
            traceback.print_exc()
            error(f"Failed to write the tracking data to {self.jsonPath}")

    def applySelections(self, selectFiles, new=False):
        if (selectFiles):
            if (not new):
                self.checkSelections(selectFiles)
            self._selections = selectFiles
        else:
            self._selections = list(self._data.keys())
        logging.debug(f"Selected Files: [{','.join(self._selections)}].")

    def checkSelections(self, selectedFiles):
        for file in selectedFiles:
            if (file not in self._data.keys()):
                error(f"Unknown <{file}>. Please choose from [{','.join(list(self._data.keys()))}]")

def main(xArgs):
    repoDir = os.path.abspath(os.path.dirname(__file__))

    # Setup logging and stdout/stderr
    logFile = os.path.join(repoDir,"private.log")
    logging.basicConfig(filename=logFile,filemode='w',
        format='[%(asctime)s]: %(message)s',
        datefmt='%I:%M:%S %p',
        level=logging.DEBUG)
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # tell the handler to use our format
    console.setFormatter(logging.Formatter('[%(asctime)s]: %(message)s',datefmt='%I:%M:%S %p'))
    # add the handler to the root logger
    logging.getLogger().addHandler(console)

    # Initialize states
    apiKey = ApiKey()
    track = TrackData(repoDir)



if __name__ == "__main__":
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description="The <private artifacts> utility.")
    
    modeGroup = xArgParser.add_mutually_exclusive_group(required=True)
    modeGroup.add_argument ('-d', '--download', help='Download the selected files.', action='store_true')
    modeGroup.add_argument ('-u', '--upload', help='Deploys the selected files.', action='store_true')
    modeGroup.add_argument ('-i', '--insert', help='Adds a file to the tracking.', action='store_true')
    modeGroup.add_argument ('-r', '--remove', help='Removes a file from the tracking.', action='store_true')

    selectGroup = xArgParser.add_mutually_exclusive_group()
    imagesGroup.add_argument ('-a', '--all', help='All tracked files. [default]', action='store_true')
    imagesGroup.add_argument ('-s', '--selectFiles', help='Select files.', nargs="*")

    xArgs = xArgParser.parse_args()
    main(xArgs)