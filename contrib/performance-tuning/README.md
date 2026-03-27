# CachyOS-inspired Performance Tuning for Surface Devices

Runtime sysctl tuning parameters that complement the kernel config optimizations
(BORE scheduler, BBR3, 1000Hz, full preemption, MGLRU, etc.).

## What it does

- Reduces dirty page writeback thresholds for better I/O latency
- Lowers scheduler migration cost for faster task wakeup
- Sets BBR3 as the default TCP congestion control algorithm
- Increases network buffer sizes for better throughput
- Reduces swappiness to prefer keeping applications in RAM
- Increases `vm.max_map_count` for gaming (Wine/Proton)
- Disables NMI watchdog to reduce power usage on laptops
- Enables proactive memory compaction
- Increases inotify watchers for IDEs

## Installation

```bash
sudo cp 99-surface-performance.conf /etc/sysctl.d/
sudo sysctl --system
```

The settings will be applied automatically on every boot.

## Verification

After installation, verify key settings:

```bash
sysctl vm.dirty_ratio vm.swappiness net.ipv4.tcp_congestion_control kernel.sched_migration_cost_ns
```

Expected output:
```
vm.dirty_ratio = 10
vm.swappiness = 10
net.ipv4.tcp_congestion_control = bbr
kernel.sched_migration_cost_ns = 250000
```
