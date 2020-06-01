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
- `SRI-Cambridge`
- `Michigan`
- `MIT`
- `LMCO`

Each of these each one should have the following subdirectories.

- `osImages/`: Contains subdirectories `firesim/`, `fpga/`, and
  `qemu/`. Each of which contains OS images for its respective
  platform. Images should be named `<os>.elf`, where `<os>` is
  `debian`, `FreeBSD`, or `busybox`.
  
- `appsBinaries/`: Contains a directory for each target
  application. Within each application, there is a subdirectory for
  each supported platform which contains the application binaries.

- `bitfiles/`: Contains subdirectories `firesim/` and `fpga/`, which
  respectively contain bitfiles for AWS and local FPGA hosts. The
  structure of each subdirectory depends on the platform.

  * The `fpga/` directory contains bitfiles
    `soc_<proc_type>_<target>.bit`, where `<proc_type>` is either
    `bluespec` or `chisel` and `<target>` is `p1`, `p2`, or `p3`. Each
    bitfile has an associated probe file with extension `.ltx`.

  * The `firesim/` directory contains a subdirectory for each
    processor. This contains a file `agfi_id.json`, which has the AGFI
    pointing to the AFI. The directories `kmods/` and `sim/` contain
    other binary artifacts associated with the FireSim build.

Binaries for more AWS platform variants will be added in the future.

## Guidelines for Storing Binaries

All binaries should be tracked using [Git
LFS](https://git-lfs.github.com/). The file `.gitattributes` contains
the list of patterns which are automatically stored using LFS. If you
are committing a binary with a path that does not match one of those
patterns, add it using `git lfs track` before you commit the binary
file. See the Git LFS documentation for more info.

## Copying from the Nix Store

Some of the artifacts in this repository are built as Nix packages in
the [FETT Nix
Environment](https://github.com/DARPA-SSITH-Demonstrators/SSITH-FETT-Environment). To
copy the latest versions of these files from the Nix store, start the
Nix shell and run the script `update.py` from this directory.
