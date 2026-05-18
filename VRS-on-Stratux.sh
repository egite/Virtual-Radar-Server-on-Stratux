sudo overlayctl unlock
# get GDL90 to SBS format converter
cd ~pi
wget -N https://github.com/egite/Stratux-GDL90-to-SBS-Converter-for-Virtual-Radar-Server/releases/latest/download/GDL90_to_SBS.py

# get files necessary for VRS
cd ~pi
sudo apt update
sudo apt install mono-complete -y
mkdir VRS ; cd VRS
# find the most recent VRS mono release and download the three needed packages
VRS_REPO="vradarserver/vrs"
VRS_TAG=$(wget -qO- "https://api.github.com/repos/$VRS_REPO/releases" | grep -oP '"tag_name":\s*"\K[^"]*-mono' | head -n1)
VRS_RELEASE=$(wget -qO- "https://api.github.com/repos/$VRS_REPO/releases/tags/$VRS_TAG")
for pkg in VirtualRadar Plugin-WebAdmin Plugin-TileServerCache; do
  url=$(echo "$VRS_RELEASE" | grep -oP "\"browser_download_url\":\s*\"\Khttps://[^\"]*/${pkg}-[^\"]*\.tar\.gz")
  wget -N "$url"
  tar -zxvf "$(basename "$url")" ; rm "$(basename "$url")"
done
mkdir -p /home/pi/.local/share/VirtualRadar ; cd /home/pi/.local/share/VirtualRadar
wget -N https://github.com/egite/Virtual-Radar-Server-on-Stratux/releases/latest/download/Configuration.xml
wget -N https://github.com/egite/Virtual-Radar-Server-on-Stratux/releases/latest/download/Users.sqb
wget -N https://github.com/egite/Virtual-Radar-Server-on-Stratux/releases/latest/download/PluginsConfiguration.txt
mkdir TileServerCache ; cd TileServerCache ; mkdir Leaflet ; cd Leaflet ; mkdir OpenStreetMap 

# get database files for VRS
mkdir ~pi/VRS_Files ; cd ~pi/VRS_Files
#wget -N http://data.flightairmap.com/data/basestation/BaseStation.sqb.gz  -O - | gunzip > BaseStation.sqb

# prep the new links for VRS
cd /opt/stratux/www
sudo wget -N https://github.com/egite/Virtual-Radar-Server-on-Stratux/releases/latest/download/VRS.jpg
cd plates
sudo wget -N https://github.com/egite/Virtual-Radar-Server-on-Stratux/releases/latest/download/status.html

# get silhouettes and flags for VRS
echo "Downloading silhouettes and flags from https://github.com/rikgale/.  You can use a different source if desired."
cd ~pi/VRS_Files/
wget -N https://github.com/rikgale/VRSOperatorFlags/raw/main/Silhouettes.zip 
mkdir silhouettes ; cd silhouettes ; unzip ../Silhouettes.zip ; rm ../Silhouettes.zip
cd ~pi/VRS_Files/
wget -N https://github.com/rikgale/VRSOperatorFlags/raw/main/OperatorFlags.zip
mkdir flags ; cd flags ; unzip ../OperatorFlags.zip ; rm ../OperatorFlags.zip

# go into silhouettes and flags folders and run this to convert all bitmap files to the right format for VRS
sudo apt install imagemagick -y
cd ~pi/VRS_Files/silhouettes ; mogrify -format bmp -define bmp:format=bmp3 *.bmp
cd ~pi/VRS_Files/flags ; mogrify -format bmp -define bmp:format=bmp3 *.bmp

#get scripts for checking program status and update crontab
cd ~pi
wget -N https://github.com/egite/Virtual-Radar-Server-on-Stratux/releases/latest/download/GDL90_to_SBS-check.sh
chmod 755 /home/pi/GDL90_to_SBS-check.sh
cd ~pi
wget -N https://github.com/egite/Virtual-Radar-Server-on-Stratux/releases/latest/download/VRS-check.sh
chmod 755 /home/pi/VRS-check.sh
line="@reboot sleep 30 ; /home/pi/GDL90_to_SBS-check.sh"
(crontab -u $(whoami) -l; echo "$line" ) | crontab -u $(whoami) -
line="@reboot sleep 60 ; /home/pi/VRS-check.sh"
(crontab -u $(whoami) -l; echo "$line" ) | crontab -u $(whoami) -


echo "The following files need to be downloaded from Google Drive.  They are too big to have a direct"
echo "link, so you'll need to download them from a browser on a computer then use 'scp' to copy from"
echo "that computer to the Pi".
echo
echo "Download the 204 MB BaseStation.sqb database from the following link."
echo "   https://drive.google.com/uc?export=download&id=1amNCk3fMYv3X-eZ1AwDRvVp1PHyDuaL2"
echo "'scp' it to the Stratux into the following folder:  '/home/pi/VRS_Files/'"
echo 
echo 
echo "Download the 112 MB full aircraft database for VRS from the following link."
echo "   https://drive.google.com/uc?export=download&id=15ilLDsOfxqI4CL51PqMtsb5sHYRc8D_e"
echo "You'll need to download it from a browser on a computer then use 'scp' to copy from that computer"
echo "'scp' it to the Stratux into the following folder:  '/home/pi/.local/share/VirtualRadar'"
echo
echo 
echo "Download and install the 5.8 GB OpenStreet offline map for VRS from the following link."
echo "   https://drive.google.com/uc?export=download&id=1tI5hb0I66zj0kR8RaK4BOru31R1Cqaua"
echo "'scp' it to the Stratux into the following folder:  ~pi/.local/share/VirtualRadar/TileServerCache/Leaflet'"
echo "Then unpack and delete it with 'tar -zxvf maps.tar.gz ; rm maps.tar.gz'."
echo
echo 
echo "If you want Stratux to have offline VFR charts (which are not current) and offline OpenStreet maps, then"
echo "download this 6.2 GB mbtiles file from a browser onto a computer:"
echo "   https://drive.google.com/uc?export=download&id=1uZAqCMZ-VXjqeqTNygL-WyMSZd_J8KtG"
echo "On the Stratux, cd into '/overlay/robase/opt/stratux/mapdata' and execute 'sudo overlayctl unlock'.  "
echo "'scp' the OpenStreet.mbtiles you downloaded onto the Stratux into the following folder:"
echo "'/overlay/robase/opt/stratux/mapdata'."
echo "On the Stratux, in the same folder, execute 'wget -N https://abatzill.de/stratux/vfrsec.mbtiles'"
echo "Then execute 'sudo systemctl restart stratux'".
echo
echo 
echo "After completing those steps, reboot your Stratux.  It may take a couple of minutes for VRS to start up."
echo "When VRS starts, go to Stratux's main status page.  You should see links for VRS at the bottom."
echo "The VRS icon will take you to VRS only when you are connected to Stratux via its wifi link, otherwise,"
echo "use the text links."
echo 
echo "The username and password for VRS' administration page is indicated in parenthesis next to the Admin link."
echo "Be sure to always include '127.0.0.1' on the list of Stratux static IPs in Stratux's 'Setting' page."
echo 
echo "When you have confirmed VRS is functioning properly, turn off "Persistent logging" in Stratux's settings."
echo "If you later want to make configuration changes top VRS, you'll need to reenable persistent logging, reboot,"
echo "make changes in VRS then disable persistent logging and reboot.  Keeping persistent logging on risks a"
echo "corrupted sdcard if you shut off the Stratux without shutting it down through the webpage."
