#!/usr/bin/env python

# Usage:    GDL90_to_SBS.py UDP_PORT TCP_PORT
# Example:  GDL90_to_SBS.py 4000 33333

# This Python program is intended to connect to Stratux's UDP port 4000 and translate the data into
# SBS format.  It makes those data available on a specified TCP port (e.g., 33333). 
# Only ownship, traffic, UAT basic and UAT long reports are translated to SBS format.
# Useful only for U.S.-based pilots.
#
# It is intended to allow Virtual Radar Server to run alongside Stratux and see all data including UAT,
# not just ADS-B.  On Stratux, ADS-B data are available via dump1090 on port 30003 but Stratux doesn't run
# dump978 to use uat2esnt with.
#
# With this program running, both the UAT and ADS-B traffic visible to Stratux are available to VRS on
# a specified TCP 33333.  Setting up a "receiver" on VRS pointed to port 33333 on 127.0.0.1 with BaseStation
# format makes all of Stratux's traffic visible.  I suggest a "SBS" receiver on port 33333 (with BaseStation
# format), an "ADS-B" receiver on port 30003 and a "merged" feed with both those receivers.

# If you enable the "Show Traffic Source in Callsign" option in Stratux's setting, this program will
# filter out all non-ADS-B traffic and only pass along UAT traffic.

# Installation of VRS on Stratux can be done by:
#   Enable developer mode on Stratux:
#     Click 8 times quickly on the version number on the main Stratux status webpage then reboot.
#   Ssh into stratux and follow the steps on https://www.virtualradarserver.co.uk/Mono.aspx 
#     Use the latest preview version of VRS:  https://github.com/vradarserver/vrs/releases
#     Place the installation in /home/pi/VRS/
#     Default login credentials for Stratux:  user: pi, password: raspberry
#     Add the following line to the crontab on Stratux (run 'crontab -e')
#       @reboot sleep 60 ; mono /home/pi/VRS/VirtualRadar.exe -nogui
#   Use E's VRS Database-Updater to create a complete database of all FAA and Canadian aircraft.
#     https://github.com/egite/E-s-VRS-Database-Updater/
#     Scp the AircraftOnlineLookupCache.sqb file created from E's updater program to stratux at:
#       /home/pi/.local/share/VirtualRadar/
#     Update this database by repeating the above twp steps when you think that aircraft registrations
#     are stale.  Every few months of perhaps appropriate.
#   Optional but highly recommended for VRS:  
#     Grab a complete set of silhouettes and operator flags.  There are several easily found sources.
#     You should run 'mogrify' on all silhouette bitmaps to be sure VRS can render them.  
#     In your silhouettes directory, with Stratux connected to the internet:
#       sudo apt-get update 
#       sudo apt-get install imagemagick
#       mogrify -format bmp -define bmp:format=bmp3 *.bmp
# Then place this Python program in /home/pi/ on Stratux.

# This Python program is not intended to make an installation of VRS on Stratux available for
# decisions related to aircraft operations.
#
# -E 2-Nov-2025

# This Python program should be run on Stratux via the crontab as a script called every minute.
# After installing VRS and this Python program as explained above, place the script below
#  (between the scissors) into /home/pi/
# Remove the first hash symbol (#) from each line in the script below. 
# Run 'chmod 755 /home/pi/GDL90_to_SBS-check.sh' to ensure the script is executable.
# Add the following line to the crontab (run 'crontab -e'):
#   * * * * /home/pi/GDL90_to_SBS-check.sh
#
#---------8<---------------DON'T INCLUDE THIS LINE

#while true ; do   
#  pgrep -a python | grep GDL90_to_SBS.py | grep 4000 | grep 33333 >/dev/null 2>/dev/null
#  if [ $? != 0 ] ; then
#    #echo "`date "+%d-%b-%y %H:%M:%S"`:  GDL90_to_SBS for stratux not up" >> /home/pi/GDL90_to_SBS_failures.txt
#    #echo "GDL90_to_SBS.py for stratux not not up."
#    /home/pi/GDL90_to_SBS.py 4000 33333 >/dev/null 2>>/home/pi/GDL90_to_SBS_failures.txt
#    echo "GDL90_to_SBS.py for stratux ended prematurely with $errormsg at `date "+%d-%b-%y %H:%M:%S"`." >> /home/pi/GDL90_to_SBS_failures.txt
#    sleep 1
#  fi
#done

#---------->8--------------DON'T INCLUDE THIS LINE

CRC_Table=[]

Callsign_Array=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
"A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
"K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
"U", "V", "W", "X", "Y", "Z", " ", " ", " ", " ",
" ", " ", " ", " "," ", " ", " ", " "," ", " ", " ", " "," ", " ", " ", " "," ", " ", " ", " "]

Emitter_Array=["cluster","light","medium","medium+","medium++","heavy","highly manoeuverable",
"rotocraft","reserved","glider/sailplane","light than air","parachutist/skydiver","ultralight/hang glider/paraglider",
"reserved","unmanned aerial vehicle","space/trans-atmospheric aircraft","reserved","emergency vehicle",
"service vehicle","point obstacle"]
#----------------------------
def CRCInit():
  global CRC_Table
  for i in range(0,256):
       CRC=(i*256)&65535
       for bitctr in range(0,8):
            if (CRC&32768)>0:
                 temp=4129
            else:
                 temp=0
            CRC=((CRC*2)&65535) ^ temp
            CRC=CRC&65535
       CRC_Table.append(CRC)
  return CRC_Table

#----------------------------
def CRCCompute(BlockData, BlockLength):
  CRCcalc=0
  if len(BlockData) == BlockLength:
       for i in range(0,BlockLength):
            temp0=CRCcalc // 256
            temp1=CRC_Table[temp0]
            temp2=(CRCcalc*256)&65535
            temp3=temp1 ^ temp2
            CRCcalc=temp3 ^ BlockData[i]
  else:
       CRCcalc = 999999999
  return CRCcalc

#----------------------------
def ownship_traffic(data):
    global skip_output
    temp=CRCCompute(data[1:29], 28)
    if temp == data[30]*256+data[29]:                  # if it isn't equal, then it's a CRC error and we don't want the data
        callsign=data[20:29].decode('ascii','ignore')  # include positions 28 and 29 in case "Show Traffic Source in Callsign" is enabled
        Callsign=""
        for i in range(20,20+len(callsign)):
            if data[i] > 13 and data[i] < 135:
                Callsign=Callsign + callsign[i-20]
        Callsign=Callsign.rstrip(" ")
        if len(Callsign) > 1:
            if Callsign[0]=="e":                       # if "Show Traffic Source in Callsign" is enabled, trap all ADS-B traffic
                skip_output=1
            else:
                if Callsign[0]=="u":
                    Callsign=Callsign[2:]

        if data[3]<16:
            ICAO="0"+hex(data[3])[2:].upper()
        else:
            ICAO=hex(data[3])[2:].upper()

        if data[4]<16:
            ICAO=ICAO+"0"+hex(data[4])[2:].upper()
        else:
            ICAO=ICAO+hex(data[4])[2:].upper()

        if data[5]<16:
            ICAO=ICAO+"0"+hex(data[5])[2:].upper()
        else:
            ICAO=ICAO+hex(data[5])[2:].upper()

        if data[6]&128 == 128:
            Latitude=((data[6]&127)*65536 + data[7]*256 + data[8] - 8388608)*0.000021457672
        else:
            Latitude=(data[6]*65536 + data[7]*256 + data[8])*0.000021457672

        if data[9]&128 == 128:
            Longitude=((data[9]&127)*65536 + data[10]*256 + data[11] - 8388608)*0.000021457672
        else:
            Longitude=(data[9]*65536 + data[10]*256 + data[11])*0.000021457672

        misc=data[13]&15
        airborne=misc&8
        if airborne == 0:
             airborne="Ground"
             squat=1
             MID=2
             Altitude = 0 # SBS format defines 0 for ground positions
             Speed_V = 0  # if you're on the ground, your VSI is zero
        else:
             airborne="Airborne"
             squat=0
             MID=4

             d=(data[13]&240) >> 4
             if d == 15 and data[12] == 255:
                  Altitude=""
             else:
                  Altitude=(data[12]*16+d - 1)*25-1000

             d=data[16]&15
             if d&8==8:
                  Speed_V=((d&7)*256 + data[17] - 2048)*64
             else:
                  Speed_V=(d*256 + data[17])*64
             if abs(Speed_V)>32576:
                  Speed_V=""
             if d==8 and data[17]==8:
                  Speed_V=""

             d=(data[13]&240) >> 4
             if d == 15 and data[12] == 255:
                  Altitude=""
             else:
                  Altitude=(data[12]*16+d - 1)*25-1000

        d=(data[16]&240) >> 4
        Speed_H=data[15]*16+d
        if Speed_H == 4095:
             Speed_H = ""

        if misc&3 == 0:
             Heading=""
        else:
             Heading=round(data[18]*360/256)

        if ICAO not in ICAOs:
             ICAOs.append(ICAO)
             if Callsign != None and Callsign[:4].rstrip(" ").isnumeric() == False:  # if it's not blank and doesn't look like a squawk, save it
                 Callsigns.append(Callsign)
             else:
                 Callsigns.append("")
             squawks.append("")
           
        idx = ICAOs.index(ICAO)
        squawk = squawks[idx]  # bring in what we had before, if anything

        if Callsign != "":
             if Callsign[:4].rstrip(" ").isnumeric():
                 squawk = Callsign[:4].rstrip(" ")
                 squawks[idx] = squawk
             if Callsigns[idx] == squawk:   # if we saved the callsign when it was a squawk, kill it and we'll grab it next time
                 Callsigns[idx] = ""
             if Callsign == squawk:   # if we saved the callsign when it was a squawk, kill it and we'll grab it next time
                 Callsign = Callsigns[idx]  # otherwise grab the previously saved callsign
        else:
             Callsign = Callsigns[idx]

        TodaysDate=datetime.today().strftime('%Y/%m/%d')
        TodaysTime=datetime.today().strftime('%H:%M:%S')

        AID=ICAOs.index(ICAO)

        global SBS
        SBS="MSG,%s,111,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,,,,%s" % (MID,AID, ICAO, AID, TodaysDate, TodaysTime+".000", TodaysDate, TodaysTime+".000", Callsign, Altitude, Speed_H, Heading, Latitude, Longitude, Speed_V, squawk, squat)
    #else:
        #print("CRC error")

#----------------------------
def UAT_Passthrough(data):

    global SBS
    global ICAOs
    global Callsigns
    global squawks

    # check CRC first
    if data[1] == 31:
        a = 39
    else:
        a = 24
    temp=CRCCompute(data[1:a], a-1)
    if temp != 999999999:
        if temp != data[a+1]*256+data[a]:
            #print("CRC failure")
            return
    else:
        print("Length mismatch")
        return
      

    MDB = (data[5]&248) >> 3   #message data block type code
    AQ = data[5]&7  # address qualifier

    if data[6]<16:
        ICAO="0"+hex(data[6])[2:].upper()
    else:
        ICAO=hex(data[6])[2:].upper()

    if data[7]<16:
        ICAO=ICAO+"0"+hex(data[7])[2:].upper()
    else:
        ICAO=ICAO+hex(data[7])[2:].upper()

    if data[8]<16:
        ICAO=ICAO+"0"+hex(data[8])[2:].upper()
    else:
        ICAO=ICAO+hex(data[8])[2:].upper()

    if data[1]==31:
        ans = sum(data[22:33])
    else:
        ans = 0

    if data[1]==31 and ans > 0:     #only message 31 has the mode status
        n = data[22]*256 + data[23]
        emitter = n//1600%40
        Callsign = Callsign_Array[n//40%40]
        Callsign = Callsign + Callsign_Array[n%40]
        n = data[24]*256 + data[25]
        Callsign = Callsign + Callsign_Array[n//1600%40]
        Callsign = Callsign + Callsign_Array[n//40%40]
        Callsign = Callsign + Callsign_Array[n%40]
        n = data[26]*256 + data[27]
        Callsign = Callsign + Callsign_Array[n//1600%40]
        Callsign = Callsign + Callsign_Array[n//40%40]
        Callsign = Callsign + Callsign_Array[n%40]
    else:
        Callsign = ""
        emitter = 8
    Callsign=Callsign.rstrip(" ")

    alt_type = data[14] & 1
    Altitude = data[15]*256+data[16]
    Altitude = Altitude >> 4
    Altitude = (Altitude - 1) * 25 - 1000

    ag_state=(data[17] & 192) >> 6
    if ag_state == 0 or ag_state == 2:
       speed_multiplier = 1
    else:
       speed_multiplier = 4   # multiply by 4 if it's supersonic

    if ag_state <= 1:
        squat = 0
        MID = 4
        N_S = 1
        E_W = 1

        north_speed = (data[17] & 15)*64 + ((data[18] & 252) >> 2) - 1
        if (data[17]&16) != 0:
            north_speed = -north_speed
            N_S = -1

        east_speed = (data[18] & 1)*512 + data[19]*2 + ((data[20] & 128) >> 7) - 1
        if (data[18]&2) != 0:
            east_speed = -east_speed
            E_W = -1

        Speed_H = math.sqrt(north_speed**2 + east_speed**2)
        Speed_H = Speed_H * speed_multiplier
        Heading = (math.atan2(east_speed,north_speed))*180/math.pi

        if Heading>=360:
            Heading = Heading - 360
        elif Heading<0:
            Heading = Heading + 360

    else:                # on ground
        Speed_H = data[17] & 15
        Speed_H = Speed_H*64 + ((data[18] & 252) >> 2) - 1
        north_speed = -1
        east_speed = -1
        Heading = data[19]*2 + ((data[20]&128) >> 7)
        Heading = Heading * 0.703125
        squat = 1
        MID = 1
    Heading = round(Heading)
    Speed_H = round(Speed_H)

    if ag_state != 2:  #VSI only valid if airborne
        Speed_V = (data[20]&31)*16 + ((data[21]&240)>>4) - 1
        Speed_V = Speed_V*64
        if (data[20]&32) > 0:
            Speed_V = -Speed_V
        Speed_V=round(Speed_V)
    else:
        Speed_V = 0

    # this is only valid for the quadrant of the globe that I live in
    Latitude = data[9]*32768 + data[10]*128 + ((data[11]&254) >> 1)
    Latitude = Latitude*0.000021457672
    Longitude = (data[11]&1)*8388608 + data[12]*32768 + data[13]*128 + ((data[14]&254) >> 1)
    Longitude = Longitude*0.000021457672
    if Longitude > 180:
        Longitude = Longitude - 360
    elif Longitude < -180:
        Longitude = Longitude + 360

    if ICAO not in ICAOs:
        ICAOs.append(ICAO)
        if Callsign != None and Callsign[:4].rstrip(" ").isnumeric() == False:  # if it's not blank and doesn't look like a squawk, save it
            Callsigns.append(Callsign)
        else:
            Callsigns.append("")
        squawks.append("")

    idx = ICAOs.index(ICAO)
    squawk = squawks[idx]  # bring in what we had before, if anything

    if Callsign != "":
         if Callsign[:4].rstrip(" ").isnumeric():
             squawk = Callsign[:4].rstrip(" ")
             squawks[idx] = squawk
             if Callsigns[idx] == squawk:   # if we saved the callsign when it was a squawk, kill it and we'll grab it next time
                 Callsigns[idx] = ""
             if Callsign == squawk:   # if we saved the callsign when it was a squawk, kill it and we'll grab it next time
                 Callsign = Callsigns[idx]
    else:
         Callsign = Callsigns[idx]

    AID=idx

    TodaysDate=datetime.today().strftime('%Y/%m/%d')
    TodaysTime=datetime.today().strftime('%H:%M:%S')

    #print("31 %s" % (Callsign.encode('utf-8').hex()))

    #print("%8s, %s, Alt: %5s, Spd: %3s, VSI: %6s, Hdg: %3s, AltT: %s, MDB: %2s, AQ: %s, Squawk: %4s, (%2.7f,%4.7f), Emit: %19s  %s" % (Callsign, ICAO, Altitude, Speed_H, Speed_V, Heading, alt_type, MDB, AQ, squawk, Latitude, Longitude, Emitter_Array[emitter], TodaysTime))

    #print("%8s, %s, Alt: %5s, Spd: %3s, VSI: %6s, Hdg: %3s, AltT: %s, MDB: %2s, AQ: %s, Squawk: %4s, (%2.7f,%4.7f), Emit: %19s  %s" % (Callsign, ICAO, Altitude, Speed_H, Speed_V, Heading, alt_type, MDB, AQ, squawk, Latitude, Longitude, Emitter_Array[emitter], TodaysTime), file=open("/home/pi/SBS","a"))

    SBS ="MSG,%s,111,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,,,,%s" % (MID,AID, ICAO, AID, TodaysDate, TodaysTime+".000", TodaysDate, TodaysTime+".000", Callsign, Altitude, Speed_H, Heading, Latitude, Longitude, Speed_V, squawk, squat)


#----------------------------
def send_output(SBS, skip_output):
    if skip_output==0:
        print("%s" % (SBS))
        SBS=SBS+"\n"
        try:
            global c
            global s
            c.send(SBS.encode())

        except socket.error:
            print("Connection was terminated.  Restarting.")
            print("Waiting for connection...",end='',flush=True)
            s.listen(1)
            c, addr = s.accept()
            print("Connection from:", str(addr))


import socket, sys, math
from datetime import datetime

if len(sys.argv) != 3:
  print("%s requires two arguments:  UDP_PORT TCP_PORT." % sys.argv[0])
  quit()

CRC_Table=CRCInit()
CRC=[1, 2]

UDP_IP = "127.0.0.1"
UDP_PORT = int(sys.argv[1])
TCP_PORT = int(sys.argv[2])

print("%s %s" % (UDP_PORT, TCP_PORT))

ICAOs=["ZZZZZZ"]
Callsigns=[""]
squawks=[""]
CurrentIndex=0
SBS=""
skip_output = 0  # set to 1 if you don't want to send the data out the TCP_PORT

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', TCP_PORT))

print("Waiting for connection...",end='',flush=True)
s.listen(1)
c, addr = s.accept()
print("Connection from:", str(addr))

# This is the main program loop.  Everything above are the functions
while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    if len(data) > 29:  # don't bother decoding if it isn't long enough
        if data[1] == 10 or data[1] == 20:
           ownship_traffic(data)
           if SBS != "":
               send_output(SBS, skip_output)
        elif data[1] == 31 or data[1] == 30:
           UAT_Passthrough(data)
           if SBS != "":
               send_output(SBS, 0)

