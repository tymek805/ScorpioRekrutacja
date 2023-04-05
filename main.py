import os
import shutil
import time

from measurments import cpu_usage_per_core, cpu_temperature_per_core, ram_info, memory_info, \
    interface_info, interface_traffic


def make_program_autorun():
    """
    Function creates .desktop file and copies it to the ~/.config/autostart/
    that allows program to run on boot-up
    """
    with open("resource-monitor.desktop", "w") as f:
        f.write(f"[Desktop Entry]\n"
                f"Name=Resource Monitor\n"
                f"Exec=/usr/bin/python3 {os.getcwd()}/autorun.py\n"
                f"Type=Application")
        f.flush()

    src = f'{os.getcwd()}/resource-monitor.desktop'
    dst = os.path.expanduser("~/.config/autostart/")
    shutil.copy(src, dst)


def take_measurements(interval=10):
    """
    Function takes measurements every *interval* and saves them to:
     - ~/system_data_readings.txt
     - <path>/Page/system_data_readings.txt
    :param interval:
    """
    while True:
        try:
            print("Taking readings...")
            data = [
                cpu_usage_per_core(),
                cpu_temperature_per_core(),
                ram_info(),
                memory_info(),
                interface_info(),
                interface_traffic()
            ]
            sep = "##########READING##########\n"
            with open(os.path.expanduser("~/system_data_readings.txt"), "a+") as f:
                f.write(sep)
                for reading in data:
                    reading = [str(item) for item in reading]
                    f.write(' '.join(reading) + "\n")

            try:
                with open(os.path.join(os.getcwd(), "Page", "system_data_readings.txt"), "a+") as f:
                    f.write(sep)
                    for reading in data:
                        reading = [str(item) for item in reading]
                        f.write(' '.join(reading) + "\n")
            except FileNotFoundError as e:
                print("Make sure that 'Page' package is in the execution folder!")
            print("Readings successfully taken and saved!")
            time.sleep(interval)
        except KeyboardInterrupt:
            print("Keyboard Interrupt!", "Ending program...", sep="\n")
            exit()


def start():
    user_answer_autorun = input("Do you want to make program autorun on boot? [Y/n]: ")
    if user_answer_autorun.lower() in ["y", "yes"]:
        make_program_autorun()
    take_measurements()


if __name__ == '__main__':
    start()
