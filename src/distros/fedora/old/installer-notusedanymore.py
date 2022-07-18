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

#### grubby shim-x64
#grub2-common grub2-tools-minimal grub2-tools-efi os-prober grub2-tools grub2-efi-x64

#  efibootmgr -c -d /dev/sda -p 1 -L "Fedora" -l '\EFI\fedora\grubx64.efi'

#args = list(sys.argv)
#distro="fedora"
#main(args, distro)
