#MOVEDDOWN from anytree.importer import DictImporter
#MOVEDDOWN from anytree.exporter import DictExporter
#MOVEDDOWN import anytree

#MOVEDDOWN args = list(sys.argv)
#MOVEDDOWN distro = subprocess.check_output(['sh', 'detect_os.sh']).decode('utf-8').replace('"',"").strip()

def switch_distro(p, next_distro):
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

#   Rename grub in sda1 from default ashos to pdistro_ashos
def rename_ashos_grub(p, pd):
    tmp_efi= subprocess.check_output("cat /dev/urandom | od -x | tr -d ' ' | head -n 1", shell=True).decode('utf-8').strip()
    os.system(f"mkdir /tmp/{tmp_efi}")
    os.system(f"mount /dev/{p} /tmp/{tmp_efi}")
    #os.system(f"mkdir /tmp/{tmp_efi}/ashos")
    #os.system(f"cp -r /tmp/{tmp_efi}/EFI/${d}_ashos/")

    #os.system(f"mkdir /tmp/{tmp_efi}/ashos_{pd}") #THIS IS REDUNDANT as cp -a creates the dest folder even if doesn't exist
    #os.system(f"cp -a /tmp/{tmp_efi}/EFI/ashos/. /tmp/{tmp_efi}/EFI/ashos_{pd}/")
    os.system(f"cp -a /tmp/{tmp_efi}/EFI/ashos /tmp/{tmp_efi}/EFI/ashos_{pd}")
    os.system(f"umount /tmp/{tmp_efi}")
    #os.system(f"rm -rf /tmp/{tmp_efi}") ##if successful umount ( check result of 'echo $?' )

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




                        #os.system(f'efibootmgr --bootnext {row["BootOrder"]}')
