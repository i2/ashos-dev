tmp_efi=$(cat /dev/urandom | od -x | tr -d ' ' | head -n 1)
mkdir /tmp/$tmp_efi
mount /dev/sda1 /tmp/$tmp_efi
cp /tmp/$tmp_efi/EFI/$distro_ashos/

umount /dev/sda1
