#!/usr/bin/python3

######33 /sbin/apk add py3
###### export PATH=/bin:$PATH


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
            print("Invalid timezone!")
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

def create_user(u, g):
    os.system(f"sudo chroot /mnt sudo /usr/sbin/adduser -h /home/{u} -G {g} -s /bin/bash {u}")
    os.system(f"echo '%{g} ALL=(ALL:ALL) ALL' | sudo tee -a /mnt/etc/sudoers")
    os.system(f"echo 'export XDG_RUNTIME_DIR=\"/run/user/1000\"' | sudo tee -a /mnt/home/{u}/.bashrc")

###def create_user(u, g):
###    os.system(f"sudo chroot /mnt sudo useradd -m -G {g} -s /bin/bash {u}")
###    os.system(f"echo '%{g} ALL=(ALL:ALL) ALL' | sudo tee -a /mnt/etc/sudoers")
###    os.system(f"echo 'export XDG_RUNTIME_DIR=\"/run/user/1000\"' | sudo tee -a /mnt/home/{u}/.bashrc")

def set_password(u, s):
    clear()
    while True:
        print(f"Setting a password for '{u}':")
        os.system(f"sudo chroot /mnt {s} passwd {u}")
        print("Was your password set properly (y/n)?")
        reply = input("> ")
        if reply.casefold() == "y":
            break
        else:
            continue

def main(args, distro):
    print("Welcome to the AshOS installer!\n\n\n\n\n")

#   Define variables
    ARCH = "x86_64"
    RELEASE = "edge"
    APK = "2.12.9-r5"
    KERNEL = "edge"
    packages = f"alpine-base linux-{KERNEL} tzdata sudo python3 py3-anytree bash \
                btrfs-progs networkmanager tmux" #linux-firmware nano doas os-prober
    #packages = "base linux linux-firmware nano python3 python-anytree bash dhcpcd \
    #            arch-install-scripts btrfs-progs networkmanager grub sudo tmux os-prober"
    choice, distro_suffix = get_multiboot(distro)
    btrdirs = [f"@{distro_suffix}", f"@.snapshots{distro_suffix}", f"@boot{distro_suffix}", f"@etc{distro_suffix}", f"@home{distro_suffix}", f"@var{distro_suffix}"]
    mntdirs = ["", ".snapshots", "boot", "etc", "home", "var"]
    tz = get_timezone()
    hostname = get_hostname()
    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False

#   Prep (format partition, etc.)
    if choice != "3":
        os.system(f"sudo mkfs.btrfs -L LINUX -f {args[1]}")
    os.system("pacman -Syy --noconfirm archlinux-keyring")

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
    for i in ("ast", "boot", "etc", "root", "rootfs", "tmp"):
        os.system(f"mkdir -p /mnt/.snapshots/{i}")
    if efi:
        os.system("sudo mkdir /mnt/boot/efi")
        os.system(f"sudo mount {args[3]} /mnt/boot/efi")

### STEP 2 BEGINS

#   Bootstrap then install anytree and necessary packages in chroot
    os.system(f"curl -L -O https://dl-cdn.alpinelinux.org/alpine/{RELEASE}/main/{ARCH}/apk-tools-static-{APK}.apk")
    os.system("tar zxf apk-tools-static-*.apk")
    excode = int(os.system(f"sudo ./sbin/apk.static --arch {ARCH} -X http://dl-cdn.alpinelinux.org/alpine/{RELEASE}/main/ \
                             -U --allow-untrusted --root /mnt --initdb add --no-cache {packages}"))
    if excode != 0:
        print("Failed to bootstrap!")
        sys.exit()
    # Mount-points needed for chrooting
    os.system("sudo mount -o x-mount.mkdir --rbind --make-rslave /dev /mnt/dev")
    os.system("sudo mount -o x-mount.mkdir --types proc /proc /mnt/proc")
    os.system("sudo mount -o x-mount.mkdir --bind --make-slave /run /mnt/run")
    os.system("sudo mount -o x-mount.mkdir --rbind --make-rslave /sys /mnt/sys")
    if efi:
        os.system("sudo mount -o x-mount.mkdir --rbind --make-rslave /sys/firmware/efi/efivars /mnt/sys/firmware/efi/efivars")
    os.system("sudo cp --dereference /etc/resolv.conf /mnt/etc/")
    os.system("sudo cp ./src/distros/alpine/repositories /mnt/etc/apk/")
    os.system("sudo cp ./src/distros/alpine/repositories /mnt/etc/apk/")

### STEP 3 BEGINS

    if efi:
        excode = int(os.system("sudo chroot /mnt /sbin/apk update && /sbin/apk add grub-efi efibootmgr"))
        if excode != 0:
            print("Failed to install grub!")
            sys.exit()
    else:
        excode = int(os.system("sudo chroot /mnt /sbin/apk update &&/sbin/apk add grub-bios"))
        if excode != 0:
            print("Failed to install grub!")
            sys.exit()

#   Update fstab
    os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" / btrfs subvol=@{distro_suffix},compress=zstd,noatime,ro 0 0' | sudo tee -a /mnt/etc/fstab")
    for mntdir in mntdirs:
        os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" /{mntdir} btrfs subvol=@{mntdir}{distro_suffix},compress=zstd,noatime 0 0' | sudo tee -a /mnt/etc/fstab")
    if efi:
        os.system(f"echo 'UUID=\"{to_uuid(args[3])}\" /boot/efi vfat umask=0077 0 2' | sudo tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/root /root none bind 0 0' | sudo tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/tmp /tmp none bind 0 0' | sudo tee -a /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@{distro_suffix}/ s,@{distro_suffix},@.snapshots{distro_suffix}/rootfs/snapshot-tmp,' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@boot{distro_suffix}/ s,@boot{distro_suffix},@.snapshots{distro_suffix}/boot/boot-tmp,' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@etc{distro_suffix}/ s,@etc{distro_suffix},@.snapshots{distro_suffix}/etc/etc-tmp,' /mnt/etc/fstab")
    os.system(f"sudo sed -i '/\@{distro_suffix}/d' /mnt/etc/fstab") # Delete @_distro entry

#   Database and config files
    os.system("sudo mkdir -p /mnt/usr/share/ast/db")
    os.system("echo '0' | sudo tee /mnt/usr/share/ast/snap")
    os.system("sudo cp -r /mnt/var/lib/apk/* /mnt/usr/share/ast/db")
    #os.system(f"sed -i s,\"#DBPath      = /var/lib/pacman/\",\"DBPath      = /usr/share/ast/db/\",g /mnt/etc/pacman.conf")
    os.system(f"sudo sed -i '/^ID/ s/{distro}/{distro}_ashos/' /mnt/etc/os-release") # Modify OS release information (optional)

#   Update hostname, hosts, locales and timezone, hosts
    os.system(f"echo {hostname} | sudo tee /mnt/etc/hostname")
    os.system(f"echo 127.0.0.1 {hostname} | sudo tee -a /mnt/etc/hosts")
    #os.system("sudo sed -i 's/^#en_US.UTF-8/en_US.UTF-8/g' /mnt/etc/locale.gen")
    #os.system("sudo chroot /mnt sudo locale-gen")
    #os.system("echo 'LANG=en_US.UTF-8' | sudo tee /mnt/etc/locale.conf")
    os.system(f"sudo ln -srf /mnt{tz} /mnt/etc/localtime")
    os.system("sudo chroot /mnt /sbin/hwclock --systohc")

#   Copy and symlink astpk and detect_os.sh
    os.system("sudo mkdir -p /mnt/.snapshots/ast/snapshots")
    os.system(f"echo '{to_uuid(args[1])}' | sudo tee /mnt/.snapshots/ast/part")
    os.system(f"sudo cp -a ./src/distros/{distro}/astpk.py /mnt/.snapshots/ast/ast")
    os.system("sudo cp -a ./src/detect_os.sh /mnt/.snapshots/ast/detect_os.sh")
    os.system("sudo ln -srf /mnt/.snapshots/ast/ast /mnt/usr/bin/ast")
    os.system("sudo ln -srf /mnt/.snapshots/ast/detect_os.sh /mnt/usr/bin/detect_os.sh")
    os.system("sudo ln -srf /mnt/.snapshots/ast /mnt/var/lib/ast")
    os.system("echo {\\'name\\': \\'root\\', \\'children\\': [{\\'name\\': \\'0\\'}]} | sudo tee /mnt/.snapshots/ast/fstree") # Initialize fstree

### STEP 4 BEGINS

#   Create user and set password
    set_password("root", "") # will fix for "doas"
    username = get_username()
    create_user(username, "wheel")
    set_password(username, "") # will fix for "doas"

#   Network
    os.system("/sbin/rc-service networkmanager start")
    os.system(f"adduser {username} plugdev")

### STEP 5 BEGINS

#   GRUB and EFI
    os.system(f"sudo chroot /mnt sudo /usr/sbin/grub-install {args[2]}")
    os.system(f"sudo chroot /mnt sudo grub-mkconfig {args[2]} -o /boot/grub/grub.cfg")
    os.system("sudo mkdir -p /mnt/boot/grub/BAK") # Folder for backing up grub configs created by astpk
    os.system(f"sudo sed -i '0,/subvol=@{distro_suffix}/ s,subvol=@{distro_suffix},subvol=@.snapshots{distro_suffix}/rootfs/snapshot-tmp,g' /mnt/boot/grub/grub.cfg")
    # Create a mapping of "distro" <=> "BootOrder number". Ash reads from this file to switch between distros.
    if efi:
        if not os.path.exists("/mnt/boot/efi/EFI/map.txt"):
            os.system("echo DISTRO,BootOrder | sudo tee /mnt/boot/efi/EFI/map.txt")
        os.system(f"echo '{distro},' $(efibootmgr -v | grep -i {distro} | awk '"'{print $1}'"' | sed '"'s/[^0-9]*//g'"') | sudo tee -a /mnt/boot/efi/EFI/map.txt")

#   BTRFS snapshots
    os.system("sudo btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-0")
    os.system("sudo btrfs sub create /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/boot/* /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/etc/* /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/boot/boot-tmp /mnt/.snapshots/boot/boot-0")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/etc/etc-tmp /mnt/.snapshots/etc/etc-0")
    os.system("sudo btrfs sub snap /mnt/.snapshots/rootfs/snapshot-0 /mnt/.snapshots/rootfs/snapshot-tmp")
    os.system("sudo chroot /mnt sudo /sbin/btrfs sub set-default /.snapshots/rootfs/snapshot-tmp")
    os.system("sudo cp -r /mnt/root/. /mnt/.snapshots/root/")
    os.system("sudo cp -r /mnt/tmp/. /mnt/.snapshots/tmp/")
    os.system("sudo rm -rf /mnt/root/*")
    os.system("sudo rm -rf /mnt/tmp/*")

### STEP 6 BEGINS

#   Copy boot and etc from snapshot's tmp to common
    if efi:
        os.system("sudo umount /mnt/boot/efi")
    os.system("sudo umount /mnt/boot")
    os.system(f"sudo mount {args[1]} -o subvol=@boot{distro_suffix},compress=zstd,noatime /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-tmp/. /mnt/boot/")
    os.system("sudo umount /mnt/etc")
    os.system(f"sudo mount {args[1]} -o subvol=@etc{distro_suffix},compress=zstd,noatime /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-tmp/. /mnt/etc/")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-0/. /mnt/.snapshots/rootfs/snapshot-tmp/boot/")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-0/. /mnt/.snapshots/rootfs/snapshot-tmp/etc/")

### STEP 7 BEGINS

#   Unmount everything and finish
    os.system("sudo umount -R /mnt")
    os.system(f"sudo mount {args[1]} -o subvolid=0 /mnt")
    os.system(f"sudo btrfs sub del /mnt/@{distro_suffix}")
    os.system("sudo umount -R /mnt")
    clear()
    print("Installation complete")
    print("You can reboot now :)")

