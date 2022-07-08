#!/usr/bin/sh
sudo mkdir /mnt/sda4
sudo mount /dev/sda4 /mnt/sda4
sudo mount /dev/sda1 /mnt/sda4/boot/efi
sudo mount --bind /dev /mnt/sda4/dev
sudo mount --bind /proc /mnt/sda4/proc
sudo mount --bind /sys /mnt/sda4/sys
sudo mount --bind /sys/firmware/efi/efivars /mnt/sda4/sys/firmware/efi/efivars
sudo chroot /mnt/sda4 efivar -l
sudo chroot /mnt/sda4 grub2-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=Fedora --recheck --debug
sudo chroot /mnt/sda4 grub2-mkconfig -o /boot/grub2/grub.cfg
# ---
sudo umount /mnt/sda4/sys/firmware/efi/efivars
sudo umount /mnt/sda4/sys
sudo umount /mnt/sda4/proc
sudo umount /mnt/sda4/dev
sudo umount /mnt/sda4/boot/efi
sudo umount /mnt/sda4
