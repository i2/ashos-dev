#!/usr/bin/python3

import os
import subprocess
from src.distros.arch import astpk

def clear():
    os.system("#clear")

def to_uuid(part):
    return subprocess.check_output(f"blkid -s UUID -o value {part}", shell=True).decode('utf-8').strip()

###def grub_ords(part):
###    letter =
    ###return ord(letter.lower())-ord('a'),

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
    print("Welcome to the astOS installer!\n\n\n\n\n")
    choice, distro_suffix = get_multiboot(distro)

#   Define variables
    btrdirs = [f"@{distro_suffix}",f"@.snapshots{distro_suffix}",f"@home{distro_suffix}",f"@var{distro_suffix}",f"@etc{distro_suffix}",f"@boot{distro_suffix}"]
    mntdirs = ["",".snapshots","home","var","etc","boot"]
    astpart = to_uuid(args[1])
    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False

    tz = get_timezone()
    hostname = get_hostname()

#   Partition and format
    if choice != "3":
        os.system(f"sudo /usr/sbin/mkfs.vfat -F32 -n EFI {args[3]}") ###DELETE THIS LINE WHEN PRODUCTION READY
        os.system(f"sudo /usr/sbin/mkfs.btrfs -L LINUX -f {args[1]}")
    os.system("pacman -Syy --noconfirm archlinux-keyring")

#   Mount and create necessary sub-volumes and directories
    if choice != "3":
        os.system(f"sudo mount {args[1]} /mnt")
    else:
        os.system(f"sudo mount -o subvolid=5 {args[1]} /mnt")
    for btrdir in btrdirs:
        os.system(f"btrfs sub create /mnt/{btrdir}")
    os.system("umount /mnt")
    for mntdir in mntdirs:
        os.system(f"mkdir -p /mnt/{mntdir}") # -p to ignore /mnt exists complaint
        os.system(f"mount {args[1]} -o subvol={btrdirs[mntdirs.index(mntdir)]},compress=zstd,noatime /mnt/{mntdir}")
    for i in ("tmp", "root"):
        os.system(f"mkdir -p /mnt/{i}")
    for i in ("ast", "boot", "etc", "root", "rootfs", "tmp", "var"):
        os.system(f"mkdir -p /mnt/.snapshots/{i}")
    if efi:
        os.system("mkdir /mnt/boot/efi")
        os.system(f"mount {args[3]} /mnt/boot/efi")

#   Modify shell profile for debug purposes in live iso (optional temporary)
    #os.system('echo "alias paste='"'"'curl -F "'"'"'"sprunge=<-"'"'"'" http://sprunge.us'"'"' " | tee -a $HOME/.*shrc')
    #os.system("shopt -s nullglob && echo 'export LC_ALL=C' | sudo tee -a /mnt/root/.*shrc")
    #os.system("find /mnt/root/ -maxdepth 1 -type f -iname '.*shrc' -exec sh -c 'echo export LC_ALL=C | sudo tee -a $1' -- {} \;")
    #os.system("echo -e 'setw -g mode-keys vi\nset -g history-limit 999999' >> $HOME/.tmux.conf")

#   Pacstrap then install anytree and necessary packages in chroot
    #os.system("pacstrap /mnt base linux linux-firmware nano python3 python-anytree dhcpcd arch-install-scripts btrfs-progs networkmanager grub sudo os-prober")
    #os.system("pacstrap /mnt base linux neovim btrfs-progs grub sudo os-prober")
    os.system("pacstrap /mnt base linux nano python3 python-anytree arch-install-scripts btrfs-progs grub sudo os-prober")
    if efi:
        os.system("pacstrap /mnt efibootmgr")
    for i in ("/dev", "/dev/pts", "/proc", "/run", "/sys", "/sys/firmware/efi/efivars"): #REZA maybe add /tmp as well?
        os.system(f"mount -B {i} /mnt{i}") # Mount-points needed for chrooting

#   Update fstab
    os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" / btrfs subvol=@{distro_suffix},compress=zstd,noatime,ro 0 0' | sudo tee /mnt/etc/fstab")
    for mntdir in mntdirs:
        os.system(f"echo 'UUID=\"{to_uuid(args[1])}\" /{mntdir} btrfs subvol=@{mntdir}{distro_suffix},compress=zstd,noatime 0 0' | sudo tee -a /mnt/etc/fstab")
    if efi:
        os.system(f"echo 'UUID=\"{to_uuid(args[3])}\" /boot/efi vfat umask=0077 0 2' | tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/root /root none bind 0 0' | tee -a /mnt/etc/fstab")
    os.system("echo '/.snapshots/ast/tmp /tmp none bind 0 0' | tee -a /mnt/etc/fstab")

    os.system("mkdir -p /mnt/usr/share/ast/db")
    os.system("echo '0' | tee /mnt/usr/share/ast/snap")
    os.system(f"cp -r /mnt/var/lib/pacman/* /mnt/usr/share/ast/db")
    os.system(f"sed -i s,\"#DBPath      = /var/lib/pacman/\",\"DBPath      = /usr/share/ast/db/\",g /mnt/etc/pacman.conf")

#   Modify OS release information (optional)
    os.system(f"sed -i '/^NAME/ s/Arch Linux/Arch Linux (ashos)/' /mnt/etc/os-release")
    os.system(f"sed -i '/PRETTY_NAME/ s/Arch Linux/Arch Linux (ashos)/' /mnt/etc/os-release")
    os.system(f"sed -i '/^ID/ s/arch/arch_ashos/' /mnt/etc/os-release")
    #os.system("echo 'HOME_URL=\"https://github.com/astos/astos\"' | tee -a /mnt/etc/os-release")

#   Update hostname, locales and timezone
    os.system(f"echo {hostname} | tee /mnt/etc/hostname")
    os.system("sed -i 's/^#en_US.UTF-8/en_US.UTF-8/g' /etc/locale.gen")
    os.system("chroot /mnt locale-gen")
    os.system("echo 'LANG=en_US.UTF-8' | tee /mnt/etc/locale.conf")
    os.system(f"chroot /mnt ln -sf {tz} /etc/localtime")
    os.system("chroot /mnt hwclock --systohc")

    # THESE 3 lines were not right, I don't know why archashos was still working!!!!!??????
    #os.system(f"sed -i '0,/@{distro_suffix}/ s,@,@{distro_suffix}.snapshots/rootfs/snapshot-tmp,' /mnt/etc/fstab")
    #os.system(f"sed -i '0,/@boot{distro_suffix}/ s,@boot{distro_suffix},@.snapshots{distro_suffix}/boot/boot-tmp,' /mnt/etc/fstab")
    #os.system(f"sed -i '0,/@etc{distro_suffix}/ s,@etc{distro_suffix},@.snapshots{distro_suffix}/etc/etc-tmp,' /mnt/etc/fstab")
    
    os.system(f"sed -i '0,/@{distro_suffix}/ s,@{distro_suffix},@.snapshots{distro_suffix}/rootfs/snapshot-tmp,' /mnt/etc/fstab")
    os.system(f"sed -i '0,/@boot{distro_suffix}/ s,@boot{distro_suffix},@.snapshots{distro_suffix}/boot/boot-tmp,' /mnt/etc/fstab")
    os.system(f"sed -i '0,/@etc{distro_suffix}/ s,@etc{distro_suffix},@.snapshots{distro_suffix}/etc/etc-tmp,' /mnt/etc/fstab")
    
    # Delete fstab created for @{distro_suffix} which is going to be deleted at the end
    os.system(f"sed -i.bak '/\@{distro_suffix}/d' /mnt/etc/fstab")

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
#######    if multiboot: # if there is already a grub efi/cfg in /dev/sda1 #TODO for bios systems
        #create tmp dir for mounting /dev/sda2 #(assumingly has OS and default subvol is the last OS booting)

#######        prev_distro = subprocess.check_output(['sh', '/usr/local/sbin/detect_os.sh /tmp/s']).decode('utf-8').replace('"',"").strip()

#######        os.system(f"mv /mnt/boot/efi/ashos /mnt/boot/efi/ashos_BAK") #TODO: Get name of previous installed distro from user or use detect_os.sh
###    if choice == "3":   # COULD BE BETTER TO CHECK FOR EXISTENCE OF 'ashos' in /dev/sda1
    if choice == "3":   # COULD BE BETTER TO CHECK FOR EXISTENCE OF 'default.txt' content in /dev/sda1
        try:
            prev_os_grub = subprocess.check_output("cat /mnt/boot/efi/EFI/default.txt", shell=True).decode('utf-8').strip()
        except:
            print("No previous OS grub found!")
        else:
            os.system(f"mv /mnt/boot/efi/EFI/{prev_os_grub} /mnt/boot/efi/EFI/{prev_os_grub}_ashos")
#        if previous_os:
###        print("#detect name of previous distro that's mounted at default subvolume")
###        pdistro = astpk.detect_previous_distro(args[1])
###        print(f"name of previous default distro is: {pdistro}")
###        #pdistro = subprocess.check_output(['sh', './src/detect_os.sh']).decode('utf-8').replace('"',"").strip()
###        print("rename ashos grub")
###        astpk.rename_ashos_grub(args[3], pdistro)
    #os.system(f"chroot /mnt sed -i s,Arch,AshOS,g /etc/default/grub")
    os.system(f"chroot /mnt grub-install {args[2]}") #REZA --recheck --no-nvram --removable
###    # MAYBE do some extra operations here if multiboot?!
    os.system(f"chroot /mnt grub-mkconfig {args[2]} -o /boot/grub/grub.cfg")
    os.system(f"sed -i '0,/subvol=@{distro_suffix}/s,subvol=@{distro_suffix},subvol=@.snapshots{distro_suffix}/rootfs/snapshot-tmp,g' /mnt/boot/grub/grub.cfg")
#   GRUB and EFI - Backup and create default entry txt
    
    # Create a map.txt file "distro" => "EFI entry"
    os.system(f"chroot /mnt echo {distro} === $(efibootmgr -v | grep '{distro}') | tee -a /mnt/boot/efi/EFI/map.txt")
    
    try:
        now_os_grub = subprocess.check_output("find /mnt/boot/efi/EFI/ -mindepth 1 -maxdepth 1 -type \
        d -name '*ashos*' -o -name '*default*' -prune -o -exec basename {} \; | \
        sudo tee /mnt/boot/efi/EFI/default.txt", shell=True).decode('utf-8').strip()
    except:
        print("An exception occurred!")
###    os.system(f"chroot /mnt cp -a /boot/efi/EFI/ashos /boot/efi/EFI/ashos{distro_suffix}.BAK")
###    os.system(f"chroot /mnt cp -a /boot/grub /boot/grub{distro_suffix}.BAK")
    else:
        os.system(f"chroot /mnt cp -a /boot/efi/EFI/{now_os_grub} /boot/efi/EFI/{now_os_grub}.BAK")
        #os.system(f"chroot /mnt cp -a /boot/grub /boot/grub{distro_suffix}.BAK")
        os.system(f"chroot /mnt cp -a /boot/grub /boot/grub{distro_suffix}_ashos.BAK")
        #.BAK file and folders are strictly for user's 'manual intervention' if things go wrong. They won't be used in the algorithm.

#   Copy astpk
    os.system(f"cp ./src/distros/{distro}/astpk.py /mnt/usr/bin/ast")
    os.system("cp ./src/detect_os.sh /mnt/usr/bin/detect_os.sh")
    os.system("chroot /mnt chmod +x /usr/sbin/ast /usr/bin/detect_os.sh")

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

###    # Copy GOOD grub.cfg (the reference one) and maybe grubx64.efi from sda2 to sda1
### os.system(f"sed -i 's/UUID/{to_uuid(args[1])}/' -i 's/BOOT/boot{distro_suffix}/' /mnt/boot/efi/EFI/ashos/grub.cfg") #MAKE SURE THIS IS THE ONE IN /dev/sda1 not sda2
### os.system("cp /mnt/boot/e /mnt/boot/efi/EFI/ashos/ "
###

#   Copy boot and etc from snapshot's tmp to common
    if efi:
        os.system("umount /mnt/boot/efi")
    os.system("umount /mnt/boot")
    os.system(f"mount {args[1]} -o subvol=@boot{distro_suffix},compress=zstd,noatime /mnt/.snapshots/boot/boot-tmp")
    os.system("cp --reflink=auto -r /mnt/.snapshots/boot/boot-tmp/* /mnt/boot")
    os.system("umount /mnt/etc")
    os.system(f"mount {args[1]} -o subvol=@etc{distro_suffix},compress=zstd,noatime /mnt/.snapshots/etc/etc-tmp")
    os.system("cp --reflink=auto -r /mnt/.snapshots/etc/etc-tmp/* /mnt/etc")

    os.system("cp --reflink=auto -r /mnt/.snapshots/boot/boot-0/* /mnt/.snapshots/rootfs/snapshot-tmp/boot")
    os.system("cp --reflink=auto -r /mnt/.snapshots/etc/etc-0/* /mnt/.snapshots/rootfs/snapshot-tmp/etc")
    os.system("cp --reflink=auto -r /mnt/.snapshots/var/var-0/* /mnt/.snapshots/rootfs/snapshot-tmp/var")

#   Unmount everything
    os.system("sudo umount -R /mnt")
    os.system(f"sudo mount {args[1]} -o subvolid=0 /mnt") # subvolid=5 needed for any cases?
    os.system(f"sudo btrfs sub del /mnt/@{distro_suffix}")
    os.system("sudo umount -R /mnt")

    clear()
    print("Installation complete")
    print("You can reboot now :)")

