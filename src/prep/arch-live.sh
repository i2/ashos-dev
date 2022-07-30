#!/bin/sh

if [ -z "$HOME" ]; then HOME=~ ; fi

# Fix signature invalid error
rm -rf /etc/pacman.d/gnupg ~/.gnupg
pacman -Syy
gpg --refresh-keys
killall gpg-agent
pacman-key --init
pacman-key --populate archlinux

# Ignore signature checking in pacman.conf (bad idea - use above fix)
#sed -e '/^SigLevel/ s|^#*|SigLevel = Never\n#|' -i /etc/pacman.conf
#sed -e '/^LocalFileSigLevel/ s|^#*|#|' -i /etc/pacman.conf

pacman -Syy --noconfirm archlinux-keyring git
echo "export LC_ALL=C LC_CTYPE=C LANGUAGE=C" | tee -a $HOME/.zshrc
#echo "alias p='curl -F "'"sprunge=<-"'" sprunge.us'" | tee -a $HOME/.zshrc
echo "alias p='curl -F "'"f:1=<-"'" ix.io'" | tee -a $HOME/.zshrc
echo "alias d='df -h | grep -v sda'" | tee -a $HOME/.zshrc
echo "setw -g mode-keys vi" | tee -a $HOME/.tmux.conf
echo "set -g history-limit 999999" | tee -a $HOME/.tmux.conf
#git clone http://github.com/i2/ashos-dev
#cd ashos-dev
#git checkout debian
#/bin/sh ./src/prep/part-efi-example.sh /dev/sda
#python3 init.py /dev/sda2 /dev/sda /dev/sda1

