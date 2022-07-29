#!/usr/bin/python3

import importlib
import subprocess
import sys

args = list(sys.argv[0:4])

try: # If distro to be installed does not match live environment, use argument 4
    distro = sys.argv[4]
except IndexError:
    distro = subprocess.check_output(['sh', './src/detect_os.sh']).decode('utf-8').replace('"',"").strip()

importlib.import_module(f"src.distros.{distro}.installer").main(args, distro)

