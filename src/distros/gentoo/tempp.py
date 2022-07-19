import os
ARCH="amd64"

tmp1 = f"http://distfiles.gentoo.org/releases/{ARCH}/autobuilds/"
tmp2 = subprocess.check_output(f'curl -L {tmp1}latest-stage3.txt | grep -i systemd | grep -Ev "multi | \
                                 desktop" | awk '"'{print $1}'"'', shell=True).decode('utf-8').strip()
os.system(f"curl -L -O {tmp1}{tmp2} --output-dir /mnt")
#os.system("mount -o bind /proc /mnt/proc")
os.system(f"tar --numeric-owner --xattrs -xvJpf stage3-*.tar.xz -C /mnt")

