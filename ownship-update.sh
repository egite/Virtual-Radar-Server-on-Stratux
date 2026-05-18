#!/bin/bash
sudo cp ~/status.html ~/www/plates/status.html
sleep 1
sudo chown pi:pi ~/www/plates/status.html
OWNSHIP=`grep OwnshipModeS /boot/stratux.conf |  sed 's/"//g'|cut -d: -f2|sed 's/ //g'|sed 's/,//g'`
grep -n icao /opt/stratux/www/plates/status.html |cut -d: -f1 > ~/lines.txt
REPLACE_STR="icao=$OWNSHIP"
while read p ; do
  p+="s"
  sudo sed -i "$p/icao.*/$REPLACE_STR/g" /opt/stratux/www/plates/status.html
done < ~/lines.txt
rm ~/lines.txt
