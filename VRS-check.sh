while true ; do
  mono /home/pi/VRS/VirtualRadar.exe -nogui
  echo "VRS ended prematurely at `date "+%d-%b-%y %H:%M:%S"`." >> /home/pi/VRS_failures.txt
  sleep 5
done