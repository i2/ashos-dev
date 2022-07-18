sudo apt-get remove -y --purge man-db # Fix slow man-db trigger
sudo apt-get -y update && sudo apt-get -y --fix-broken install git tmux parted btrfs-progs dosfstools
echo "export LC_ALL=C LC_CTYPE=C LANGUAGE=C" | tee -a $HOME/.bashrc
echo "alias p='curl -F "'"sprunge=<-"'" sprunge.us'" | tee -a $HOME/.bashrc
echo "alias d='df -h | grep -v sda'" | tee -a $HOME/.bashrc
echo "setw -g mode-keys vi" | tee -a $HOME/.tmux.conf
echo "set -g history-limit 999999" | tee -a $HOME/.tmux.conf
git clone http://github.com/i2/ashos-dev
cd ashos-dev
git checkout debian
#/bin/bash ./src/prep/part-efi-example.sh /dev/sda
#sudo python3 init.py /dev/sda2 /dev/sda /dev/sda1

