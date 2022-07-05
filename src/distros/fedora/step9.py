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

#   GRUB and EFI
    os.system(f"chroot /mnt /usr/sbin/grub2-install {args[2]}") #REZA --recheck --no-nvram --removable
    os.system("mkdir -p /mnt/boot/grub2/BAK/") # Folder for backing up grub configs created by astpk
    os.system(f"chroot /mnt /usr/sbin/grub2-mkconfig {args[2]} -o /boot/grub2/grub.cfg")
    os.system(f"sed -i '0,/subvol=@{distro_suffix}/s,subvol=@{distro_suffix},subvol=@.snapshots{distro_suffix}/rootfs/snapshot-tmp,g' /mnt/boot/grub2/grub.cfg")
    if efi: # Create a map.txt file "distro" <=> "BootOrder number" Ash reads from this file to switch between distros
        if not os.path.exists("/mnt/boot/efi/EFI/map.txt"):
            os.system("echo DISTRO,BootOrder | tee /mnt/boot/efi/EFI/map.txt")
        os.system(f"echo '{distro},' $(efibootmgr -v | grep {distro} | awk '"'{print $1}'"' | sed '"'s/[^0-9]*//g'"') | tee -a /mnt/boot/efi/EFI/map.txt")

##done
    #os.system("btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-0")
    #os.system("btrfs sub create /mnt/.snapshots/boot/boot-tmp")
    #os.system("btrfs sub create /mnt/.snapshots/etc/etc-tmp")
    #os.system("btrfs sub create /mnt/.snapshots/var/var-tmp")

####### STEP 9 BEGINS HERE




args = list(sys.argv)
distro="fedora"
main(args, distro)
