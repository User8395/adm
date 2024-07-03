import inquirer as inq
from sys import platform
from os import system, listdir, getcwd, chdir, path
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

def fileprompt(message, type):
    originaldirectory = getcwd()
    while True:
        try:
            clear()
            selected = inq.prompt([inq.List(
                "answer",
                f"{message} from {getcwd()}",
                ["Cancel"] + ["Parent directory"] + sorted(list(map(lambda i: i + "/", filter(lambda i: path.isdir(i), listdir())))) + sorted(list(filter(lambda i: i.endswith(type), filter(lambda i: path.isfile(i), listdir()))))
            )])["answer"]
            if path.isdir(selected):
                chdir(selected)
            elif selected == "Parent directory":
                chdir("..")
            elif selected == "Cancel":
                chdir(originaldirectory)
                return ""
            else:
                fullpath = path.join(getcwd(), selected)
                chdir(originaldirectory)
                return fullpath
        except PermissionError:
            clear()
            error("Cannot access directory: permission denied")
            sleep(2)
        


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
    info(f"Device: {check_output([adb, "shell", "getprop", "ro.product.manufacturer"]).decode("ascii").splitlines()[0]} {check_output([adb, "shell", "getprop", "ro.product.model"]).decode("ascii").splitlines()[0]}")
    info(f"Serial number: {serialnum}")
    action = inq.prompt([inq.List(
        "answer",
        "Choose an action",
        ["Reboot", "Shell", "Install app from APK", "Uninstall app", "Back"]
    )])
    if action["answer"] == "Reboot":
        adbReboot()
    elif action["answer"] == "Shell":
        adbShell()
    elif action["answer"] == "Install app from APK":
        adbAPK()
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

def adbShell():
    clear()
    info("Now dropping to a shell")
    info("If you got here by mistake, type \"exit\" and press [ENTER]")
    system(f"{adb} shell")
    adbUSB()

def adbAPK():
    apk = fileprompt("Select APK file", "apk")
    if apk == "":
        adbUSB()
    else:
        clear()
        info(f"APK to install: {apk}")
        info(f"Installing to: {check_output([adb, "shell", "getprop", "ro.product.manufacturer"]).decode("ascii").splitlines()[0]} {check_output([adb, "shell", "getprop", "ro.product.model"]).decode("ascii").splitlines()[0]}")
        warn("Make sure you downloaded the APK from a reliable source")
        warn("Unknown APKs can cause issues with your device")
        confirm = inq.prompt([inq.List(
            "answer",
            "Install APK?",
            ["Yes", "No"]
        )])["answer"]
        if confirm == "Yes":
            adbInstall(apk)
        elif confirm == "No":
            adbUSB()
        
def adbInstall(apk):
    clear()
    info(f"Installing {apk}")
    installstatus = check_output([adb, "install", apk]).decode("ascii").splitlines()[1]
    if installstatus == "Success":
        clear()
        info("APK installed")
        info("Returning in 3 seconds")
        sleep(3)
        adbUSB()
    else:
        clear()
        error("An error occurred while installing")
        error(f"Error message {installstatus.split(" ")[1]}")
        confirm = inq.prompt([inq.List(
            "answer",
            "Try again?",
            ["Yes", "No"] 
        )])["answer"]
        if confirm == "Yes":
            adbInstall(apk)
        elif confirm == "No":
            adbUSB()

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