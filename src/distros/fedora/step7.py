#!/usr/bin/python3

# might need to append /bin/sh or /bin/bash to chroot commands, as arch iso live cd use zsh and choroot environment is bash

import os
import subprocess
import sys

def clear():
    os.system("#clear")

def to_uuid(part):
    return subprocess.check_output(f"/usr/sbin/blkid -s UUID -o value {part}", shell=True).decode('utf-8').strip()

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
    os.system(f"chroot /mnt /usr/sbin/useradd -m -G wheel -s /bin/bash {u}")
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
    choice, distro_suffix = get_multiboot(distro)

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
    #packages = "passwd which grub2-efi-x64-modules shim-x64 btrfs-progs python-anytree sudo tmux neovim NetworkManager dhcpcd"
    packages = "passwd which grub2-efi-x64-modules shim-x64 btrfs-progs python-anytree sudo neovim efibootmgr"

#   Partition and format
#    if choice != "3":
#        os.system(f"/usr/sbin/mkfs.vfat -F32 -n EFI {args[3]}") ### DELETE THIS LINE WHEN PRODUCTION READY
#        os.system(f"/usr/sbin/mkfs.btrfs -L LINUX -f {args[1]}")
#    os.system("pacman -Syy --noconfirm archlinux-keyring dnf")

    astpart = to_uuid(args[1]) ### DELETE THIS LINE WHEN PRODUCTION READY

#### STEP 7 Begins here

#################### IMPORTANT: Installations continue to go into  /usr/sbin which is not in PATH and binaries are not found automatically. I should find a way to add /usr/sbin to PATH
################### cp /usr/sbin/btrfs* /usr/bin/
################### cp /usr/sbin/blkid /usr/bin/

    distro="fedora"

#   GRUB and EFI
#   REALLY ANNOYING BUG: https://bugzilla.redhat.com/show_bug.cgi?id=1917213
#   https://fedoraproject.org/wiki/GRUB_2#Instructions_for_UEFI-based_systems
    #os.system(f"chroot /mnt /usr/sbin/grub2-install {args[2]}") #REZA --recheck --no-nvram --removable (not needed for Fedora on EFI)
    # if dnf reinstall shim-* grub2-efi-* grub2-common return an exitcode of error (excode != 0), run dnf install shim-x64 grub2-efi-x64 grub2-common
    os.system("mkdir -p /mnt/boot/grub2/BAK") # Folder for backing up grub configs created by astpk
    os.system(f"chroot /mnt sudo /usr/sbin/grub2-mkconfig {args[2]} -o /boot/grub2/grub.cfg")
#### In Fedora files are under /boot/loader/entries/
    os.system(f"sed -i '0,/subvol=@{distro_suffix}/ s,subvol=@{distro_suffix},subvol=@.snapshots{distro_suffix}/rootfs/snapshot-tmp,g' /mnt/boot/loader/entries/*")
    if efi: # Create a map.txt file "distro" <=> "BootOrder number" Ash reads from this file to switch between distros
        if not os.path.exists("/mnt/boot/efi/EFI/map.txt"):
            os.system("echo DISTRO,BootOrder | tee /mnt/boot/efi/EFI/map.txt")
        os.system(f"efibootmgr -c -d {args[2]} -p 1 -L 'Fedora' -l '\EFI\fedora\grubx64.efi'")
        os.system(f"echo '{distro},' $(efibootmgr -v | grep -i {distro} | awk '"'{print $1}'"' | sed '"'s/[^0-9]*//g'"') | tee -a /mnt/boot/efi/EFI/map.txt")



#### grubby shim-x64
#grub2-common grub2-tools-minimal grub2-tools-efi os-prober grub2-tools grub2-efi-x64

#  efibootmgr -c -d /dev/sda -p 1 -L "Fedora" -l '\EFI\fedora\grubx64.efi'

args = list(sys.argv)
distro="fedora"
main(args, distro)







