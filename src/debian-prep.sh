sudo apt-get -y update && apt-get -y install git tmux parted btrfs-progs dosfstools
echo "export LC_ALL=C LC_CTYPE=C LANGUAGE=C" | tee -a $HOME/.bashrc
echo "alias p='curl -F "'"sprunge=<-"'" sprunge.us" | tee -a $HOME/.bashrc
echo "setw -g mode-keys vi" | tee -a $HOME/.tmux.conf
git clone http://github.com/i2/ashos-dev
cd ashos-dev
git checkout debian
/bin/bash ./src/part-efi-example.sh /dev/sda
#sudo python3 init.py /dev/sda2 /dev/sda /dev/sda1

