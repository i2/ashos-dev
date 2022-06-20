#!/usr/bin/python3

import sys
import subprocess

args = list(sys.argv)

def detect_distro():
    dname = str(subprocess.check_output(['sh', './src/distros/detect.sh']))
    return dname.replace("b'","").replace('"',"").replace("\\n'","")

def main():
    if 'debian' in dname:
        from src.distro.debian import installer
    elif 'arch' in dname:
        from src.distro.arch import installer

    installer.main(args)

main()

