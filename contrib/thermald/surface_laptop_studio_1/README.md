# Thermald Configuration for Surface Laptop Studio 1

A thermald configuration for the Surface Laptop Studio 1 (Intel Tiger Lake H35, 28 W TDP).
The Surface Laptop Studio 1 uses an Intel Core i5-11300H or i7-11370H processor.
Because the H35 SKUs have a configurable TDP envelope up to 35 W (and short-term boost
beyond that), the device can run noticeably hot under sustained load.  This configuration
lowers the sustained CPU temperature cap to around 65 °C and falls back to disabling
Turbo Boost when that is not enough, keeping the device cooler and quieter.

> **Tip:** Raise the `<Temperature>` values if you prefer more performance headroom at
> the cost of higher skin temperatures.

## Sensor path note

The thermal management relies on the `x86_pkg_temp` sensor that Intel exposes through
the kernel's `thermal` subsystem.  The `rapl_controller` cooling device is used first
(via Intel RAPL power limits), followed by `intel_pstate` (P-state scaling) and finally
a hard Turbo Boost disable.

## Installation

1. Ensure `thermald` is installed (many distributions include it by default; if not, install it via your package manager).
2. Copy both XML files into `/etc/thermald/`:
   ```
   sudo cp thermal-conf.xml /etc/thermald/
   sudo cp thermal-cpu-cdev-order.xml /etc/thermald/
   ```
3. If your distribution passes `--adaptive` to thermald you need to remove that flag so
   that thermald uses your custom configuration instead of the ACPI-based adaptive mode:
   ```
   sudo systemctl edit thermald.service
   ```
   In the override file add:
   ```
   [Service]
   ExecStart=
   ExecStart=/usr/sbin/thermald --no-daemon --dbus-enable --ignore-cpuid-check
   ```
4. Restart thermald:
   ```
   sudo systemctl restart thermald
   ```

## Adjusting the temperature threshold

The `<Temperature>65000</Temperature>` value is in milli-degrees Celsius (65 °C).
Lower it for a quieter device; raise it to allow the processor to boost more aggressively.
