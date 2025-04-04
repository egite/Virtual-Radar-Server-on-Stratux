# Virtual-Radar-Server-on-Stratux
Installs and runs Virtual Radar Server on Stratux with offline maps and complete aircraft database.

The script [VRS-on-Stratux.sh](https://github.com/egite/Virtual-Radar-Server-on-Stratux/releases/download/v1.1/VRS-on-Stratux.sh) will install on Stratux nearly everything needed to run Virtual Radar Server in offline mode (since we don't have internet in the sky) so you get a complete map of the US and full database of all US, Canadian and many international aircraft with proper silhouettes and operator flags.  

Installation includes (nearly all are automatic):
- mono
- Virtual Radar Server
  - webadmin plugin
  - tileservercache plugin
  - preconfigured config files for zero required setup
  - Silhouettes
  - Operator flags
- 'imagemagick' (to use 'mogrify' to reformat bitmaps to compatible format for VRS)
- Custom [python GDL90 to SBS converter](https://github.com/egite/Stratux-GDL90-to-SBS-Converter-for-Virtual-Radar-Server) to make all Stratux output available to VRS
- Custom built comprehensive database with all US and Canadian aircraft and many international aircraft
  - You can later update the database as frequently as you like using [E's VRS Database Updater](https://github.com/egite/E-s-VRS-Database-Updater)
- Manual download of OpenStreet maps to zoom level 13 for VRS (and optionally for Stratux's map)

The [custom python program I wrote](https://github.com/egite/Stratux-GDL90-to-SBS-Converter-for-Virtual-Radar-Server) connects to Stratux's UDP port 4000 and translates the data into SBS format.  It makes those data available on TCP port 33333, which VRS then connects to.  If you are outside the US, you don't need the python program since the 1090 data are available on port 30003 of Stratux, but it doesn't cause any issues running the python program in the absence of UAT data.  However, since I only include a US OpenStreet map, you will need to assemble your own map for offline use if you're outside the US.

If you enable the "Show Traffic Source in Callsign" option in Stratux's settings, my python program will filter out all non-ADS-B traffic and only pass along UAT traffic on port 33333.  In this way, the "UAT" receiver in VRS can be selected to view only UAT traffic and the "ADS-B" receiver can be used to see just ADS-B traffic from the 1090 receiver on port 30003.  The default setting is to use the "Merged Feed" of both receivers (port 30003 from dump1090 and the GDL90-translated-to-SCS data on port 33333) so that both traffic sources are visible unless otherwise selected in VRS.

**How to install:**
- I suggest a 32 GB minimum size sdcard, though you can fit everything on 16 GB if you're strategic about it.
- Connect your Stratux to the internet.
- Connect to your Stratux's settings page and add '127.0.0.1' in the "Static IPs" list.
  - Do not skip this step, or you won't see UAT traffic in VRS.
- Enable developer mode then reboot.
- Enable persistent logging then reboot.
- ssh into the Stratux (defaults are pi/raspberry).
- Run the following from the command line:
  - wget -N https://github.com/egite/Virtual-Radar-Server-on-Stratux/releases/download/v1.1/VRS-on-Stratux.sh
  - chmod 755 VRS-on-Stratux.sh
  - ./VRS-on-Stratux.sh
  
It will take some time to download all the necessary files and packages.  When it's done, you'll need to download several large files from Google Drive. These files don't have direct links because of their size, so you'll need to download them from a browser on a computer then use 'scp' to copy from that computer to the Pi.

- Download the 204 MB BaseStation.sqb database from the following link.
  - https://drive.google.com/uc?export=download&id=1amNCk3fMYv3X-eZ1AwDRvVp1PHyDuaL2
  - 'scp' it to the Stratux into the following folder:  '/home/pi/VRS_Files/'
- Download the 112 MB full aircraft custom database for VRS from the following link.
  - https://drive.google.com/uc?export=download&id=15ilLDsOfxqI4CL51PqMtsb5sHYRc8D_e
  - 'scp' it to the Stratux into the following folder:  '/home/pi/.local/share/VirtualRadar'
  - You can later update this database as frequently as you like using [E's VRS Database Updater](https://github.com/egite/E-s-VRS-Database-Updater)
- Download and unpack the 5.8 GB OpenStreet offline map for VRS from the following link.
  - https://drive.google.com/uc?export=download&id=1tI5hb0I66zj0kR8RaK4BOru31R1Cqaua
  - 'scp' it to the Stratux into the following folder:  ~pi/.local/share/VirtualRadar/TileServerCache/Leaflet'
  - Then unpack and delete it with 'tar -zxvf maps.tar.gz ; rm maps.tar.gz'.
- <em>Optional</em>:  In addition to VRS' offline OpenStreet maps, if you also want <em>Stratux's</em> maps (not just VRS') to have offline OpenStreet maps and offline VFR charts (which may not be current):
  - Download this 6.2 GB mbtiles file from a browser onto a computer:
    - https://drive.google.com/uc?export=download&id=1uZAqCMZ-VXjqeqTNygL-WyMSZd_J8KtG
    - On the Stratux, cd into '/overlay/robase/opt/stratux/mapdata' and execute 'sudo overlayctl unlock'.
    - 'scp' the OpenStreet.mbtiles you downloaded onto the Stratux into ~pi/ then:
    - 'mv ~pi/OpenStreet.mbtiles /overlay/robase/opt/stratux/mapdata'
  - On the Stratux, in the same folder, execute 'wget -N https://abatzill.de/stratux/vfrsec.mbtiles' to get the ~700 MB VFR charts.
  - Then execute 'sudo systemctl restart stratux'.
  - Verify that the VFR charts and offline OpenStreet maps are available in Stratux's 'Map' web page.

After completing those steps, reboot your Stratux.  It may take a couple of minutes for VRS to start up.  You can check for the VRS process with '<em>ps -eaf|grep mono</em>'.
After VRS starts, go to Stratux's main status page.  You should see links for VRS at the bottom.  It may take 10-20 seconds for VRS to serve its pages (longer if VRS isn't yet running).
The VRS icon will take you to VRS only when you are connected to Stratux via its wifi link, otherwise, use the text links.  Those links will take you to the aircraft on the map that is defined as "ownship" within Stratux.  The script that updates the address for those links run every minute, however Stratux may not update the page for several minutes, so it may take a little bit for the links to update.

The username and password for VRS' administration page is indicated in parenthesis next to the Admin link.
Be sure to always include '127.0.0.1' on the list of Stratux static IPs in Stratux's 'Settings' page.

When you have confirmed VRS is functioning properly, turn off persistent logging in Stratux's settings and reboot.
If you later want to make configuration changes to VRS, you'll need to first reenable persistent logging, reboot, make changes in VRS then disable persistant logging when you're done then reboot (with persistent logging off, changes made to VRS' settings will be lost on the next Stratux reboot).  Keeping persistent logging on risks a corrupted sdcard if you shut off the Stratux without shutting it down through the webpage.

