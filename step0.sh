parted --align minimal --script /dev/sda mklabel gpt unit MiB mkpart ESP fat32 0% 256 set 1 boot on mkpart primary ext4 256 100%
mkfs.btrfs -L BTRFS /dev/sda2
sudo mkfs.vfat -F32 -n EFI /dev/sda1
