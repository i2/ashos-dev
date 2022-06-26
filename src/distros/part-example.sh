#!/bin/sh

sudo parted --align minimal --script $1 mklabel gpt unit MiB mkpart ESP fat32 0% 256 set 1 boot on mkpart primary ext4 256 20% mkpart primary ext4 20% 40%
sudo /usr/sbin/mkfs.vfat -F32 -n EFI ${1}1

