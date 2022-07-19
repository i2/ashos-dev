import os

if os.path.exists("/sys/firmware/efi"):
    efi = True
else:
    efi = False

os.system("sudo mount -o x-mount.mkdir --rbind --make-rslave /dev /mnt/dev")
os.system("sudo mount -o x-mount.mkdir --types proc /proc /mnt/proc")
os.system("sudo mount -o x-mount.mkdir --bind --make-slave /run /mnt/run")
os.system("sudo mount -o x-mount.mkdir --rbind --make-rslave /sys /mnt/sys")
if efi: # Bad idea to combine --make-[r]slave and --[r]bind ? https://unix.stackexchange.com/questions/120827/recursive-umount-after-rbind-mount
    os.system("sudo mount -o x-mount.mkdir,remount,rw --types efivarfs efivarfs /mnt/sys/firmware/efi/efivars")
