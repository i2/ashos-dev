#!/usr/bin/python3

import os
import subprocess
import sys ### temporary just for testing steps
#from src.distros.arch import astpk

def clear():
    os.system("#clear")

def to_uuid(part):
    return subprocess.check_output(f"blkid -s UUID -o value {part}", shell=True).decode('utf-8').strip()

#   This function returns a tuple: (1. choice whether partitioning and formatting should happen
#   2. Underscore plus name of distro if it should be appended to sub-volume names
def get_multiboot(dist):
    clear()
    while True:
        print("Please choose one of the following:\n1. Single OS installation\n2. Initiate a multi-boot ashos setup\n3. Adding to an already installed ashos")
        print("Please be aware choosing option 1 and 2 will wipe {args[1]}")
        i = input("> ")
        if i == "1":
            return i,""
            break
        elif i == "2":
            return i,f"_{dist}"
            break
        elif i == "3":
            return i,f"_{dist}"
            break
        else:
            print("Invalid choice!")
            continue

def get_hostname():
    clear()
    while True:
        print("Enter hostname:")
        hostname = input("> ")
        if hostname:
            print("Happy with your hostname (y/n)?")
            reply = input("> ")
            if reply.casefold() == "y":
                break
            else:
                continue
    return hostname

def get_timezone():
    clear()
    while True:
        print("Select a timezone (type list to list):")
        zone = input("> ")
        if zone == "list":
            os.system("ls /usr/share/zoneinfo | less")
        elif os.path.isfile(f"/usr/share/zoneinfo/{zone}"):
            return str(f"/usr/share/zoneinfo/{zone}")
        else:
            print("Invalid Timezone!")
            continue

def get_username():
    clear()
    while True:
        print("Enter username (all lowercase, max 8 letters)")
        username = input("> ")
        if username:
            print("Happy with your username (y/n)?")
            reply = input("> ")
            if reply.casefold() == "y":
                break
            else:
                continue
    return username

def create_user(u):
    os.system(f"chroot /mnt useradd -m -G wheel -s /bin/bash {u}")
    os.system("echo '%wheel ALL=(ALL:ALL) ALL' | tee -a /mnt/etc/sudoers")
    os.system(f"echo 'export XDG_RUNTIME_DIR=\"/run/user/1000\"' | tee -a /mnt/home/{u}/.bashrc")

def set_password(u):
    clear()
    while True:
        print(f"Setting a password for '{u}':")
        os.system(f"chroot /mnt passwd {u}")
        print("Was your password set properly (y/n)?")
        reply = input("> ")
        if reply.casefold() == "y":
            break
        else:
            continue

def main(args, distro):
    print("Welcome to the astOS installer!\n\n\n\n\n")
    choice, distro_suffix = get_multiboot("fedora")

#   Define variables
    ARCH="x86_64"
    RELEASE="rawhide"
    #astpart = to_uuid(args[1])
    btrdirs = [f"@{distro_suffix}",f"@.snapshots{distro_suffix}",f"@home{distro_suffix}",f"@var{distro_suffix}",f"@etc{distro_suffix}",f"@boot{distro_suffix}"]
    mntdirs = ["",".snapshots","home","var","etc","boot"]
    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False

    astpart = to_uuid(args[1]) ### DELETE THIS LINE WHEN PRODUCTION READY

    tz= get_timezone()
    hostname  = get_hostname()

####### STEP 4 BEGINS HERE

    os.system(f"echo 'releasever={RELEASE}' | tee /mnt/etc/yum.conf") ########NEW FOR FEDORA
    
    ### glibc-locale-source is already installed
    os.system(f"chroot /mnt dnf install -y systemd ncurses bash-completion kernel glibc-locale-source glibc-langpack-en --releasever={RELEASE}") ########NEW FOR FEDORA package 'systemd' already installed using whatever above packages came

#   Update hostname, hosts, locales and timezone, hosts
    os.system(f"echo {hostname} | tee /mnt/etc/hostname")
    os.system(f"echo 127.0.0.1 {hostname} | sudo tee -a /mnt/etc/hosts")
#    os.system("sed -i 's/^#en_US.UTF-8/en_US.UTF-8/g' /etc/locale.gen")
    ### os.system("yum -y install glibc-langpack-en") ######### glibc-locale-source is already installed
    os.system("chroot /mnt localedef -v -c -i en_US -f UTF-8 en_US.UTF-8") #######REZA got error (
    os.system("echo 'LANG=en_US.UTF-8' | tee /mnt/etc/locale.conf")
    os.system(f"chroot /mnt ln -sf {tz} /etc/localtime")
    os.system("chroot /mnt /usr/sbin/hwclock --systohc")    #REZA hwclock and locale-gen commands not found!

args = list(sys.argv)
distro="fedora"
main(args, distro)
