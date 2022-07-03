    os.system("pacstrap /mnt base linux neovim btrfs-progs grub sudo os-prober")
    os.system("pacstrap /mnt base linux neovim python3 python-anytree arch-install-scripts btrfs-progs grub sudo os-prober tmux")

    # THESE 3 lines were not right, I don't know why archashos was still working!!!!!??????
    #os.system(f"sed -i '0,/@{distro_suffix}/ s,@,@{distro_suffix}.snapshots/rootfs/snapshot-tmp,' /mnt/etc/fstab")
    #os.system(f"sed -i '0,/@boot{distro_suffix}/ s,@boot{distro_suffix},@.snapshots{distro_suffix}/boot/boot-tmp,' /mnt/etc/fstab")
    #os.system(f"sed -i '0,/@etc{distro_suffix}/ s,@etc{distro_suffix},@.snapshots{distro_suffix}/etc/etc-tmp,' /mnt/etc/fstab")

#   GRUB
#######    if multiboot: # if there is already a grub efi/cfg in /dev/sda1 #TODO for bios systems
        #create tmp dir for mounting /dev/sda2 #(assumingly has OS and default subvol is the last OS booting)

#######        prev_distro = subprocess.check_output(['sh', '/usr/local/sbin/detect_os.sh /tmp/s']).decode('utf-8').replace('"',"").strip()

#######        os.system(f"mv /mnt/boot/efi/ashos /mnt/boot/efi/ashos_BAK") #TODO: Get name of previous installed distro from user or use detect_os.sh
###    if choice == "3":   # COULD BE BETTER TO CHECK FOR EXISTENCE OF 'ashos' in /dev/sda1
    if choice == "3":   # COULD BE BETTER TO CHECK FOR EXISTENCE OF 'default.txt' content in /dev/sda1
        try:
            prev_os_grub = subprocess.check_output("cat /mnt/boot/efi/EFI/default.txt", shell=True).decode('utf-8').strip()
        except:
            print("No previous OS grub found!")
        else:
            os.system(f"mv /mnt/boot/efi/EFI/{prev_os_grub} /mnt/boot/efi/EFI/{prev_os_grub}_ashos")
.
.
.
#        if previous_os:
###        print("#detect name of previous distro that's mounted at default subvolume")
###        pdistro = astpk.detect_previous_distro(args[1])
###        print(f"name of previous default distro is: {pdistro}")
###        #pdistro = subprocess.check_output(['sh', './src/detect_os.sh']).decode('utf-8').replace('"',"").strip()
###        print("rename ashos grub")
###        astpk.rename_ashos_grub(args[3], pdistro)

    os.system(f"chroot /mnt sed -i s,Arch,AshOS Arch,g /etc/default/grub")  ##### REZA IS THIS WHY GRUB FILES ARE NOT CREATED IN /dev/sda1 ? It doesn't make an issue for Arch!
###    os.system(f"chroot /mnt grub-install --bootloader-id=ashos {args[2]}") #REZA --recheck --no-nvram --removable

###    # MAYBE do some extra operations here if multiboot?!
.
.
.
#   GRUB and EFI - Backup and create default entry txt
    os.system(f"chroot /mnt sed -i s,Arch,AshOS Arch,g /etc/default/grub")
.
.
.
### NOT NEEDED AS I'M GOINGTO USE efibootmgr inside astpk.py
###    try:
###        now_os_grub = subprocess.check_output("find /mnt/boot/efi/EFI/ -mindepth 1 -maxdepth 1 -type \
###        d -name '*ashos*' -o -name '*default*' -prune -o -exec basename {} \; | \
###        sudo tee /mnt/boot/efi/EFI/default.txt", shell=True).decode('utf-8').strip()
###    except:
###        print("An exception occurred!")
###    os.system(f"chroot /mnt cp -a /boot/efi/EFI/ashos /boot/efi/EFI/ashos{distro_suffix}.BAK")
###    os.system(f"chroot /mnt cp -a /boot/grub /boot/grub{distro_suffix}.BAK")
###    else:
###        os.system(f"chroot /mnt cp -a /boot/efi/EFI/{now_os_grub} /boot/efi/EFI/{now_os_grub}.BAK")
###        #os.system(f"chroot /mnt cp -a /boot/grub /boot/grub{distro_suffix}.BAK")
###        os.system(f"chroot /mnt cp -a /boot/grub /boot/grub{distro_suffix}_ashos.BAK")
###        #.BAK file and folders are strictly for user's 'manual intervention' if things go wrong. They won't be used in the algorithm.

###    # Copy GOOD grub.cfg (the reference one) and maybe grubx64.efi from sda2 to sda1
### os.system(f"sed -i 's/UUID/{to_uuid(args[1])}/' -i 's/BOOT/boot{distro_suffix}/' /mnt/boot/efi/EFI/ashos/grub.cfg") #MAKE SURE THIS IS THE ONE IN /dev/sda1 not sda2
### os.system("cp /mnt/boot/e /mnt/boot/efi/EFI/ashos/ "
###

    if efi: # Create a map.txt file "distro" <=> "BootOrder number"
        os.system(f"chroot /mnt echo {distro} === $(efibootmgr -v | grep '{distro}') | tee -a /mnt/boot/efi/EFI/map.txt") # will throw error: efibootmgr not found (it does get installed already by packages above) and even if installed (check when booted in snapshot?), when you are inside a chroot of next_distro it would give error that efi variable not supported on this system!

#   Copy astpk
###    os.system("chroot /mnt chmod a+x /usr/sbin/ast /usr/bin/detect_os.sh") # Might not be necessary by 'cp -a'




#DO NOT mount /tmp to /mnt/tmp!!! THIS CAUSE EFIVAR NOT SUPPORTED ISSUE and system not bootable.
### for i in ("/dev", "/dev/pts", "/proc", "/run", "/sys", "/sys/firmware/efi/efivars /tmp"):
