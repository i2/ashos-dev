#!/usr/bin/python3

import os
import subprocess

def clear():
    os.system("#clear")

def to_uuid(part):
    return subprocess.check_output(f"blkid -s UUID -o value {part}", shell=True).decode('utf-8').strip()

def get_hostname():
    while True:
        clear()
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
    while True:
        clear()
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
    while True:
        clear()
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
    while True:
        clear()
        print(f"Setting a password for '{u}':")
        os.system(f"chroot /mnt passwd {u}")
        print("Was your password set properly (y/n)?")
        reply = input("> ")
        if reply.casefold() == "y":
            break
        else:
            clear()
            continue

def main(args):
    print("Welcome to the astOS installer!\n\n\n\n\n")

#   Partition and format
    os.system(f"/usr/sbin/mkfs.btrfs -L LINUX -f {args[1]}")
    os.system("pacman -Syy --noconfirm archlinux-keyring")

#   Define variables
    DISTRO = "arch"
    #btrdirs = ["@","@.snapshots","@home","@var","@etc","@boot"]
    btrdirs = [f"@_{DISTRO}",f"@.snapshots_{DISTRO}",f"@home_{DISTRO}",f"@var_{DISTRO}",f"@etc_{DISTRO}",f"@boot_{DISTRO}"]
    mntdirs = ["",".snapshots","home","var","etc","boot"]
    #mntdirs = [f'"",".snapshots_{DISTRO}","home_{DISTRO}","var_{DISTRO}","etc_{DISTRO}","boot_{DISTRO}"']
    mntdirs_n = mntdirs[1:]
    astpart = to_uuid(args[1])
    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False

    tz = get_timezone()
    hostname = get_hostname()

#   Mount and create necessary sub-volumes and directories
    os.system(f"mount {args[1]} /mnt")
    for btrdir in btrdirs:
        os.system(f"btrfs sub create /mnt/{btrdir}")
    os.system("umount /mnt")
    os.system(f"mount {args[1]} -o subvol=@_{DISTRO},compress=zstd,noatime /mnt")
    for mntdir in mntdirs_n:
        os.system(f"mkdir /mnt/{mntdir}")
        os.system(f"mount {args[1]} -o subvol={btrdirs[mntdirs.index(mntdir)]},compress=zstd,noatime /mnt/{mntdir}")
    for i in ("tmp", "root"):
        os.system(f"mkdir -p /mnt/{i}")
    for i in ("ast", "boot", "etc", "root", "rootfs", "tmp", "var"):
        os.system(f"mkdir -p /mnt/.snapshots/{i}")
    if efi:
        os.system("mkdir /mnt/boot/efi")
        os.system(f"mount {args[3]} /mnt/boot/efi")

#   Install anytree and necessary packages in chroot
    os.system("pacstrap /mnt base linux linux-firmware nano python3 python-anytree dhcpcd arch-install-scripts btrfs-progs networkmanager grub sudo")
    if efi:
        os.system("pacstrap /mnt efibootmgr")
    for i in ("/dev", "/dev/pts", "/proc", "/run", "/sys", "/sys/firmware/efi/efivars"):
        os.system(f"mount -B {i} /mnt{i}") # Mount-points needed for chrooting

#   Update fstab
    os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" / btrfs subvol=@_{DISTRO},compress=zstd,noatime,ro 0 0' | tee /mnt/etc/fstab")
    for mntdir in mntdirs_n:
        os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" /{mntdir} btrfs subvol=@{mntdir}_{DISTRO},compress=zstd,noatime 0 0' | tee -a /mnt/etc/fstab")
    if efi:
        os.system(f"echo 'UUID=\"{to_uuid(args[3])}\" /boot/efi vfat umask=0077 0 2' | tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/root /root none bind 0 0' | tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/tmp /tmp none bind 0 0' | tee -a /mnt/etc/fstab")

    os.system("mkdir -p /mnt/usr/share/ast/db")
    os.system("echo '0' | tee /mnt/usr/share/ast/snap")
    os.system(f"cp -r /mnt/var/lib/pacman/* /mnt/usr/share/ast/db")
    os.system(f"sed -i s,\"#DBPath      = /var/lib/pacman/\",\"DBPath      = /usr/share/ast/db/\",g /mnt/etc/pacman.conf")

#   Modify OS release information (optional)
#    os.system(f"echo 'NAME=\"astOS\"' | tee /mnt/etc/os-release")
#    os.system(f"echo 'PRETTY_NAME=\"astOS\"' | tee -a /mnt/etc/os-release")
#    os.system(f"echo 'ID=astos' | tee -a /mnt/etc/os-release")
#    os.system(f"echo 'BUILD_ID=rolling' | tee -a /mnt/etc/os-release")
#    os.system(f"echo 'ANSI_COLOR=\"38;2;23;147;209\"' | tee -a /mnt/etc/os-release")
#    os.system(f"echo 'HOME_URL=\"https://github.com/CuBeRJAN/astOS\"' | tee -a /mnt/etc/os-release")
#    os.system(f"echo 'LOGO=astos-logo' | tee -a /mnt/etc/os-release")
#    os.system(f"echo 'DISTRIB_ID=\"astOS\"' | tee /mnt/etc/lsb-release")
#    os.system(f"echo 'DISTRIB_RELEASE=\"rolling\"' | tee -a /mnt/etc/lsb-release")
#    os.system(f"echo 'DISTRIB_DESCRIPTION=astOS' | tee -a /mnt/etc/lsb-release")

#   Update hostname, locales and timezone
    os.system(f"echo {hostname} | tee /mnt/etc/hostname")
    os.system("sed -i 's/^#en_US.UTF-8/en_US.UTF-8/g' /etc/locale.gen")
    os.system("chroot /mnt locale-gen")
    os.system("echo 'LANG=en_US.UTF-8' | tee /mnt/etc/locale.conf")
    os.system(f"chroot /mnt ln -sf {tz} /etc/localtime")
    os.system("chroot /mnt hwclock --systohc")

    os.system(f"sudo sed -i '0,/@_{DISTRO}/s,@,@.snapshots/rootfs/snapshot-tmp,' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@boot_{DISTRO}/s,@boot,@.snapshots/boot/boot-tmp,' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@etc_{DISTRO}/s,@etc,@.snapshots/etc/etc-tmp,' /mnt/etc/fstab")

    os.system("mkdir -p /mnt/.snapshots/ast/snapshots")
    os.system("chroot /mnt ln -s /.snapshots/ast /var/lib/ast")

#   Create user and set password
    set_password("root")
    username = get_username()
    create_user(username)
    set_password(username)

    os.system("chroot /mnt systemctl enable NetworkManager")

#   Initialize fstree
    os.system("echo {\\'name\\': \\'root\\', \\'children\\': [{\\'name\\': \\'0\\'}]} | tee /mnt/.snapshots/ast/fstree")

#   GRUB
    os.system(f"chroot /mnt sed -i s,Arch,astOS,g /etc/default/grub")
    os.system(f"chroot /mnt grub-install {args[2]}")
    os.system(f"chroot /mnt grub-mkconfig {args[2]} -o /boot/grub/grub.cfg")
    os.system(f"sudo sed -i '0,/subvol=@_{DISTRO}/s,subvol=@_{DISTRO},subvol=@.snapshots_{DISTRO}/rootfs/snapshot-tmp,g' /mnt/boot/grub/grub.cfg")

#   Copy astpk
    os.system(f"cp ./src/distros/{DISTRO}/astpk.py /mnt/usr/sbin/ast")
    os.system("chroot /mnt chmod +x /usr/sbin/ast")

    os.system("btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-0")
    os.system("btrfs sub create /mnt/.snapshots/boot/boot-tmp")
    os.system("btrfs sub create /mnt/.snapshots/etc/etc-tmp")
    os.system("btrfs sub create /mnt/.snapshots/var/var-tmp")

    for i in ("pacman", "systemd"):
        os.system(f"mkdir -p /mnt/.snapshots/var/var-tmp/lib/{i}")
    os.system("cp --reflink=auto -r /mnt/var/lib/pacman/* /mnt/.snapshots/var/var-tmp/lib/pacman/")
    os.system("cp --reflink=auto -r /mnt/var/lib/systemd/* /mnt/.snapshots/var/var-tmp/lib/systemd/")
    os.system("cp --reflink=auto -r /mnt/boot/* /mnt/.snapshots/boot/boot-tmp")
    os.system("cp --reflink=auto -r /mnt/etc/* /mnt/.snapshots/etc/etc-tmp")
    os.system("btrfs sub snap -r /mnt/.snapshots/boot/boot-tmp /mnt/.snapshots/boot/boot-0")
    os.system("btrfs sub snap -r /mnt/.snapshots/etc/etc-tmp /mnt/.snapshots/etc/etc-0")
    os.system("btrfs sub snap -r /mnt/.snapshots/var/var-tmp /mnt/.snapshots/var/var-0")

    os.system(f"echo '{astpart}' | tee /mnt/.snapshots/ast/part")

    os.system("btrfs sub snap /mnt/.snapshots/rootfs/snapshot-0 /mnt/.snapshots/rootfs/snapshot-tmp")
    os.system("chroot /mnt btrfs sub set-default /.snapshots/rootfs/snapshot-tmp")

    os.system("cp -r /mnt/root/. /mnt/.snapshots/root/")
    os.system("cp -r /mnt/tmp/. /mnt/.snapshots/tmp/")
    os.system("rm -rf /mnt/root/*")
    os.system("rm -rf /mnt/tmp/*")

#   Copy boot and etc from snapshot's tmp to common
    if efi:
        os.system("umount /mnt/boot/efi")
    os.system("umount /mnt/boot")
    os.system(f"mount {args[1]} -o subvol=@boot,compress=zstd,noatime /mnt/.snapshots/boot/boot-tmp")
    os.system("cp --reflink=auto -r /mnt/.snapshots/boot/boot-tmp/* /mnt/boot")
    os.system("umount /mnt/etc")
    os.system(f"mount {args[1]} -o subvol=@etc,compress=zstd,noatime /mnt/.snapshots/etc/etc-tmp")
    os.system("cp --reflink=auto -r /mnt/.snapshots/etc/etc-tmp/* /mnt/etc")

    os.system("cp --reflink=auto -r /mnt/.snapshots/boot/boot-0/* /mnt/.snapshots/rootfs/snapshot-tmp/boot")
    os.system("cp --reflink=auto -r /mnt/.snapshots/etc/etc-0/* /mnt/.snapshots/rootfs/snapshot-tmp/etc")
    os.system("cp --reflink=auto -r /mnt/.snapshots/var/var-0/* /mnt/.snapshots/rootfs/snapshot-tmp/var")

#   Unmount everything
    os.system("umount -R /mnt")
    os.system(f"mount {args[1]} -o subvolid=5 /mnt")
    os.system("btrfs sub del /mnt/@")
    os.system("umount -R /mnt")
    clear()
    print("Installation complete")
    print("You can reboot now :)")

