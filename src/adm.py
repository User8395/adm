import inquirer as inq
from sys import platform
from os import system
from subprocess import check_output
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
        exit(0)
    # print("Searching for devices...")
    # check_output([adb, "disconnect"])
    # adb_devices = check_output([adb, "devices"]).decode("ascii").splitlines().remove("List of devices attached")
    # fastboot_devices = check_output([fastboot, "devices"]).decode("ascii").splitlines()
    # if adb_devices == None and fastboot_devices == []:
    #     NoDevicesFound()
    # elif adb_devices != None and fastboot_devices == []:
    #     FastbootDevices()
    

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
        del devicestemp[0]
        del devicestemp[-1]
        if devicestemp == ['List of devices attached', '']:
            break
        i += 1
        if i == 10000:
            NoDevicesFound("adb")
    device = {}
    for i in devicestemp:
        i = i.replace("\t", " ").split(" ")
        device[i[0]] = i[1]
    if len(device) > 1:
        TooManyDevices("ADB")
    info("Found the following device")
    for identification, mode in device:
        info(f"Serial: {identification}")
        info(f"Serial: {mode}")
        if mode == "unauthorized":
            adbUnauthorized()
        elif mode == "device":
            adbNormal()

def adbUnauthorized():
    clear()
    error("Device is unauthorized")
    error("Please accept the \"Allow USB Debugging?\" prompt on your device")
    info("Tip: Select the checkbox \"Always allow from this computer\" to prevent the dialog box from showing up again")
    exit(1)

def adbNormal():
    info("")

def adbSideload():
    clear()
    error("Sideloading is not support in ADM yet")
    exit(1)

def fastbootMenu():
    clear()
    error("Fastboot is not supported in ADM yet")
    exit(1)

if __name__ == "__main__":
    MainMenu()