import inquirer as inq
from sys import platform
from os import system
from subprocess import check_output, CalledProcessError
from time import sleep
from colorama import Fore


if platform == "linux":
    def clear():
        system("clear")
    adb = "linux/adb"
    fastboot = "linux/fastboot"
elif platform == "darwin":
    def clear():
        system("clear")
    adb = "darwin/adb"
    fastboot = "darwin/fastboot"
elif platform == "nt":
    def clear():
        system("cls")
    adb = "win/adb.exe"
    fastboot = "win/fastboot.exe"
else:
    print("Invalid system!")
    exit(1)


def info(text):
    print(f"[{Fore.BLUE}i{Fore.WHITE}] {text}")

def warn(text):
    print(f"[{Fore.YELLOW}!{Fore.WHITE}] {text}")

def error(text):
    print(f"[{Fore.RED}x{Fore.WHITE}] {text}")


def MainMenu():
    clear()
    program = inq.prompt([inq.List(
        "answer",
        "Choose program",
        ["ADB", "Fastboot", "Exit"]
    )])
    if program["answer"] == "ADB":
        adbMenu()
    elif program["answer"] == "Fastboot":
        fastbootMenu()
    elif program["answer"] == "Exit":
        clear()
        info("Thank you for using ADM")
        exit(0)
    

def NoDevicesFound(program):
    clear()
    tryagain = inq.prompt([inq.List(
        "answer", 
        "Could not find any devices, please make sure they are plugged in", 
        ["Try again", "Exit"]
    )])
    if tryagain["answer"] == "Try again":
        if program == "adb":
            adbUSB()
    elif tryagain["answer"] == "Exit":
        if program == "adb":
            adbMenu()

def adbMenu():
    clear()
    devicetype = inq.prompt([inq.List(
        "answer",
        "Select connection method",
        ["Wi-Fi (Android 11+)", "USB", "Back"]
    )])
    if devicetype["answer"] == "Wi-Fi (Android 11+)":
        clear()
        warn("ADM does not support Wi-Fi connection right now")
        exit(1)
    elif devicetype["answer"] == "USB":
        adbUSB()
    elif devicetype["answer"] == "Back":
        MainMenu()

def TooManyDevices(program):
    clear()
    error(f"Too many {program} devices connected")
    error(f"Please make sure only one {program} device is connected")
    exit(1)

def adbUSB():
    clear()
    info("Waiting for device...")
    i = 0
    while True:
        devicestemp = check_output([adb, "-d", "devices"]).decode("ascii").splitlines()
        if devicestemp != ['List of devices attached', '']:
            del devicestemp[0]
            del devicestemp[-1]
            break
        i += 1
        if i == 10000:
            NoDevicesFound("adb")
    device = []
    for i in devicestemp:
        i = i.replace("\t", " ").split(" ")
        device.append(i[0])
        device.append(i[1])
    if len(device) > 2:
        TooManyDevices("ADB")
    print(device[1])
    while device[1] == "offline":
        adbUSB()
    if device[1] == "unauthorized":
        adbUnauthorized()
    elif device[1] == "device":
        adbNormal(device[0])
    elif device[1] == "sideload":
        adbSideload()

def adbUnauthorized():
    clear()
    error("Device is unauthorized")
    error("Please accept the \"Allow USB Debugging?\" prompt on your device")
    info("Tip: Select the checkbox \"Always allow from this computer\" to prevent the dialog box from showing up again")
    exit(1)

def adbNormal(serialnum):
    clear()
    info("Device connected")
    info(f"Serial number: {serialnum}")
    action = inq.prompt([inq.List(
        "answer",
        "What would you like to do?",
        ["Reboot", "Shell", "Install app from APK", "Uninstall app", "Back"]
    )])
    if action["answer"] == "Reboot":
        adbReboot()
    elif action["answer"] == "Back":
        MainMenu()
 
def adbReboot():
    clear()
    rebootto = inq.prompt([inq.List(
        "answer",
        "Reboot to",
        ["Normal", "Recovery", "Bootloader", "Fastboot", "Cancel"]
    )])
    if rebootto["answer"] == "Cancel":
        adbUSB()
    elif rebootto["answer"] == "Normal":
        clear()
        info("Rebooting device...")
        try: 
            check_output([adb, "reboot"])
            clear()
            MainMenu()
            exit(0)
        except CalledProcessError:
            clear()
            error("Could not reboot device. You either have too many devices connected or the requested device was disconnected.")
            exit(1)
    elif rebootto["answer"] == "Recovery":
        clear()
        info("Rebooting device to recovery...")
        try: 
            check_output([adb, "reboot", "recovery"])
            clear()
            MainMenu()
            exit(0)
        except CalledProcessError:
            clear()
            error("Could not reboot device. You either have too many devices connected or the requested device was disconnected.")
            exit(1)
    elif rebootto["answer"] == "Bootloader":
        clear()
        info("Rebooting device to bootloader...")
        try: 
            check_output([adb, "reboot", "bootloader"])
            clear()
            MainMenu()
            exit(0)
        except CalledProcessError:
            clear()
            error("Could not reboot device. You either have too many devices connected or the requested device was disconnected.")
            exit(1)
    elif rebootto["answer"] == "Fastboot":
        clear()
        info("Rebooting device to Fastboot...")
        try: 
            check_output([adb, "reboot", "fastboot"])
            clear()
            MainMenu()
            exit(0)
        except CalledProcessError:
            clear()
            error("Could not reboot device. You either have too many devices connected or the requested device was disconnected.")
            exit(1)

def adbSideload():
    clear()
    error("Sideloading is not supported in ADM yet")
    info("If you want to exit sideload mode, run the command `adb reboot`")
    exit(1)

def fastbootMenu():
    clear()
    error("Fastboot is not supported in ADM yet")
    exit(1)

if __name__ == "__main__":
    MainMenu()