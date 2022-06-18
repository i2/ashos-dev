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

    #Actual Step 3 begins here

    mntdirs_n = mntdirs
    mntdirs_n.remove("")
    os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" / btrfs subvol=@,compress=zstd,noatime,ro 0 0' | sudo tee /mnt/etc/fstab")

    for mntdir in mntdirs_n:
        os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" /{mntdir} btrfs subvol=@{mntdir},compress=zstd,noatime 0 0' | sudo tee -a /mnt/etc/fstab")

    if efi:
        os.system(f"echo 'UUID=\"{to_uuid(args[3])}\" /boot/efi vfat umask=0077 0 2' | sudo tee -a /mnt/etc/fstab")

    os.system("echo '/.snapshots/ast/root /root none bind 0 0' | sudo tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/tmp /tmp none bind 0 0' | sudo tee -a /mnt/etc/fstab")

    astpart = to_uuid(args[1])

    os.system(f"sudo mkdir -p /mnt/usr/share/ast/db")
    os.system(f"echo '0' | sudo tee /mnt/usr/share/ast/snap")

    os.system(f"echo 'NAME=\"astOS\"' | sudo tee /mnt/etc/os-release")
    os.system(f"echo 'PRETTY_NAME=\"astOS\"' | sudo tee -a /mnt/etc/os-release")
    os.system(f"echo 'ID=astos' | sudo tee -a /mnt/etc/os-release")
    os.system(f"echo 'BUILD_ID=rolling' | sudo tee -a /mnt/etc/os-release")
    os.system(f"echo 'ANSI_COLOR=\"38;2;23;147;209\"' | sudo tee -a /mnt/etc/os-release")
    os.system(f"echo 'HOME_URL=\"https://github.com/CuBeRJAN/astOS\"' | sudo tee -a /mnt/etc/os-release")
    os.system(f"echo 'LOGO=astos-logo' | sudo tee -a /mnt/etc/os-release")
    #os.system(f"sudo cp -r /mnt/var/lib/pacman/* /mnt/usr/share/ast/db")
    #os.system(f"sudo sed -i s,\"#DBPath      = /var/lib/pacman/\",\"DBPath      = /usr/share/ast/db/\",g /mnt/etc/pacman.conf")
    os.system(f"echo 'DISTRIB_ID=\"astOS\"' | sudo tee /mnt/etc/lsb-release")
    os.system(f"echo 'DISTRIB_RELEASE=\"rolling\"' | sudo tee -a /mnt/etc/lsb-release")
    os.system(f"echo 'DISTRIB_DESCRIPTION=astOS' | sudo tee -a /mnt/etc/lsb-release")

    os.system(f"sudo chroot /mnt ln -sf {timezone} /etc/localtime")
    
main(args)

