# SSITH Demonstrator Binaries

This repository is meant to store binary artifacts associated with
FETT. These include:
- Application binaries
- OS Images
- Bitfiles

## Directory Structure

At the top level, each directory corresponds to a source for the
binaries. These are currently:
- `GFE` (binaries for unmodified processors)
- `CHERI`
- `Michigan`

Each of these each one should have the following subdirectories.
- `osImages/`: Contains OS images
- `appsBinaries/`: Contains a directory for each target
  application. Within each application, there is a subdirectory for
  each supported platform which contains the application binaries.
- `bitfiles/`: Contains processor bitfiles

## Guidelines for Storing Binaries

All binaries should be tracked using [Git
LFS](https://git-lfs.github.com/). The file `.gitattributes` contains
the list of patterns which are automatically stored using LFS. If you
are committing a binary with a path that does not match one of those
patterns, add it using `git lfs track` before you commit the binary
file. See the Git LFS documentation for more info.
