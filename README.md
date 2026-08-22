# Surface Laptop Studio kernel

This fork builds Linux 7.2.0 for my first-generation Microsoft Surface Laptop Studio running Fedora 42. It is not a general linux-surface package repository.

The build applies the Surface patch series and the CachyOS BORE scheduler to Fedora's `kernel-7.2.0-2` kernel-ark tag. The machine config enables CachyOS-style pre-emption, timer, CPU, memory, storage, networking and compression settings. It produces RPMs named `kernel-surface`.

CPU vulnerability and bus-lock mitigations remain enabled. Secure Boot support is absent because this machine has Secure Boot disabled.

## Build

Install Fedora's kernel build dependencies once:

```bash
sudo dnf install @rpm-development-tools git
sudo dnf builddep kernel
```

Build the binary RPMs from the repository root:

```bash
python3 pkg/fedora/kernel-surface/build-linux-surface.py
```

The script uses `kernel-ark/` as a disposable source tree and deletes all uncommitted files inside it on every run. RPMs are copied to `out/`.

To build only the source RPM:

```bash
python3 pkg/fedora/kernel-surface/build-linux-surface.py --mode srpm
```

## Install and rollback

Install the generated packages with DNF so the transaction remains in RPM history:

```bash
sudo dnf install out/*.rpm
```

Reboot into the new `kernel-surface` entry, then check the running release:

```bash
uname -r
```

Keep the current Fedora kernel installed. If the custom kernel fails, select the Fedora kernel from GRUB and remove the custom packages with the matching DNF history transaction.

## Source layout

- `patches/7.2/` contains the linux-surface patch series ported to Linux 7.2.
- `patches/cachyos-7.2/` contains the CachyOS BORE scheduler port for Fedora kernel-ark.
- `configs/surface-laptop-studio.config` contains the overrides for this machine.
- `pkg/fedora/kernel-surface/` contains the Fedora RPM build scripts and packaging patches.

Kernel-derived patches retain their original licences. See each patch for its licence and authorship.
