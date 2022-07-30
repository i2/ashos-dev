# AshOS (Any Snapshot Hierarchical OS)
### An immutable tree-shaped meta-distribution using snapshots

![ashos-logo](logo.png)

---

## Table of contents
* [What is AshOS?](https://github.com/ashos/ashos#what-is-ashos)
* [AshOS compared to other similar distributions](https://github.com/ashos/ashos#ashos-compared-to-other-similar-distributions)
* [ast and astOS documentation](https://github.com/ashos/ashos#additional-documentation)
  * [Installation](https://github.com/ashos/ashos#installation)
  * [Post installation](https://github.com/ashos/ashos#post-installation-setup)
  * [Snapshot management and deployments](https://github.com/ashos/ashos#snapshot-management)
  * [Package management](https://github.com/ashos/ashos#package-management)
* [Additional documentation](https://github.com/ashos/ashos#additional-documentation)
  * [Updating the pacman keys](https://github.com/ashos/ashos#fixing-pacman-corrupt-packages--key-issues)
  * [Saving configuration changes made in /etc persistent](https://github.com/ashos/ashos#saving-configuration-changes-made-in-etc-persistent)
  * [Configuring dual boot](https://github.com/ashos/ashos#dual-boot)
  * [Updating ast itself](https://github.com/ashos/ashos#updating-ast-itself)
* [Advanced features](https://github.com/ashos/ashos#advanced-features)
  * [LUKS](https://github.com/ashos/ashos#luks)
  * [Mutability toggle](https://github.com/ashos/ashos#mutability-toggle)
  * [Debugging ast](https://github.com/ashos/ashos#debugging-ast)
* [Known bugs](https://github.com/ashos/ashos#known-bugs)
* [Contributing](https://github.com/ashos/ashos#contributing)
* [Community](https://github.com/ashos/ashos#community)
* [ToDos](https://github.com/ashos/ashos#todos)

---

## What is AshOS?

AshOS is a modern meta-distribution that:
- aims to bring immutability even to distros that do not have this very useful feature i.e. Arch Linux, Gentoo, etc.
- wraps around any Linux distribution that can be bootstrapped (pretty much any major distribution)

It was initially inspired by Arch Linux, but it uses an immutable (read-only) root filesystem.
Software is installed and configured into individual snapshot trees, which can then be deployed and booted into.
It does not invent yet another package format or package manager, but instead relies on the native package manager for instance [pacman](https://wiki.archlinux.org/title/pacman) from Arch.

Ashes are one of the oldest trees in the world and they inspired naming AshOS.

**This has several advantages:**

* Security
  * Even if running an application with eleveted permissions, it cannot replace system libraries with malicious versions
* Stability and reliability
  * Due to the system being mounted as read only, it's not possible to accidentally overwrite system files
  * If the system runs into issues, you can easily rollback the last working snapshot within minutes
  * Atomic updates - Updating your system all at once is more reliable
  * Thanks to the snapshot feature, AshOS can ship cutting edge software without becoming unstable
  * AshOS needs little maintenance, as it has a built in fully automatic update tool that creates snapshots before updates and automatically checks if the system upgraded properly before deploying the new snapshot
* Configurability
  * With the snapshots organised into a tree, you can easily have multiple different configurations of your software available, with varying packages, without any interference
  * For example: you can have a single Gnome desktop installed and then have 2 snapshots on top - one with your video games, with the newest kernel and drivers, and the other for work, with the LTS kernel and more stable software, you can then easily switch between these depending on what you're trying to do
  * You can also easily try out software without having to worry about breaking your system or polluting it with unnecessary files, for example you can try out a new desktop environment in a snapshot and then delete the snapshot after, without modifying your main system at all
  * This can also be used for multi-user systems, where each user has a completely separate system with different software, and yet they can share certain packages such as kernels and drivers
  * AshOS allows you to install software by chrooting into snapshots, therefore you can use software such as the AUR to install additional packages
  * AshOS is, very customizable, you can choose exactly which software you want to use (just like Arch Linux)

* Thanks to it's reliabilty and automatic upgrades, AshOS is well suitable for single use or embedded devices
* It also makes for a good workstation or general use distribution utilizing development containers and flatpak for desktop applications

As AshOS strives to be minimal solid and follow a LEGO like structure (start small, customize as you go), we primarily focus development on the base, meaning by default no Desktop Environment (not even Window Manager) is installed. This is by design as otherwise team has to support many DEs on many distros. What is provided is `profiles`. As DEs/WMs are just packages, with power of snapshotting, one can use ast to install the desired DE/WM.
For instance to install GNOME in snapshot 1:
```
sudo ast clone 0
sudo ast install-profile gnome 1
sudo ast deploy 1
sudo reboot
```

---
## AshOS compared to other similar distributions
* **NixOS** - compared to nixOS, AshOS is a more traditional system with how it's setup and maintained. While nixOS is entirely configured using the Nix programming language, AshOS uses the native package manager of target distribution, for instance pacman for Arch, apt-get for Debian, etc. AshOS consumes less storage, and configuring your system is faster and easier (less reproducible however), it also gives you more customization options. AshOS is FHS compliant, ensuring proper software compatability.
  * AshOS allows declarative configuration using Ansible, for somewhat similar functionality to NixOS
* **Fedora Silverblue/Kinoite** - AshOS is more customizable, but does require more manual setup. AshOS supports dual boot, unlike Silverblue.
* **OpenSUSE MicroOS** - AshOS is a more customizable system, but once again requires a bit more manual setup. MicroOS works similarly in the way it utilizes btrfs snapshots. AshOS has an official KDE install, but also supports other desktop environments, while MicroOS only properly supports Gnome. AshOS supports dual boot.

---
## Installation
* AshOS is installed from the official live iso for target distribution. For example [https://archlinux.org/download/](Arch Linux) or [https://www.debian.org/CD/http-ftp/](Debian)
* If you run into issues installing packages during installation, make sure you're using the newest iso, and update the package manager's keyring if needed
* You need an internet connection to install AshOS
* Currently AshOS ships 3 installation profiles, one for minimal installs and two for desktop, one with the Gnome desktop environment and one with KDE Plasma, but support for more DE's will be added
* The installation script is easily configurable and adjusted for your needs (but it works just fine without any modifications)

Install git first - this will allow us to download the install script

```
pacman -Sy git
```
Clone repository

```
git clone "https://github.com/ashos/ashos"
cd ashos
```
Partition and format drive

* If installing on a BIOS system, use a dos (MBR) partition table
* On EFI you can use GPT
* The EFI partition has to be formatted to FAT32 before running the installer (```mkfs.fat -F32 /dev/<part>```)
* There are prep scripts under `./src/prep/`

```
lsblk  # Find your drive name
cfdisk /dev/*** # Format drive, make sure to add an EFI partition, if using BIOS leave 2M free space before first partition
mkfs.btrfs /dev/*** # Create a btrfs filesystem, don't skip this step!
```
Run installer

```
python3 main.py /dev/<partition> /dev/<drive> /dev/<efi part> # Skip the EFI partition if installing in BIOS mode
```

## Post installation setup
* Post installation setup is not necessary if you install one of the desktop editions (Gnome or KDE)
* A lot of information for how to handle post-install setup is available on the [ArchWiki page](https://wiki.archlinux.org/title/general_recommendations)
* Here is a small example setup procedure:
  * Start by creating a new snapshot from `base` using ```ast clone 0```
  * Chroot inside this new snapshot (```ast chroot <snapshot>```) and begin setup
    * Start by adding a new user account: ```useradd username```
    * Set the user password ```passwd username```
    * Now set a new password for root user ```passwd root```
    * Now you can install additional packages (desktop environments, container technologies, flatpak) using pacman
    * Once done, exit the chroot with ```exit```
    * Then you can deploy it with ```ast deploy <snapshot>```

## Additional documentation
* It is advised to refer to the [Arch wiki](https://wiki.archlinux.org/) for documentation not part of this project
* Report issues/bugs on the [Github issues page](https://github.com/ashos/ashos/issues)
* **HINT: you can use `ast help` to get a quick cheatsheet of all available commands**

#### Base snapshot
* The snapshot ```0``` is reserved for the base system snapshot, it cannot be changed and can only be updated using ```ast base-update```

## Snapshot Management

#### Show filesystem tree

```
ast tree
```

* The output can look for example like this:

```
root - root
├── 0 - base snapshot
└── 1 - multiuser system
    └── 4 - applications
        ├── 6 - MATE full desktop
        └── 2*- Plasma full desktop
```
* The asterisk shows which snapshot is currently selected as default

* You can also get only the number of the currently booted snapshot with

```
ast current
```
#### Add descritption to snapshot
* Snapshots allow you to add a description to them for easier identification

```
ast desc <snapshot> <description>
```
#### Delete a tree
* This removes the tree and all it's branches

```
ast del <tree>
```
#### Custom boot configuration
* If you need to use a custom grub configuration, chroot into a snapshot and edit ```/etc/default/grub```, then deploy the snapshot and reboot

#### chroot into snapshot
* Once inside the chroot the OS behaves like regular Arch, so you can install and remove packages using pacman or similar
* Do not run ast from inside a chroot, it could cause damage to the system, there is a failsafe in place, which can be bypassed with ```--chroot``` if you really need to (not recommended)
* The chroot has to be exited properly with ```exit```, otherwise the changes made will not be saved
* If you don't exit chroot the "clean" way with ```exit```, it's recommended to run ```ast tmp``` to clear temporary files left behind


```
ast chroot <snapshot>
```

* You can enter an unlocked shell inside the current booted snapshot with

```
ast live-chroot
```

* The changes made to live session are not saved on new deployments

#### Other chroot options

* Runs a specified command inside snapshot

```
ast run <snapshot> <command>
```

* Runs a specified command inside snapshot and all it's branches

```
ast tree-run <tree> <command>
```

#### Clone snapshot
* This clones the snapshot as a new tree

```
ast clone <snapshot>
```
#### Create new tree branch

* Adds a new branch to specified snapshot

```
ast branch <snapshot to branch from>
```
#### Clone snapshot under same parent

```
ast cbranch <snapshot>
```
#### Clone snapshot under specified parent

* Make sure to sync the tree afterwards

```
ast ubranch <parent> <snapshot>
```
#### Create new base tree

```
ast new
```
#### Deploy snapshot

* Reboot to  boot into the new snapshot after deploying

```
ast deploy <snapshot>
```

#### Update base which new snapshots are built from

```
ast base-update
```
* Note: the base itself is located at ```/.snapshots/rootfs/snapshot-0``` with it's specific ```/var``` files and ```/etc``` being located at ```/.snapshots/var/var-0``` and ```/.snapshots/etc/etc-0``` respectively, therefore if you really need to make a configuration change, you can mount snapshot these as read-write and then snapshot back as read only

## Package management

#### Software installation
* Run ```ast deploy <snapshot>``` and reboot after installing new software for changes to apply (unless using live install, more info below)
* Software can also be installed using pacman in a chroot
* AUR can be used under the chroot
* Flatpak can be used for persistent package installation
* Using containers for additional software installation is also an option. An easy way of doing this is with [distrobox](https://github.com/89luca89/distrobox)

```
ast install <snapshot> <package>
```
* After installing you can sync the newly installed packages to all the branches of the tree with
* Syncing the tree also automatically updates all the snapshots

```
ast sync <tree>
```

* If you wish to sync without updating (could cause package duplication in database) then use

```
ast force-sync <tree>
```

* ast also supports installing packages without rebooting
```
ast install --live <snapshot> <package>
```

#### Removing software

* For a single snapshot

```
ast remove <snapshot> <package or packages>
```

* Recursively

```
ast tree-rmpkg <tree> <pacakge or packages>
```



#### Updating
* It is advised to clone a snapshot before updating it, so you can roll back in case of failure
* This update only updates the system packages, in order to update ast itself see [this section](https://github.com/ashos/ashos#updating-ast-itself)


* To update a single snapshot

```
ast upgrade <snapshot>
```
* To recursively update an entire tree

```
ast tree-upgrade <tree>
```

* This can be configured in a script (ie. a crontab script) for easy and safe automatic updates

* If the system becomes unbootable after an update, you can boot last working deployment (select in grub menu) and then perform a rollback

```
ast rollback
```

* Then you can reboot back to a working system

## Extras

#### Fixing pacman corrupt packages / key issues
* Arch's pacman package manager sometimes requires a refresh of the PGP keys
* To fix this issue we can simply reinstall they arch keyring

```
ast install <snapshots> archlinux-keyring
```

#### Saving configuration changes made in ``/etc`` persistent
* Normally configuration should be done with ``ast chroot``, but sometimes you may want to apply changes you've made to the booted system persistently
* To do this use the following command

```
ast etc-update
```

* This allows you to configure your system by modifying ``/etc`` as usual, and then saving these changes.

#### Dual boot
* AshOS supports dual boot using the GRUB bootloader
* When installing the system, use the existing EFI partition
* to configure dual boot, we must begin by installing the ```os-prober``` package:

```
ast install <snapshot> os-prober
```

* Now we have to configure grub

```
ast chroot <snapshot>
echo 'GRUB_DISABLE_OS_PROBER=false' >> /etc/default/grub
exit
```

* Now just deploy the snapshot to reconfigure the bootloader

```
ast deploy <snapshot>
```

#### Updating ast itself
* ast doesn't get updated alongside the system when `ast upgrade` is used
* sometimes it may be necessary to update ast itself
* ast can be updated with a single command

```
ast ast-sync
```

## Advanced features

These are some advanced feature and we suggest you use them only if you are ready for breakage, doing data backups and occasional fixes. They may not be prime-time ready.

#### LUKS

Full-disk encryption using LUKS2 is implemented. This means also encrypting /boot which is an experimental feature of GRUB since v2.06. Right now in mainstream, it only supports pbkdf2 and not the default argon2. This will significantly slow down booting as for example cryptomount decryption is about 30 seconds on 8kb keyfile.

#### Mutability toggle

The beauty of customizability of AshOS is that we can have a mix of immutable and non-immutable nodes!
Within the forest/tree of AshOS, one can make any snapshot (other than base `0`) mutable. For instance, to make node 9 mutable run `sudo ast immen 9`. This makes a node and any children (that are created afterwards) mutable.

#### Debugging ast

- sometimes it may be necessary to debug ast
- the following command is useful as it shows outputs of commands when running astpk.py:

```
sed -e 's| >/dev/null 2>&1||g' /usr/bin/ash > ashpk.py
```

## Known bugs

* At the end of installer if LUKS is used, there would be warning `remove ioctl device or resource busy`. They can be ignore. Most likely cause: systemd-journald
* Running ast without root permissions shows permission denied errors instead of an error message
* Swap partition doesn't work, it's recommended to use a swapfile or zram instead
* Docker has issues with permissions, to fix run
```
sudo chmod 666 /var/run/docker.sock
```

* If you run into any issues, report them on [the issues page](https://github.com/ashos/ashos/issues)

# Contributing
* Please take a look under `/src/profiles/` and add a desktop environment or windows manager if missing. Please try to be as minimal and vanilla as possible. If a package has different names in different distros (like networkmanager in Arch and network-manager in Debian, create a file with the distro suffix for the profile i.e. under gnome: packages-arch.txt vs. packages-debian.txt
* Code and documentation contributions are welcome!
* Bug reports are a good way of contributing to the project too
* Before submitting a pull request test your code and make sure to comment it properly

# Community
* Please feel free to join us on [Discord](https://discord.gg/YVHEC6XNZw) for further discussion and support!
* Happy worry-free snapshotting!

# ToDos
* A clean way to completely unistall ast
* Implement AUR package maintenance between snapshots

---

**This project is licensed under the AGPLv3.**

**Please note that, for the purpose of this project, comforming to 'pythonic' way was not a goal as in future, implementation might change to Rust, C, C++, etc. We would like to be as close to POSIX-compliant sans-bashism shell as possible.**
