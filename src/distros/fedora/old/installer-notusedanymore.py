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
