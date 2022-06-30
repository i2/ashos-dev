#!/usr/bin/python3

# Steps: partition, format, mount root partition, debootstrap, chroot, mount-bind etc.
# modify fstab, network (/etc/{network/interfaces,resolv.conf,hostname,hosts}), cp sources.list to chroot
# apt-get update, apt-get --no-install-recommends install stuff, set locales tz,

import os
import subprocess
from src.distros.arch import astpk

def clear():
    os.system("#clear")

def to_uuid(part):
    return subprocess.check_output(f"sudo blkid -s UUID -o value {part}", shell=True).decode('utf-8').strip()

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
    choice, distro_suffix = get_multiboot(distro)

#   Define variables
    RELEASE = "bullseye"
    ARCH = "amd64"
    btrdirs = [f"@{distro_suffix}",f"@.snapshots{distro_suffix}",f"@home{distro_suffix}",f"@var{distro_suffix}",f"@etc{distro_suffix}",f"@boot{distro_suffix}"]
    mntdirs = ["",".snapshots","home","var","etc","boot"]
    #astpart = to_uuid(args[1])
    if os.path.exists("/sys/firmware/efi"):
        efi = True
    else:
        efi = False

    tz = get_timezone()
    hostname = get_hostname()

#   Partition and format
    #os.system("find $HOME -maxdepth 1 -type f -iname '.*shrc' -exec sh -c 'echo export LC_ALL=C LANGUAGE=C LANG=C >> $1' -- {} \;") # Perl complains if not set
    os.system("sudo apt-get remove -y --purge man-db") # make installs faster (because of trigger man-db bug)
    os.system("sudo apt-get update -y")
    os.system("sudo apt-get install -y parted dosfstools") #REZA ###DELETE THIS LINE WHEN PRODUCTION READY
    os.system("sudo apt-get install -y btrfs-progs ntp")
    #os.system("sudo parted --align minimal --script /dev/sda mklabel gpt unit MiB mkpart ESP fat32 0% 256 set 1 boot on mkpart primary ext4 256 100%")
    if choice != "3":
        os.system(f"sudo /usr/sbin/mkfs.vfat -F32 -n EFI {args[3]}") ###DELETE THIS LINE WHEN PRODUCTION READY
        os.system(f"sudo /usr/sbin/mkfs.btrfs -L LINUX -f {args[1]}")

    astpart = to_uuid(args[1]) #REZA ###DELETE THIS LINE WHEN PRODUCTION READY

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
    for i in ("ast", "boot", "etc", "root", "rootfs", "tmp", "var"):
        os.system(f"mkdir -p /mnt/.snapshots/{i}")
#MOVEDAFTERDEBOOTSTRAP    if efi:
#MOVEDAFTERDEBOOTSTRAP        os.system("sudo mkdir /mnt/boot/efi")
#MOVEDAFTERDEBOOTSTRAP        os.system(f"sudo mount {args[3]} /mnt/boot/efi")

#   Modify shell profile for debug purposes in live iso (optional temporary)
    #os.system('echo "alias paste='"'"'curl -F "'"'"'"sprunge=<-"'"'"'" http://sprunge.us'"'"' " | tee -a $HOME/.*shrc')
    #os.system("shopt -s nullglob && echo 'export LC_ALL=C' | sudo tee -a /mnt/root/.*shrc")
    #os.system("find /mnt/root/ -maxdepth 1 -type f -iname '.*shrc' -exec sh -c 'echo export LC_ALL=C | sudo tee -a $1' -- {} \;")
    #os.system("echo -e 'setw -g mode-keys vi\nset -g history-limit 999999' >> $HOME/.tmux.conf")

#   Bootstrap (minimal)
    os.system("sudo apt-get install -y debootstrap")
    excl = subprocess.check_output("dpkg-query -f '${binary:Package} ${Priority}\n' -W | grep -v 'required\|important' | awk '{print $1}'", shell=True).decode('utf-8').strip().replace("\n",",")
    os.system(f"sudo debootstrap --arch {ARCH} --exclude={excl} {RELEASE} /mnt http://archive.ubuntu.com/ubuntu")
    for i in ("/dev", "/dev/pts", "/proc", "/run", "/sys", "/sys/firmware/efi/efivars"): #REZA maybe add /tmp as well?
        os.system(f"sudo mount -B {i} /mnt{i}") # Mount-points needed for chrooting
    os.system(f"sudo chroot /mnt apt-get install -y linux-image-{ARCH}")

    if efi: ###REZA #MOVED FROM ABOVE See if there are still files in sda1 unnecessarily heavy (ONLY FOR DEBOOSTRAP BASED OS, NOT FOR ARCH)
        os.system("sudo mkdir /mnt/boot/efi")
        os.system(f"sudo mount {args[3]} /mnt/boot/efi")

#   Install anytree and necessary packages in chroot
    os.system("sudo systemctl enable --now ntp && sleep 30s && ntpq -p") # Sync time in the live iso
    os.system(f"echo 'deb [trusted=yes] http://www.deb-multimedia.org {RELEASE} main' | sudo tee -a /mnt/etc/apt/sources.list.d/multimedia.list >/dev/null")
    os.system("sudo chroot /mnt apt-get update -y -oAcquire::AllowInsecureRepositories=true")
    os.system("sudo chroot /mnt apt-get install -y deb-multimedia-keyring --allow-unauthenticated")
    #os.system("sudo chroot /mnt apt-get install -y python3-anytree network-manager btrfs-progs dhcpcd5 locales sudo os-prober")
    os.system("sudo chroot /mnt apt-get install -y python3-anytree btrfs-progs locales sudo")
    if efi:
        os.system("sudo chroot /mnt apt-get install -y grub-efi")
    else:
        os.system("sudo chroot /mnt apt-get install -y grub-pc")

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
    os.system("sudo cp -r /mnt/var/lib/dpkg/* /mnt/usr/share/ast/db")
    #os.system(f"echo 'RootDir=/usr/share/ast/db/' | sudo tee -a /mnt/etc/apt/apt.conf")

#   Modify OS release information (optional)
    os.system(f"sed -i '/^NAME/ s/Ubuntu/Ubuntu (ashos)/' /mnt/etc/os-release")
    os.system(f"sed -i '/PRETTY_NAME/ s/Ubuntu/Ubuntu (ashos)/' /mnt/etc/os-release")
    os.system(f"sed -i '/^ID/ s/ubuntu/ubuntu_ashos/' /mnt/etc/os-release")
    #os.system("echo 'HOME_URL=\"https://github.com/astos/astos\"' | tee -a /mnt/etc/os-release")

#   Update hostname, locales and timezone
    os.system(f"echo {hostname} | sudo tee /mnt/etc/hostname")
    os.system("sudo sed -i 's/^#en_US.UTF-8/en_US.UTF-8/g' /etc/locale.gen")
    os.system("sudo chroot /mnt locale-gen")
    os.system("echo 'LANG=en_US.UTF-8' | sudo tee /mnt/etc/locale.conf")
    os.system(f"sudo chroot /mnt ln -sf {tz} /etc/localtime")
    os.system("sudo chroot /mnt hwclock --systohc")

    os.system(f"sudo sed -i '0,/@{distro_suffix}/ s,@,@{distro_suffix}.snapshots/rootfs/snapshot-tmp,' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@boot{distro_suffix}/ s,@boot{distro_suffix},@.snapshots{distro_suffix}/boot/boot-tmp,' /mnt/etc/fstab")
    os.system(f"sudo sed -i '0,/@etc{distro_suffix}/ s,@etc{distro_suffix},@.snapshots{distro_suffix}/etc/etc-tmp,' /mnt/etc/fstab")

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
#######    if multiboot: # if there is already a grub efi/cfg in /dev/sda1 #TODO for bios systems
        #create tmp dir for mounting /dev/sda2 #(assumingly has OS and default subvol is the last OS booting)

#######        prev_distro = subprocess.check_output(['sh', '/usr/local/sbin/detect_os.sh /tmp/s']).decode('utf-8').replace('"',"").strip()

#######        os.system(f"mv /mnt/boot/efi/ashos /mnt/boot/efi/ashos_BAK") #TODO: Get name of previous installed distro from user or use detect_os.sh
    if choice == "3":   # COULD BE BETTER TO CHECK FOR EXISTENCE OF 'ashos' in /dev/sda1
        print("#detect name of previous distro that's mounted at default subvolume")
        pdistro = astpk.detect_previous_distro(args[1])
        print(f"name of previous default distro is: {pdistro}")
        #pdistro = subprocess.check_output(['sh', './src/distros/detect_os.sh']).decode('utf-8').replace('"',"").strip()
        print("rename ashos grub")
        astpk.rename_ashos_grub(args[3], pdistro)
    os.system(f"sudo chroot /mnt sed -i s,Ubuntu,AshOS,g /etc/default/grub")
    os.system(f"sudo chroot /mnt grub-install {args[2]}") #REZA --recheck --no-nvram --removable
###    # MAYBE do some extra operations here if multiboot?!
    os.system(f"sudo chroot /mnt grub-mkconfig {args[2]} -o /boot/grub/grub.cfg")
    os.system(f"sudo sed -i '0,/subvol=@{distro_suffix}/s,subvol=@{distro_suffix},subvol=@.snapshots{distro_suffix}/rootfs/snapshot-tmp,g' /mnt/boot/grub/grub.cfg")
#   Backup GRUB and EFI
    os.system(f"chroot /mnt cp -a /boot/efi/EFI/ashos /boot/efi/EFI/ashos{distro_suffix}.BAK")
    os.system(f"chroot /mnt cp -a /boot/grub /boot/grub{distro_suffix}.BAK")

#   Copy astpk
    os.system(f"cp ./src/distros/{distro}/astpk.py /mnt/usr/bin/ast")
    os.system("chroot /mnt chmod +x /usr/sbin/ast")
    os.system(f"cp ./src/distros/detect_os.sh /mnt/usr/bin/detect_os.sh")
    os.system("chroot /mnt chmod +x /usr/bin/detect_os.sh")

    os.system("sudo btrfs sub snap -r /mnt /mnt/.snapshots/rootfs/snapshot-0")
    os.system("sudo btrfs sub create /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub create /mnt/.snapshots/var/var-tmp")

    for i in ("dpkg", "systemd"):
        os.system(f"sudo mkdir -p /mnt/.snapshots/var/var-tmp/lib/{i}")
    os.system("sudo cp --reflink=auto -r /mnt/var/lib/dpkg/* /mnt/.snapshots/var/var-tmp/lib/dpkg/")
    os.system("sudo cp --reflink=auto -r /mnt/var/lib/systemd/* /mnt/.snapshots/var/var-tmp/lib/systemd/")
    os.system("sudo cp --reflink=auto -r /mnt/boot/* /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/etc/* /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/boot/boot-tmp /mnt/.snapshots/boot/boot-0")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/etc/etc-tmp /mnt/.snapshots/etc/etc-0")
    os.system("sudo btrfs sub snap -r /mnt/.snapshots/var/var-tmp /mnt/.snapshots/var/var-0")

    os.system(f"echo '{astpart}' | sudo tee /mnt/.snapshots/ast/part")

    os.system("sudo btrfs sub snap /mnt/.snapshots/rootfs/snapshot-0 /mnt/.snapshots/rootfs/snapshot-tmp")
    os.system("sudo chroot /mnt btrfs sub set-default /.snapshots/rootfs/snapshot-tmp")

    os.system("sudo cp -r /mnt/root/. /mnt/.snapshots/root/")
    os.system("sudo cp -r /mnt/tmp/. /mnt/.snapshots/tmp/")
    os.system("sudo rm -rf /mnt/root/*")
    os.system("sudo rm -rf /mnt/tmp/*")

###    # Copy GOOD grub.cfg (the reference one) and maybe grubx64.efi from sda2 to sda1
### os.system(f"sed -i 's/UUID/{to_uuid(args[1])}/' -i 's/BOOT/boot{distro_suffix}/' /mnt/boot/efi/EFI/ashos/grub.cfg") #MAKE SURE THIS IS THE ONE IN /dev/sda1 not sda2
### os.system("cp /mnt/boot/e /mnt/boot/efi/EFI/ashos/ "
###

#   Clean unnecessary packages (optional)
    os.system("sudo apt-get autoremove -y")
    os.system("sudo apt-get autoclean -y")

#   Copy boot and etc from snapshot's tmp to common
    if efi:
        os.system("sudo umount /mnt/boot/efi")
    os.system("sudo umount /mnt/boot")
    os.system(f"sudo mount {args[1]} -o subvol=@boot{distro_suffix},compress=zstd,noatime /mnt/.snapshots/boot/boot-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-tmp/* /mnt/boot")
    os.system("sudo umount /mnt/etc")
    os.system(f"sudo mount {args[1]} -o subvol=@etc{distro_suffix},compress=zstd,noatime /mnt/.snapshots/etc/etc-tmp")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-tmp/* /mnt/etc")

    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/boot/boot-0/* /mnt/.snapshots/rootfs/snapshot-tmp/boot")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/etc/etc-0/* /mnt/.snapshots/rootfs/snapshot-tmp/etc")
    os.system("sudo cp --reflink=auto -r /mnt/.snapshots/var/var-0/* /mnt/.snapshots/rootfs/snapshot-tmp/var")

#   Unmount everything
    os.system("sudo umount -R /mnt")
    os.system(f"sudo mount {args[1]} -o subvolid=0 /mnt") # subvolid=5 needed for any cases?
    os.system(f"sudo btrfs sub del /mnt/@{distro_suffix}")
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
