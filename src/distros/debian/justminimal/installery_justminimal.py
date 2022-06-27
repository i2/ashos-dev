#!/usr/bin/python3

import os
import subprocess

def clear():
    os.system("#clear")

def to_uuid(part):
    return subprocess.check_output(f"sudo blkid -s UUID -o value {part}", shell=True).decode('utf-8').strip()

def get_multiboot(dist):
    clear()
    while True:
        print("Please choose one of the following:\n1. Single OS installation\n2. Initiate a multi-boot ashos setup\n3. Adding to an already installed ashos")
        i = input("> ")
        if i == "1":
            return False,""
            break
        elif i == "2":
            return True,f"_{dist}"
            break
        elif i == "3":
            return True,f"_{dist}"
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
    os.system(f"sudo chroot /mnt useradd -m -G sudo -s /bin/bash {u}")
    os.system("echo '%sudo ALL=(ALL:ALL) ALL' | sudo tee -a /mnt/etc/sudoers")
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
    print("Welcome to the astOS installer!\n\n\n\n\n")
    multiboot, DISTRO = get_multiboot(distro)
    
#   Partition and format
    #os.system("find $HOME -maxdepth 1 -type f -iname '.*shrc' -exec sh -c 'echo export LC_ALL=C LANGUAGE=C LANG=C >> $1' -- {} \;") # Perl complains if not set
    os.system("sudo apt-get remove -y --purge man-db") # make installs faster (because of trigger man-db bug)
    os.system("sudo apt-get update -y")
    os.system("sudo apt-get install -y parted btrfs-progs dosfstools ntp")
    os.system("sudo parted --align minimal --script /dev/sda mklabel gpt unit MiB mkpart ESP fat32 0% 256 set 1 boot on mkpart primary ext4 256 100%")
    if not multiboot:
        os.system(f"sudo /usr/sbin/mkfs.vfat -F32 -n EFI {args[3]}")
        os.system(f"sudo /usr/sbin/mkfs.btrfs -L LINUX -f {args[1]}")
    #else:
    #    DISTRO = f"_{distro}" # Ro distinguish between snapshots of different Linux

#   Define variables
    #DISTRO = "debian"
    RELEASE = "bullseye"
    ARCH = "amd64"
    #btrdirs = ["@","@.snapshots","@home","@var","@etc","@boot"]
    btrdirs = [f"@{DISTRO}",f"@.snapshots{DISTRO}",f"@home{DISTRO}",f"@var{DISTRO}",f"@etc{DISTRO}",f"@boot{DISTRO}"]
    mntdirs = ["",".snapshots","home","var","etc","boot"]
    #mntdirs = [f'"",".snapshots{DISTRO}","home{DISTRO}","var{DISTRO}","etc{DISTRO}","boot{DISTRO}"']
    mntdirs_n = mntdirs[1:]
    astpart = to_uuid(args[1])
    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False

    tz = get_timezone()
    hostname = get_hostname()

#   Mount and create necessary sub-volumes and directories
    os.system(f"sudo mount {args[1]} /mnt")
    for btrdir in btrdirs:
        os.system(f"sudo btrfs sub create /mnt/{btrdir}")
    os.system("sudo umount /mnt")
    os.system(f"sudo mount {args[1]} -o subvol=@{DISTRO},compress=zstd,noatime /mnt")
    for mntdir in mntdirs_n:
        os.system(f"sudo mkdir /mnt/{mntdir}")
        os.system(f"sudo mount {args[1]} -o subvol={btrdirs[mntdirs.index(mntdir)]},compress=zstd,noatime /mnt/{mntdir}")
    for i in ("tmp", "root"):
        os.system(f"mkdir -p /mnt/{i}")
    for i in ("ast", "boot", "etc", "root", "rootfs", "tmp", "var"):
        os.system(f"mkdir -p /mnt/.snapshots/{i}")
    if efi:
        os.system("sudo mkdir /mnt/boot/efi")
        os.system(f"sudo mount {args[3]} /mnt/boot/efi")

#   Modify shell profile for debug purposes in live iso (optional temporary)
    #os.system('echo "alias paste='"'"'curl -F "'"'"'"sprunge=<-"'"'"'" http://sprunge.us'"'"' " | tee -a $HOME/.*shrc')
    #os.system("shopt -s nullglob && echo 'export LC_ALL=C' | sudo tee -a /mnt/root/.*shrc")
    #os.system("find /mnt/root/ -maxdepth 1 -type f -iname '.*shrc' -exec sh -c 'echo export LC_ALL=C | sudo tee -a $1' -- {} \;")
    #os.system("echo -e 'setw -g mode-keys vi\nset -g history-limit 999999' >> $HOME/.tmux.conf")

#   Bootstrap (minimal)
    os.system("sudo apt-get install -y debootstrap")
    excl = subprocess.check_output("dpkg-query -f '${binary:Package} ${Priority}\n' -W | grep -v 'required\|important' | awk '{print $1}'", shell=True).decode('utf-8').strip().replace("\n",",")
    os.system(f"sudo debootstrap --arch {ARCH} --exclude={excl} {RELEASE} /mnt http://ftp.debian.org/debian")
    for i in ("/dev", "/dev/pts", "/proc", "/run", "/sys", "/sys/firmware/efi/efivars"):
        os.system(f"sudo mount -B {i} /mnt{i}") # Mount-points needed for chrooting
    os.system(f"sudo chroot /mnt apt-get install -y linux-image-{ARCH}")

#   Install anytree and necessary packages in chroot
    os.system("sudo systemctl enable --now ntp && sleep 30s && ntpq -p") # Sync time in the live iso
    os.system(f"echo 'deb [trusted=yes] http://www.deb-multimedia.org {RELEASE} main' | sudo tee -a /mnt/etc/apt/sources.list.d/multimedia.list >/dev/null")
    os.system("sudo chroot /mnt apt-get update -y -oAcquire::AllowInsecureRepositories=true")
    os.system("sudo chroot /mnt apt-get install -y deb-multimedia-keyring --allow-unauthenticated")
    os.system("sudo chroot /mnt apt-get install -y python3-anytree network-manager btrfs-progs dhcpcd5 locales sudo")
    if efi:
        os.system("sudo chroot /mnt apt-get install -y grub-efi")
    else:
        os.system("sudo chroot /mnt apt-get install -y grub-pc")

#   Update fstab
    os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" / btrfs subvol=@{DISTRO},compress=zstd,noatime,ro 0 0' | sudo tee /mnt/etc/fstab")
    for mntdir in mntdirs_n:
        os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" /{mntdir} btrfs subvol=@{mntdir}{DISTRO},compress=zstd,noatime 0 0' | sudo tee -a /mnt/etc/fstab")
    if efi:
        os.system(f"echo 'UUID=\"{to_uuid(args[3])}\" /boot/efi vfat umask=0077 0 2' | sudo tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/root /root none bind 0 0' | sudo tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/tmp /tmp none bind 0 0' | sudo tee -a /mnt/etc/fstab")

    os.system("sudo mkdir -p /mnt/usr/share/ast/db")
    os.system("echo '0' | sudo tee /mnt/usr/share/ast/snap")
    os.system("sudo cp -r /mnt/var/lib/dpkg/* /mnt/usr/share/ast/db")
    #os.system(f"echo 'RootDir=/usr/share/ast/db/' | sudo tee -a /mnt/etc/apt/apt.conf")

#   Modify OS release information (optional)
    os.system(f"sed -i '/^NAME/ s/Arch Linux/Arch Linux (ashos)/' /mnt/etc/os-release")
    os.system(f"sed -i '/PRETTY_NAME/ s/Arch Linux/Arch Linux (ashos)/' /mnt/etc/os-release")
    os.system(f"sed -i '/^ID/ s/arch/arch_ashos/' /mnt/etc/os-release")

#   Update hostname, locales and timezone
    os.system(f"echo {hostname} | sudo tee /mnt/etc/hostname")
    os.system("sudo sed -i 's/^#en_US.UTF-8/en_US.UTF-8/g' /etc/locale.gen")
    os.system("sudo chroot /mnt locale-gen")
    os.system("echo 'LANG=en_US.UTF-8' | sudo tee /mnt/etc/locale.conf")
    os.system(f"sudo chroot /mnt ln -sf {tz} /etc/localtime")
    os.system("sudo chroot /mnt hwclock --systohc")

    os.system(f"sudo sed -i '0,/@{DISTRO}/ s,@,@{DISTRO}.snapshots/rootfs/snapshot-tmp,' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@boot{DISTRO}/ s,@boot{DISTRO},@.snapshots{DISTRO}/boot/boot-tmp,' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@etc{DISTRO}/ s,@etc{DISTRO},@.snapshots{DISTRO}/etc/etc-tmp,' /mnt/etc/fstab")

    os.system("sudo mkdir -p /mnt/.snapshots/ast/snapshots")
    os.system("sudo chroot /mnt ln -s /.snapshots/ast /var/lib/ast")

#   Create user and set password
    set_password("root")
    username = get_username()
    create_user(username)
    set_password(username)

    os.system("sudo chroot /mnt systemctl enable NetworkManager")

#   Initialize fstree
    os.system("echo {\\'name\\': \\'root\\', \\'children\\': [{\\'name\\': \\'0\\'}]} | sudo tee /mnt/.snapshots/ast/fstree")

#   GRUB
    os.system(f"sudo chroot /mnt sed -i s,Arch,astOS,g /etc/default/grub")
    os.system(f"sudo chroot /mnt grub-install {args[2]}")
    os.system(f"sudo chroot /mnt grub-mkconfig {args[2]} -o /boot/grub/grub.cfg")
    os.system(f"sudo sed -i '0,/subvol=@{DISTRO}/s,subvol=@{DISTRO},subvol=@.snapshots{DISTRO}/rootfs/snapshot-tmp,g' /mnt/boot/grub/grub.cfg")

#   Copy astpk
    os.system(f"sudo cp ./src/distros/{distro}/astpk.py /mnt/usr/bin/ast")
    os.system("sudo chroot /mnt chmod +x /usr/sbin/ast")

    os.system("sudo btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-0")
    os.system("sudo btrfs sub create /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/var/var-tmp")

#### SHARED
    for i in ("dpkg", "systemd"):
        os.system(f"sudo mkdir -p /mnt/.snapshots/var/var-tmp/lib/{i}")
    os.system("sudo cp --reflink=auto -r /mnt/var/lib/dpkg/* /mnt/.snapshots/var/var-tmp/lib/dpkg/")
    os.system("sudo cp --reflink=auto -r /mnt/var/lib/systemd/* /mnt/.snapshots/var/var-tmp/lib/systemd/")
    os.system("sudo cp --reflink=auto -r /mnt/boot/* /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/etc/* /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/boot/boot-tmp /mnt/.snapshots/boot/boot-0")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/etc/etc-tmp /mnt/.snapshots/etc/etc-0")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/var/var-tmp /mnt/.snapshots/var/var-0")
####

    os.system(f"echo '{astpart}' | sudo tee /mnt/.snapshots/ast/part")

#### SHARED
    os.system("sudo btrfs sub snap /mnt/.snapshots/rootfs/snapshot-0 /mnt/.snapshots/rootfs/snapshot-tmp")
    print("chroot /mnt btrfs sub set-default /.snapshots/rootfs/snapshot-tmp")
    os.system("sudo chroot /mnt btrfs sub set-default /.snapshots/rootfs/snapshot-tmp")
####

    os.system("sudo cp -r /mnt/root/. /mnt/.snapshots/root/")
    os.system("sudo cp -r /mnt/tmp/. /mnt/.snapshots/tmp/")
    os.system("sudo rm -rf /mnt/root/*")
    os.system("sudo rm -rf /mnt/tmp/*")

#   Clean unnecessary packages (optional)
    os.system("sudo apt-get autoremove -y")
    os.system("sudo apt-get autoclean -y")

#   Copy boot and etc from snapshot's tmp to common
    if efi:
        os.system("sudo umount /mnt/boot/efi")
    os.system("sudo umount /mnt/boot")
    os.system(f"sudo mount {args[1]} -o subvol=@boot{DISTRO},compress=zstd,noatime /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-tmp/* /mnt/boot")
    os.system("sudo umount /mnt/etc")
    os.system(f"sudo mount {args[1]} -o subvol=@etc{DISTRO},compress=zstd,noatime /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-tmp/* /mnt/etc")

    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-0/* /mnt/.snapshots/rootfs/snapshot-tmp/boot")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-0/* /mnt/.snapshots/rootfs/snapshot-tmp/etc")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/var/var-0/* /mnt/.snapshots/rootfs/snapshot-tmp/var")

#   Unmount everything
    os.system("sudo umount -R /mnt")
    print("mount {args[1]} -o subvolid=5 /mnt")
    os.system(f"sudo mount {args[1]} -o subvolid=5 /mnt")
    print("btrfs sub del /mnt/@{DISTRO}")
    os.system(f"sudo btrfs sub del /mnt/@{DISTRO}")
    print("umount -R /mnt")
    os.system("sudo umount -R /mnt")
    clear()
    print("Installation complete")
    print("You can reboot now :)")

# This is based off of files:
# last-to-become-justminimal-but-still-has-guinstall-function-keep-for-reference-ashize-oses-later.py which is just a symlink to
# installeryolo-justminimal-based-on-before-drousy_THIS_IS_WHERE_ID_FINISH_MY_WORK_FROM_OTHER_FILES.py

# move this functionality from installer.py aka main.py to astpk.py:
#    for i in packages:
#        os.system(f"sudo chroot /mnt apt-get install -y {i}")
