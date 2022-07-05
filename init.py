#!/usr/bin/python3

import sys
import subprocess

args = list(sys.argv)

if args[3]:
    distro = args[3]
else:
    distro = subprocess.check_output(['sh', './src/detect_os.sh']).decode('utf-8').replace('"',"").strip()

if 'debian' in distro:
    from src.distros.debian import installer
elif 'arch' in distro:
    from src.distros.arch import installer
elif 'fedora' in distro:
    from src.distros.fedora import step1

installer.main(args, distro)

