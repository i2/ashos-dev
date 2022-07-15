#!/usr/bin/python3
#
import sys
import subprocess

args = list(sys.argv)
distro = subprocess.check_output(['sh', './src/detect_os.sh']).decode('utf-8').replace('"',"").strip()
#distro = "fedora" # Use this if using archiso just to bootstrap another distro

if 'arch' in distro:
    from src.distros.arch import installer
elif 'debian' in distro:
    from src.distros.debian import installer
elif 'fedora' in distro:
    from src.distros.fedora import installer
elif 'gentoo' in distro:
    from src.distros.gentoo import installer
elif 'ubuntu' in distro:
    from src.distros.ubuntu import installer

installer.main(args, distro)

