#!/bin/sh

sudo parted --align minimal --script $1 mklabel msdos unit MiB mkpart primary ext3 1MiB 256 set 1 boot on mkpart primary ext3 256 20% mkpart primary ext4 20% 100%
sudo /usr/sbin/mkfs.ext4 -F32 -n EFI ${1}1

