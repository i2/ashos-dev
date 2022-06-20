#!/usr/bin/python3

import sys
import subprocess

args = list(sys.argv)

dname = str(subprocess.check_output(['sh', './src/distros/detect.sh']))
dname.replace("b'","").replace('"',"").replace("\\n'","")

def main():
    if 'debian' in dname:
        from src.distro.debian import installer
    elif 'arch' in dname:
        from src.distro.arch import installer

    installer.main(args)

main()

