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

Each team will be providing binaries for the platforms that they
support. These platforms are `qemu`, `fpga`, and the following AWS
platform variants.
- `firesim`
- `connectal`
- `awsteria`

Each directory at the top level should have the following subdirectories.

- `osImages/`: Contains a subdirectory for each supported platform
  containing OS images. Images should be named `<os>.elf`, where
  `<os>` is `debian`, `FreeBSD`, or `busybox`.
  
- `appsBinaries/`: Contains a directory for each target
  application. Within each application, there is a subdirectory for
  each supported platform which contains the application binaries.

- `bitfiles/`: Contains subdirectories for each supported
  platform. The structure of each subdirectory depends on the
  platform.

  * The `fpga/` directory contains bitfiles
    `soc_<proc_type>_<target>.bit`, where `<proc_type>` is either
    `bluespec` or `chisel` and `<target>` is `p1`, `p2`, or `p3`. Each
    bitfile has an associated probe file with extension `.ltx`.

  * The directory for an AWS platform variant contains a subdirectory
    for each processor. This contains a file `agfi_id.json`, which has
    the AGFI pointing to the AFI. Any other binaries associated with
    that processor should also be stored here. For example, building a
    processor with FireSim produced several libraries and kernel
    modules.

To summarize what was described above, the directory structure should
look something like this:

```
├── <team>
│   ├── appsBinaries
│   │   ├── database
│   │   │   └── <os>
│   │   │       └── sqlite
│   │   ├── voting
│   │   │   └── <os>
│   │   │       ├── bvrs
│   │   │       └── kfcgi
│   │   └── webserver
│   │       └── <os>
│   │           └── sbin
│   │               └── nginx
│   ├── bitfiles
│   │   ├── <pvAWS>
│   │   │   └── <proc>_<target>
│   │   │       └── agfi_id.json
│   │   └── fpga
│   │       ├── soc_<proc>_<target>.bit
│   │       └── soc_<proc>_<target>.ltx
└── └── osImages
        └── <platform>
            └── <os>.elf
```

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
