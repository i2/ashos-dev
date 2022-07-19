#https://docs.fedoraproject.org/en-US/fedora/latest/system-administrators-guide/kernel-module-driver-configuration/Manually_Upgrading_the_Kernel/

    #os.system(f"sudo dnf makecache --refresh --releasever={RELEASE} -c ./src/distros/fedora/base.repo") # This causes many errors 'insert into requirename values'

# might need to append /bin/sh or /bin/bash to chroot commands, as arch iso live cd use zsh and chroot environment is bash

#   Modify shell profile for debug purposes in live iso (optional temporary)
    #os.system('echo "alias paste='"'"'curl -F "'"'"'"sprunge=<-"'"'"'" http://sprunge.us'"'"' " | tee -a $HOME/.*shrc')
    #os.system("shopt -s nullglob && echo 'export LC_ALL=C' | sudo tee -a /mnt/root/.*shrc")
    #os.system("find /mnt/root/ -maxdepth 1 -type f -iname '.*shrc' -exec sh -c 'echo export LC_ALL=C | sudo tee -a $1' -- {} \;")
    #os.system("echo -e 'setw -g mode-keys vi\nset -g history-limit 999999' >> $HOME/.tmux.conf")

    for i in ("dnf", "rpm", "systemd"): # what about rpm-state
        os.system(f"mkdir -p /mnt/.snapshots/var/var-tmp/lib/{i}")
    os.system("cp --reflink=auto -r /mnt/var/lib/dnf/* /mnt/.snapshots/var/var-tmp/lib/dnf/")
    os.system("cp --reflink=auto -r /mnt/var/lib/rpm/* /mnt/.snapshots/var/var-tmp/lib/rpm/")
    os.system("cp --reflink=auto -r /mnt/var/lib/systemd/* /mnt/.snapshots/var/var-tmp/lib/systemd/")

    os.system("btrfs sub snap -r /mnt/.snapshots/var/var-tmp /mnt/.snapshots/var/var-0")

    os.system("cp --reflink=auto -r /mnt/.snapshots/var/var-0/. /mnt/.snapshots/rootfs/snapshot-tmp/var/")

    ### NOT NEEDED AT ALL os.system("cp /etc/resolv.conf /mnt/etc/")  ###########NEW FOR FEDORA, it says already cped this file!
    ### glibc-locale-source is already installed

    ### os.system("yum -y install glibc-langpack-en") ######### glibc-locale-source is already installed

#   Modify OS release information (optional)
    #os.system(f"sudo sed -i '/^NAME/ s/Fedora Linux/Fedora Linux (ashos)/' /mnt/etc/os-release")
    #os.system(f"sudo sed -i '/PRETTY_NAME/ s/Fedora Linux/Fedora Linux (ashos)/' /mnt/etc/os-release")
    os.system(f"sudo sed -i '/^ID/ s/{distro}/{distro}_ashos/' /mnt/etc/os-release")
    #os.system("echo 'HOME_URL=\"https://github.com/astos/astos\"' | sudo tee -a /mnt/etc/os-release")

#   GRUB and EFI
#   REALLY ANNOYING BUG: https://bugzilla.redhat.com/show_bug.cgi?id=1917213 & https://fedoraproject.org/wiki/GRUB_2#Instructions_for_UEFI-based_systems
    #os.system(f"chroot /mnt /usr/sbin/grub2-install {args[2]}") #REZA --recheck --no-nvram --removable (not needed for Fedora on EFI)
    # if dnf reinstall shim-* grub2-efi-* grub2-common return an exitcode of error (excode != 0), run dnf install shim-x64 grub2-efi-x64 grub2-common
...
    os.system(f"sudo sed -i '0,/subvol=@{distro_suffix}/ s,subvol=@{distro_suffix},subvol=@.snapshots{distro_suffix}/rootfs/snapshot-tmp,g' /mnt/boot/loader/entries/*")
    # Create a symlink to the newest systemd-boot entry
    os.system(f"sudo ln -sf /mnt/boot/loader/entries/`ls -rt /mnt/boot/loader/entries | tail -n1` /mnt/boot/loader/entries/current.cfg") ###REVIEW_LATER I think without sudo can't create



#   Database
    #os.system("if [ ! -L /usr/lib/sysimage/rpm/rpmdb.sqlite || -L /var/lib/rpm ]; then \
    #           mv /usr/lib/sysimage/rpm/* /var/lib/rpm/")



#### grubby shim-x64
#grub2-common grub2-tools-minimal grub2-tools-efi os-prober grub2-tools grub2-efi-x64

#  efibootmgr -c -d /dev/sda -p 1 -L "Fedora" -l '\EFI\fedora\grubx64.efi'

#args = list(sys.argv)
#distro="fedora"
#main(args, distro)


#   Unmount everything
    os.system(f"sudo mount {args[1]} -o subvolid=0 /mnt") # subvolid=5 needed for any cases?













--------------------------------------------------------------------

#   Initialize fstree
    os.system("echo {\\'name\\': \\'root\\', \\'children\\': [{\\'name\\': \\'0\\'}]} | sudo tee /mnt/.snapshots/ast/fstree")

#######
    input("breakpoint1 before grub check if any entries in /boot/grub2/grub.cfg>") ### YES THERE IS BUT IT IS GENERIC ONE WITHOUT ANY Fedora entry in 10_linux section or anywhere!
#######

#   GRUB and EFI (For now I use non-BLS format. Entries go in /boot/grub2/grub.cfg not in /boot/loader/entries/)

--------------------------------------------------------------------

    if efi:
        if not os.path.exists("/mnt/boot/efi/EFI/map.txt"):
            os.system("echo DISTRO,BootOrder | sudo tee /mnt/boot/efi/EFI/map.txt")
#######
        input("breakpoint2 before creating efi entry. was it automatically created? >") ### NO Fedora efi entry is created yet!
#######
        os.system(f"efibootmgr -c -d {args[2]} -p 1 -L 'Fedora' -l '\\EFI\\fedora\\shim.efi'") ###REVIEW_LATER shim.efi vs shimx64.efi ### CAN I REMOVE THIS?
        os.system(f"echo '{distro},' $(efibootmgr -v | grep -i {distro} | awk '"'{print $1}'"' | sed '"'s/[^0-9]*//g'"') | tee -a /mnt/boot/efi/EFI/map.txt")

--------------------------------------------------------------------

