#!/usr/bin/python3

import sys
import subprocess

args = list(sys.argv)
distro = subprocess.check_output(['sh', './src/distros/detect.sh']).decode('utf-8').replace('"',"").strip()

if 'debian' in distro:
    from src.distros.debian.justminimal import installery_justminimal
elif 'arch' in distro:
    from src.distros.arch import installery_justminimal

installery_justminimal.main(args, distro)

