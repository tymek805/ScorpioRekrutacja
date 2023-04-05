import os
import shutil
import socket
import subprocess
import sys
import time

# Ensure that psutil package is installed
try:
    import psutil
except ImportError as e:
    user_ans_package = input("'psutil' package not found!\n"
                             "Do you want to install it? [Y/n] ")
    if user_ans_package.lower() in ["y", "yes"]:
        if subprocess.call([sys.executable, '-m', 'pip', 'install', 'psutil']) == 0:
            import psutil
        else:
            print("During installation occurred fatal error!\n"
                  "Please ensure that 'pip' is installed on your computer!"
                  "Closing program...")
            exit()
    else:
        print("Closing program...")
        exit()


def cpu_usage_per_core(interval=1) -> list[float]:
    """
    Compares system CPU times before and after the *interval*.
    :param interval:
    :returns: list of floats that represent the current utilization of the CPU cores as a percentage.
    """
    psutil.cpu_percent()
    with open('/proc/stat') as f:
        measurements = [line.replace('\n', '').split()[1:] for line in f.readlines() if line.startswith("cpu")][1:]
        initial_cpu_times = [list(map(int, measurement)) for measurement in measurements]

    time.sleep(interval)

    cpu_load = []
    with open('/proc/stat') as f:
        measurements = [line.replace('\n', '').split()[1:] for line in f.readlines() if line.startswith("cpu")][1:]

        for i, measurement in enumerate(measurements):
            measurement = list(map(int, measurement))
            delta_cpu_time = [measurement[j] - initial_cpu_times[i][j] for j in range(len(measurement))]
            total_cpu_time = sum(delta_cpu_time)
            cpu_load.append(round((total_cpu_time - delta_cpu_time[3]) / total_cpu_time * 100, 2))
    return cpu_load


def cpu_temperature_per_core() -> list[float]:
    """
    Measures the current temperature on each core.
    :returns: list of floats that represent the temperature of the CPU cores.
    """
    base_path = "/sys/devices/virtual/thermal/"
    paths = [path for path in os.listdir(base_path) if path.startswith("thermal_zone")]
    cpu_temperature = []
    for path in paths:
        with open(os.path.join(base_path, path, "temp")) as f:
            cpu_temperature.append(float(f.readline()) / 1000)

    return cpu_temperature


def ram_info():
    """
    Returns info of RAM memory:
     - total
     - available
     - used
    """
    mem = psutil.virtual_memory()
    mem = [data for data in [mem.total, mem.available, mem.used]]
    return mem


def memory_info() -> list[int]:
    """Return disk free space in bytes."""
    return [shutil.disk_usage("/").free]


def interface_info() -> list[str]:
    """
    Returns list of interfaces that contains:
     - ip address
     - status (UP/DOWN/UNKNOWN)
    """
    interfaces = []
    stats = psutil.net_if_stats()
    for interface_name, addresses in psutil.net_if_addrs().items():
        interface = []
        for address in addresses:
            if address.family == socket.AF_INET:
                interface.append(address.address)

        if interface_name in stats:
            if stats[interface_name].isup:
                interface.append('UP')
            else:
                interface.append('DOWN')
        else:
            interface.append('UNKNOWN')
        interfaces.append(' '.join(interface))
    return interfaces


def interface_traffic(interval=1) -> list[str]:
    """
    Returns information about traffic in interfaces.

    Transfer speed is measured from readings before and after *interval*.
    :param interval:
    """
    interfaces = []

    initial_counters = psutil.net_io_counters(pernic=True)
    time.sleep(interval)
    final_counters = psutil.net_io_counters(pernic=True)

    for name in final_counters:
        interface = [final_counters[name].bytes_sent - initial_counters[name].bytes_sent,
                     final_counters[name].bytes_recv - initial_counters[name].bytes_recv]
        interface = [str(round(i / interval)) for i in interface]
        interfaces.append(' '.join(interface))

    return interfaces
