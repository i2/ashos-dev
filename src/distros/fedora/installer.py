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
        print("Please choose one of the following:\n1. Single OS installation\n2. Initiate a multi-boot ashos setup\n3. Adding to an already installed ashos")
        print("Please be aware choosing option 1 and 2 will wipe root partition")
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
        print("Enter username (all lowercase, max 8 letters)")
        u = input("> ")
        if u:
            print("Happy with your username? (y/n)")
            reply = input("> ")
            if reply.casefold() == "y":
                break
            else:
                continue
    return u

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
    ARCH = "x86_64"
    RELEASE = "rawhide"
    packages = "dnf passwd which grub2-efi-x64-modules shim-x64 btrfs-progs python python-anytree sudo tmux neovim NetworkManager \
                dhcpcd efibootmgr systemd ncurses bash-completion kernel glibc-locale-source glibc-langpack-en" # bash os-prober
    choice, distro_suffix = get_multiboot(distro)
    btrdirs = [f"@{distro_suffix}", f"@.snapshots{distro_suffix}", f"@boot{distro_suffix}", f"@etc{distro_suffix}", f"@home{distro_suffix}", f"@var{distro_suffix}"]
    mntdirs = ["", ".snapshots", "boot", "etc", "home", "var"]
    tz = get_timezone()
#    hostname = get_hostname()
    hostname = subprocess.check_output(f"git rev-parse --short HEAD", shell=True).decode('utf-8').strip() # Just for debugging
    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False

#   Prep (format partition, etc.)
    if choice != "3":
        os.system(f"sudo mkfs.btrfs -L LINUX -f {args[1]}")
    os.system("pacman -Syy --noconfirm archlinux-keyring dnf")

#   Mount and create necessary sub-volumes and directories
    if choice != "3":
        os.system(f"sudo mount -t btrfs {args[1]} /mnt")
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
        os.system("sudo mkdir -p /mnt/boot/efi")
        os.system(f"sudo mount {args[3]} /mnt/boot/efi")

#   Bootstrap then install anytree and necessary packages in chroot
#################
    input("bp0 > any systemd rpmdb services? I don't think so!") # NOPE!
    # Mount-points needed for chrooting
    os.system("sudo mount -o x-mount.mkdir --rbind --make-rslave /dev /mnt/dev")
    os.system("sudo mount -o x-mount.mkdir --types proc /proc /mnt/proc")
    os.system("sudo mount -o x-mount.mkdir --bind --make-slave /run /mnt/run")
    os.system("sudo mount -o x-mount.mkdir --rbind --make-rslave /sys /mnt/sys")
    if efi:
        os.system("sudo mount -o x-mount.mkdir --rbind --make-rslave /sys/firmware/efi/efivars /mnt/sys/firmware/efi/efivars")
    os.system("sudo cp --dereference /etc/resolv.conf /mnt/etc/") ### Not needed for Fedora and can be removed. as it says they are same file. Somewhere before this step, it already does that for us.
    excode = int(os.system(f"sudo dnf -c ./src/distros/fedora/base.repo --installroot=/mnt install -y {packages} --releasever={RELEASE} --forcearch={ARCH}")) ### TEST IF IT WORKS HERE!
    if excode != 0:
        print("Failed to febootstrap!")
        sys.exit()
#################
    input("bp1 > any systemd rpmdb services? maybe!") #YES there is service in /mnt/usr/lib/systemd/system/rpmXYZ not sure if it's active yet (it exists under /mnt/etc/systemd/system/basic-tafrget/rpm-migrateXYZ yet) /mnt/usr/lib/sysimage/rpm/XYZ files are symlinked to /var/lib/rpm/XYZ files
    ####### in the 2nd most recent installatiom with smaller number of packages installed, there is no trace of the above!
    if efi:
        os.system("sudo dnf -c ./src/distros/fedora/base.repo --installroot=/mnt install -y efibootmgr grub2-efi-x64") #addeed grub2-efi-x64 as I think without it, grub2-mkcongig and mkinstall don't exists! is that correct?  # grub2-common already installed at this point
### MOVED UP    if efi:
### MOVED UP        os.system("sudo chroot /mnt dnf install -y efibootmgr grub2-efi-x64") #addeed grub2-efi-x64 as I think without it, grub2-mkcongig and mkinstall don't exists! is that correct?  # grub2-common already installed at this point
### MOVED UP    os.system(f"sudo chroot /mnt dnf install -y {packages} --releasever={RELEASE}") ######## 'systemd' can be removed from packages list as it gets installed using some other package?!
#################
    input("bp2 > before yum.conf")   ### NO yum.conf file created yet
    os.system(f"echo 'releasever={RELEASE}' | tee /mnt/etc/yum.conf") ########NEW FOR FEDORA WHY DID I ADD THIS? ### CAN I REMOVE THIS?

#################
    input("bp3 > after yum?")


#   Update fstab
    os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" / btrfs subvol=@{distro_suffix},compress=zstd,noatime,ro 0 0' | sudo tee -a /mnt/etc/fstab")
    for mntdir in mntdirs:
        os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" /{mntdir} btrfs subvol=@{mntdir}{distro_suffix},compress=zstd,noatime 0 0' | sudo tee -a /mnt/etc/fstab")
    if efi:
        os.system(f"echo 'UUID=\"{to_uuid(args[3])}\" /boot/efi vfat umask=0077 0 2' | sudo tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/root /root none bind 0 0' | sudo tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/tmp /tmp none bind 0 0' | sudo tee -a /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@{distro_suffix}/ s|@{distro_suffix}|@.snapshots{distro_suffix}/rootfs/snapshot-tmp|' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@boot{distro_suffix}/ s|@boot{distro_suffix}|@.snapshots{distro_suffix}/boot/boot-tmp|' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@etc{distro_suffix}/ s|@etc{distro_suffix}|@.snapshots{distro_suffix}/etc/etc-tmp|' /mnt/etc/fstab")
    os.system(f"sudo sed -i '/\@{distro_suffix}/d' /mnt/etc/fstab") # Delete @_distro entry

#   Database and config files
    os.system("sudo mkdir -p /mnt/usr/share/ast/db")
    os.system("echo '0' | sudo tee /mnt/usr/share/ast/snap")
    # If rpmdb is under /usr, move it to /var and create a symlink
    if os.path.islink("/var/lib/dnf") or os.path.isfile("/usr/lib/sysimage/dnf/history.sqlite"):
        os.system("sudo rm -r /var/lib/dnf")
        os.system("sudo mv /usr/lib/sysimage/dnf /var/lib/")
        os.system("sudo ln -s /usr/lib/sysimage/dnf /var/lib/dnf")
    if os.path.islink("/var/lib/rpm") or os.path.isfile("/usr/lib/sysimage/rpm/rpmdb.sqlite"):
        os.system("sudo rm -r /var/lib/rpm")
        os.system("sudo mv /usr/lib/sysimage/rpm /var/lib/")
        os.system("sudo ln -s /usr/lib/sysimage/rpm /var/lib/rpm")
    os.system(f"sudo cp -a /mnt/var/lib/dnf /mnt/usr/share/ast/db/")
    os.system("sudo cp -a /mnt/var/lib/rpm /mnt/usr/share/ast/db/")
    os.system('echo persistdir="/usr/share/ast/db/dnf" | sudo tee -a /mnt/etc/dnf/dnf.conf') ### REVIEW_LATER I'm not sure if this works?!
    os.system(f"sudo sed -i '/^ID/ s|{distro}|{distro}_ashos|' /mnt/etc/os-release") # Modify OS release information (optional)

#   Update hostname, hosts, locales and timezone, hosts
    os.system(f"echo {hostname} | sudo tee /mnt/etc/hostname")
    os.system(f"echo 127.0.0.1 {hostname} | sudo tee -a /mnt/etc/hosts")
    os.system("sudo chroot /mnt sudo localedef -v -c -i en_US -f UTF-8 en_US.UTF-8") ####### REVIEW_LATER got error?!
    os.system("echo 'LANG=en_US.UTF-8' | sudo tee /mnt/etc/locale.conf")
    os.system(f"sudo ln -srf /mnt{tz} /mnt/etc/localtime")
    os.system("sudo chroot /mnt sudo hwclock --systohc")

#   Copy and symlink astpk and detect_os.sh
    os.system("sudo mkdir -p /mnt/.snapshots/ast/snapshots")
    os.system(f"echo '{to_uuid(args[1])}' | sudo tee /mnt/.snapshots/ast/part")
    os.system(f"sudo cp -a ./src/distros/{distro}/astpk.py /mnt/.snapshots/ast/ast")
    os.system("sudo cp -a ./src/detect_os.sh /mnt/.snapshots/ast/detect_os.sh")
    os.system("sudo ln -srf /mnt/.snapshots/ast/ast /mnt/usr/bin/ast")
    os.system("sudo ln -srf /mnt/.snapshots/ast/detect_os.sh /mnt/usr/bin/detect_os.sh")
    os.system("sudo ln -srf /mnt/.snapshots/ast /mnt/var/lib/ast")
    os.system("echo {\\'name\\': \\'root\\', \\'children\\': [{\\'name\\': \\'0\\'}]} | sudo tee /mnt/.snapshots/ast/fstree") # Initialize fstree

#   Create user and set password
    set_password("root")
    username = get_username()
    create_user(username, "wheel")
    set_password(username)

#   Services (init, network, etc.)
    os.system("sudo chroot /mnt systemctl enable NetworkManager")
    os.system("sudo chroot /mnt systemctl disable rpmdb-migrate") # https://fedoraproject.org/wiki/Changes/RelocateRPMToUsr ### WHEN IS THIS SERVICE ACTIVATED, DO A BREAKPOINT CHECK

#   GRUB and EFI (For now I use non-BLS format. Entries go in /boot/grub2/grub.cfg not in /boot/loader/entries/)
    os.system('grep -qxF GRUB_ENABLE_BLSCFG="false" /mnt/etc/default/grub || \
               echo GRUB_ENABLE_BLSCFG="false" | sudo tee -a /mnt/etc/default/grub')
############
    input("bp888 > any good grub.cfg in boot/grub2 ?") ### No grub.cfg in /mnt/boot/grub2/
    os.system(f"sudo chroot /mnt sudo grub2-mkconfig {args[2]} -o /boot/grub2/grub.cfg")
    os.system("sudo mkdir -p /mnt/boot/grub2/BAK") # Folder for backing up grub configs created by astpk
    os.system(f"sudo sed -i '0,/subvol=@{distro_suffix}/ s,subvol=@{distro_suffix},subvol=@.snapshots{distro_suffix}/rootfs/snapshot-tmp,g' /mnt/boot/grub2/grub.cfg")
    # Create EFI entry and a mapping of "distro" <=> "BootOrder number". Ash reads from this file to switch between distros.
    if efi:
        if not os.path.exists("/mnt/boot/efi/EFI/map.txt"):
            os.system("echo DISTRO,BootOrder | sudo tee /mnt/boot/efi/EFI/map.txt")
        os.system(f"efibootmgr -c -d {args[2]} -p 1 -L 'Fedora' -l '\\EFI\\fedora\\shim.efi'") ###REVIEW_LATER shim.efi vs shimx64.efi ### CAN I REMOVE THIS?
        os.system(f"echo '{distro},' $(efibootmgr -v | grep -i {distro} | awk '"'{print $1}'"' | sed '"'s|[^0-9]*||g'"') | sudo tee -a /mnt/boot/efi/EFI/map.txt")

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

#   Unmount everything and finish
    os.system("sudo umount --recursive /mnt")
    os.system(f"sudo mount {args[1]} -o subvolid=0 /mnt")
    os.system(f"sudo btrfs sub del /mnt/@{distro_suffix}")
    os.system("sudo umount --recursive /mnt")
    clear()
    print("Installation complete")
    print("You can reboot now :)")

