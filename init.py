#!/usr/bin/python3

import sys
import subprocess

args = list(sys.argv)
distro = str(subprocess.check_output(['sh', './src/distros/detect.sh']))
distro.replace("b'","").replace('"',"").replace("\\n'","")

if 'debian' in distro:
    from src.distros.debian import installer
elif 'arch' in distro:
    from src.distros.arch import installer

installer.main(args)

