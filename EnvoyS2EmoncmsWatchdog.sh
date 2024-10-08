#!/bin/bash
#
# Watchdog file for checking correct behaviour of main process
#
# coded by:
# author : Frederic Metrich
# Email : Frederic.Metrich@Live.COM

FILE="/tmp/EnvoyS2Emoncms_Watchdog"
LOGFILE="/var/log/EnvoyS2Emoncms_Watchdog.log"
PROCESS="python3 /usr/local/bin/EnvoyS2Emoncms.py"
TimeNow=$(date +%s)
ProcessID=$(ps -ef|grep -v grep|grep "$PROCESS"| awk '{print $2}')

WriteLog() {
        echo "$(date -u +'%F %T') $1" >> $LOGFILE
}

if [ -f "$FILE" ];
then
   # File exists
   TimeInWatchdogFile=`cat "$FILE"`
   TimeDifference=$((TimeNow-TimeInWatchdogFile))
   if [ "$TimeDifference" -gt "10" ] && [ "$TimeInWatchdogFile" != "" ];
   then
      # Time difference is to big  
      WriteLog "Watchdog file found."
      WriteLog "Time difference is to big ($TimeDifference), now it is $TimeNow and the file contains ($TimeInWatchdogFile)." 
	if [ -z "$ProcessID" ];
      then
	 # No process found so start it
         WriteLog "No ProcessID ($ProcessID) belonging to Process($PROCESS) found, start it!"
         $PROCESS 2>&1 >/dev/null &
      else
	 # Process seems to be running, but something is wrong so kill it, and start is afterwards
         WriteLog "ProcessID ($ProcessID) belonging to Process($PROCESS) found, but something is wrong, kill it hard, and start it!" 
         kill -9 "$ProcessID"
         $PROCESS 2>&1 >/dev/null &
      fi

   fi

else
   # File does not exist, start it if no process is running otherwise kill and start it
      WriteLog "Watchdog file does not exist" 
      if [ -z "$ProcessID" ];
      then
         # No process found so start it
         WriteLog "No ProcessID ($ProcessID) belonging to Process($PROCESS) found, start it!"
         $PROCESS 2>&1 >/dev/null &
      else
         # Process seems to be running, but something is wrong so kill it, and start is afterwards
         WriteLog "ProcessID ($ProcessID) belonging to Process($PROCESS) found, but something is wrong, kill it hard, and start it!"
         kill -9 "$ProcessID"
         $PROCESS 2>&1 >/dev/null &
      fi
fi
