#!/usr/bin/python3
import os
import time
import sys
import subprocess

# TODO: the installer needs a proper rewrite

#os.system("sudo apt-get update")
#os.system("sudo apt-get install -y parted btrfs-progs dosfstools debootstrap tmux git")
#os.system("sudo parted --align minimal --script /dev/sda mklabel gpt unit MiB mkpart ESP fat32 0% 256 set 1 boot on mkpart primary ext4 256 100%")
#os.system("sudo /usr/sbin/mkfs.btrfs -L BTRFS /dev/sda2")
#os.system("sudo /usr/sbin/mkfs.vfat -F32 -n EFI /dev/sda1")
#sudo debootstrap bullseye /mnt http://ftp.debian.org/debian

args = list(sys.argv)

def clear():
    os.system("#clear")

def to_uuid(part):
    uuid = str(subprocess.check_output(f"sudo blkid -s UUID -o value {part}", shell=True))
    return uuid.replace("b'","").replace('"',"").replace("\\n'","")

def main(args):

    while True:
        clear()
        print("Welcome to the astOS installer!\n\n\n\n\n")
        print("Select installation profile:\n1. Minimal install - suitable for embedded devices or servers\n2. Desktop install (Gnome) - suitable for workstations\n3. Desktop install (KDE Plasma)")
        InstallProfile = str(input("> "))
        if InstallProfile == "1":
            DesktopInstall = 0
            break
        if InstallProfile == "2":
            DesktopInstall = 1
            break
        if InstallProfile == "3":
            DesktopInstall = 2
            break

    clear()
    while True:
        print("Select a timezone (type list to list):")
        zone = input("> ")
        if zone == "list":
            os.system("ls /usr/share/zoneinfo | less")
        else:
            timezone = str(f"/usr/share/zoneinfo/{zone}")
            break

    clear()
    print("Enter hostname:")
    hostname = input("> ")

#    os.system("pacman -S --noconfirm archlinux-keyring")
#    os.system(f"mkfs.btrfs -f {args[1]}")

    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False

    os.system(f"sudo mount {args[1]} /mnt")
    btrdirs = ["@","@.snapshots","@home","@var","@etc","@boot"]
    mntdirs = ["",".snapshots","home","var","etc","boot"]

    for btrdir in btrdirs:
        os.system(f"sudo btrfs sub create /mnt/{btrdir}")

    os.system(f"sudo umount /mnt")
    os.system(f"sudo mount {args[1]} -o subvol=@,compress=zstd,noatime /mnt")

    for mntdir in mntdirs:
        os.system(f"sudo mkdir /mnt/{mntdir}")
        os.system(f"sudo mount {args[1]} -o subvol={btrdirs[mntdirs.index(mntdir)]},compress=zstd,noatime /mnt/{mntdir}")

    for i in ("tmp", "root"):
        os.system(f"mkdir -p /mnt/{i}")
    for i in ("ast", "boot", "etc", "root", "rootfs", "tmp", "var"):
        os.system(f"mkdir -p /mnt/.snapshots/{i}")

    if efi:
        os.system("sudo mkdir /mnt/boot/efi")
        os.system(f"sudo mount {args[3]} /mnt/boot/efi")

main(args)

