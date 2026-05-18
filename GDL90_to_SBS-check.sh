#!/bin/bash
while true ; do
  pgrep -a python | grep GDL90_to_SBS >/dev/null 2>/dev/null
  if [ $? != 0 ] ; then
    /home/pi/GDL90_to_SBS.py 4000 33333 >/dev/null 2>>/home/pi/GDL90_to_SBS_failures.txt
    echo "GDL90_to_SBS.py ended prematurely at `date "+%d-%b-%y %H:%M:%S"`." >> /home/pi/GDL90_to_SBS_failures.txt
    sleep 1
  fi
done
