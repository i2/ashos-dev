#!/usr/bin/python3

import os
import subprocess

def clear():
    os.system("#clear")

def to_uuid(part):
    uuid = str(subprocess.check_output(f"sudo blkid -s UUID -o value {part}", shell=True))
    return uuid.replace("b'","").replace('"',"").replace("\\n'","")

def set_user():
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
    os.system(f"sudo chroot /mnt useradd {username}")
    return username

def set_password(username):
    clear()
    print("Please enter a password:")
    while True:
        os.system(f"sudo chroot /mnt passwd {username}")
        print("Was your password set properly (y/n)?")
        reply = input("> ")
        if reply.casefold() == "y":
            break
        else:
            clear()
            continue

def set_timezone():
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

def guinstall(username, packages, DesktopInstall):
    os.system(f"echo {DesktopInstall} | sudo tee /mnt/usr/share/ast/snap")
    for i in packages:
        os.system(f"sudo chroot /mnt apt-get install -y {i}")
    username = set_user()
    set_password(username)
    os.system(f"sudo chroot /mnt usermod -aG audio,input,video,wheel {username}")
    os.system("sudo chroot /mnt passwd -l root")
    os.system("sudo chmod +w /mnt/etc/sudoers")
    os.system("echo '%wheel ALL=(ALL:ALL) ALL' | sudo tee -a /mnt/etc/sudoers")
    os.system("sudo chmod -w /mnt/etc/sudoers")
    os.system(f"sudo chroot /mnt mkdir /home/{username}")
    os.system(f"echo 'export XDG_RUNTIME_DIR=\"/run/user/1000\"' | sudo tee -a /home/{username}/.bashrc")
    os.system(f"sudo chroot /mnt chown -R {username} /home/{username}")
    os.system("sudo cp -r /mnt/var/lib/dpkg/* /mnt/usr/share/ast/db")
    os.system("sudo btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-1")
    os.system("sudo btrfs sub del /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub del /mnt/.snapshots/var/var-tmp")
    os.system("sudo btrfs sub del /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/var/var-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/boot/boot-tmp")
    for i in ("dpkg", "systemd"):
        os.system(f"sudo mkdir -p /mnt/.snapshots/var/var-tmp/lib/{i}")
    os.system("sudo cp --reflink=auto -r /mnt/var/lib/dpkge/* /mnt/.snapshots/var/var-tmp/lib/dpkg/")
    os.system("sudo cp --reflink=auto -r /mnt/var/lib/systemd/* /mnt/.snapshots/var/var-tmp/lib/systemd/")
    os.system("sudo cp --reflink=auto -r /mnt/boot/* /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/etc/* /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/var/var-tmp /mnt/.snapshots/var/var-1")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/boot/boot-tmp /mnt/.snapshots/boot/boot-1")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/etc/etc-tmp /mnt/.snapshots/etc/etc-1")
    os.system("sudo btrfs sub snap /mnt/.snapshots/rootfs/snapshot-1 /mnt/.snapshots/rootfs/snapshot-tmp")
    os.system("sudo chroot /mnt btrfs sub set-default /.snapshots/rootfs/snapshot-tmp")

def main(args):

    # Define variables
    btrdirs = ["@","@.snapshots","@home","@var","@etc","@boot"]
    mntdirs = ["",".snapshots","home","var","etc","boot"]
    mntdirs_n = mntdirs[1:]
    #astpart = to_uuid(args[1])  # if partitioning is not done yet, this will error
    RELEASE = "bullseye"
    ARCH = "amd64"
    DesktopInstall = None

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
    tz = set_timezone()

    clear()
    print("Enter hostname:")
    hostname = input("> ")

    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False

### STEP 1

    # Partitioning
    os.system("export LC_ALL=C LANGUAGE=C LANG=C") # So that perl does not complain (alternatively echo 'export LC_ALL=C' | tee ~/.bashrc)
    os.system("sudo apt-get remove -y --purge man-db") # make installs faster (because of trigger man-db bug)
    os.system("sudo apt-get update")
    os.system("sudo apt-get autoremove -y")
    os.system("sudo apt-get install -y parted btrfs-progs dosfstools")
    os.system("sudo parted --align minimal --script /dev/sda mklabel gpt unit MiB mkpart ESP fat32 0% 256 set 1 boot on mkpart primary ext4 256 100%")
    os.system("sudo /usr/sbin/mkfs.vfat -F32 -n EFI /dev/sda1")
    os.system(f"sudo /usr/sbin/mkfs.btrfs -L LINUX -f {args[1]}")

    # Sync time in the live iso (optional)
    #os.system("sudo apt-get install -y ntp")
    #os.system("echo 'Installing ntp. It will pause 30s. Sometimes it's needed to restart ntp service to have time sync again'")
    #os.system("sudo systemctl enable --now ntp && sleep 30s && ntpq -p")
    #os.system("sudo apt-get update")

    # Mount and create necessary sub-volumes and directories
    os.system(f"sudo mount {args[1]} /mnt")

    for btrdir in btrdirs:
        os.system(f"sudo btrfs sub create /mnt/{btrdir}")

    os.system("sudo umount /mnt")
    os.system(f"sudo mount {args[1]} -o subvol=@,compress=zstd,noatime /mnt")

    for mntdir in mntdirs:
        os.system(f"sudo mkdir /mnt/{mntdir}")
        os.system(f"sudo mount {args[1]} -o subvol={btrdirs[mntdirs.index(mntdir)]},compress=zstd,noatime /mnt/{mntdir}")

    for i in ("tmp", "root"):
        os.system(f"mkdir -p /mnt/{i}")
    for i in ("ast", "boot", "etc", "root", "rootfs", "tmp", "var"):
        os.system(f"mkdir -p /mnt/.snapshots/{i}")

    if efi:
        os.system("sudo mkdir /mnt/boot/efi")
        os.system(f"sudo mount {args[3]} /mnt/boot/efi")

    # Modify shell profile for debug purposes in live iso (optional temporary)
    os.system('echo "alias paste='"'"'curl -F "'"'"'"sprunge=<-"'"'"'" http://sprunge.us'"'"' " | tee -a $HOME/.*zhrc')
    os.system("echo 'export LC_ALL=C' | tee -a $HOME/.*shrc")
    os.system("echo 'export LC_ALL=C' | sudo tee -a /mnt/root/.*shrc")
    os.system("echo 'setw -g mode-keys vi' | tee -a $HOME/.tmux.conf")

### STEP 2

    # Bootstrap
    os.system("sudo apt-get install -y debootstrap")
    os.system(f"sudo debootstrap --arch {ARCH} {RELEASE} /mnt http://ftp.debian.org/debian")

    # Mount-points needed for chrooting
    for i in ("/dev", "/dev/pts", "/proc", "/run", "/sys", "/sys/firmware/efi/efivars"):
        os.system(f"sudo mount -B {i} /mnt{i}")

    # Perl complains if LC_ALL is not set
    os.system(f'sudo chroot /mnt /bin/sh -c "LC_ALL=C apt-get install -y linux-image-{ARCH}"')

    # Install anytree and necessary packages in chroot
    os.system(f"echo 'deb [trusted=yes] http://www.deb-multimedia.org {RELEASE} main' | sudo tee -a /mnt/etc/apt/sources.list.d/multimedia.list >/dev/null")
    os.system('sudo chroot /mnt /bin/sh -c "LC_ALL=C apt-get install -y deb-multimedia-keyring --allow-unauthenticated"')
    os.system('sudo chroot /mnt /bin/sh -c "LC_ALL=C apt-get update -oAcquire::AllowInsecureRepositories=true"')
    os.system("sudo chmod -R 1777 /mnt/tmp") #REZA this might need to be commented out if no error
    os.system('sudo chroot /mnt /bin/sh -c "LC_ALL=C apt-get install -y python3-anytree network-manager btrfs-progs dhcpcd5 locales sudo"')

    if efi:
        os.system('sudo chroot /mnt /bin/sh -c "LC_ALL=C apt-get install -y grub-efi"')
    else:
        os.system('sudo chroot /mnt /bin/sh -c "LC_ALL=C apt-get install -y grub-pc"')

### STEP 3

    os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" / btrfs subvol=@,compress=zstd,noatime,ro 0 0' | sudo tee /mnt/etc/fstab")

    for mntdir in mntdirs_n:
        os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" /{mntdir} btrfs subvol=@{mntdir},compress=zstd,noatime 0 0' | sudo tee -a /mnt/etc/fstab")

    if efi:
        os.system(f"echo 'UUID=\"{to_uuid(args[3])}\" /boot/efi vfat umask=0077 0 2' | sudo tee -a /mnt/etc/fstab")

    os.system("echo '/.snapshots/ast/root /root none bind 0 0' | sudo tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/tmp /tmp none bind 0 0' | sudo tee -a /mnt/etc/fstab")
    
    astpart = to_uuid(args[1]) ###THIS will be removed when partitioning happens outside this installer

    os.system("sudo mkdir -p /mnt/usr/share/ast/db")
    os.system("echo '0' | sudo tee /mnt/usr/share/ast/snap")

    os.system(f"echo 'NAME=\"astOS\"' | sudo tee /mnt/etc/os-release")
    os.system(f"echo 'PRETTY_NAME=\"astOS\"' | sudo tee -a /mnt/etc/os-release")
    os.system(f"echo 'ID=astos' | sudo tee -a /mnt/etc/os-release")
    os.system(f"echo 'BUILD_ID=rolling' | sudo tee -a /mnt/etc/os-release")
    os.system(f"echo 'ANSI_COLOR=\"38;2;23;147;209\"' | sudo tee -a /mnt/etc/os-release")
    os.system(f"echo 'HOME_URL=\"https://github.com/CuBeRJAN/astOS\"' | sudo tee -a /mnt/etc/os-release")
    os.system(f"echo 'LOGO=astos-logo' | sudo tee -a /mnt/etc/os-release")
    os.system("sudo cp -r /mnt/var/lib/dpkg/* /mnt/usr/share/ast/db")
    #os.system(f"echo 'RootDir=/usr/share/ast/db/' | sudo tee -a /mnt/etc/apt/apt.conf")
    os.system(f"echo 'DISTRIB_ID=\"astOS\"' | sudo tee /mnt/etc/lsb-release")
    os.system(f"echo 'DISTRIB_RELEASE=\"rolling\"' | sudo tee -a /mnt/etc/lsb-release")
    os.system(f"echo 'DISTRIB_DESCRIPTION=astOS' | sudo tee -a /mnt/etc/lsb-release")

    os.system(f"sudo chroot /mnt ln -sf {tz} /etc/localtime")

###    #REZA: STEP 4 BEGINS HERE
    os.system("sudo sed -i 's/^#en_US.UTF-8/en_US.UTF-8/g' /etc/locale.gen")
    os.system("sudo chroot /mnt locale-gen")
    os.system("sudo chroot /mnt hwclock --systohc")
    os.system("echo 'LANG=en_US.UTF-8' | sudo tee /mnt/etc/locale.conf")
    os.system(f"echo {hostname} | sudo tee /mnt/etc/hostname")

    os.system("sudo sed -i '0,/@/{s,@,@.snapshots/rootfs/snapshot-tmp,}' /mnt/etc/fstab")
    os.system("sudo sed -i '0,/@etc/{s,@etc,@.snapshots/etc/etc-tmp,}' /mnt/etc/fstab")
    os.system("sudo sed -i '0,/@boot/{s,@boot,@.snapshots/boot/boot-tmp,}' /mnt/etc/fstab")
    os.system("sudo mkdir -p /mnt/.snapshots/ast/snapshots")

    os.system("sudo chroot /mnt ln -s /.snapshots/ast /var/lib/ast")

    set_password("root")

    os.system("sudo chroot /mnt systemctl enable NetworkManager")

### STEP 5

    os.system("echo {\\'name\\': \\'root\\', \\'children\\': [{\\'name\\': \\'0\\'}]} | sudo tee /mnt/.snapshots/ast/fstree")

    if DesktopInstall:
        os.system("echo {\\'name\\': \\'root\\', \\'children\\': [{\\'name\\': \\'0\\'},{\\'name\\': \\'1\\'}]} | sudo tee /mnt/.snapshots/ast/fstree")
        os.system(f"echo '{astpart}' | sudo tee /mnt/.snapshots/ast/part")

    os.system(f"sudo chroot /mnt sed -i s,Arch,astOS,g /etc/default/grub")

    os.system(f"sudo chroot /mnt grub-install {args[2]}")
    os.system(f"sudo chroot /mnt grub-mkconfig {args[2]} -o /boot/grub/grub.cfg")
    os.system("sudo sed -i '0,/subvol=@/{s,subvol=@,subvol=@.snapshots/rootfs/snapshot-tmp,g}' /mnt/boot/grub/grub.cfg")
    os.system("sudo cp ./src/distros/debian/astpk.py /mnt/usr/local/sbin/ast")
    os.system("sudo chroot /mnt chmod +x /usr/local/sbin/ast")
    os.system("sudo btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-0")
    os.system("sudo btrfs sub create /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/var/var-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/boot/boot-tmp")
    for i in ("dpkg", "systemd"):
        os.system(f"sudo mkdir -p /mnt/.snapshots/var/var-tmp/lib/{i}")   # i didn't have sudo here before, so probbly wasn't creating these folders!
    os.system("sudo cp --reflink=auto -r /mnt/var/lib/dpkg/* /mnt/.snapshots/var/var-tmp/lib/dpkg/")
    os.system("sudo cp --reflink=auto -r /mnt/var/lib/systemd/* /mnt/.snapshots/var/var-tmp/lib/systemd/")
    os.system("sudo cp --reflink=auto -r /mnt/boot/* /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/etc/* /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/var/var-tmp /mnt/.snapshots/var/var-0")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/boot/boot-tmp /mnt/.snapshots/boot/boot-0")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/etc/etc-tmp /mnt/.snapshots/etc/etc-0")
    os.system(f"echo '{astpart}' | sudo tee /mnt/.snapshots/ast/part")

    if DesktopInstall == 1:
        packages = ["gnome", "gnome-extra", "gnome-themes-extra", "gdm", "pipewire", "pipewire-pulse", "sudo"]
        guinstall(username, packages)
        os.system("sudo chroot /mnt systemctl enable gdm")
    elif DesktopInstall == 2:
        packages = ["plasma", "xorg", "kde-applications", "sddm", "pipewire", "pipewire-pulse", "sudo"]
        guinstall(username, packages)
        os.system("sudo chroot /mnt systemctl enable sddm")
        os.system("echo '[Theme]' | sudo tee /mnt/etc/sddm.conf")
        os.system("echo 'Current=breeze' | sudo tee -a /mnt/etc/sddm.conf")
    else:
        os.system("sudo btrfs sub snap /mnt/.snapshots/rootfs/snapshot-0 /mnt/.snapshots/rootfs/snapshot-tmp")
        os.system("sudo chroot /mnt btrfs sub set-default /.snapshots/rootfs/snapshot-tmp")

### STEP 6 (is in fact 3 line above but for aesthetics I put it here. Will be removed anyways!

    os.system("sudo cp -r /mnt/root/. /mnt/.snapshots/root/")
    os.system("sudo cp -r /mnt/tmp/. /mnt/.snapshots/tmp/")
    os.system("sudo rm -rf /mnt/root/*")
    os.system("sudo rm -rf /mnt/tmp/*")
#    os.system("umount /mnt/var")

    if efi:
        os.system("sudo umount /mnt/boot/efi")

    os.system("sudo umount /mnt/boot")
#    os.system("mkdir /mnt/.snapshots/var/var-tmp")
#    os.system("mkdir /mnt/.snapshots/boot/boot-tmp")
#    os.system(f"mount {args[1]} -o subvol=@var,compress=zstd,noatime /mnt/.snapshots/var/var-tmp")
    os.system(f"sudo mount {args[1]} -o subvol=@boot,compress=zstd,noatime /mnt/.snapshots/boot/boot-tmp")
#    os.system("cp --reflink=auto -r /mnt/.snapshots/var/var-tmp/* /mnt/var")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-tmp/* /mnt/boot") #why umounted /mnt/boot and then do this?
    os.system("sudo umount /mnt/etc")
#    os.system("mkdir /mnt/.snapshots/etc/etc-tmp")
    os.system(f"sudo mount {args[1]} -o subvol=@etc,compress=zstd,noatime /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-tmp/* /mnt/etc")

    if DesktopInstall:
        os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-1/* /mnt/.snapshots/rootfs/snapshot-tmp/etc")
        os.system("sudo cp --reflink=auto -r /mnt/.snapshots/var/var-1/* /mnt/.snapshots/rootfs/snapshot-tmp/var")
        os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-1/* /mnt/.snapshots/rootfs/snapshot-tmp/boot")
    else:
        os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-0/* /mnt/.snapshots/rootfs/snapshot-tmp/etc")
        os.system("sudo cp --reflink=auto -r /mnt/.snapshots/var/var-0/* /mnt/.snapshots/rootfs/snapshot-tmp/var")
        os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-0/* /mnt/.snapshots/rootfs/snapshot-tmp/boot")

###  STEP 7

#    os.system("sudo umount -R /mnt")   #gives error /mnt target busy --- maybe I should use: sudo umount -R /mnt/*
#    os.system(f"sudo mount {args[1]} /mnt")
###    os.system("sudo btrfs sub del /mnt/@") # it gives an error could not statfs: No such file or directory (could not statfs, no such file or directory)
#    os.system("sudo umount -R /mnt")
#    clear()
#    print("Installation complete")
#    print("You can reboot now :)")

