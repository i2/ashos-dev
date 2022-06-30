#!/usr/bin/python3

import sys
import subprocess

args = list(sys.argv)
distro = subprocess.check_output(['sh', './src/detect_os.sh']).decode('utf-8').replace('"',"").strip()

if 'debian' in distro:
    from src.distros.debian import installer
elif 'arch' in distro:
    from src.distros.arch import installer

installer.main(args, distro)

