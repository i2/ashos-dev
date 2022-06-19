#!/usr/bin/python3
import os
import time
import sys
import subprocess

# TODO: the installer needs a proper rewrite

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

#    os.system(f"mount {args[1]} /mnt")
    btrdirs = ["@","@.snapshots","@home","@var","@etc","@boot"]
    mntdirs = ["",".snapshots","home","var","etc","boot"]

# Step 2 begins here:

#    os.system("pacstrap /mnt base linux linux-firmware nano python3 python-anytree dhcpcd arch-install-scripts btrfs-progs networkmanager grub")
    os.system("sudo debootstrap bullseye /mnt http://ftp.debian.org/debian")
    
    os.system("sudo mount --bind /dev /mnt/dev")
    os.system("sudo mount -t proc none /mnt/proc")
    os.system("sudo mount -t sysfs sys /mnt/sys")
    
    os.system("echo JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ")
    os.system("sudo chroot /mnt apt-get install linux-image-5.10.0-13-amd64")

    #Do these in the live system (not needed inside chroot)
    #sudo systemctl start systemd-timesyncd (not presebt in my debian!!!!)
    
    #sync time needed to download python3-anytree
    #sudo apt install ntp
    #sudo systemctl enable --now ntp
    #ntpq -p
    #sudo hwclock --hctosys
    
    #os.system("sudo wget http://bit.ly/3xV2F5o -O /mnt/tmp/anytree")
    #os.system("sudo chroot /mnt dpkg -i /tmp/anytree")
    #os.system("echo "deb https://www.deb-multimedia.org bullseye main non-free" | sudo tee -a /mnt/etc/apt/sources.list.d/multimedia.list > /dev/null
    #os.system("sudo chroot /mnt apt update")

    os.system("sudo chroot /mnt apt-get install -y python3 python3-anytree grub-efi network-manager btrfs-progs dhcpcd5")
    #os.system("sudo chroot /mnt apt-get install -y efibootmgr nano") #redundant as I think efibootmgr is included in a one of the previous packages

#    if efi:
#        os.system("pacstrap /mnt efibootmgr")

main(args)

