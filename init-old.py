#!/usr/bin/python3

import importlib
import subprocess
import sys

args = list(sys.argv)
distro = subprocess.check_output(['sh', './src/detect_os.sh']).decode('utf-8').replace('"',"").strip()
#distro = "fedora" # If distro to be installed does not match live environment

if 'arch' in distro:
    from src.distros.arch import installer
elif 'debian' in distro:
    from src.distros.debian import installer
elif 'fedora' in distro:
    from src.distros.fedora import installer
elif 'gentoo' in distro:
    from src.distros.gentoo import installer
elif 'ubuntu' in distro:
    from src.distros.ubuntu import installer

installer.main(args, distro)

#import importlib
#importlib.import_module(f"src.distros.{distro}.installer")


### ------------------------------------------------
#import importlib.util
#spec = importlib.util.spec_from_file_location('installer', f"src/distros/{distro}/installer.py")
#module = importlib.util.module_from_spec(spec)
#spec.loader.exec_module(module)
#module.main(args, distro)
### ------------------------------------------------


#sys.modules[module_name] = module

#from pluginX import hello
#hello()

