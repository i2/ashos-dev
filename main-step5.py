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

#REZA: STEP 5 BEGINS HERE
    os.system("echo {\\'name\\': \\'root\\', \\'children\\': [{\\'name\\': \\'0\\'}]} | sudo tee /mnt/.snapshots/ast/fstree")

    if DesktopInstall:
        os.system("echo {\\'name\\': \\'root\\', \\'children\\': [{\\'name\\': \\'0\\'},{\\'name\\': \\'1\\'}]} | sudo tee /mnt/.snapshots/ast/fstree")
        os.system(f"echo '{astpart}' | sudo tee /mnt/.snapshots/ast/part")

    os.system(f"sudo chroot /mnt sed -i s,Arch,astOS,g /etc/default/grub")
    os.system(f"sudo chroot /mnt grub-install {args[2]}")
    os.system(f"sudo chroot /mnt grub-mkconfig {args[2]} -o /boot/grub/grub.cfg")
    os.system("sudo sed -i '0,/subvol=@/{s,subvol=@,subvol=@.snapshots/rootfs/snapshot-tmp,g}' /mnt/boot/grub/grub.cfg")
    os.system("sudo cp ./astpk.py /mnt/usr/local/sbin/ast")
    os.system("sudo chroot /mnt chmod +x /usr/local/sbin/ast")
    os.system("sudo btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-0")
    os.system("sudo btrfs sub create /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/var/var-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/boot/boot-tmp")
#    os.system("cp --reflink=auto -r /mnt/var/* /mnt/.snapshots/var/var-tmp")
    #os.system("sudo mkdir -p /mnt/.snapshots/var/var-tmp/lib/pacman")       #shouldl be changed for debian
    os.system("sudo mkdir -p /mnt/.snapshots/var/var-tmp/lib/systemd")
#    os.system("sudo cp --reflink=auto -r /mnt/var/lib/pacman/* /mnt/.snapshots/var/var-tmp/lib/pacman/") #shouldl be changed for debian
    os.system("sudo cp --reflink=auto -r /mnt/var/lib/systemd/* /mnt/.snapshots/var/var-tmp/lib/systemd/")
    os.system("sudo cp --reflink=auto -r /mnt/boot/* /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/etc/* /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/var/var-tmp /mnt/.snapshots/var/var-0")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/boot/boot-tmp /mnt/.snapshots/boot/boot-0")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/etc/etc-tmp /mnt/.snapshots/etc/etc-0")
    os.system(f"echo '{astpart}' | sudo tee /mnt/.snapshots/ast/part")

    os.system("sudo btrfs sub snap /mnt/.snapshots/rootfs/snapshot-0 /mnt/.snapshots/rootfs/snapshot-tmp")

main(args)

