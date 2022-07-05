#!/usr/bin/python3
#
import sys
import subprocess

args = list(sys.argv)
distro = subprocess.check_output(['sh', './src/detect_os.sh']).decode('utf-8').replace('"',"").strip() #NEW

#if args[3]:
#    distro = args[3]
#    del args[-1]
#else:
#    distro = subprocess.check_output(['sh', './src/detect_os.sh']).decode('utf-8').replace('"',"").strip()

if 'arch' in distro:
    from src.distros.arch import installer
elif 'debian' in distro:
    from src.distros.debian import installer
elif 'fedora' in distro:
    from src.distros.fedora import step1
elif 'ubuntu' in distro:
    from src.distros.ubuntu import installer

installer.main(args, distro)

