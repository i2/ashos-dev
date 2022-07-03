#!/usr/bin/python3

import sys
import ast
import subprocess
#from anytree.importer import DictImporter
#from anytree.exporter import DictExporter
#import anytree
import os
import re

args = list(sys.argv)
#distro = subprocess.check_output(['sh', '/usr/local/sbin/detect_os.sh']).decode('utf-8').replace('"',"").strip()
distro = subprocess.check_output(['sh', 'detect_os.sh']).decode('utf-8').replace('"',"").strip()

# TODO ------------
# General code cleanup
# Maybe port for other distros?
# A clean way to completely unistall ast
# Implement AUR package maintenance between snapshots
# -----------------

# Directories
# All snapshots share one /var
# global boot is always at @boot
# *-tmp - temporary directories used to boot deployed snapshot
# *-chr - temporary directories used to chroot into snapshot or copy snapshots around
# /.snapshots/var/var-* == individual /var for each snapshot
# /.snapshots/etc/etc-* == individual /etc for each snapshot
# /.snapshots/boot/boot-* == individual /boot for each snapshot
# /.snapshots/rootfs/snapshot-* == snapshots
# /root/snapshots/*-desc == descriptions
# /usr/share/ast == files that store current snapshot info
# /usr/share/ast/db == package database
# /var/lib/ast(/fstree) == ast files, stores fstree, symlink to /.snapshots/ast

#   This function returns either empty string or underscore plus name of distro if it was appended to sub-volume names to distinguish
def get_distro():
    if "ashos" in distro:
        return f'_{distro.replace("_ashos","")}'
    else:
        return ""

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

#   Import filesystem tree file in this function
def import_tree_file(treename):
    treefile = open(treename,"r")
    tree = ast.literal_eval(treefile.readline())
    return(tree)

#   Print out tree with descriptions
def print_tree(tree):
    snapshot = get_snapshot()
    for pre, fill, node in anytree.RenderTree(tree):
        if os.path.isfile(f"/.snapshots/ast/snapshots/{node.name}-desc"):
            descfile = open(f"/.snapshots/ast/snapshots/{node.name}-desc","r")
            desc = descfile.readline()
            descfile.close()
        else:
            desc = ""
        if str(node.name) == "0":
            desc = "base snapshot"
        if snapshot != str(node.name):
            print("%s%s - %s" % (pre, node.name, desc))
        else:
            print("%s%s*- %s" % (pre, node.name, desc))

#   Write new description
def write_desc(snapshot, desc):
    os.system(f"touch /.snapshots/ast/snapshots/{snapshot}-desc")
    descfile = open(f"/.snapshots/ast/snapshots/{snapshot}-desc","w")
    descfile.write(desc)
    descfile.close()

#   Add to root tree
def append_base_tree(tree,val):
    add = anytree.Node(val, parent=tree.root)

#   Add child to node
def add_node_to_parent(tree, id, val):
    par = (anytree.find(tree, filter_=lambda node: ("x"+str(node.name)+"x") in ("x"+str(id)+"x")))
    add = anytree.Node(val, parent=par)

#   Clone within node
def add_node_to_level(tree,id, val):
    npar = get_parent(tree, id)
    par = (anytree.find(tree, filter_=lambda node: ("x"+str(node.name)+"x") in ("x"+str(npar)+"x")))
    add = anytree.Node(val, parent=par)

#   Remove node from tree
def remove_node(tree, id):
    par = (anytree.find(tree, filter_=lambda node: ("x"+str(node.name)+"x") in ("x"+str(id)+"x")))
    par.parent = None

#   Save tree to file
def write_tree(tree):
    exporter = DictExporter()
    to_write = exporter.export(tree)
    fsfile = open(fstreepath,"w")
    fsfile.write(str(to_write))

#   Get parent
def get_parent(tree, id):
    par = (anytree.find(tree, filter_=lambda node: ("x"+str(node.name)+"x") in ("x"+str(id)+"x")))
    return(par.parent.name)

#   Return all children for node
def return_children(tree, id):
    children = []
    par = (anytree.find(tree, filter_=lambda node: ("x"+str(node.name)+"x") in ("x"+str(id)+"x")))
    for child in anytree.PreOrderIter(par):
        children.append(child.name)
    if id in children:
        children.remove(id)
    return (children)

#   Return order to recurse tree
def recurstree(tree, cid):
    order = []
    for child in (return_children(tree,cid)):
        par = get_parent(tree, child)
        if child != cid:
            order.append(par)
            order.append(child)
    return (order)

#   Get current snapshot
def get_snapshot():
    csnapshot = open("/usr/share/ast/snap","r")
    snapshot = csnapshot.readline()
    csnapshot.close()
    snapshot = snapshot.replace('\n',"")
    return(snapshot)

#   Get drive partition
def get_part():
    cpart = open("/.snapshots/ast/part","r")
    uuid = cpart.readline().replace('\n',"")
    cpart.close()
    part = str(subprocess.check_output(f"blkid | grep '{uuid}' | awk '{{print $1}}'", shell=True))
    return(part.replace(":","").replace("b'","").replace("\\n'",""))

#   Get tmp partition state
def get_tmp():
    mount = str(subprocess.check_output("mount | grep 'on / type'", shell=True))
    if "tmp0" in mount:
        return("tmp0")
    else:
        return("tmp")

#   Deploy snapshot
def deploy(snapshot):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{snapshot}")):
        print(f"F: cannot deploy as snapshot {snapshot} doesn't exist.")
    else:
        update_boot(snapshot)
        tmp = get_tmp()
        os.system(f"btrfs sub set-default /.snapshots/rootfs/snapshot-{tmp} >/dev/null 2>&1") # Set default volume
        untmp()
        if "tmp0" in tmp:
            tmp = "tmp"
        else:
            tmp = "tmp0"
        etc = snapshot
        os.system(f"btrfs sub snap /.snapshots/rootfs/snapshot-{snapshot} /.snapshots/rootfs/snapshot-{tmp} >/dev/null 2>&1")
        os.system(f"btrfs sub snap /.snapshots/etc/etc-{snapshot} /.snapshots/etc/etc-{tmp} >/dev/null 2>&1")
        os.system(f"btrfs sub create /.snapshots/var/var-{tmp} >/dev/null 2>&1")
        os.system(f"cp --reflink=auto -r /.snapshots/var/var-{etc}/* /.snapshots/var/var-{tmp} >/dev/null 2>&1")
        os.system(f"btrfs sub snap /.snapshots/boot/boot-{snapshot} /.snapshots/boot/boot-{tmp} >/dev/null 2>&1")
        os.system(f"mkdir /.snapshots/rootfs/snapshot-{tmp}/etc >/dev/null 2>&1")
        os.system(f"rm -rf /.snapshots/rootfs/snapshot-{tmp}/var >/dev/null 2>&1")
        os.system(f"mkdir /.snapshots/rootfs/snapshot-{tmp}/boot >/dev/null 2>&1")
        os.system(f"cp --reflink=auto -r /.snapshots/etc/etc-{etc}/* /.snapshots/rootfs/snapshot-{tmp}/etc >/dev/null 2>&1")
        os.system(f"btrfs sub snap /var /.snapshots/rootfs/snapshot-{tmp}/var >/dev/null 2>&1")
        os.system(f"cp --reflink=auto -r /.snapshots/boot/boot-{etc}/* /.snapshots/rootfs/snapshot-{tmp}/boot >/dev/null 2>&1")
        os.system(f"echo '{snapshot}' > /.snapshots/rootfs/snapshot-{tmp}/usr/share/ast/snap")
        switchtmp()
        os.system(f"rm -rf /var/lib/systemd/* >/dev/null 2>&1")
        os.system(f"rm -rf /.snapshots/rootfs/snapshot-{tmp}/var/lib/systemd/* >/dev/null 2>&1")
        os.system(f"cp --reflink=auto -r /.snapshots/var/var-{etc}/* /.snapshots/rootfs/snapshot-{tmp}/var/ >/dev/null 2>&1")
        os.system(f"cp --reflink=auto -r /.snapshots/var/var-{etc}/lib/systemd/* /var/lib/systemd/ >/dev/null 2>&1")
        os.system(f"cp --reflink=auto -r /.snapshots/var/var-{etc}/lib/systemd/* /.snapshots/rootfs/snapshot-{tmp}/var/lib/systemd/ >/dev/null 2>&1")
        os.system(f"btrfs sub set-default /.snapshots/rootfs/snapshot-{tmp}") # Set default volume
        print(f"Snapshot {snapshot} deployed to /.")

#   Add node to branch
def extend_branch(snapshot, desc=""):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{snapshot}")):
        print(f"F: cannot branch as snapshot {snapshot} doesn't exist.")
    else:
        i = findnew()
        os.system(f"btrfs sub snap -r /.snapshots/rootfs/snapshot-{snapshot} /.snapshots/rootfs/snapshot-{i} >/dev/null 2>&1")
        os.system(f"btrfs sub snap -r /.snapshots/etc/etc-{snapshot} /.snapshots/etc/etc-{i} >/dev/null 2>&1")
        os.system(f"btrfs sub snap -r /.snapshots/var/var-{snapshot} /.snapshots/var/var-{i} >/dev/null 2>&1")
        os.system(f"btrfs sub snap -r /.snapshots/boot/boot-{snapshot} /.snapshots/boot/boot-{i} >/dev/null 2>&1")
        add_node_to_parent(fstree,snapshot,i)
        write_tree(fstree)
        if desc: write_desc(i, desc)
        print(f"Branch {i} added under snapshot {snapshot}.")

#   Clone branch under same parent,
def clone_branch(snapshot):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{snapshot}")):
        print(f"F: cannot clone as snapshot {snapshot} doesn't exist.")
    else:
        i = findnew()
        os.system(f"btrfs sub snap -r /.snapshots/rootfs/snapshot-{snapshot} /.snapshots/rootfs/snapshot-{i} >/dev/null 2>&1")
        os.system(f"btrfs sub snap -r /.snapshots/etc/etc-{snapshot} /.snapshots/etc/etc-{i} >/dev/null 2>&1")
        os.system(f"btrfs sub snap -r /.snapshots/var/var-{snapshot} /.snapshots/var/var-{i} >/dev/null 2>&1")
        os.system(f"btrfs sub snap -r /.snapshots/boot/boot-{snapshot} /.snapshots/boot/boot-{i} >/dev/null 2>&1")
        add_node_to_level(fstree,snapshot,i)
        write_tree(fstree)
        desc = str(f"clone of {snapshot}")
        write_desc(i, desc)
        print(f"Branch {i} added to parent of {snapshot}.")

#   Clone under specified parent
def clone_under(snapshot, branch):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{snapshot}")) or (not(os.path.exists(f"/.snapshots/rootfs/snapshot-{branch}"))):
        print(f"F: cannot clone as snapshot {snapshot} doesn't exist.")
    else:
        i = findnew()
        os.system(f"btrfs sub snap -r /.snapshots/rootfs/snapshot-{branch} /.snapshots/rootfs/snapshot-{i} >/dev/null 2>&1")
        os.system(f"btrfs sub snap -r /.snapshots/etc/etc-{branch} /.snapshots/etc/etc-{i} >/dev/null 2>&1")
        os.system(f"btrfs sub snap -r /.snapshots/var/var-{branch} /.snapshots/var/var-{i} >/dev/null 2>&1")
        os.system(f"btrfs sub snap -r /.snapshots/boot/boot-{branch} /.snapshots/boot/boot-{i} >/dev/null 2>&1")
        add_node_to_parent(fstree,snapshot,i)
        write_tree(fstree)
        desc = str(f"clone of {snapshot}")
        write_desc(i, desc)
        print(f"Branch {i} added under snapshot {snapshot}.")

#   Lock ast
def ast_lock():
    os.system("touch /.snapshots/ast/lock-disable")

#   Unlock
def ast_unlock():
    os.system("rm -rf /.snapshots/ast/lock")

def get_lock():
    if os.path.exists("/.snapshots/ast/lock"):
        return(True)
    else:
        return(False)

#   Recursively remove package in tree
def remove_from_tree(tree,treename,pkg):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{treename}")):
        print(f"F: cannot update as tree {treename} doesn't exist.")
    else:
        remove(treename, pkg)
        order = recurstree(tree, treename)
        if len(order) > 2:
            order.remove(order[0])
            order.remove(order[0])
        while True:
            if len(order) < 2:
                break
            arg = order[0]
            sarg = order[1]
            print(arg,sarg)
            order.remove(order[0])
            order.remove(order[0])
            remove(sarg,pkg)
        print(f"Tree {treename} updated.")

#   Recursively run an update in tree
def update_tree(tree,treename):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{treename}")):
        print(f"F: cannot update as tree {treename} doesn't exist.")
    else:
        upgrade(treename)
        order = recurstree(tree, treename)
        if len(order) > 2:
            order.remove(order[0])
            order.remove(order[0])
        while True:
            if len(order) < 2:
                break
            arg = order[0]
            sarg = order[1]
            print(arg,sarg)
            order.remove(order[0])
            order.remove(order[0])
            autoupgrade(sarg)
        print(f"Tree {treename} updated.")

#   Recursively run an update in tree
def run_tree(tree,treename,cmd):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{treename}")):
        print(f"F: cannot update as tree {treename} doesn't exist.")
    else:
        prepare(treename)
        os.system(f"chroot /.snapshots/rootfs/snapshot-chr{treename} {cmd}")
        posttrans(treename)
        order = recurstree(tree, treename)
        if len(order) > 2:
            order.remove(order[0])
            order.remove(order[0])
        while True:
            if len(order) < 2:
                break
            arg = order[0]
            sarg = order[1]
            print(arg,sarg)
            order.remove(order[0])
            order.remove(order[0])
            prepare(sarg)
            os.system(f"chroot /.snapshots/rootfs/snapshot-chr{sarg} {cmd}")
            posttrans(sarg)
        print(f"Tree {treename} updated.")

#   Sync tree and all it's snapshots
def sync_tree(tree,treename,forceOffline):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{treename}")):
        print(f"F: cannot sync as tree {treename} doesn't exist.")
    else:
        if not forceOffline: # Syncing tree automatically updates it, unless 'force-sync' is used
            update_tree(tree, treename)
        order = recurstree(tree, treename)
        if len(order) > 2:
            order.remove(order[0])
            order.remove(order[0])
        while True:
            if len(order) < 2:
                break
            arg = order[0]
            sarg = order[1]
            print(arg,sarg)
            order.remove(order[0])
            order.remove(order[0])
            prepare(sarg)
            os.system(f"cp --reflink=auto -r /.snapshots/var/var-{arg}/lib/systemd/* /.snapshots/var/var-chr{sarg}/lib/systemd/ >/dev/null 2>&1")
            os.system(f"cp --reflink=auto -r /.snapshots/var/var-{arg}/lib/systemd/* /.snapshots/rootfs/snapshot-chr{sarg}/var/lib/systemd/ >/dev/null 2>&1")
            os.system(f"cp --reflink=auto -n -r /.snapshots/rootfs/snapshot-{arg}/* /.snapshots/rootfs/snapshot-chr{sarg}/ >/dev/null 2>&1")
            posttrans(sarg)
        print(f"Tree {treename} synced.")

#   Clone tree
def clone_as_tree(snapshot):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{snapshot}")):
        print(f"F: cannot clone as snapshot {snapshot} doesn't exist.")
    else:
        i = findnew()
        os.system(f"btrfs sub snap -r /.snapshots/rootfs/snapshot-{snapshot} /.snapshots/rootfs/snapshot-{i} >/dev/null 2>&1")
        os.system(f"btrfs sub snap -r /.snapshots/etc/etc-{snapshot} /.snapshots/etc/etc-{i} >/dev/null 2>&1")
        os.system(f"btrfs sub snap -r /.snapshots/var/var-{snapshot} /.snapshots/var/var-{i} >/dev/null 2>&1")
        os.system(f"btrfs sub snap -r /.snapshots/boot/boot-{snapshot} /.snapshots/boot/boot-{i} >/dev/null 2>&1")
        append_base_tree(fstree,i)
        write_tree(fstree)
        desc = str(f"clone of {snapshot}")
        write_desc(i, desc)
        print(f"Tree {i} cloned from {snapshot}.")

#   Creates new tree from base file
def new_snapshot(desc=""):
    i = findnew()
    os.system(f"btrfs sub snap -r /.snapshots/rootfs/snapshot-0 /.snapshots/rootfs/snapshot-{i} >/dev/null 2>&1")
    os.system(f"btrfs sub snap -r /.snapshots/etc/etc-0 /.snapshots/etc/etc-{i} >/dev/null 2>&1")
    os.system(f"btrfs sub snap -r /.snapshots/boot/boot-0 /.snapshots/boot/boot-{i} >/dev/null 2>&1")
    os.system(f"btrfs sub snap -r /.snapshots/var/var-0 /.snapshots/var/var-{i} >/dev/null 2>&1")
    append_base_tree(fstree,i)
    write_tree(fstree)
    if desc: write_desc(i, desc)
    print(f"New tree {i} created.")

#   Calls print function
def show_fstree():
    print_tree(fstree)

#   Saves changes made to /etc to snapshot
def update_etc():
    tmp = get_tmp()
    snapshot = get_snapshot()
    os.system(f"btrfs sub del /.snapshots/etc/etc-{snapshot} >/dev/null 2>&1")
    os.system(f"btrfs sub snap -r /.snapshots/etc/etc-{tmp} /.snapshots/etc/etc-{snapshot} >/dev/null 2>&1")

#   Update boot
def update_boot(snapshot):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{snapshot}")):
        print(f"F: cannot update boot as snapshot {snapshot} doesn't exist.")
    else:
        tmp = get_tmp()
        part = get_part()
        prepare(snapshot)
        os.system(f"chroot /.snapshots/rootfs/snapshot-chr{snapshot} grub-mkconfig {part} -o /boot/grub/grub.cfg")
        os.system(f"chroot /.snapshots/rootfs/snapshot-chr{snapshot} sed -i s,snapshot-chr{snapshot},snapshot-{tmp},g /boot/grub/grub.cfg")
        os.system(f"chroot /.snapshots/rootfs/snapshot-chr{snapshot} sed -i '0,/AshOS\ Linux/s//AshOS\ Linux\ snapshot\ {snapshot}/' /boot/grub/grub.cfg")
        posttrans(snapshot)

#   Chroot into snapshot
def chroot(snapshot):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{snapshot}")):
        print(f"F: cannot chroot as snapshot {snapshot} doesn't exist.")
    elif snapshot == "0":
        print("F: changing base snapshot is not allowed.")
    else:
        prepare(snapshot)
        os.system(f"chroot /.snapshots/rootfs/snapshot-chr{snapshot}")
        posttrans(snapshot)

#   Run command in snapshot
def chrrun(snapshot,cmd):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{snapshot}")):
        print(f"F: cannot chroot as snapshot {snapshot} doesn't exist.")
    elif snapshot == "0":
        print("F: changing base snapshot is not allowed.")
    else:
        prepare(snapshot)
        os.system(f"chroot /.snapshots/rootfs/snapshot-chr{snapshot} {cmd}")
        posttrans(snapshot)

#   Clean chroot mount dirs
def unchr(snapshot):
    os.system(f"btrfs sub del /.snapshots/etc/etc-chr{snapshot} >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/var/var-chr{snapshot} >/dev/null 2>&1")
    os.system(f"rm -rf /.snapshots/var/var-chr{snapshot} >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/boot/boot-chr{snapshot} >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/rootfs/snapshot-chr{snapshot}/* >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/rootfs/snapshot-chr{snapshot} >/dev/null 2>&1")

#   Clean tmp dirs
def untmp():
    tmp = get_tmp()
    if "tmp0" in tmp:
        tmp = "tmp"
    else:
        tmp = "tmp0"
    os.system(f"btrfs sub del /.snapshots/rootfs/snapshot-{tmp}/* >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/rootfs/snapshot-{tmp} >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/etc/etc-{tmp} >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/var/var-{tmp} >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/boot/boot-{tmp} >/dev/null 2>&1")

#   Install live
def live_install(pkg):
    tmp = get_tmp()
    part = get_part()
    os.system(f"mount --bind /.snapshots/rootfs/snapshot-{tmp} /.snapshots/rootfs/snapshot-{tmp} >/dev/null 2>&1")
    os.system(f"mount --bind /home /.snapshots/rootfs/snapshot-{tmp}/home >/dev/null 2>&1")
    os.system(f"mount --bind /var /.snapshots/rootfs/snapshot-{tmp}/var >/dev/null 2>&1")
    os.system(f"mount --bind /etc /.snapshots/rootfs/snapshot-{tmp}/etc >/dev/null 2>&1")
    os.system(f"mount --bind /tmp /.snapshots/rootfs/snapshot-{tmp}/tmp >/dev/null 2>&1")
    os.system(f"chroot /.snapshots/rootfs/snapshot-{tmp} pacman -S --overwrite \\* --noconfirm {pkg}")
    os.system(f"umount /.snapshots/rootfs/snapshot-{tmp}/* >/dev/null 2>&1")
    os.system(f"umount /.snapshots/rootfs/snapshot-{tmp} >/dev/null 2>&1")

#   Live unlocked shell
def live_unlock():
    tmp = get_tmp()
    part = get_part()
    os.system(f"mount --bind /.snapshots/rootfs/snapshot-{tmp} /.snapshots/rootfs/snapshot-{tmp} >/dev/null 2>&1")
    os.system(f"mount --bind /home /.snapshots/rootfs/snapshot-{tmp}/home >/dev/null 2>&1")
    os.system(f"mount --bind /var /.snapshots/rootfs/snapshot-{tmp}/var >/dev/null 2>&1")
    os.system(f"mount --bind /etc /.snapshots/rootfs/snapshot-{tmp}/etc >/dev/null 2>&1")
    os.system(f"mount --bind /tmp /.snapshots/rootfs/snapshot-{tmp}/tmp >/dev/null 2>&1")
    os.system(f"chroot /.snapshots/rootfs/snapshot-{tmp}")
    os.system(f"umount /.snapshots/rootfs/snapshot-{tmp}/* >/dev/null 2>&1")
    os.system(f"umount /.snapshots/rootfs/snapshot-{tmp} >/dev/null 2>&1")

#   Install packages
def install(snapshot,pkg):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{snapshot}")):
        print(f"F: cannot install as snapshot {snapshot} doesn't exist.")
    elif snapshot == "0":
        print("F: changing base snapshot is not allowed.")
    else:
        prepare(snapshot)
        excode = str(os.system(f"chroot /.snapshots/rootfs/snapshot-chr{snapshot} pacman -S {pkg} --overwrite '/var/*'"))
        if int(excode) == 0:
            posttrans(snapshot)
            print(f"Package {pkg} installed in snapshot {snapshot} successfully.")
        else:
            print("F: install failed and changes discarded.")

#   Install from a text file
def install_profile(snapshot, profile):
    install(snapshot, subprocess.check_output(f"cat {profile}", shell=True).decode('utf-8').strip())

#   Remove packages
def remove(snapshot,pkg):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{snapshot}")):
        print(f"F: cannot remove as snapshot {snapshot} doesn't exist.")
    elif snapshot == "0":
        print("F: changing base snapshot is not allowed.")
    else:
        prepare(snapshot)
        excode = str(os.system(f"chroot /.snapshots/rootfs/snapshot-chr{snapshot} pacman --noconfirm -Rns {pkg}"))
        if int(excode) == 0:
            posttrans(snapshot)
            print(f"Package {pkg} removed from snapshot {snapshot} successfully.")
        else:
            print("F: remove failed and changes discarded.")

#   Delete tree or branch
def delete(snapshot):
    print(f"Are you sure you want to delete snapshot {snapshot}? (y/N)")
    choice = input("> ")
    run = True
    if choice.casefold() != "y":
        print("Aborted")
        run = False
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{snapshot}")):
        print(f"F: cannot delete as snapshot {snapshot} doesn't exist.")
    elif snapshot == "0":
        print("F: changing base snapshot is not allowed.")
    elif run == True:
        children = return_children(fstree,snapshot)
        os.system(f"btrfs sub del /.snapshots/boot/boot-{snapshot} >/dev/null 2>&1")
        os.system(f"btrfs sub del /.snapshots/etc/etc-{snapshot} >/dev/null 2>&1")
        os.system(f"btrfs sub del /.snapshots/var/var-{snapshot} >/dev/null 2>&1")
        os.system(f"btrfs sub del /.snapshots/rootfs/snapshot-{snapshot} >/dev/null 2>&1")
        for child in children: # This deletes the node itself along with it's children
            os.system(f"btrfs sub del /.snapshots/boot/boot-{child} >/dev/null 2>&1")
            os.system(f"btrfs sub del /.snapshots/etc/etc-{child} >/dev/null 2>&1")
            os.system(f"btrfs sub del /.snapshots/var/var-{child} >/dev/null 2>&1")
            os.system(f"btrfs sub del /.snapshots/rootfs/snapshot-{child} >/dev/null 2>&1")
        remove_node(fstree,snapshot) # Remove node from tree or root
        write_tree(fstree)
        print(f"Snapshot {snapshot} removed.")

#   Update base
def update_base():
    prepare("0")
    os.system(f"chroot /.snapshots/rootfs/snapshot-chr0 pacman -Syyu")
    posttrans("0")

#   Prepare snapshot to chroot dir to install or chroot into
def prepare(snapshot):
    unchr(snapshot)
    part = get_part()
    etc = snapshot
    os.system(f"btrfs sub snap /.snapshots/rootfs/snapshot-{snapshot} /.snapshots/rootfs/snapshot-chr{snapshot} >/dev/null 2>&1")
    os.system(f"btrfs sub snap /.snapshots/etc/etc-{snapshot} /.snapshots/etc/etc-chr{snapshot} >/dev/null 2>&1")
    os.system(f"mkdir -p /.snapshots/var/var-chr{snapshot} >/dev/null 2>&1")
    # pacman gets weird when chroot directory is not a mountpoint, so the following mount is necessary
    os.system(f"mount --bind /.snapshots/rootfs/snapshot-chr{snapshot} /.snapshots/rootfs/snapshot-chr{snapshot} >/dev/null 2>&1")
    os.system(f"mount --bind /var /.snapshots/rootfs/snapshot-chr{snapshot}/var >/dev/null 2>&1")
    os.system(f"mount --rbind /dev /.snapshots/rootfs/snapshot-chr{snapshot}/dev >/dev/null 2>&1")
    os.system(f"mount --rbind /sys /.snapshots/rootfs/snapshot-chr{snapshot}/sys >/dev/null 2>&1")
    os.system(f"mount --rbind /tmp /.snapshots/rootfs/snapshot-chr{snapshot}/tmp >/dev/null 2>&1")
    os.system(f"mount --rbind /proc /.snapshots/rootfs/snapshot-chr{snapshot}/proc >/dev/null 2>&1")
    os.system(f"btrfs sub snap /.snapshots/boot/boot-{snapshot} /.snapshots/boot/boot-chr{snapshot} >/dev/null 2>&1")
    os.system(f"cp -r --reflink=auto /.snapshots/etc/etc-chr{snapshot}/* /.snapshots/rootfs/snapshot-chr{snapshot}/etc >/dev/null 2>&1")
    os.system(f"cp -r --reflink=auto /.snapshots/boot/boot-chr{snapshot}/* /.snapshots/rootfs/snapshot-chr{snapshot}/boot >/dev/null 2>&1")
    os.system(f"rm -rf /.snapshots/rootfs/snapshot-chr{snapshot}/var/lib/systemd/* >/dev/null 2>&1")
    os.system(f"cp -r --reflink=auto /.snapshots/var/var-{snapshot}/lib/systemd/* /.snapshots/rootfs/snapshot-chr{snapshot}/var/lib/systemd/ >/dev/null 2>&1")
    os.system(f"mount --bind /home /.snapshots/rootfs/snapshot-chr{snapshot}/home >/dev/null 2>&1")
    os.system(f"mount --rbind /run /.snapshots/rootfs/snapshot-chr{snapshot}/run >/dev/null 2>&1")
    os.system(f"cp /etc/machine-id /.snapshots/rootfs/snapshot-chr{snapshot}/etc/machine-id")
    os.system(f"mkdir -p /.snapshots/rootfs/snapshot-chr{snapshot}/.snapshots/ast && cp -f /.snapshots/ast/fstree /.snapshots/rootfs/snapshot-chr{snapshot}/.snapshots/ast/")
    os.system(f"mount --bind /etc/resolv.conf /.snapshots/rootfs/snapshot-chr{snapshot}/etc/resolv.conf >/dev/null 2>&1")
    os.system(f"mount --bind /root /.snapshots/rootfs/snapshot-chr{snapshot}/root >/dev/null 2>&1")

#   Post transaction function, copy from chroot dirs back to read only snapshot dir
def posttrans(snapshot):
    etc = snapshot
    tmp = get_tmp()
    os.system(f"umount /.snapshots/rootfs/snapshot-chr{snapshot} >/dev/null 2>&1")
    os.system(f"umount /.snapshots/rootfs/snapshot-chr{snapshot}/etc/resolv.conf >/dev/null 2>&1")
    os.system(f"umount /.snapshots/rootfs/snapshot-chr{snapshot}/root >/dev/null 2>&1")
    os.system(f"umount /.snapshots/rootfs/snapshot-chr{snapshot}/home >/dev/null 2>&1")
    os.system(f"umount /.snapshots/rootfs/snapshot-chr{snapshot}/run >/dev/null 2>&1")
    os.system(f"umount /.snapshots/rootfs/snapshot-chr{snapshot}/dev >/dev/null 2>&1")
    os.system(f"umount /.snapshots/rootfs/snapshot-chr{snapshot}/sys >/dev/null 2>&1")
    os.system(f"umount /.snapshots/rootfs/snapshot-chr{snapshot}/proc >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/rootfs/snapshot-{snapshot} >/dev/null 2>&1")
    os.system(f"rm -rf /.snapshots/etc/etc-chr{snapshot}/* >/dev/null 2>&1")
    os.system(f"cp -r --reflink=auto /.snapshots/rootfs/snapshot-chr{snapshot}/etc/* /.snapshots/etc/etc-chr{snapshot} >/dev/null 2>&1")
    os.system(f"rm -rf /.snapshots/var/var-chr{snapshot}/* >/dev/null 2>&1")
    os.system(f"mkdir -p /.snapshots/var/var-chr{snapshot}/lib/systemd >/dev/null 2>&1")
    os.system(f"cp -r --reflink=auto /.snapshots/rootfs/snapshot-chr{snapshot}/var/lib/systemd/* /.snapshots/var/var-chr{snapshot}/lib/systemd >/dev/null 2>&1")
    os.system(f"cp -r -n --reflink=auto /.snapshots/rootfs/snapshot-chr{snapshot}/var/cache/pacman/pkg/* /var/cache/pacman/pkg/ >/dev/null 2>&1")
    os.system(f"rm -rf /.snapshots/boot/boot-chr{snapshot}/* >/dev/null 2>&1")
    os.system(f"cp -r --reflink=auto /.snapshots/rootfs/snapshot-chr{snapshot}/boot/* /.snapshots/boot/boot-chr{snapshot} >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/etc/etc-{etc} >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/var/var-{etc} >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/boot/boot-{etc} >/dev/null 2>&1")
    os.system(f"btrfs sub snap -r /.snapshots/etc/etc-chr{snapshot} /.snapshots/etc/etc-{etc} >/dev/null 2>&1")
    os.system(f"btrfs sub create /.snapshots/var/var-{etc} >/dev/null 2>&1")
    os.system(f"mkdir -p /.snapshots/var/var-{etc}/lib/systemd >/dev/null 2>&1")
    os.system(f"cp --reflink=auto -r /.snapshots/var/var-chr{snapshot}/lib/systemd/* /.snapshots/var/var-{etc}/lib/systemd >/dev/null 2>&1")
    os.system(f"rm -rf /var/lib/systemd/* >/dev/null 2>&1")
    os.system(f"cp --reflink=auto -r /.snapshots/rootfs/snapshot-{tmp}/var/lib/systemd/* /var/lib/systemd >/dev/null 2>&1")
    os.system(f"btrfs sub snap -r /.snapshots/rootfs/snapshot-chr{snapshot} /.snapshots/rootfs/snapshot-{snapshot} >/dev/null 2>&1")
    os.system(f"btrfs sub snap -r /.snapshots/boot/boot-chr{snapshot} /.snapshots/boot/boot-{etc} >/dev/null 2>&1")
    unchr(snapshot)

#   Upgrade snapshot
def upgrade(snapshot):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{snapshot}")):
        print(f"F: cannot upgrade as snapshot {snapshot} doesn't exist.")
    elif snapshot == "0":
        print("F: changing base snapshot is not allowed.")
    else:
        prepare(snapshot)
        excode = str(os.system(f"chroot /.snapshots/rootfs/snapshot-chr{snapshot} pacman -Syyu")) # Default upgrade behaviour is now "safe" update, meaning failed updates get fully discarded
        if int(excode) == 0:
            posttrans(snapshot)
            print(f"Snapshot {snapshot} upgraded successfully.")
        else:
            print("F: upgrade failed and changes discarded.")

#   Refresh snapshot
def refresh(snapshot):
    if not (os.path.exists(f"/.snapshots/rootfs/snapshot-{snapshot}")):
        print(f"F: cannot refresh as snapshot {snapshot} doesn't exist.")
    elif snapshot == "0":
        print("F: changing base snapshot is not allowed.")
    else:
        prepare(snapshot)
        excode = str(os.system(f"chroot /.snapshots/rootfs/snapshot-chr{snapshot} pacman -Syy"))
        if int(excode) == 0:
            posttrans(snapshot)
            print(f"Snapshot {snapshot} refreshed successfully.")
        else:
            print("F: refresh failed and changes discarded.")

#   Noninteractive update
def autoupgrade(snapshot):
    prepare(snapshot)
    excode = str(os.system(f"chroot /.snapshots/rootfs/snapshot-chr{snapshot} pacman --noconfirm -Syyu"))
    if int(excode) == 0:
        posttrans(snapshot)
        os.system("echo 0 > /.snapshots/ast/upstate")
        os.system("echo $(date) >> /.snapshots/ast/upstate")
    else:
        os.system("echo 1 > /.snapshots/ast/upstate")
        os.system("echo $(date) >> /.snapshots/ast/upstate")

#   Check if last update was successful
def check_update():
    upstate = open("/.snapshots/ast/upstate", "r")
    line = upstate.readline()
    date = upstate.readline()
    if "1" in line:
        print(f"F: Last update on {date} failed.")
    if "0" in line:
        print(f"Last update on {date} completed successfully.")
    upstate.close()

def chroot_check():
    chroot = True # When inside chroot
    with open("/proc/mounts", "r") as mounts:
        for line in mounts:
            if str("/.snapshots btrfs") in str(line):
                chroot = False
    return(chroot)

#   Rollback last booted deployment
def rollback():
    tmp = get_tmp()
    i = findnew()
    clone_as_tree(tmp)
    write_desc(i, "rollback")
    deploy(i)

#   Switch between /tmp deployments
def switchtmp():
    udistro = get_distro()
    mount = get_tmp()
    part = get_part()
    os.system(f"mkdir -p /etc/mnt/boot >/dev/null 2>&1")
    os.system(f"mount {part} -o subvol=@boot{udistro} /etc/mnt/boot") # Mount boot partition for writing
    if "tmp0" in mount:
        os.system("cp --reflink=auto -r /.snapshots/rootfs/snapshot-tmp/boot/* /etc/mnt/boot")  ######REZA WHATABOUTTHIS?
        os.system(f"sed -i 's,@.snapshots{udistro}/rootfs/snapshot-tmp0,@.snapshots{udistro}/rootfs/snapshot-tmp,g' /etc/mnt/boot/grub/grub.cfg") # Overwrite grub config boot subvolume
        os.system(f"sed -i 's,@.snapshots{udistro}/rootfs/snapshot-tmp0,@.snapshots{udistro}/rootfs/snapshot-tmp,g' /.snapshots/rootfs/snapshot-tmp/boot/grub/grub.cfg")
        os.system(f"sed -i 's,@.snapshots{udistro}/rootfs/snapshot-tmp0,@.snapshots{udistro}/rootfs/snapshot-tmp,g' /.snapshots/rootfs/snapshot-tmp/etc/fstab") # Write fstab for new deployment
        os.system(f"sed -i 's,@.snapshots{udistro}/etc/etc-tmp0,@.snapshots{udistro}/etc/etc-tmp,g' /.snapshots/rootfs/snapshot-tmp/etc/fstab")
        os.system(f"sed -i 's,@.snapshots{udistro}/boot/boot-tmp0,@.snapshots{udistro}/boot/boot-tmp,g' /.snapshots/rootfs/snapshot-tmp/etc/fstab")
        sfile = open("/.snapshots/rootfs/snapshot-tmp0/usr/share/ast/snap","r")
        snap = sfile.readline()
        snap = snap.replace(" ", "")
        sfile.close()
    else:
        os.system("cp --reflink=auto -r /.snapshots/rootfs/snapshot-tmp0/boot/* /etc/mnt/boot")
        os.system(f"sed -i 's,@.snapshots{udistro}/rootfs/snapshot-tmp,@.snapshots{udistro}/rootfs/snapshot-tmp0,g' /etc/mnt/boot/grub/grub.cfg")
        os.system(f"sed -i 's,@.snapshots{udistro}/rootfs/snapshot-tmp,@.snapshots{udistro}/rootfs/snapshot-tmp0,g' /.snapshots/rootfs/snapshot-tmp0/boot/grub/grub.cfg")
        os.system(f"sed -i 's,@.snapshots{udistro}/rootfs/snapshot-tmp,@.snapshots{udistro}/rootfs/snapshot-tmp0,g' /.snapshots/rootfs/snapshot-tmp0/etc/fstab")
        os.system(f"sed -i 's,@.snapshots{udistro}/etc/etc-tmp,@.snapshots{udistro}/etc/etc-tmp0,g' /.snapshots/rootfs/snapshot-tmp0/etc/fstab")
        os.system(f"sed -i 's,@.snapshots{udistro}/boot/boot-tmp,@.snapshots{udistro}/boot/boot-tmp0,g' /.snapshots/rootfs/snapshot-tmp0/etc/fstab")
        sfile = open("/.snapshots/rootfs/snapshot-tmp/usr/share/ast/snap", "r")
        snap = sfile.readline()
        snap = snap.replace(" ","")
        sfile.close()
    #
    snap = snap.replace('\n',"")
    grubconf = open("/etc/mnt/boot/grub/grub.cfg","r")
    line = grubconf.readline()
    while "BEGIN /etc/grub.d/10_linux" not in line:
        line = grubconf.readline()
    line = grubconf.readline()
    gconf = str("")
    while "}" not in line:
        gconf = str(gconf)+str(line)
        line = grubconf.readline()
    if "snapshot-tmp0" in gconf:
        gconf = gconf.replace("snapshot-tmp0","snapshot-tmp")
    else:
        gconf = gconf.replace("snapshot-tmp", "snapshot-tmp0")
    if "AshOS Linux" in gconf:
        gconf = re.sub('\d', '', gconf)
        gconf = gconf.replace(f"AshOS Linux snapshot",f"AshOS last booted deployment (snapshot {snap})")
    grubconf.close()
    os.system("sed -i '$ d' /etc/mnt/boot/grub/grub.cfg")
    grubconf = open("/etc/mnt/boot/grub/grub.cfg", "a")
    grubconf.write(gconf)
    grubconf.write("}\n")
    grubconf.write("### END /etc/grub.d/41_custom ###")
    grubconf.close()

    grubconf = open("/.snapshots/rootfs/snapshot-tmp0/boot/grub/grub.cfg","r")
    line = grubconf.readline()
    while "BEGIN /etc/grub.d/10_linux" not in line:
        line = grubconf.readline()
    line = grubconf.readline()
    gconf = str("")
    while "}" not in line:
        gconf = str(gconf)+str(line)
        line = grubconf.readline()
    if "snapshot-tmp0" in gconf:
        gconf = gconf.replace("snapshot-tmp0","snapshot-tmp")
    else:
        gconf = gconf.replace("snapshot-tmp", "snapshot-tmp0")
    if "AshOS Linux" in gconf:
        gconf = re.sub('\d', '', gconf)
        gconf = gconf.replace(f"AshOS Linux snapshot", f"AshOS last booted deployment (snapshot {snap})")
    grubconf.close()
    os.system("sed -i '$ d' /.snapshots/rootfs/snapshot-tmp0/boot/grub/grub.cfg")
    grubconf = open("/.snapshots/rootfs/snapshot-tmp0/boot/grub/grub.cfg", "a")
    grubconf.write(gconf)
    grubconf.write("}\n")
    grubconf.write("### END /etc/grub.d/41_custom ###")
    grubconf.close()
    os.system("umount /etc/mnt/boot >/dev/null 2>&1")

# Clear all temporary snapshots
def tmpclear():
    os.system(f"btrfs sub del /.snapshots/etc/etc-chr* >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/var/var-chr* >/dev/null 2>&1")
    os.system(f"rm -rf /.snapshots/var/var-chr* >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/boot/boot-chr* >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/rootfs/snapshot-chr*/* >/dev/null 2>&1")
    os.system(f"btrfs sub del /.snapshots/rootfs/snapshot-chr* >/dev/null 2>&1")

def list_subvolumes():
    os.system(f"btrfs sub list / | grep -i {distro}")

# Find new unused snapshot dir
def findnew():
    i = 0
    snapshots = os.listdir("/.snapshots/rootfs")
    etcs = os.listdir("/.snapshots/etc")
    vars = os.listdir("/.snapshots/var")
    boots = os.listdir("/.snapshots/boot")
    snapshots.append(etcs)
    snapshots.append(vars)
    snapshots.append(boots)
    while True:
        i += 1
        if str(f"snapshot-{i}") not in snapshots and str(f"etc-{i}") not in snapshots and str(f"var-{i}") not in snapshots and str(f"boot-{i}") not in snapshots:
            return(i)

#   Main function
def main(args):
    udistro = get_distro()
    snapshot = get_snapshot() # Get current snapshot
    etc = snapshot
    importer = DictImporter() # Dict importer
    exporter = DictExporter() # And exporter
    isChroot = chroot_check()
    lock = get_lock() # True = locked
    global fstree # Currently these are global variables, fix sometime
    global fstreepath # ---
    fstreepath = str("/.snapshots/ast/fstree") # Path to fstree file
    fstree = importer.import_(import_tree_file("/.snapshots/ast/fstree")) # Import fstree file
    # Recognize argument and call appropriate function
    arg = args[1]
    if isChroot == True and ("--chroot" not in args):
        print("Please don't use ast inside a chroot!")
    elif lock == True:
        print("ast is locked. To manually unlock, run 'rm -rf /var/lib/ast/lock'.")
    elif arg == "new-tree" or arg == "new":
        args_2 = args
        args_2.remove(args_2[0])
        args_2.remove(args_2[0])
        new_snapshot(str(" ").join(args_2))
    elif arg == "boot-update" or arg == "boot":
        update_boot(args[args.index(arg)+1])
    elif arg == "chroot" or arg == "cr" and (lock != True):
        ast_lock()
        chroot(args[args.index(arg)+1])
        ast_unlock()
    elif arg == "live-chroot":
        ast_lock()
        live_unlock()
        ast_unlock()
    elif arg == "install" or (arg == "in") and (lock != True):
        ast_lock()
        args_2 = args
        args_2.remove(args_2[0])
        args_2.remove(args_2[0])
        live = False
        if args_2[0] == "--live":
            args_2.remove(args_2[0])
        if args_2[0] == get_snapshot():
            live = True
        csnapshot = args_2[0]
        args_2.remove(args_2[0])
        install(csnapshot, str(" ").join(args_2))
        if live:
            live_install(str(" ").join(args_2))
        ast_unlock()
    elif arg == "run" and (lock != True):
        ast_lock()
        args_2 = args
        args_2.remove(args_2[0])
        args_2.remove(args_2[0])
        csnapshot = args_2[0]
        args_2.remove(args_2[0])
        chrrun(csnapshot, str(" ").join(args_2))
        ast_unlock()
    elif arg == "add-branch" or arg == "branch":
        extend_branch(args[args.index(arg)+1])
    elif arg == "tmpclear" or arg == "tmp":
        tmpclear()
    elif arg == "clone-branch" or arg == "cbranch":
        clone_branch(args[args.index(arg)+1])
    elif arg == "clone-under" or arg == "ubranch":
        clone_under(args[args.index(arg)+1], args[args.index(arg)+2])
    elif arg == "clone" or arg == "tree-clone":
        clone_as_tree(args[args.index(arg)+1])
    elif arg == "deploy":
        deploy(args[args.index(arg)+1])
    elif arg == "rollback":
        rollback()
    elif arg == "upgrade" or arg == "up" and (lock != True):
        ast_lock()
        upgrade(args[args.index(arg)+1])
        ast_unlock()
    elif arg == "refresh" or arg == "ref" and (lock != True):
        ast_lock()
        refresh(args[args.index(arg)+1])
        ast_unlock()
    elif arg == "etc-update" or arg == "etc" and (lock != True):
        ast_lock()
        update_etc()
        ast_unlock()
    elif arg == "current" or arg == "c":
        print(snapshot)
    elif arg == "rm-snapshot" or arg == "del":
        delete(args[args.index(arg)+1])
    elif arg == "remove" and (lock != True):
        ast_lock()
        args_2 = args
        args_2.remove(args_2[0])
        args_2.remove(args_2[0])
        csnapshot = args_2[0]
        args_2.remove(args_2[0])
        remove(csnapshot, str(" ").join(args_2))
        ast_unlock()
    elif arg == "desc" or arg == "description":
        n_lay = args[args.index(arg)+1]
        args_2 = args
        args_2.remove(args_2[0])
        args_2.remove(args_2[0])
        args_2.remove(args_2[0])
        write_desc(n_lay, str(" ").join(args_2))
    elif arg == "base-update" or arg == "bu" and (lock != True):
        ast_lock()
        update_base()
        ast_unlock()
    elif arg == "sync" or arg == "tree-sync" and (lock != True):
        ast_lock()
        sync_tree(fstree,args[args.index(arg)+1],False)
        ast_unlock()
    elif arg == "fsync" or arg == "force-sync" and (lock != True):
        ast_lock()
        sync_tree(fstree,args[args.index(arg)+1],True)
        ast_unlock()
    elif arg == "auto-upgrade" and (lock != True):
        ast_lock()
        autoupgrade(snapshot)
        ast_unlock()
    elif arg == "check":
        check_update()
    elif arg == "tree-upgrade" or arg == "tupgrade" and (lock != True):
        ast_lock()
        upgrade(args[args.index(arg)+1])
        update_tree(fstree,args[args.index(arg)+1])
        ast_unlock()
    elif arg == "tree-run" or arg == "trun" and (lock != True):
        ast_lock()
        args_2 = args
        args_2.remove(args_2[0])
        args_2.remove(args_2[0])
        csnapshot = args_2[0]
        args_2.remove(args_2[0])
        run_tree(fstree, csnapshot, str(" ").join(args_2))
        ast_unlock()
    elif arg == "tree-rmpkg" or arg == "tremove" and (lock != True):
        ast_lock()
        args_2 = args
        args_2.remove(args_2[0])
        args_2.remove(args_2[0])
        csnapshot = args_2[0]
        args_2.remove(args_2[0])
        remove(csnapshot, str(" ").join(args_2))
        remove_from_tree(fstree, csnapshot, str(" ").join(args_2))
        ast_unlock()
    elif arg == "tree":
        show_fstree()
    elif arg == "list":
        list_subvolumes()
    else:
        print("Operation not found.")

#   Call main
if __name__ == "__main__":
    from anytree.importer import DictImporter
    from anytree.exporter import DictExporter
    import anytree

    main(args)


