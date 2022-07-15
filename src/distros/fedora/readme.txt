sudo dnf makecache --refresh
sudo dnf -y install supermin

 […]# dnf --releasever=35 --best --setopt=install_weak_deps=False --installroot=/var/lib/machines/{CTNAME}/ \
install dhcp-client dnf fedora-release glibc glibc-langpack-en glibc-langpack-de iputils less ncurses passwd systemd systemd-networkd systemd-resolved vim-default-editor
F34 installs 165 packages (247M) and allocates 557M in the file system. F35 installs 174 packages (270M) and allocates 527M in the file system.

might have to supplement all chroot /mnt with chroot /mnt /bin/bash as arch iso that i;m reading from has zsh but fedora bootstrap has dnf



/etc/hostname was hostrez in fedora tha I doubt I set. Did it spill ober from oyerh disreos?

-----------------------


$ sudo usermod -aG wheel username


----------------------------

Do not use the grub2-install command on UEFI systems. On those systems, bootloaders are in the shim and grub-efi RPM packages. By reinstalling those packages, the bootloaders are reinstalled to their proper location in /boot/efi/ on the EFI System volume.

----------------------------


FYI, you don't need grub2-install for EFI systems, it makes no sense.  

1. Generate the grub.cfg file in the correct place (e.g. /boot/efi/EFI/<DISTRO NAME>)
2. Tell the efi where it is, e.g.

efibootmgr -c -d  /dev/<part>  -p 1 -L <OS name, e.g. centos> -l '\EFI\BOOT/BOOTX64.efi'.

Pb

----------------

The problem to solve is: on UEFI, grub2-install results in the Fedora signed grub$arch.efi file being silently replaced with a non-signed version (that also has rather different behaviors than the signed one) resulting in user confusion and boot failure when Secure Boot is enabled

In order to properly install the bootloader on UEFI:
a. An RPM -V verified copy of grub$arch.efi needs to be in /usr/lib/grub
b. Copy /usr/lib/grub/grub$arch.efi and /usr/lib/grub/$arch modules (if present) to the user specified destination; or to /boot/efi/EFI/fedora if not specified

@rharwood any opinion on doing this instead of --force? And then also reverting the "grub2-install: error: this utility cannot be used for EFI platforms because it does not support UEFI Secure Boot" patch?

---------------

Eugene, grub2-install shouldn't be used on any (U)EFI computers. The correct procedure for reinstalling the bootloaders on Macs and other (U)EFI computers is:

sudo dnf reinstall shim-* grub2-*

Fedora 33 and older:
sudo grub2-mkconfig -o /boot/efi/EFI/fedora/grub.cfg

Fedora 34 and newer:
sudo grub2-mkconfig -o /boot/grub2/grub.cfg

In the usual case, none of this should be necessary anymore because grub.cfg is static and unchanging. The real bootloader configuration files when kernels are added/removed are located in /boot/loader/entries/.

For the case of buggy firmware corrupting NVRAM entries, instead of using grub2-install, use efibootmgr --bootorder to make sure the correct boot entry you want (for Fedora's shim) has its boot entry number listed first in boot order. If the entry is missing, you can find the proper command to use with 'grep efibootmgr /var/log/anaconda/storage.log' remembering to add an extra \ character to escape the ones found in the log.

In very unusual cases, some specific use cases might need GRUB modules not included in the Fedora pre-created grubx64.efi file; in that case there is a separate modules package to install and copy the modules into the correct location, rather than using grub2-install.



------------------------
Distros would say one USB stick per installer image. They're not designed to share a flash drive.

But, distro specific bootloaders and configs in their own EFI/ directory, and using the firmware boot manager to choose which distro boots. That'd work reliably whether UEFI Secure Boot is enabled or not. 

I don't see what this use case has to do with grub2-install though. What does a grub2-install grubx64.efi do that Fedora's grubx64.efi can't do. Any modules that aren't in the Fedora grubx64.efi can be loaded by grub.cfg insmod command, and making sure the proper grub2-efi-$ARCH-modules packages is installed, and the modules you need are copied to the distro specific directory/$ARCH/*mod
------------------------

I ran through all these comments but in order to build a bootable usb installer, I had to do the following for fedora 33:

https://gresch.io/2019/05/fedora-30-when-grub2-mkconfig-doesnt-work/

sed -i 's/GRUB_ENABLE_BLSCFG=true/GRUB_ENABLE_BLSCFG=false/' /etc/default/grub

#prepare to reinstall grub
mkdir -p /boot/efi/EFI/fedora
dnf reinstall grub2* shim*

# generate the grub.cfg
grub2-mkconfig -o boot/efi/EFI/fedora/grub.cfg

# Note: this should be outputting linuxefi /vmlinuz... it doesn't, so fix it.
sed -i 's/linux\s\/vml/linuxefi \/vml/g' boot/efi/EFI/fedora/grub.cfg

No need to grub2-install.  That is all.


--------------
