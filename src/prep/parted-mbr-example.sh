#!/bin/sh

sudo parted --align minimal --script $1 mklabel msdos unit MiB mkpart primary \
            ext4 1MiB 80% set 1 boot on mkpart primary ext4 80% 100%
#sudo mkfs.ext4 -L MBR ${1}1

