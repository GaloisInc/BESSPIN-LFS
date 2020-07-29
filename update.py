#!/usr/bin/env python3
# This script will not work unless it is run with the FETT Nix shell.

import os, shutil
from itertools import product

systems = ["debian", "FreeBSD", "busybox"]
testingPlatforms = ["fpga", "qemu", "firesim", "connectal"]
processors = ["chisel_p1", "chisel_p2", "bluespec_p2"]
extensions = ["bit", "ltx"]

def bitfilePaths():
    bitfileVar = 'FETT_GFE_BITFILE_DIR'
    if bitfileVar not in os.environ:
        print("Error: bitfile directory not in Nix environment.")
        exit(1)
    bitfileDir = os.environ[bitfileVar]
    bitfiles = [ f"soc_{proc}.{ext}" for proc, ext in product(processors, extensions)]
    return [(os.path.join(bitfileDir, path), os.path.join('bitfiles', 'fpga', path))
            for path in bitfiles]

def imagePaths():
    pairs = []
    for system, platform in product(systems, testingPlatforms):
        elfVar = f"FETT_GFE_{system.upper()}_{platform.upper()}"
        imageVar = f"FETT_GFE_{system.upper()}_ROOTFS_{platform.upper()}"
        # Ensure FreeBSD is named freebsd when connectal is the platform
        if system.lower() == 'freebsd' and platform.lower() == 'connectal':
            systemName = 'freebsd'
        else:
            systemName = system

        if elfVar not in os.environ:
            print(f"OS image for {systemName} on {platform} not in Nix environment.")
        else:
            pairs.append((os.environ[elfVar], os.path.join('osImages', platform, systemName + '.elf')))
        if imageVar in os.environ:
            pairs.append((os.environ[imageVar], os.path.join('osImages', platform, systemName + '.img.zst')))
    return pairs

def copyFromNix(baseDir):
    if baseDir is None:
        prefix = 'GFE'
    else:
        prefix = os.path.join(baseDir, 'GFE')
    paths = bitfilePaths() + imagePaths()
    print("Copying files from Nix store")
    for src, dest in paths:
        destFullPath = os.path.join(prefix, dest)
        try:
            shutil.copy(src, destFullPath)
            os.chmod(destFullPath, 0o664) # Files in the nix store are read only
            print(src, "->", os.path.join(prefix, destFullPath))
        except Exception as e:
            print(f"Error when copying {src} to {dest}")
            exit(1)

copyFromNix(None)
