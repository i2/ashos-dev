# Steps: partition, format, mount root partition, debootstrap, chroot, mount-bind etc.
# modify fstab, network (/etc/{network/interfaces,resolv.conf,hostname,hosts}), cp sources.list to chroot
# apt-get update, apt-get --no-install-recommends install stuff, set locales tz,
# os.system(f"sudo debootstrap --arch {ARCH} --exclude={excl} {RELEASE} /mnt http://archive.ubuntu.com/ubuntu")

###def grub_ords(part):
###    letter =
    ###return ord(letter.lower())-ord('a'),

