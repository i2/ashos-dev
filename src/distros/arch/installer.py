#!/usr/bin/python3

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
        print("Please choose one of the following:\n1. Single OS installation\n2. Initiate a multi-boot ashos setup\n3. Adding to an already installed ashos.")
        print("Please be aware choosing option 1 and 2 will wipe root partition.")
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
        h = input("> ")
        if h:
            print("Happy with your hostname? (y/n)")
            reply = input("> ")
            if reply.casefold() == "y":
                break
            else:
                continue
    return h

def get_timezone():
    clear()
    while True:
        print("Select a timezone (type list to list):")
        z = input("> ")
        if z == "list":
            os.system("ls /usr/share/zoneinfo | less")
        elif os.path.isfile(f"/usr/share/zoneinfo/{z}"):
            return str(f"/usr/share/zoneinfo/{z}")
        else:
            print("Invalid timezone!")
            continue

def get_username():
    clear()
    while True:
        print("Enter username (all lowercase):")
        u = input("> ")
        if u:
            print("Happy with your username? (y/n)")
            reply = input("> ")
            if reply.casefold() == "y":
                break
            else:
                continue
    return u

def get_luks():
    clear()
    while True:
        print("Would you like to use LUKS? (y/n)")
        reply = input("> ")
        if reply.casefold() == "y":
            e = True
            break
        elif reply.casefold() == "n":
            e = False
            break
        else:
            continue
    return e

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
    packages = "base linux btrfs-progs dhcpcd nano bash grub sudo tmux" # Just for debugging
    choice, distro_suffix = get_multiboot(distro)
    btrdirs = [f"@{distro_suffix}", f"@.snapshots{distro_suffix}", f"@boot{distro_suffix}", f"@etc{distro_suffix}", f"@home{distro_suffix}", f"@var{distro_suffix}"]
    mntdirs = ["", ".snapshots", "boot", "etc", "home", "var"]
    isLUKS = get_luks()
    tz = get_timezone()
#    hostname = get_hostname()
    hostname = subprocess.check_output(f"git rev-parse --short HEAD", shell=True).decode('utf-8').strip() # Just for debugging
    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False
    if isLUKS:
        btrfs_root = "/dev/mapper/luks_root"
        if efi:
            luks_grub_args = "luks2 btrfs part_gpt cryptodisk pbkdf2 gcry_rijndael gcry_sha512"
        else:
            luks_grub_args = "luks2 btrfs biosdisk part_msdos cryptodisk pbkdf2 gcry_rijndael gcry_sha512"
    else:
        btrfs_root = args[1]
        luks_grub_args = ""

#   Prep (format partition, etc.)
    if isLUKS:
        os.system("sudo modprobe dm-crypt")
        print("--- Create LUKS partition --- ")
        os.system(f"sudo cryptsetup -y -v -c aes-xts-plain64 -s 512 --hash sha512 --pbkdf pbkdf2 --type luks2 luksFormat {args[1]}")
        print("--- Open LUKS partition --- ")
        os.system(f"sudo cryptsetup --allow-discards --persistent --type luks2 open {args[1]} luks_root")
    if choice != "3":
        os.system(f"sudo mkfs.btrfs -L LINUX -f {btrfs_root}")
    os.system("pacman -Syy --noconfirm archlinux-keyring")

#   Mount and create necessary sub-volumes and directories
    if choice != "3":
        os.system(f"sudo mount -t btrfs {btrfs_root} /mnt")
    else:
        os.system(f"sudo mount -o subvolid=5 {btrfs_root} /mnt")
    for btrdir in btrdirs:
        os.system(f"sudo btrfs sub create /mnt/{btrdir}")
    os.system("sudo umount /mnt")
    for mntdir in mntdirs:
        os.system(f"sudo mkdir -p /mnt/{mntdir}") # -p to ignore /mnt exists complaint
        os.system(f"sudo mount {btrfs_root} -o subvol={btrdirs[mntdirs.index(mntdir)]},compress=zstd,noatime /mnt/{mntdir}")
    for i in ("tmp", "root"):
        os.system(f"mkdir -p /mnt/{i}")
    for i in ("ash", "boot", "etc", "root", "rootfs", "tmp"):
        os.system(f"mkdir -p /mnt/.snapshots/{i}")
    if efi:
        os.system("sudo mkdir -p /mnt/boot/efi")
        os.system(f"sudo mount {args[3]} /mnt/boot/efi")

#   Bootstrap then install anytree and necessary packages in chroot
    excode = int(os.system(f"sudo pacstrap /mnt {packages}"))
    if excode != 0:
        print("Failed to bootstrap!")
        sys.exit()
    if efi:
        excode = int(os.system("sudo pacstrap /mnt efibootmgr"))
        if excode != 0:
            print("Failed to download packages!")
            sys.exit()
    # Mount-points needed for chrooting
    os.system("sudo mount -o x-mount.mkdir --rbind --make-rslave /dev /mnt/dev")
    os.system("sudo mount -o x-mount.mkdir --types proc /proc /mnt/proc")
    os.system("sudo mount -o x-mount.mkdir --bind --make-slave /run /mnt/run")
    os.system("sudo mount -o x-mount.mkdir --rbind --make-rslave /sys /mnt/sys")
    if efi:
        os.system("sudo mount -o x-mount.mkdir --rbind --make-rslave /sys/firmware/efi/efivars /mnt/sys/firmware/efi/efivars")
    os.system("sudo cp --dereference /etc/resolv.conf /mnt/etc/")

#   Update fstab
    os.system(f"echo 'UUID=\"{to_uuid(btrfs_root)}\" / btrfs subvol=@{distro_suffix},compress=zstd,noatime,ro 0 0' | sudo tee -a /mnt/etc/fstab")
    for mntdir in mntdirs:
        os.system(f"echo 'UUID=\"{to_uuid(btrfs_root)}\" /{mntdir} btrfs subvol=@{mntdir}{distro_suffix},compress=zstd,noatime 0 0' | sudo tee -a /mnt/etc/fstab")
    if efi:
        os.system(f"echo 'UUID=\"{to_uuid(args[3])}\" /boot/efi vfat umask=0077 0 2' | sudo tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ash/root /root none bind 0 0' | sudo tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ash/tmp /tmp none bind 0 0' | sudo tee -a /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@{distro_suffix}/ s|@{distro_suffix}|@.snapshots{distro_suffix}/rootfs/snapshot-deploy|' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@boot{distro_suffix}/ s|@boot{distro_suffix}|@.snapshots{distro_suffix}/boot/boot-deploy|' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@etc{distro_suffix}/ s|@etc{distro_suffix}|@.snapshots{distro_suffix}/etc/etc-deploy|' /mnt/etc/fstab")
    os.system(f"sudo sed -i '/\@{distro_suffix}/d' /mnt/etc/fstab") # Delete @_distro entry

#   Database and config files
    os.system("sudo mkdir -p /mnt/usr/share/ash/db")
    os.system("echo '0' | sudo tee /mnt/usr/share/ash/snap")
    os.system("sudo cp -r /mnt/var/lib/pacman/. /mnt/usr/share/ash/db/")
    os.system(f"sed -i 's|[#?]DBPath.*$|DBPath       = /usr/share/ash/db/|g' /mnt/etc/pacman.conf")
    os.system(f"sudo sed -i '/^ID/ s|{distro}|{distro}_ashos|' /mnt/etc/os-release") # Modify OS release information (optional)

#   Update hostname, hosts, locales and timezone, hosts
    os.system(f"echo {hostname} | sudo tee /mnt/etc/hostname")
    os.system(f"echo 127.0.0.1 {hostname} | sudo tee -a /mnt/etc/hosts")
    os.system("sudo sed -i 's|^#en_US.UTF-8|en_US.UTF-8|g' /mnt/etc/locale.gen")
    os.system("sudo chroot /mnt sudo locale-gen")
    os.system("echo 'LANG=en_US.UTF-8' | sudo tee /mnt/etc/locale.conf")
    os.system(f"sudo ln -srf /mnt{tz} /mnt/etc/localtime")
    os.system("sudo chroot /mnt sudo hwclock --systohc")

#   Copy and symlink ashpk and detect_os.sh
    os.system("sudo mkdir -p /mnt/.snapshots/ash/snapshots")
    os.system(f"echo '{to_uuid(btrfs_root)}' | sudo tee /mnt/.snapshots/ash/part")
    os.system(f"sudo cp -a ./src/distros/{distro}/ashpk.py /mnt/.snapshots/ash/ash")
    os.system("sudo cp -a ./src/detect_os.sh /mnt/.snapshots/ash/detect_os.sh")
    os.system("sudo ln -srf /mnt/.snapshots/ash/ash /mnt/usr/bin/ash")
    os.system("sudo ln -srf /mnt/.snapshots/ash/detect_os.sh /mnt/usr/bin/detect_os.sh")
    os.system("sudo ln -srf /mnt/.snapshots/ash /mnt/var/lib/ash")
    os.system("echo {\\'name\\': \\'root\\', \\'children\\': [{\\'name\\': \\'0\\'}]} | sudo tee /mnt/.snapshots/ash/fstree") # Initialize fstree

#   Create user and set password
    set_password("root")
    username = get_username()
    create_user(username, "wheel")
    set_password(username)

#   Services (init, network, etc.)
    os.system("sudo chroot /mnt systemctl enable NetworkManager")

#   GRUB and EFI
    if isLUKS:
        os.system("sudo dd bs=512 count=4 if=/dev/random of=/mnt/etc/crypto_keyfile.bin iflag=fullblock")
        os.system("sudo chmod 600 /mnt/etc/crypto_keyfile.bin")
        os.system(f"sudo cryptsetup luksAddKey {args[1]} /mnt/etc/crypto_keyfile.bin")
        os.system("sudo sed -i -e '/^HOOKS/ s/filesystems/encrypt filesystems/' \
                    -e 's|^FILES=(|FILES=(/etc/crypto_keyfile.bin|' /mnt/etc/mkinitcpio.conf")
        os.system("sudo chroot /mnt sudo mkinitcpio -p linux")
        os.system("sudo sed -i 's/^#GRUB_ENABLE_CRYPTODISK/GRUB_ENABLE_CRYPTODISK/' -i /mnt/etc/default/grub")
        os.system(f"sudo sed -i -E 's|^#?GRUB_CMDLINE_LINUX=\"|GRUB_CMDLINE_LINUX=\"cryptdevice=UUID={to_uuid(args[1])}:luks_root|' /mnt/etc/default/grub")
        os.system(f"sed -e 's|DISTRO|{distro}|' -e 's|LUKS_UUID_NODASH|{to_uuid(args[1]).replace('-', '')}|' \
                        -e '/^#/d' ./src/distros/arch/grub-luks2.conf | sudo tee /mnt/etc/grub-luks2.conf")
    if efi: # running this seems to write core.img so it's important for this to be before mkimage
        os.system(f'sudo chroot /mnt sudo grub-install {args[2]} --modules="{luks_grub_args}"')
    else:
        os.system(f'sudo chroot /mnt sudo grub-install {args[2]} --modules="{luks_grub_args}"')
    if isLUKS: # Make LUKS2 compatible grub image
        if efi:
            os.system(f'sudo chroot /mnt sudo grub-mkimage -p "(crypto0)/@boot_arch/grub" -O x86_64-efi -c /etc/grub-luks2.conf -o /boot/efi/EFI/{distro}/grubx64.efi {luks_grub_args}') # without '/grub' gives error normal.mod not found (maybe only one of these here and grub-luks2.conf is enough?!) ### changed from /tmp to $HOME
        else:
            os.system(f'sudo chroot /mnt sudo grub-mkimage -p "(crypto0)/@boot_arch/grub" -O i386-pc -c /etc/grub-luks2.conf -o /boot/grub/i386-pc/core_luks2.img {luks_grub_args}') # without '/grub' gives error normal.mod not found (maybe only one of these here and grub-luks2.conf is enough?!) ### 'biosdisk' module not needed eh?
            os.system(f'dd oflag=seek_bytes seek=512 if=/mnt/boot/grub/i386-pc/core_luks2.img of={args[2]}')
    os.system(f"sudo chroot /mnt sudo grub-mkconfig {args[2]} -o /boot/grub/grub.cfg")
    os.system("sudo mkdir -p /mnt/boot/grub/BAK") # Folder for backing up grub configs created by ashpk
###    os.system(f"sudo sed -i '0,/subvol=@{distro_suffix}/ s,subvol=@{distro_suffix},subvol=@.snapshots{distro_suffix}/rootfs/snapshot-tmp,g' /mnt/boot/grub/grub.cfg") ### This was not replacing mount points in Advanced section
    os.system(f"sudo sed -i 's|subvol=@{distro_suffix}|subvol=@.snapshots{distro_suffix}/rootfs/snapshot-deploy|g' /mnt/boot/grub/grub.cfg")
    # Create a mapping of "distro" <=> "BootOrder number". Ash reads from this file to switch between distros.
    if efi:
        if not os.path.exists("/mnt/boot/efi/EFI/map.txt"):
            os.system("echo DISTRO,BootOrder | sudo tee /mnt/boot/efi/EFI/map.txt")
        os.system(f"echo '{distro},' $(efibootmgr -v | grep -i {distro} | awk '"'{print $1}'"' | sed '"'s|[^0-9]*||g'"') | sudo tee -a /mnt/boot/efi/EFI/map.txt")

#   BTRFS snapshots
    os.system("sudo btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-0")
    os.system("sudo btrfs sub create /mnt/.snapshots/boot/boot-deploy")
    os.system("sudo btrfs sub create /mnt/.snapshots/etc/etc-deploy")
    os.system("sudo cp --reflink=auto -r /mnt/boot/* /mnt/.snapshots/boot/boot-deploy")
    os.system("sudo cp --reflink=auto -r /mnt/etc/* /mnt/.snapshots/etc/etc-deploy")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/boot/boot-deploy /mnt/.snapshots/boot/boot-0")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/etc/etc-deploy /mnt/.snapshots/etc/etc-0")
    os.system("sudo btrfs sub snap /mnt/.snapshots/rootfs/snapshot-0 /mnt/.snapshots/rootfs/snapshot-deploy")
    os.system("sudo chroot /mnt sudo btrfs sub set-default /.snapshots/rootfs/snapshot-deploy")
    os.system("sudo cp -r /mnt/root/. /mnt/.snapshots/root/")
    os.system("sudo cp -r /mnt/tmp/. /mnt/.snapshots/tmp/")
    os.system("sudo rm -rf /mnt/root/*")
    os.system("sudo rm -rf /mnt/tmp/*")

#   Copy boot and etc: deployed snapshot <===> common
    if efi:
        os.system("sudo umount /mnt/boot/efi")
    os.system("sudo umount /mnt/boot")
    os.system(f"sudo mount {btrfs_root} -o subvol=@boot{distro_suffix},compress=zstd,noatime /mnt/.snapshots/boot/boot-deploy")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-deploy/. /mnt/boot/")
    os.system("sudo umount /mnt/etc")
    os.system(f"sudo mount {btrfs_root} -o subvol=@etc{distro_suffix},compress=zstd,noatime /mnt/.snapshots/etc/etc-deploy")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-deploy/. /mnt/etc/")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-0/. /mnt/.snapshots/rootfs/snapshot-deploy/boot/")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-0/. /mnt/.snapshots/rootfs/snapshot-deploy/etc/")

#   Unmount everything and finish
    os.system("sudo umount --recursive /mnt")
    os.system(f"sudo mount {btrfs_root} -o subvolid=0 /mnt")
    os.system(f"sudo btrfs sub del /mnt/@{distro_suffix}")
    os.system("sudo umount --recursive /mnt")
    if isLUKS:
        #os.system("sudo udevadm settle")
        os.system("sudo cryptsetup close luks_root")
    clear()
    print("Installation complete!")
    print("You can reboot now :)")

