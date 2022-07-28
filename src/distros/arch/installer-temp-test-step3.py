#!/usr/bin/python3

#########3 space_cache=v2 -----------> mount -o noatime,compress=zstd,ssd,space_cache=v2 "${__mapper__}" /mnt

import os
import subprocess
import sys ### REMOVE WHEN USING TRY CATCH

def clear():
    os.system("#clear")

def to_uuid(part):
    return subprocess.check_output(f"sudo blkid -s UUID -o value {part}", shell=True).decode('utf-8').strip()

#   This function returns a tuple: (1. choice whether partitioning and formatting should happen
#   2. Underscore plus name of distro if it should be appended to sub-volume names
def get_multiboot(dist):
    clear()
    while True:
        print("Please choose one of the following:\n1. Single OS installation\n2. Initiate a multi-boot ashos setup\n3. Adding to an already installed ashos")
        print("Please be aware choosing option 1 and 2 will wipe {args[1]}")
        i = input("> ")
        if i == "1":
            return i, ""
            break
        elif i == "2":
            return i, f"_{dist}"
            break
        elif i == "3":
            return i, f"_{dist}"
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
            print("Happy with your hostname? (y/n)")
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
            print("Invalid timezone!")
            continue

def get_username():
    clear()
    while True:
        print("Enter username (all lowercase, max 8 letters)")
        username = input("> ")
        if username:
            print("Happy with your username? (y/n)")
            reply = input("> ")
            if reply.casefold() == "y":
                break
            else:
                continue
    return username

def get_luks():
    clear()
    while True:
        print("Would you like to use LUKS? (y/n)")
        reply = input("> ")
        if reply.casefold() == "y":
            enc = True
            break
        elif reply.casefold() == "n":
            enc = False
            break
        else:
            continue
    return enc

def create_user(u, g):
    os.system(f"sudo chroot /mnt sudo useradd -m -G {g} -s /bin/bash {u}")
    os.system(f"echo '%{g} ALL=(ALL:ALL) ALL' | sudo tee -a /mnt/etc/sudoers")
    os.system(f"echo 'export XDG_RUNTIME_DIR=\"/run/user/1000\"' | sudo tee -a /mnt/home/{u}/.bashrc")

def set_password(u):
    clear()
    while True:
        print(f"Setting a password for '{u}':")
        os.system(f"sudo chroot /mnt sudo passwd {u}")
        print("Was your password set properly? (y/n)")
        reply = input("> ")
        if reply.casefold() == "y":
            break
        else:
            continue

def main(args, distro):
    print("Welcome to the AshOS installer!\n\n\n\n\n")

#   Define variables
    #packages = "base linux linux-firmware nano python3 python-anytree bash dhcpcd \
    #            arch-install-scripts btrfs-progs networkmanager grub sudo tmux os-prober"
    packages = "base linux bash \
                btrfs-progs grub sudo"
    choice, distro_suffix = get_multiboot(distro)
    btrdirs = [f"@{distro_suffix}", f"@.snapshots{distro_suffix}", f"@boot{distro_suffix}", f"@etc{distro_suffix}", f"@home{distro_suffix}", f"@var{distro_suffix}"]
    mntdirs = ["", ".snapshots", "boot", "etc", "home", "var"]
    tz = get_timezone()
    hostname = get_hostname()
    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False
    luks_grub_args = ""
    isLUKS = get_luks()

#   Prep (format partition, etc.)
    if isLUKS:
        luks_grub_args = "luks2 btrfs part_gpt cryptodisk gcry_rijndael pbkdf2 gcry_sha512"
        btrfs_root = "/dev/mapper/luks_root"
    else:
        btrfs_root = args[1]


###   RAN THESE BY HAND
#    if isLUKS:
#        os.system(f"sudo sed -i '/^HOOKS/ s/filesystems/encrypt filesystems/' /mnt/etc/mkinitcpio.conf")
#        os.system("sudo chroot /mnt sudo mkinitcpio -p linux")

#    os.system(f'sudo chroot /mnt sudo grub-install --modules="{luks_grub_args}" {args[2]}')

#    if isLUKS: # Make LUKS2 compatible grub image
#        os.system(f"sed -i.bak 's|LUKS_UUID_WITHOUT_DASHES|{to_uuid(args[1]).replace('-', '')}|' ./src/distros/arch/grub-luks2.conf")
#        os.system(f"sed -i.bak 's|DISTRO_SUFFIX|{distro_suffix}|' ./src/distros/arch/grub-luks2.conf")
#        os.system("cp -a ./src/distros/arch/grub-luks2.conf /mnt/tmp/")
#        os.system(f'sudo chroot /mnt sudo grub-mkimage -p "(crypto0)/@boot_arch" -O x86_64-efi -c /tmp/grub-luks2.conf -o /boot/efi/EFI/{distro}/grubx64.efi {luks_grub_args}')
        
#    os.system(f"sudo chroot /mnt sudo grub-mkconfig {args[2]} -o /boot/grub/grub.cfg")

##########
    input("> after bp1")
##########


    os.system("sudo mkdir -p /mnt/boot/grub/BAK") # Folder for backing up grub configs created by astpk
###    os.system(f"sudo sed -i '0,/subvol=@{distro_suffix}/ s,subvol=@{distro_suffix},subvol=@.snapshots{distro_suffix}/rootfs/snapshot-tmp,g' /mnt/boot/grub/grub.cfg") ### This was not replacing mount points in Advanced section
    os.system(f"sudo sed -i 's,subvol=@{distro_suffix},subvol=@.snapshots{distro_suffix}/rootfs/snapshot-tmp,g' /mnt/boot/grub/grub.cfg")
    # Create a mapping of "distro" <=> "BootOrder number". Ash reads from this file to switch between distros.
    if efi:
        if not os.path.exists("/mnt/boot/efi/EFI/map.txt"):
            os.system("echo DISTRO,BootOrder | sudo tee /mnt/boot/efi/EFI/map.txt")
        os.system(f"echo '{distro},' $(efibootmgr -v | grep -i {distro} | awk '"'{print $1}'"' | sed '"'s/[^0-9]*//g'"') | sudo tee -a /mnt/boot/efi/EFI/map.txt")


##########
    input("> bp2")
##########

#   BTRFS snapshots
    os.system("sudo btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-0")
    os.system("sudo btrfs sub create /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/boot/* /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/etc/* /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/boot/boot-tmp /mnt/.snapshots/boot/boot-0")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/etc/etc-tmp /mnt/.snapshots/etc/etc-0")
    os.system("sudo btrfs sub snap /mnt/.snapshots/rootfs/snapshot-0 /mnt/.snapshots/rootfs/snapshot-tmp")
    os.system("sudo chroot /mnt sudo btrfs sub set-default /.snapshots/rootfs/snapshot-tmp")
    os.system("sudo cp -r /mnt/root/. /mnt/.snapshots/root/")
    os.system("sudo cp -r /mnt/tmp/. /mnt/.snapshots/tmp/")
    os.system("sudo rm -rf /mnt/root/*")
    os.system("sudo rm -rf /mnt/tmp/*")

##########
    input("> bp3")
##########


#   Copy boot and etc from snapshot's tmp to common
    if efi:
        os.system("sudo umount /mnt/boot/efi")
    os.system("sudo umount /mnt/boot")
    os.system(f"sudo mount {btrfs_root} -o subvol=@boot{distro_suffix},compress=zstd,noatime /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-tmp/. /mnt/boot/")
    os.system("sudo umount /mnt/etc")
    os.system(f"sudo mount {btrfs_root} -o subvol=@etc{distro_suffix},compress=zstd,noatime /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-tmp/. /mnt/etc/")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-0/. /mnt/.snapshots/rootfs/snapshot-tmp/boot/")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-0/. /mnt/.snapshots/rootfs/snapshot-tmp/etc/")

#   Unmount everything and finish
    os.system("sudo umount -R /mnt")
    os.system(f"sudo mount {btrfs_root} -o subvolid=0 /mnt")
    os.system(f"sudo btrfs sub del /mnt/@{distro_suffix}")
    os.system("sudo umount -R /mnt")
    if isLUKS:
        os.system("sudo cryptsetup close luks_root")
    clear()
    print("Installation complete")
    print("You can reboot now :)")




args = list(sys.argv)
distro="arch"
distro_suffix="_arch"
main(args, distro)
