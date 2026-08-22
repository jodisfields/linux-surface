#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
def grub2_editenv(*args: str, capture_output: bool = False) -> None:
    subprocess.run(
        ["grub2-editenv", *args], check=True, capture_output=capture_output
    )


def main() -> int:
    boot = Path("/boot")
    machine_id_file = Path("/etc/machine-id")

    if not boot.is_dir():
        print("Error: /boot does not exist", file=sys.stderr)
        return 1

    if not machine_id_file.is_file():
        print("Error: /etc/machine-id does not exist", file=sys.stderr)
        return 1

    bls_dir = boot / "loader" / "entries"

    if not bls_dir.is_dir():
        print("Error: /boot/loader/entries does not exist", file=sys.stderr)
        return 1

    try:
        grub2_editenv("--help", capture_output=True)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Error: grub2-editenv failed: {error}", file=sys.stderr)
        return 1

    # The inode change time reflects package installation more closely than mtime,
    # which can retain the kernel build timestamp.
    kernels = sorted(
        boot.glob("vmlinuz-*.surface.*"),
        key=lambda kernel: kernel.stat().st_ctime,
        reverse=True,
    )

    if not kernels:
        print("Error: no Surface kernel found in /boot", file=sys.stderr)
        return 1

    kernel = kernels[0]
    machine_id = machine_id_file.read_text().strip()
    version = kernel.name.removeprefix("vmlinuz-")
    bls_config = bls_dir / f"{machine_id}-{version}.conf"

    if not bls_config.is_file():
        print(f"Error: {bls_config} does not exist", file=sys.stderr)
        return 1

    print(f"Kernel: {kernel}")
    print(f"BLS entry: {bls_config}")
    grub2_editenv("-", "set", f"saved_entry={bls_config.stem}")

    # rEFInd uses this timestamp to identify the newest kernel.
    kernel.touch(exist_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
