import socket
import os
import time
import subprocess
import sys
import shutil

# Ensure that psutil package is installed
try:
    import psutil
except ImportError as e:
    ans = input("'psutil' package not found!\n"
                "Do you want to install it? [Y/n] ")
    if ans.lower() in ["y", "yes"]:
        subprocess.call([sys.executable, '-m', 'pip', 'install', 'psutil'])
        import psutil
    else:
        print("Closing program...")
        exit()


def make_program_autorun():
    with open("resource-monitor.desktop", "w") as f:
        f.write(f"[Desktop Entry]\n"
                f"Name=Resource Monitor\n"
                f"Exec=/usr/bin/python3 {os.getcwd()}/autorun.py\n"
                f"Type=Application")
        f.flush()

    src = f'{os.getcwd()}/resource-monitor.desktop'
    dst = '/home/tymoteusz/.config/autostart/'
    shutil.copy(src, dst)


def cpu_usage_per_core(interval=1):
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


def cpu_temperature_per_core():
    base_path = "/sys/devices/virtual/thermal/"
    paths = [path for path in os.listdir(base_path) if path.startswith("thermal_zone")]
    cpu_temperature = []
    for path in paths:
        with open(base_path + path + "/temp") as f:
            cpu_temperature.append(float(f.readline()) / 1000)

    return cpu_temperature


def ram_info():
    mem = psutil.virtual_memory()
    mem = [data / 1_000_000_000 for data in [mem.total, mem.available, mem.used]]
    return mem


def interface_info():
    interfaces = []
    stats = psutil.net_if_stats()
    for interface_name, addresses in psutil.net_if_addrs().items():
        interface = {'name': interface_name}
        for address in addresses:
            if address.family == socket.AF_INET:
                interface['ip_address'] = address.address

        if interface_name in stats:
            if stats[interface_name].isup:
                interface['status'] = 'UP'
            else:
                interface['status'] = 'DOWN'
        else:
            interface['status'] = 'UNKNOWN'
        interfaces.append(interface)
    return interfaces


def interface_traffic(interval=1):
    interfaces = []

    initial_counters = psutil.net_io_counters(pernic=True)
    time.sleep(interval)
    final_counters = psutil.net_io_counters(pernic=True)

    for name in final_counters:
        interface = {
            'name': name,
            'bytes_sent': final_counters[name].bytes_sent - initial_counters[name].bytes_sent,
            'bytes_recv': final_counters[name].bytes_recv - initial_counters[name].bytes_recv,
            }
        interface['transfer_speed'] = round(interface['bytes_recv'] / interval)
        interfaces.append(interface)

    return interfaces


def resource_measurements(interval=10):
    run = True
    while run:
        try:
            print("Taking readings...")
            data = [
                cpu_usage_per_core(),
                cpu_temperature_per_core(),
                ram_info(),
                interface_info(),
                interface_traffic()
            ]
            with open(f"{os.getcwd()}/system_data_readings.txt", "a+") as f:
                f.write("##########READING##########\n")
                for reading in data:
                    reading = [str(item) for item in reading]
                    f.write(' '.join(reading) + "\n")
                f.flush()
            print("Readings successfully taken and saved!")

        except KeyboardInterrupt:
            print("\nProgram closed forcefully!\n"
                  "Closing...")
            exit()

        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\nEnding program...")
            run = False


if __name__ == '__main__':
    ans = input("Do you want to make program autorun on boot? [Y/n]: ")
    if ans.lower() in ["y", "yes"]:
        try:
            make_program_autorun()
        except PermissionError:
            print("In order to make program run on boot, run it with administrative privileges")
    resource_measurements()

# TODO:
#   etap 1
#     - get measurements of:
#           • Obciążenie każdego rdzenia procesora (w %)
#           • Temperatura każdego rdzenia procesora
#           • Wykorzystanie pamięci RAM (ilość całkowitej pamięci RAM, ilość zajętej pamięci RAM, ilość
#           dostępnej pamięci RAM)
#           • Ilość wolnego miejsca na dysku
#           • Dla wszystkich dostępnych interfejsów sieciowych: status (UP/DOWN/UNKNOWN), adres IP
#           • Ruch sieciowy na wszystkich dostępnych interfejsach (ilość odbieranych danych, ilość
#           wysyłanych danych w b/s)
#     -
#     - after set time get another measurements
#     - write data to .txt file (~/system_data_readings.txt.)
#   etap 2
#     -autostart with boot
