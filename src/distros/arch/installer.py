#!/usr/bin/python3

import os
import subprocess

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
    os.system(f"sudo chroot /mnt /usr/sbin/useradd -m -G wheel -s /bin/bash {u}")
    os.system("echo '%wheel ALL=(ALL:ALL) ALL' | sudo tee -a /mnt/etc/sudoers")
    os.system(f"echo 'export XDG_RUNTIME_DIR=\"/run/user/1000\"' | sudo tee -a /mnt/home/{u}/.bashrc")

def set_password(u):
    clear()
    while True:
        print(f"Setting a password for '{u}':")
        os.system(f"sudo chroot /mnt passwd {u}")
        print("Was your password set properly (y/n)?")
        reply = input("> ")
        if reply.casefold() == "y":
            break
        else:
            continue

def main(args, distro):
    print("Welcome to the AshOS installer!\n\n\n\n\n")
    choice, distro_suffix = get_multiboot(distro)

#   Define variables
    packages = "base linux linux-firmware nano python3 python-anytree bash dhcpcd arch-install-scripts btrfs-progs networkmanager grub sudo tmux os-prober"
    #astpart = to_uuid(args[1])
    btrdirs = [f"@{distro_suffix}", f"@.snapshots{distro_suffix}", f"@boot{distro_suffix}", f"@etc{distro_suffix}", f"@home{distro_suffix}", f"@var{distro_suffix}"]
    mntdirs = ["", ".snapshots", "boot", "etc", "home", "var"]
    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False

    tz = get_timezone()
    hostname = get_hostname()

#   Partition and format
    if choice != "3":
        if efi:
            os.system(f"sudo /usr/sbin/mkfs.vfat -F32 -n EFI {args[3]}") ### DELETE THIS LINE WHEN PRODUCTION READY
        os.system(f"sudo /usr/sbin/mkfs.btrfs -L LINUX -f {args[1]}")
    os.system("pacman -Syy --noconfirm archlinux-keyring")

    astpart = to_uuid(args[1]) ### DELETE THIS LINE WHEN PRODUCTION READY

#   Mount and create necessary sub-volumes and directories
    if choice != "3":
        os.system(f"sudo mount {args[1]} /mnt")
    else:
        os.system(f"sudo mount -o subvolid=5 {args[1]} /mnt")
    for btrdir in btrdirs:
        os.system(f"sudo btrfs sub create /mnt/{btrdir}")
    os.system("sudo umount /mnt")
    for mntdir in mntdirs:
        os.system(f"sudo mkdir -p /mnt/{mntdir}") # -p to ignore /mnt exists complaint
        os.system(f"sudo mount {args[1]} -o subvol={btrdirs[mntdirs.index(mntdir)]},compress=zstd,noatime /mnt/{mntdir}")
    for i in ("tmp", "root"):
        os.system(f"mkdir -p /mnt/{i}")
    for i in ("ast", "boot", "etc", "root", "rootfs", "tmp"): ### JULY11, 2022 removed "var" as it's not needed!
        os.system(f"mkdir -p /mnt/.snapshots/{i}")
    if efi:
        os.system("sudo mkdir /mnt/boot/efi")
        os.system(f"sudo mount {args[3]} /mnt/boot/efi")

#   Modify shell profile for debug purposes in live iso (optional temporary)
    #os.system('echo "alias paste='"'"'curl -F "'"'"'"sprunge=<-"'"'"'" http://sprunge.us'"'"' " | tee -a $HOME/.*shrc')
    #os.system("shopt -s nullglob && echo 'export LC_ALL=C' | sudo tee -a /mnt/root/.*shrc")
    #os.system("find /mnt/root/ -maxdepth 1 -type f -iname '.*shrc' -exec sh -c 'echo export LC_ALL=C | sudo tee -a $1' -- {} \;")
    #os.system("echo -e 'setw -g mode-keys vi\nset -g history-limit 999999' >> $HOME/.tmux.conf")

#   Bootstrap then install anytree and necessary packages in chroot
    excode = int(os.system(f"sudo pacstrap /mnt {packages}"))
    if excode != 0:
        print("Failed to download packages!")
        sys.exit()
    if efi:
        excode = int(os.system("sudo pacstrap /mnt efibootmgr"))
        if excode != 0:
            print("Failed to download packages!")
            sys.exit()
    for i in ("/dev", "/dev/pts", "/proc", "/run", "/sys", "/sys/firmware/efi/efivars"):
        os.system(f"sudo mount -B {i} /mnt{i}") # Mount-points needed for chrooting

#   Update fstab
    os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" / btrfs subvol=@{distro_suffix},compress=zstd,noatime,ro 0 0' | sudo tee /mnt/etc/fstab")
    for mntdir in mntdirs:
        os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" /{mntdir} btrfs subvol=@{mntdir}{distro_suffix},compress=zstd,noatime 0 0' | sudo tee -a /mnt/etc/fstab")
    if efi:
        os.system(f"echo 'UUID=\"{to_uuid(args[3])}\" /boot/efi vfat umask=0077 0 2' | sudo tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/root /root none bind 0 0' | sudo tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/tmp /tmp none bind 0 0' | sudo tee -a /mnt/etc/fstab")

    os.system("sudo mkdir -p /mnt/usr/share/ast/db")
    os.system("echo '0' | sudo tee /mnt/usr/share/ast/snap")
    os.system("sudo cp -r /mnt/var/lib/pacman/* /mnt/usr/share/ast/db")
    os.system(f"sed -i s,\"#DBPath      = /var/lib/pacman/\",\"DBPath      = /usr/share/ast/db/\",g /mnt/etc/pacman.conf")

#   Modify OS release information (optional)
    os.system(f"sudo sed -i '/^NAME/ s/Arch Linux/Arch Linux (ashos)/' /mnt/etc/os-release")
    os.system(f"sudo sed -i '/PRETTY_NAME/ s/Arch Linux/Arch Linux (ashos)/' /mnt/etc/os-release")
    os.system(f"sudo sed -i '/^ID/ s/arch/arch_ashos/' /mnt/etc/os-release")
    #os.system("echo 'HOME_URL=\"https://github.com/astos/astos\"' | sudo tee -a /mnt/etc/os-release")

#   Update hostname, hosts, locales and timezone, hosts
    os.system(f"echo {hostname} | sudo tee /mnt/etc/hostname")
    os.system(f"echo 127.0.0.1 {hostname} | sudo tee -a /mnt/etc/hosts")
    os.system("sudo sed -i 's/^#en_US.UTF-8/en_US.UTF-8/g' /etc/locale.gen")
    os.system("sudo chroot /mnt locale-gen")
    os.system("echo 'LANG=en_US.UTF-8' | sudo tee /mnt/etc/locale.conf")
    os.system(f"sudo chroot /mnt ln -sf {tz} /etc/localtime")
    os.system("sudo chroot /mnt /usr/sbin/hwclock --systohc")

    os.system(f"sudo sed -i '0,/@{distro_suffix}/ s,@{distro_suffix},@.snapshots{distro_suffix}/rootfs/snapshot-tmp,' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@boot{distro_suffix}/ s,@boot{distro_suffix},@.snapshots{distro_suffix}/boot/boot-tmp,' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@etc{distro_suffix}/ s,@etc{distro_suffix},@.snapshots{distro_suffix}/etc/etc-tmp,' /mnt/etc/fstab")
    # Delete fstab created for @{distro_suffix} which is going to be deleted (at the end of installer)
    os.system(f"sudo sed -i.bak '/\@{distro_suffix}/d' /mnt/etc/fstab")

#   Copy and symlink astpk and detect_os.sh                                     ###MOVEDTOHERE
    os.system("sudo mkdir -p /mnt/.snapshots/ast/snapshots")
    os.system(f"sudo cp -a ./src/distros/{distro}/astpk.py /mnt/.snapshots/ast/ast")
    os.system("sudo cp -a ./src/detect_os.sh /mnt/.snapshots/ast/detect_os.sh")
    os.system("sudo chroot /mnt ln -s /.snapshots/ast/ast /usr/bin/ast")             ####PR32 Can I moved it somewhere better?
    os.system("sudo chroot /mnt ln -s /.snapshots/ast/detect_os.sh /usr/bin/detect_os.sh")
    os.system("sudo chroot /mnt ln -s /.snapshots/ast /var/lib/ast")

#   Create user and set password
    set_password("root")
    username = get_username()
    create_user(username)
    set_password(username)

#   Systemd
    os.system("sudo chroot /mnt systemctl enable NetworkManager")

#   Initialize fstree
    os.system("echo {\\'name\\': \\'root\\', \\'children\\': [{\\'name\\': \\'0\\'}]} | sudo tee /mnt/.snapshots/ast/fstree")

#   GRUB and EFI
###    os.system(f"sudo arch-chroot /mnt sed -i s,Arch,astOS,g /etc/default/grub") ###NOT_PLANNING_TO_USE_THIS_APPROACH_AT_ALL
    os.system(f"sudo chroot /mnt grub-install {args[2]}") #REZA --recheck --no-nvram --removable
    os.system(f"sudo chroot /mnt grub-mkconfig {args[2]} -o /boot/grub/grub.cfg")
    os.system("sudo mkdir -p /mnt/boot/grub/BAK/") # Folder for backing up grub configs created by astpk
    os.system(f"sudo sed -i '0,/subvol=@{distro_suffix}/ s,subvol=@{distro_suffix},subvol=@.snapshots{distro_suffix}/rootfs/snapshot-tmp,g' /mnt/boot/grub/grub.cfg")
    # Create a mapping of "distro" <=> "BootOrder number". Ash reads from this file to switch between distros.
    if efi:
        if not os.path.exists("/mnt/boot/efi/EFI/map.txt"):
            os.system("echo DISTRO,BootOrder | sudo tee /mnt/boot/efi/EFI/map.txt")
        os.system(f"echo '{distro},' $(efibootmgr -v | grep -i {distro} | awk '"'{print $1}'"' | sed '"'s/[^0-9]*//g'"') | sudo tee -a /mnt/boot/efi/EFI/map.txt")

    os.system("sudo btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-0")
    os.system("sudo btrfs sub create /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/etc/etc-tmp")

    os.system("sudo cp --reflink=auto -r /mnt/boot/* /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/etc/* /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/boot/boot-tmp /mnt/.snapshots/boot/boot-0")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/etc/etc-tmp /mnt/.snapshots/etc/etc-0")

    os.system(f"echo '{astpart}' | sudo tee /mnt/.snapshots/ast/part")

    os.system("sudo btrfs sub snap /mnt/.snapshots/rootfs/snapshot-0 /mnt/.snapshots/rootfs/snapshot-tmp")
    os.system("sudo chroot /mnt btrfs sub set-default /.snapshots/rootfs/snapshot-tmp")

    os.system("sudo cp -r /mnt/root/. /mnt/.snapshots/root/")
    os.system("sudo cp -r /mnt/tmp/. /mnt/.snapshots/tmp/")
    os.system("sudo rm -rf /mnt/root/*")
    os.system("sudo rm -rf /mnt/tmp/*")

#   Copy boot and etc from snapshot's tmp to common
    if efi:
        os.system("sudo umount /mnt/boot/efi")
    os.system("sudo umount /mnt/boot")
    os.system(f"sudo mount {args[1]} -o subvol=@boot{distro_suffix},compress=zstd,noatime /mnt/.snapshots/boot/boot-tmp") ### IS this mnt point empty?
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-tmp/. /mnt/boot/")
    os.system("sudo umount /mnt/etc")
    os.system(f"sudo mount {args[1]} -o subvol=@etc{distro_suffix},compress=zstd,noatime /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-tmp/. /mnt/etc/")

    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-0/. /mnt/.snapshots/rootfs/snapshot-tmp/boot/")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-0/. /mnt/.snapshots/rootfs/snapshot-tmp/etc/")

#   Unmount everything
    os.system("sudo umount -R /mnt")
    os.system(f"sudo mount {args[1]} -o subvolid=0 /mnt") # subvolid=5 needed for any cases?
    os.system(f"sudo btrfs sub del /mnt/@{distro_suffix}")
    os.system("sudo umount -R /mnt")

    clear()
    print("Installation complete")
    print("You can reboot now :)")

