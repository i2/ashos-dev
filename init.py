#!/usr/bin/python3

import sys
import subprocess

args = list(sys.argv)
distro = str(subprocess.check_output(['sh', './src/distros/detect.sh']))
distro.replace("b'","").replace('"',"").replace("\\n'","")

if 'debian' in distro:
    from src.distros.debian import installeryolo
elif 'arch' in distro:
    from src.distros.arch import installeryolo

installeryolo.main(args)

