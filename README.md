# Virtual-Radar-Server-on-Stratux
Installs and runs Virtual Radar Server on Stratux with offline maps and complete aircraft database.

The script 'VRS-on-Stratux.sh' will install on Stratux nearly everything needed to run Virtual Radar Server in offline mode (since we don't have internet in the sky) so you get a complete map of the US and full database of all US, Canadian and many international aircraft with proper silhouettes and operator flags.  

Installation includes mono, virtual radar server, webadmin plugin, tileservercache plugin, silhouettes, operator flags, custom python GDL90 to SBS converter to make all Stratux output available to VRS, OpenStreet maps to zoom level 13 for both Stratux and VRS, custom built comprehensive database with all US and Canadian aircraft and many international aircraft.

The custom python program connects to Stratux's UDP port 4000 and translates the data into SBS format.  It makes those data available on TCP port 33333.  If you are outside the US, you don't need the python program since the 1090 data are available on port 30003 of Stratux, but it doesn't cause any issues running the python program in the absence of UAT data.  However, since I only include a US OpenStreet map, you will need to assemble your own map for offline use if you're outside the US.

If you enable the "Show Traffic Source in Callsign" option in Stratux's settings, the python program will filter out all non-ADS-B traffic and only pass along UAT traffic on port 33333.  Thus, the "UAT" receiver in VRS can be selected to view only UAT traffic.

Installation:
- I suggest a 64 GB minimum size sdcard, though you can fit everything on 32 GB if you're strategic about it.
- Connect your Stratux to the internet.
- Connect to your Stratux's settings page and add '127.0.0.1' in the "Static IPs" list.  Do not skip this step, or you won't see UAT traffic in VRS.
- Enable developer mode then reboot.
- Enable persistent logging then reboot.
- ssh into the Stratux (defaults are pi/raspberry)
- run:  wget -N sudo wget -N https://github.com/egite/Virtual-Radar-Server-on-Stratux/releases/download/v1.0/VRS-on-Stratux.sh
- run:  chmod 755 VRS-on-Stratux
- run:  ./VRS-on-Stratux.sh
  
It will take some time to download all the necessary files and packages.  When it's done, you'll need to download several large files from Google Drive. These files don't have direct links because of their size, so you'll need to download them from a browser on a computer then use 'scp' to copy from that computer to the Pi.

- Download the 204 MB BaseStation.sqb database from the following link.
  - https://drive.google.com/uc?export=download&id=1amNCk3fMYv3X-eZ1AwDRvVp1PHyDuaL2
  - 'scp' it to the Stratux into the following folder:  '/home/pi/VRS_Files/'

- Download the 112 MB full aircraft custom database for VRS from the following link.
  - https://drive.google.com/uc?export=download&id=15ilLDsOfxqI4CL51PqMtsb5sHYRc8D_e
  - 'scp' it to the Stratux into the following folder:  '/home/pi/.local/share/VirtualRadar'

- Download and unpack the 5.8 GB OpenStreet offline map for VRS from the following link.
  - https://drive.google.com/uc?export=download&id=1tI5hb0I66zj0kR8RaK4BOru31R1Cqaua
  - 'scp' it to the Stratux into the following folder:  ~pi/.local/share/VirtualRadar/TileServerCache/Leaflet'
  - Then unpack and delete it with 'tar -zxvf maps.tar.gz ; rm maps.tar.gz'.

- If you want Stratux to have offline OpenStreet maps and offline VFR charts (which may not be current):
  - Download this 6.2 GB mbtiles file from a browser onto a computer:
    - https://drive.google.com/uc?export=download&id=1uZAqCMZ-VXjqeqTNygL-WyMSZd_J8KtG
    - On the Stratux, cd into '/overlay/robase/opt/stratux/mapdata' and execute 'sudo overlayctl unlock'.
    - 'scp' the OpenStreet.mbtiles you downloaded onto the Stratux into ~pi/ then:
    - 'mv ~pi/OpenStreet.mbtiles /overlay/robase/opt/stratux/mapdata'
  - On the Stratux, in the same folder, execute 'wget -N https://abatzill.de/stratux/vfrsec.mbtiles' to get the ~700 MB VFR charts.
    - Then execute 'sudo systemctl restart stratux'.
  - Verify that the VFR charts and offline OpenStreet maps are available in Stratux's 'Map' web page.

After completing those steps, reboot your Stratux.  It may take a couple of minutes for VRS to start up.  You can check processes with 'ps -eaf|grep mono'.
When VRS starts, go to Stratux's main status page.  You should see links for VRS at the bottom.
The VRS icon will take you to VRS only when you are connected to Stratux via its wifi link, otherwise,
use the text links.

The username and password for VRS' administration page is indicated in parenthesis next to the Admin link.
Be sure to always include '127.0.0.1' on the list of Stratux static IPs in Stratux's 'Settings' page.

When you have confirmed VRS is functioning properly, turn off persistent logging in Stratux's settings and reboot.
If you later want to make configuration changes top VRS, you'll need to reenable persistent logging, reboot, make changes in VRS then disable persistant logging and reboot.  Keeping persistent logging on risks a corrupted sdcard if you shut off the Stratux without shutting it down through the webpage.

