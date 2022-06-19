#!/usr/bin/python3
import os
import time
import sys
import subprocess

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

    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False

    btrdirs = ["@","@.snapshots","@home","@var","@etc","@boot"]
    mntdirs = ["",".snapshots","home","var","etc","boot"]

    mntdirs_n = mntdirs
    mntdirs_n.remove("")

    astpart = to_uuid(args[1])

#REZA: STEP 4 BEGINS HERE

    os.system("sudo sed -i '0,/@/{s,@,@.snapshots/rootfs/snapshot-tmp,}' /mnt/etc/fstab")
    os.system("sudo sed -i '0,/@etc/{s,@etc,@.snapshots/etc/etc-tmp,}' /mnt/etc/fstab")
#    os.system("sed -i '0,/@var/{s,@var,@.snapshots/var/var-tmp,}' /mnt/etc/fstab")
    os.system("sudo sed -i '0,/@boot/{s,@boot,@.snapshots/boot/boot-tmp,}' /mnt/etc/fstab")
    os.system("sudo mkdir -p /mnt/.snapshots/ast/snapshots")

    os.system("sudo chroot /mnt ln -s /.snapshots/ast /var/lib/ast")

    clear()
    os.system("sudo chroot /mnt passwd")
    while True:
        print("did your password set properly (y/n)?")
        reply = input("> ")
        if reply.casefold() == "y":
            break
        else:
            clear()
            os.system("sudo chroot /mnt passwd")

    os.system("sudo chroot /mnt systemctl enable NetworkManager")

main(args)

