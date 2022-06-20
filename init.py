#!/usr/bin/python3

import sys
import subprocess

args = list(sys.argv)

dname = str(subprocess.check_output(['sh', './src/distros/detect.sh']))
dname.replace("b'","").replace('"',"").replace("\\n'","")

def main():
    if 'debian' in dname:
        from src.distros.debian import installer
    elif 'arch' in dname:
        from src.distros.arch import installer

    installer.main(args)

main()

