#!/bin/sh

sudo parted --align minimal --script $1 mklabel msdos unit MiB mkpart primary \
            ext4 1MiB 256 set 1 boot on mkpart primary ext4 256 20% mkpart primary ext4 20% 100%
sudo /usr/sbin/mkfs.ext4 -L MBR ${1}1

