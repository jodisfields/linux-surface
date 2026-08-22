#!/usr/bin/env python3

import argparse
import subprocess
from pathlib import Path


PACKAGE_NAME = "surface"
PACKAGE_TAG = "kernel-7.2.0-2"
PACKAGE_RELEASE = "1"
KERNEL_BUILDOPTS = "+up +baseonly -debuginfo -doc -headers -efiuki"

parser = argparse.ArgumentParser(
    description="Build the Fedora 42 kernel for this Surface Laptop Studio."
)
parser.add_argument("--ark-dir", default="kernel-ark")
parser.add_argument("--ark-url", default="https://gitlab.com/cki-project/kernel-ark")
parser.add_argument("--mode", choices=["rpms", "srpm"], default="rpms")
parser.add_argument("--outdir", default="out")
args = parser.parse_args()

script_dir = Path(__file__).resolve().parent
repo_dir = script_dir.parents[2]
patches = sorted((repo_dir / "patches" / "7.2").glob("*.patch"))
performance_patches = sorted((repo_dir / "patches" / "cachyos-7.2").glob("*.patch"))
config = repo_dir / "configs" / "surface-laptop-studio.config"
packaging_patches = sorted((script_dir / "patches").glob("*.patch"))
packaging_files = sorted(path for path in (script_dir / "files").glob("*") if path.is_file())

if not patches:
    parser.error("patches/7.2 contains no patches")
if not performance_patches:
    parser.error("patches/cachyos-7.2 contains no patches")
if not config.is_file():
    parser.error(f"missing machine config: {config}")

command = [
    script_dir / "build-ark.py",
    "--ark-dir", args.ark_dir,
    "--ark-url", args.ark_url,
    "--mode", args.mode,
    "--outdir", args.outdir,
    "--package-name", PACKAGE_NAME,
    "--package-tag", PACKAGE_TAG,
    "--package-release", PACKAGE_RELEASE,
    "--patch", *performance_patches,
    "--patch", *patches,
    "--patch", *packaging_patches,
    "--config", config,
    f"--buildopts={KERNEL_BUILDOPTS}",
]
if packaging_files:
    command.extend(["--file", *packaging_files])

subprocess.run(command, check=True)
