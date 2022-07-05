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

args = list(sys.argv)
distro="fedora"
main(args, distro)

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

####### STEP 7 BEGINS HERE



    os.system(f"sed -i '0,/@{distro_suffix}/ s,@{distro_suffix},@.snapshots{distro_suffix}/rootfs/snapshot-tmp,' /mnt/etc/fstab")
    os.system(f"sed -i '0,/@boot{distro_suffix}/ s,@boot{distro_suffix},@.snapshots{distro_suffix}/boot/boot-tmp,' /mnt/etc/fstab")
    os.system(f"sed -i '0,/@etc{distro_suffix}/ s,@etc{distro_suffix},@.snapshots{distro_suffix}/etc/etc-tmp,' /mnt/etc/fstab")
    # Delete fstab created for @{distro_suffix} which is going to be deleted at the end
    os.system(f"sed -i.bak '/\@{distro_suffix}/d' /mnt/etc/fstab")

#   Copy and symlink astpk and detect_os.sh                                                              ###MOVEDTOHERE
    os.system("mkdir -p /mnt/.snapshots/ast/snapshots")
    os.system(f"cp -a ./src/distros/{distro}/astpk.py /mnt/.snapshots/ast/ast")
    os.system("cp -a ./src/detect_os.sh /mnt/.snapshots/ast/detect_os.sh")
    os.system("chroot /mnt ln -s /.snapshots/ast/ast /usr/bin/ast")             ####PR32 Can I moved it somewhere better?
    os.system("chroot /mnt ln -s /.snapshots/ast/detect_os.sh /usr/bin/detect_os.sh")
    os.system("chroot /mnt ln -s /.snapshots/ast /var/lib/ast")
    

