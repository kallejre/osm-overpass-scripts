#!/bin/bash
# Install R with required dependencies, tested on Ubuntu 20.04 VM.
echo "This script will NOT work on WSL systems."
sudo apt install open-vm-tools open-vm-tools-desktop -y
sudo apt install dirmngr gnupg git curl apt-transport-https libudunits2-dev libfontconfig1-dev libicu66 libcairo2-dev ca-certificates python3-pip software-properties-common software-properties-common dirmngr -y

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
sudo add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"
sudo add-apt-repository ppa:c2d4u.team/c2d4u4.0+ -y
sudo apt install r-base build-essential -y
sudo apt install libssl-dev -y
sudo apt install libxml2-dev -y
sudo apt install libcurl4-openssl-dev -y
sudo apt install libgdal-dev -y
sudo apt install ristretto -y
# sudo apt install dos2unix -y
# sudo apt install python3-autopep8 -y

cd ~
git clone https://github.com/ZeLonewolf/osm-overpass-scripts.git
cd osm-overpass-scripts/
pip install -r requirements.txt 
sudo ./install.R  # Running this command takes around 30-50 min
