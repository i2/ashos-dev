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

#    os.system("pacman -S --noconfirm archlinux-keyring")
#    os.system(f"mkfs.btrfs -f {args[1]}")

    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False

#    os.system(f"mount {args[1]} /mnt")
    btrdirs = ["@","@.snapshots","@home","@var","@etc","@boot"]
    mntdirs = ["",".snapshots","home","var","etc","boot"]

    mntdirs_n = mntdirs
    mntdirs_n.remove("")

    astpart = to_uuid(args[1])

#REZA: STEP 6 BEGINS HERE
    os.system("sudo chroot /mnt btrfs sub set-default /.snapshots/rootfs/snapshot-tmp")

    os.system("sudo cp -r /mnt/root/. /mnt/.snapshots/root/")
    os.system("sudo cp -r /mnt/tmp/. /mnt/.snapshots/tmp/")
    os.system("sudo rm -rf /mnt/root/*")
    os.system("sudo rm -rf /mnt/tmp/*")
#    os.system("umount /mnt/var")

    if efi:
        os.system("sudo umount /mnt/boot/efi")

    os.system("sudo umount /mnt/boot")
#    os.system("mkdir /mnt/.snapshots/var/var-tmp")
#    os.system("mkdir /mnt/.snapshots/boot/boot-tmp")
#    os.system(f"mount {args[1]} -o subvol=@var,compress=zstd,noatime /mnt/.snapshots/var/var-tmp")
    os.system(f"sudo mount {args[1]} -o subvol=@boot,compress=zstd,noatime /mnt/.snapshots/boot/boot-tmp")
#    os.system("cp --reflink=auto -r /mnt/.snapshots/var/var-tmp/* /mnt/var")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-tmp/* /mnt/boot")
    os.system("sudo umount /mnt/etc")
#    os.system("mkdir /mnt/.snapshots/etc/etc-tmp")
    os.system(f"sudo mount {args[1]} -o subvol=@etc,compress=zstd,noatime /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-tmp/* /mnt/etc")

    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-0/* /mnt/.snapshots/rootfs/snapshot-tmp/etc")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/var/var-0/* /mnt/.snapshots/rootfs/snapshot-tmp/var")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-0/* /mnt/.snapshots/rootfs/snapshot-tmp/boot")

main(args)

