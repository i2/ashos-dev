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

####### STEP 2 BEGINS HERE

    #os.system(f"dnf makecache --refresh --releasever={RELEASE} -c ./src/distros/fedora/base.repo")
    
    for i in ("/dev", "/dev/pts", "/proc", "/run", "/sys", "/sys/firmware/efi/efivars"):  ### REZA In debian, these mount-points operations go 'after' debootstrapping and there is no complaint! In fedora, if so, dnf would complain /dev is not mounted!
        #os.system(f"mkdir -p /mnt{i}")
        os.system(f"mount -B {i} /mnt{i}") # Mount-points needed for chrooting
    
    os.system(f"dnf -c ./src/distros/fedora/base.repo --installroot=/mnt install dnf -y --releasever={RELEASE}")  #### removed basearch as it was giving unrecognized arguments error!
    if efi:
        os.system("chroot /mnt dnf install -y efibootmgr grub2-efi-x64 grub2-common")

####### STEP 3 BEGINS HERE

    #os.system("chroot /mnt dnf install -y passwd which grub2-efi-x64-modules os-prober shim-x64")
    
    #   Update fstab
    os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" / btrfs subvol=@{distro_suffix},compress=zstd,noatime,ro 0 0' | sudo tee /mnt/etc/fstab")
    for mntdir in mntdirs:
        os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" /{mntdir} btrfs subvol=@{mntdir}{distro_suffix},compress=zstd,noatime 0 0' | sudo tee -a /mnt/etc/fstab")
    if efi:
        os.system(f"echo 'UUID=\"{to_uuid(args[3])}\" /boot/efi vfat umask=0077 0 2' | tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/root /root none bind 0 0' | tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/tmp /tmp none bind 0 0' | tee -a /mnt/etc/fstab")

    os.system("mkdir -p /mnt/usr/share/ast/db")
    os.system("echo '0' | tee /mnt/usr/share/ast/snap")
    #os.system(f"cp -r /mnt/var/lib/pacman/* /mnt/usr/share/ast/db")
    #os.system(f"sed -i s,\"#DBPath      = /var/lib/pacman/\",\"DBPath      = /usr/share/ast/db/\",g /mnt/etc/pacman.conf")

#   Modify OS release information (optional)
    os.system(f"sed -i '/^NAME/ s/Fedora Linux/Fedora Linux (ashos)/' /mnt/etc/os-release")
    os.system(f"sed -i '/PRETTY_NAME/ s/Fedora Linux/Fedora Linux (ashos)/' /mnt/etc/os-release")
    os.system(f"sed -i '/^ID/ s/fedora/fedora_ashos/' /mnt/etc/os-release")
    #os.system("echo 'HOME_URL=\"https://github.com/astos/astos\"' | tee -a /mnt/etc/os-release")


args = list(sys.argv)
distro="fedora"
main(args, distro)
