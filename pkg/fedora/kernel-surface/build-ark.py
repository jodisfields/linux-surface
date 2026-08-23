#!/usr/bin/env python3

import argparse
import shutil
import subprocess
from itertools import chain
from pathlib import Path


def run(*command: str | Path, cwd: Path | None = None) -> None:
    subprocess.run([str(part) for part in command], cwd=cwd, check=True)


parser = argparse.ArgumentParser(description="Build a patched Fedora kernel RPM.")
parser.add_argument("--package-name", required=True)
parser.add_argument("--package-tag", required=True)
parser.add_argument("--package-release", required=True)
parser.add_argument("--ark-dir", default="kernel-ark")
parser.add_argument("--ark-url", default="https://gitlab.com/cki-project/kernel-ark")
parser.add_argument("--patch", action="append", nargs="+")
parser.add_argument("--config", action="append", nargs="+")
parser.add_argument("--file", action="append", nargs="+")
parser.add_argument("--buildopts", action="append", nargs="+")
parser.add_argument("--mode", choices=["rpms", "srpm"], default="rpms")
parser.add_argument("--outdir", default="out")
args = parser.parse_args()

patches = [Path(item).resolve() for item in chain.from_iterable(args.patch or [])]
configs = [Path(item).resolve() for item in chain.from_iterable(args.config or [])]
files = [Path(item).resolve() for item in chain.from_iterable(args.file or [])]
buildopts = list(chain.from_iterable(args.buildopts or []))
if "-configchecks" not in buildopts:
    buildopts.append("-configchecks")
ark_dir = Path(args.ark_dir).resolve()
out_dir = Path(args.outdir).resolve()

for source in [*patches, *configs, *files]:
    if not source.is_file():
        parser.error(f"missing input: {source}")

if not ark_dir.exists():
    run("git", "clone", args.ark_url, ark_dir)

# kernel-ark is a disposable build tree. Each run discards its local changes.
tag_ref = f"refs/tags/{args.package_tag}"
tag_exists = subprocess.run(
    ["git", "rev-parse", "--verify", "--quiet", tag_ref], cwd=ark_dir
).returncode == 0
if not tag_exists:
    run("git", "fetch", "origin", f"{tag_ref}:{tag_ref}", cwd=ark_dir)
run("git", "clean", "-dfx", cwd=ark_dir)
run("git", "reset", "--hard", cwd=ark_dir)
run("git", "checkout", "--detach", args.package_tag, cwd=ark_dir)

for patch in patches:
    run("git", "am", "-3", patch, cwd=ark_dir)

fedora_files = ark_dir / "redhat" / "fedora_files"
for source in files:
    shutil.copy2(source, fedora_files)

# kernel-ark stores each override in a file named after its Kconfig symbol.
overrides = ark_dir / "redhat" / "configs" / "custom-overrides" / "generic"
overrides.mkdir(parents=True, exist_ok=True)
for config in configs:
    for line in config.read_text().splitlines(keepends=True):
        if line.startswith("CONFIG_"):
            name = line.partition("=")[0]
        elif line.startswith("# CONFIG_") and line.rstrip().endswith(" is not set"):
            name = line.split()[1]
        else:
            continue
        print(f"Applying {line.rstrip()}")
        (overrides / name).write_text(line)

run("git", "add", overrides, cwd=ark_dir)
run("git", "commit", "--allow-empty", "-m", f"Merge {args.package_name} config", cwd=ark_dir)

target = "dist-rpms" if args.mode == "rpms" else "dist-srpm"
make_command = [
    "make", target,
    f"SPECPACKAGE_NAME=kernel-{args.package_name}",
    f"DISTLOCALVERSION=.{args.package_name}",
    f"BUILD={args.package_release}",
    "NO_CONFIGCHECKS=1",
    "VERSION_ON_UPSTREAM=0",
]
if buildopts:
    make_command.append(f"BUILDOPTS={' '.join(buildopts)}")
run(*make_command, cwd=ark_dir)

rpm_dir = ark_dir / "redhat" / "rpm" / ("RPMS" if args.mode == "rpms" else "SRPMS")
artifacts = list(rpm_dir.rglob("*.rpm"))
if not artifacts:
    parser.error(f"build produced no RPMs in {rpm_dir}")
out_dir.mkdir(parents=True, exist_ok=True)
for artifact in artifacts:
    shutil.copy2(artifact, out_dir)
