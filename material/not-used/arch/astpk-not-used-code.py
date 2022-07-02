def switch_distro_OLDEST(p, next_distro):
    # Move grub and efi
    tmp_efi= subprocess.check_output("cat /dev/urandom | od -x | tr -d ' ' | head -n 1", shell=True).decode('utf-8').strip()
    os.system(f"mkdir /tmp/{tmp_efi}")
    os.system(f"mount /dev/{p} /tmp/{tmp_efi}")
    os.system(f"mv /tmp/{tmp_efi}/boot/efi/EFI/ashos /tmp/{tmp_efi}/boot/efi/EFI/ashos{distro}")
    os.system(f"mv /tmp/{tmp_efi}/boot/efi/EFI/ashos_{next_distro} /tmp/{tmp_efi}/boot/efi/EFI/ashos")
    os.system(f"umount /tmp/{tmp_efi}")
    tmp_efi= subprocess.check_output("cat /dev/urandom | od -x | tr -d ' ' | head -n 1", shell=True).decode('utf-8').strip()
    os.system(f"mkdir /tmp/{tmp_efi}")
    os.system(f"mount /dev/{p} /tmp/{tmp_efi}")
    os.system(f"mv /mnt/boot/grub /mnt/boot/grub{distro}")
    os.system(f"mv /mnt/boot/grub_{next_distro} /mnt/boot/grub")

def switch_distro_OLDER(p):
    # Move grub and efi
    # Look in /mnt/boot/efi/EFI/ for folders with 'ashos' in their name, present them as options to user
###    next_distro_options = subprocess.check_output("find /mnt/boot/efi/EFI/ -mindepth 1 -maxdepth 1 -type \
###        d -name '*ashos*' -o -exec basename {} \;", shell=True).decode('utf-8').strip()
    while True:
        print("Type the name of a distro to switch to: (type 'list' to list them)")
        next_distro = input("> ")
        if next_distro == "q":
            break
        elif next_distro == "list":
            os.system("ls /boot/efi/EFI/ | grep -i 'ashos' | sed 's/_ashos//' | less")
        elif os.path.exists(f"/boot/efi/EFI/{next_distro}_ashos"):
            os.system(f"mv /boot/grub /boot/grub{distro}_ashos")
            os.system(f"mv /boot/grub{next_distro}_ashos /boot/grub")
            os.system(f"mv /boot/efi/EFI/{distro} /boot/efi/EFI/{distro}_ashos")
            os.system(f"mv /boot/efi/EFI/{next_distro}_ashos /boot/efi/EFI/{next_distro}")
            os.system(f"echo {next_distro} >> /boot/efi/EFI/default.txt")
            break
        else:
            print("Invalid distro!")
            continue

def switch_distro_OLX(next_distro):
    import csv
    
    with open('/home/me/Downloads/meeeeeeeeeeeee/awk-test.txt', 'r') as f:
        input_file = csv.DictReader(f, delimiter=',', quoting=csv.QUOTE_NONE)
        for row in input_file:
            if row["DISTRO"] == next_distro:
                return row["BootOrder"]

def choose_distro_to_switch_OLDER():
    import csv
    with open('/home/me/Downloads/meeeeeeeeeeeee/awk-test.txt','r') as f:
    data = list( csv.reader(f, delimiter ="=") )
    while True:
        print("Type the name of a distro to switch to: (type 'list' to list them)")
        next_distro = input("> ")
        if next_distro == "q":
            break
        elif next_distro == "list":
            os.system("cat /boot/efi/EFI/map.txt | awk 'BEGIN { FS = "'"'" === "'"'" } ; { print $1 }' | less")
        elif next_distro in subprocess.check_output("cat /boot/efi/EFI/map.txt | awk 'BEGIN { FS = "'"'" === "'"'" } ; { print $1 }'", shell=True).decode('utf-8').strip():
            return subprocess.check_output(f"cat /boot/efi/EFI/map.txt | grep {next_distro}' | awk '{{print $(NF)}}'", shell=True)
            break
        else:
            print("Invalid distro!")
            continue

def choose_distro_to_switch_OLDEST():
    while True:
        print("Type the name of a distro to switch to: (type 'list' to list them)")
        next_distro = input("> ")
        if next_distro == "q":
            break
        elif next_distro == "list":
            os.system("cat /boot/efi/EFI/map.txt | awk 'BEGIN { FS = "'"'" === "'"'" } ; { print $1 }' | less")
        elif next_distro in subprocess.check_output("cat /boot/efi/EFI/map.txt | awk 'BEGIN { FS = "'"'" === "'"'" } ; { print $1 }'", shell=True).decode('utf-8').strip():
            return subprocess.check_output(f"cat /boot/efi/EFI/map.txt | grep {next_distro}' | awk '{{print $(NF)}}'", shell=True)
            break
        else:
            print("Invalid distro!")
            continue

    os.system(f"mv /tmp/{tmp_efi}/boot/efi/EFI/ashos /tmp/{tmp_efi}/boot/efi/EFI/ashos{distro}")
    os.system(f"mv /tmp/{tmp_efi}/boot/efi/EFI/ashos_{next_distro} /tmp/{tmp_efi}/boot/efi/EFI/ashos")
    os.system(f"umount /tmp/{tmp_efi}")
    tmp_efi= subprocess.check_output("cat /dev/urandom | od -x | tr -d ' ' | head -n 1", shell=True).decode('utf-8').strip()
    os.system(f"mkdir /tmp/{tmp_efi}")
    os.system(f"mount /dev/{p} /tmp/{tmp_efi}")
    os.system(f"mv /mnt/boot/grub /mnt/boot/grub{distro}")
    os.system(f"mv /mnt/boot/grub_{next_distro} /mnt/boot/grub")

### #   Rename grub in sda1 from default ashos to pdistro_ashos
### def rename_ashos_grub(p, pd):
###     tmp_efi= subprocess.check_output("cat /dev/urandom | od -x | tr -d ' ' | head -n 1", shell=True).decode('utf-8').strip()
###     os.system(f"mkdir /tmp/{tmp_efi}")
###     os.system(f"mount /dev/{p} /tmp/{tmp_efi}")
###     #os.system(f"mkdir /tmp/{tmp_efi}/ashos")
###     #os.system(f"cp -r /tmp/{tmp_efi}/EFI/${d}_ashos/")
###     #os.system(f"mkdir /tmp/{tmp_efi}/ashos_{pd}") #THIS IS REDUNDANT as cp -a creates the dest folder even if doesn't exist
###     #os.system(f"cp -a /tmp/{tmp_efi}/EFI/ashos/. /tmp/{tmp_efi}/EFI/ashos_{pd}/")
###     os.system(f"cp -a /tmp/{tmp_efi}/EFI/ashos /tmp/{tmp_efi}/EFI/ashos_{pd}")
###     os.system(f"umount /tmp/{tmp_efi}")
###     #os.system(f"rm -rf /tmp/{tmp_efi}") ##if successful umount ( check result of 'echo $?' )

############# BOTH WHEN INSTALLING ASHOS / UPDATING AKA DEPLOYING FROM AST, CREATE A BACKUP OF FILES
############# sudo mv /tmp/{tmp_efi}/EFI/ashos/grub.cfg /tmp/{tmp_efi}/EFI/ashos/grub.cfg{DISTRO}
############# sudo mv /tmp/{tmp_efi}/EFI/ashos/grubx64.efi /tmp/{tmp_efi}/EFI/ashos/grubx64.efi{DISTRO}
############# sudo mv /tmp/{tmp_efi}/EFI/ashos/grub{NEXTDISTRO}.cfg /tmp/{tmp_efi}/EFI/ashos/grub.cfg
############# sudo mv /tmp/{tmp_efi}/EFI/ashos/grubx64.efi{NEXTDISTRO} /tmp/{tmp_efi}/EFI/ashos/grubx64.efi

#IF THE GRUB IN INSTALLER OF A DISTRO DIDN'T CREATE {THAT "REFERENCE" grub.cfg} in /dev/sda1 (for example arch doesn't -- maybe it creates it in /dev/sda2 ???? double check!)
# CREATE IT FROM MY CACHE (either store in astpk.py or installer.py as a paragraph) and copy it over to /tmp/{tmp_efi}/EFI/ashos/ as grub.cfg


def detect_previous_distro(p):
    tmp_sda2 = subprocess.check_output("cat /dev/urandom | od -x | tr -d ' ' | head -n 1", shell=True).decode('utf-8').strip()
    os.system(f"mkdir /tmp/{tmp_sda2}")
    os.system(f"mount /dev/{p} /tmp/{tmp_sda2}")
    pd = subprocess.check_output(['sh', f'detect_os.sh /tmp/{tmp_sda2}/']).decode('utf-8').replace('"',"").strip()
    os.system(f"umount /tmp/{tmp_sda2}")
    return pd
    #os.system(f"rm -rf /tmp/{tmp_sda2}") ##if successful umount ( check result of 'echo $?' )

def rename_distro_subvolumes(p):  ### Maybe can reuse ast functions from cuberjan3? #potentially receive 3 arguments: partition, string1 (suffix right now) and string2 (desired suffix)
    tmp_sda2 = subprocess.check_output("cat /dev/urandom | od -x | tr -d ' ' | head -n 1", shell=True).decode('utf-8').strip()
###     os.system(f"mkdir /tmp/{tmp_sda2}")
###     os.system(f"mount -o subvolid=5 /dev/{p} /tmp/{tmp_sda2}")
    for i in ["@.snapshots", "@boot", "@etc", "@home", "var"]:
        os.system(f'mv "/tmp/{tmp_sda2}/{i}" "/tmp/{tmp_sda2}/{i}_{d}"')
###     pd = subprocess.check_output(['sh', f'detect_os.sh /tmp/{tmp_sda2}/']).decode('utf-8').replace('"',"").strip()
###     os.system(f"umount /tmp/{tmp_sda2}")
###     return pd
    #os.system(f"rm -rf /tmp/{tmp_sda2}") ##if successful umount ( check result of 'echo $?' )

def rename_distro_bare_grub(p, currd): # In case someone is installing on a system that was previously chosen option 1 but changed opinion
    tmp_efi= subprocess.check_output("cat /dev/urandom | od -x | tr -d ' ' | head -n 1", shell=True).decode('utf-8').strip()
    os.system(f"mkdir /tmp/{tmp_efi}")
    os.system(f"mount /dev/{p} /tmp/{tmp_efi}")
    os.system(f"sed -i 's/@boot\/grub/@boot_arch\/grub/' /tmp/{tmp_efi}/EFI/ashos/grub.cfg")
    # IS THIS A GOOD PLACE TO COPY GRUBX64.EFI AND GRUB.CFG TO /tmp/{tmp_efi} ?
    os.system(f"umount /tmp/{tmp_efi}")
    #os.system(f"rm -rf /tmp/{tmp_efi}") ##if successful umount ( check result of 'echo $?' )

