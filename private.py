#! /usr/bin/env python3

"""
Utility to add/update/download the private resources that are not LFS tracked
"""

import os, sys, subprocess, traceback 
import logging, argparse, json, hashlib

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

def computeSha256 (filepath):
    BLOCKSIZE = 65536
    try:
        fIn = open(filepath,"rb")
        sha256 = hashlib.sha256()
        while True:
            chunk = fIn.read(BLOCKSIZE)
            if (not chunk):
                break
            sha256.update(chunk)
        sha256Val = sha256.hexdigest()
    except:
        traceback.print_exc()
        error(f"Failed to compute sha256 for <{filepath}>.")
    fIn.close()
    return sha256Val

def computeHashAndSize (filepath):
    sha256 = computeSha256(absPath)
    size = os.path.getsize(absPath)
    return (sha256,size)

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
        self.repoDir = repoDir
        self.jsonPath = os.path.join(repoDir,TRACKING_DATA)
        self.loadJson()

    def loadJson(self):
        try:
            with open(self.jsonPath,"r") as fJson:
                self._data = json.load(fJson)
        except:
            traceback.print_exc()
            error(f"Failed to load the tracking data from {self.jsonPath}")

    def updateData(self):
        try:
            with open(self.jsonPath,"w") as fJson:
                fJson.write(json.dumps(self._data, indent=4, sort_keys=True))
        except:
            traceback.print_exc()
            error(f"Failed to write the tracking data to {self.jsonPath}")

    def applySelections(self, select, new=False, isfile=False):
        if (select):
            if (not new):
                self.verifySelectionsExistInData(select)
            if (isfile):
                self.verifySelectionsAreFiles(select)
            self._selections = select
        else:
            self._selections = list(self._data.keys())
        logging.debug(f"Selected Files: [{','.join(self._selections)}].")

    def verifySelectionsExistInData(self, selectedFiles):
        for file in selectedFiles:
            if (file not in self._data.keys()):
                error(f"Unknown <{file}>. Please choose from [{','.join(list(self._data.keys()))}]")

    def verifySelectionsAreFiles(self, selectedFiles):
        for file in selectedFiles:
            absPath = os.path.join(self.repoDir,file)
            if (not os.path.isfile(absPath)):
                error(f"<{abspath}> not found!")

    def downloadSelections(self):
        for file in self._selections:
            info = self._data[file]
            absPath = os.path.join(self.repoDir,file)
            
            # If file exists, does it need an update?
            if (os.path.isfile(file)):
                sha256Existing, sizeExisting = computeHashAndSize(absPath)
                if ((sha256Existing != info["sha256"]) or (sizeExisting != info["size"])):
                    logging.info(f"<{file}> already exists, but does not match the info. Will overwrite.")
                else:
                    logging.info(f"<{file}> already exists. Will skip.")
                    continue

            logging.info(f"Downloading <{file}>...")
            transfer ("download", absPath, file)
            sha256, size = computeHashAndSize(absPath)
            # Check the values
            if ((sha256 != info["sha256"]) or (size != info["size"])):
                logging.warning (f"<{file}> mismatch! Fetched [sha256:{sha256}, size:{size}], but "
                    f"data has [sha256:{info['sha256']}, size:{info['size']}].")
            else:
                logging.info(f"<{file}> match!")

    def uploadSelections(self):
        for file in self._selections:
            absPath = os.path.join(self.repoDir,file)
            logging.info(f"Uploading <{absPath}>...")
            transfer ("upload", absPath, file)
            logging.info(f"<{file}> uploaded!")

    def insertSelections(self):
        for file in self._selections:
            if (file in self._data.keys()):
                error(f"<{file}> is already tracked. Please use [--update] instead.")
            absPath = os.path.join(self.repoDir,file)
            sha256, size = computeHashAndSize(absPath)
            self._data[file] = {"sha256" : sha256, "size" : size}
            logging.info(f"<{file}> inserted! [sha256:{sha256}, size:{size}]")

    def appendToGitIgnore(self):
        for file in self._selections:
            fIgnorePath = os.path.join(self.repoDir, os.path.dirname(file), ".gitignore")
            try:
                with open(fIgnorePath,"a") as fIgnore:
                    fIgnore.write(f"{file}\n")
            except:
                traceback.print_exc()
                error(f"Failed to append to gitignore for {file}.")

    def removeFromGitIgnore(self):
        for file in self._selections:
            fIgnorePath = os.path.join(self.repoDir, os.path.dirname(file), ".gitignore")
            try:
                fIgnore = open(fIgnorePath,"r")
                lines = fIgnore.read().splitlines()
                fIgnore.close()
                lines.remove(file)
                fIgnore = open(fIgnorePath,"w")
                fIgnore.write('\n'.join(lines))
                fIgnore.close()
            except:
                traceback.print_exc()
                error(f"Failed to remove {file} from gitignore.")

    def updateSelections(self):
        for file in self._selections:
            info = self._data[file]
            absPath = os.path.join(self.repoDir,file)
            sha256, size = computeHashAndSize(absPath)
            self._data[file] = {"sha256" : sha256, "size" : size}
            logging.info(f"<{file}> updated! "
                f"\n\t\tOld: [sha256:{info['sha256']}, size:{info['size']}]"
                f"\n\t\tNew: [sha256:{sha256}, size:{size}]")

    def removeSelections(self):
        for file in self._selections:
            del self._data[file]
            logging.info(f"<{file}> untracked!")
        logging.warning("File are still in the artifactory. You have to delete them manually in order "
            "to completely remove them.")


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
    data = TrackData(repoDir)

    # Execute the modes
    if (xArgs.download):
        apiKey.verify()
        data.applySelections(xArgs.select, new=False, isfile=False)
        data.downloadSelections()
    elif (xArgs.insert):
        if (not xArgs.select):
            error("Cannot use [--insert] without [--select].")
        data.applySelections(xArgs.select, new=True, isfile=True)
        data.insertSelections()
        data.updateData()
        data.appendToGitIgnore()
    elif (xArgs.upload):
        apiKey.verify()
        data.applySelections(xArgs.select, new=False, isfile=True)
        data.uploadSelections()
    elif (xArgs.update):
        data.applySelections(xArgs.select, new=False, isfile=True)
        data.updateSelections()
        data.updateData()
    elif (xArgs.remove):
        if (not xArgs.select):
            error("Cannot use [--remove] without [--select]!")
        data.applySelections(xArgs.select, new=False, isfile=False)
        data.removeSelections()
        data.updateData()
        data.removeFromGitIgnore()


if __name__ == "__main__":
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description="The <private artifacts> utility.")
    
    modeGroup = xArgParser.add_mutually_exclusive_group(required=True)
    modeGroup.add_argument ('-d', '--download', help='Download the selected files.', action='store_true')
    modeGroup.add_argument ('-u', '--upload', help='Deploys the selected files.', action='store_true')
    modeGroup.add_argument ('-i', '--insert', help='Adds a file to the tracking.', action='store_true')
    modeGroup.add_argument ('-c', '--update', help='Update the selected files info.', action='store_true')
    modeGroup.add_argument ('-r', '--remove', help='Removes a file from the tracking.', action='store_true')

    selectGroup = xArgParser.add_mutually_exclusive_group()
    selectGroup.add_argument ('-a', '--all', help='All tracked files. [default]', action='store_true')
    selectGroup.add_argument ('-s', '--select', help='Select files.', nargs="*")

    xArgs = xArgParser.parse_args()
    main(xArgs)